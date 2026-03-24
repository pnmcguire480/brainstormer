#!/usr/bin/env python3
"""
Assemble all BrainStormer agent batch files into .md files.

Usage:
    python scripts/assemble_agents.py          # Write to agents/_staging/
    python scripts/assemble_agents.py --apply  # Replace ~/.claude/agents/
"""
import sys
import os
import shutil
import importlib.util
from pathlib import Path
from datetime import datetime
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

SCRIPTS_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPTS_DIR.parent
STAGING_DIR = PROJECT_DIR / "agents" / "_staging"
AGENTS_DIR = Path.home() / ".claude" / "agents"

# Batch files to import
BATCH_FILES = [
    'agents_backend',
    'agents_python',
    'agents_languages',
    'agents_devops',
    'agents_data',
    'agents_security_testing_sre',
    'agents_ai_arch',
    'agents_mobile_game',
    'agents_design_docs',
    'agents_business',
    'agents_meta_niche',
]


def normalize_agent(a):
    """Normalize an agent dict to standard format {filename, frontmatter, body}."""
    if 'filename' in a and 'frontmatter' in a:
        return a  # Already standard
    # Handle alternate format: {name, description, stack/category, emoji, body}
    name = a.get('name', 'unknown')
    return {
        'filename': name.lower().replace(' ', '-').replace('/', '-') + '.md',
        'frontmatter': {
            'name': name,
            'description': a.get('description', ''),
            'category': a.get('stack', a.get('category', 'general')),
            'emoji': a.get('emoji', ''),
            'source': 'brainstormer',
            'version': '1.0',
        },
        'body': a.get('body', '').strip()
    }


def load_batch(name):
    """Import a batch file and return its AGENTS list, normalized."""
    path = SCRIPTS_DIR / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception as e:
        print(f"  ERROR loading {name}: {e}")
        return []
    raw = getattr(mod, 'AGENTS', [])
    return [normalize_agent(a) for a in raw]


def load_frontend_agents():
    """Load the frontend agents defined inline."""
    # Import just the AGENTS list, avoiding Path concatenation issues
    path = SCRIPTS_DIR / "rewrite_agents.py"
    try:
        # Read and exec just the agent definitions
        content = path.read_text(encoding='utf-8')
        # Extract everything between AGENTS = [] and def main():
        start = content.find('AGENTS = []')
        end = content.find('\ndef main():')
        if start == -1 or end == -1:
            print("  Could not find AGENTS section in rewrite_agents.py")
            return []

        snippet = content[start:end]
        # Need the agent helper function too
        helper_start = content.find('def agent(')
        helper_end = content.find('\n\n', helper_start)
        helper = content[helper_start:helper_end]

        ns = {}
        exec(helper + '\n\n' + snippet, ns)
        raw = ns.get('AGENTS', [])
        return [normalize_agent(a) for a in raw]
    except Exception as e:
        print(f"  ERROR loading frontend agents: {e}")
        return []


def write_agent_md(agent_def, output_dir):
    """Write a single agent definition to a .md file."""
    filename = agent_def['filename']
    fm = agent_def['frontmatter']
    body = agent_def['body']

    lines = ['---']
    for k, v in fm.items():
        sv = str(v)
        # Quote values with special chars
        if any(c in sv for c in [':', '"', "'", '#', '{', '}', '[', ']', ',', '&', '*', '?', '|', '>', '<', '=', '!', '%', '@', '`']):
            lines.append(f'{k}: "{sv}"')
        else:
            lines.append(f'{k}: {sv}')
    lines.append('---')
    lines.append('')
    lines.append(body)
    lines.append('')

    path = output_dir / filename
    path.write_text('\n'.join(lines), encoding='utf-8')
    return path


def main():
    apply_mode = "--apply" in sys.argv

    print("=" * 60)
    print("  BrainStormer Agent Assembly")
    print("=" * 60)
    print()

    # Collect all agents
    all_agents = []

    # Frontend agents from main script
    print("Loading frontend agents...")
    frontend = load_frontend_agents()
    print(f"  {len(frontend)} frontend agents")
    all_agents.extend(frontend)

    # Batch files
    for batch_name in BATCH_FILES:
        print(f"Loading {batch_name}...")
        batch = load_batch(batch_name)
        print(f"  {len(batch)} agents")
        all_agents.extend(batch)

    print(f"\nTotal agents collected: {len(all_agents)}")

    # Check for filename collisions
    filenames = defaultdict(list)
    for a in all_agents:
        filenames[a['filename']].append(a['frontmatter']['name'])

    dupes = {k: v for k, v in filenames.items() if len(v) > 1}
    if dupes:
        print(f"\n  WARNING: {len(dupes)} filename collisions:")
        for fn, names in sorted(dupes.items()):
            print(f"    {fn}: {names}")
        # Dedupe — keep first occurrence
        seen = set()
        deduped = []
        for a in all_agents:
            if a['filename'] not in seen:
                seen.add(a['filename'])
                deduped.append(a)
            else:
                print(f"    Skipping duplicate: {a['filename']} ({a['frontmatter']['name']})")
        all_agents = deduped
        print(f"  After dedup: {len(all_agents)} agents")

    # Category breakdown
    categories = defaultdict(int)
    for a in all_agents:
        categories[a['frontmatter'].get('category', 'unknown')] += 1

    print(f"\nCategory breakdown:")
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        print(f"  {cat:25s} {count:3d}")

    # Determine output directory
    if apply_mode:
        output_dir = AGENTS_DIR
        backup_dir = AGENTS_DIR.parent / f"agents_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        print(f"\n  APPLY MODE — backing up to {backup_dir}")
        if AGENTS_DIR.exists():
            shutil.copytree(AGENTS_DIR, backup_dir)
            # Clear the agents directory
            for f in AGENTS_DIR.glob("*.md"):
                f.unlink()
        print(f"  Backup complete. Old agents preserved at {backup_dir}")
    else:
        output_dir = STAGING_DIR
        if output_dir.exists():
            shutil.rmtree(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

    # Write all agents
    print(f"\nWriting {len(all_agents)} agents to {output_dir}...")
    written = 0
    for a in all_agents:
        write_agent_md(a, output_dir)
        written += 1

    print(f"\n{'=' * 60}")
    print(f"  ASSEMBLY COMPLETE")
    print(f"{'=' * 60}")
    print(f"  Agents written:    {written}")
    print(f"  Output directory:  {output_dir}")
    print(f"  Categories:        {len(categories)}")

    if not apply_mode:
        print(f"\n  To deploy: python scripts/assemble_agents.py --apply")
        print(f"  (Will backup existing agents first)")
    else:
        print(f"\n  Agents deployed to {AGENTS_DIR}")
        print(f"  Backup at {backup_dir}")

    # Write manifest
    manifest_path = output_dir / "_manifest.txt"
    with open(manifest_path, 'w', encoding='utf-8') as f:
        f.write(f"# BrainStormer Agent Catalog — {datetime.now().isoformat()}\n")
        f.write(f"# Total: {written} agents\n\n")
        for a in sorted(all_agents, key=lambda x: x['filename']):
            fm = a['frontmatter']
            f.write(f"{a['filename']:50s} | {fm['name']:35s} | {fm.get('category',''):15s} | {fm.get('emoji','')}\n")
    print(f"  Manifest:          {manifest_path}")


if __name__ == "__main__":
    main()
