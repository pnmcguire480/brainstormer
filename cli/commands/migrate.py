"""brainstormer migrate — Import existing AI tool configurations."""

import re
from pathlib import Path
from datetime import datetime


# Files to detect and import from other AI tools
MIGRATE_SOURCES = {
    ".cursorrules": {
        "tool": "Cursor",
        "target": "CLAUDE.md",
        "section": "Imported from Cursor",
    },
    ".windsurfrules": {
        "tool": "Windsurf",
        "target": "CLAUDE.md",
        "section": "Imported from Windsurf",
    },
    ".github/copilot-instructions.md": {
        "tool": "GitHub Copilot",
        "target": "CLAUDE.md",
        "section": "Imported from GitHub Copilot",
    },
    ".aider.conf.yml": {
        "tool": "Aider",
        "target": "CLAUDE.md",
        "section": "Imported from Aider",
    },
    ".aider.model.settings.yml": {
        "tool": "Aider",
        "target": "CLAUDE.md",
        "section": "Imported from Aider (model settings)",
    },
    "AGENTS.md": {
        "tool": "Existing project",
        "target": "AGENTS.md",
        "section": None,
    },
}


def cmd_migrate(opts: dict) -> int:
    """Import existing AI tool configurations."""
    project_root = Path.cwd()
    dry_run = opts.get("dry_run", False)
    force = opts.get("force", False)

    print()
    print("  BrainStormer Migrate")
    print("  " + "=" * 50)
    print()

    # Scan for importable files
    found = {}
    for source_path, meta in MIGRATE_SOURCES.items():
        full_path = project_root / source_path
        if full_path.exists():
            found[source_path] = meta

    if not found:
        print("  No AI tool configurations found to import.")
        print()
        print("  Looked for:")
        for source_path, meta in MIGRATE_SOURCES.items():
            print(f"    - {source_path} ({meta['tool']})")
        print()
        return 0

    # Report what was found
    print(f"  Found {len(found)} importable configuration(s):")
    print()
    for source_path, meta in found.items():
        full_path = project_root / source_path
        size = full_path.stat().st_size
        print(f"    {meta['tool']:<25s} {source_path} ({size} bytes)")
    print()

    if dry_run:
        print("  --dry-run: No changes made.")
        print()
        return 0

    # Import each file
    imported = 0
    for source_path, meta in found.items():
        full_path = project_root / source_path
        target = meta["target"]
        section = meta["section"]

        try:
            content = full_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            print(f"    ! Could not read {source_path}: {e}")
            continue

        if not content.strip():
            print(f"    - {source_path}: empty, skipping")
            continue

        target_path = project_root / target

        if target == "CLAUDE.md":
            _merge_into_claude_md(target_path, content, section, force)
            imported += 1
            print(f"    + {source_path} -> {target} (merged)")
        elif target_path.exists() and not force:
            print(f"    - {target} already exists (use --force to overwrite)")
        else:
            target_path.write_text(content, encoding="utf-8")
            imported += 1
            print(f"    + {source_path} -> {target}")

    print()
    if imported:
        print(f"  ✅ Imported {imported} configuration(s).")
        print()
        print("  Review the imported content in CLAUDE.md and adjust as needed.")
        print("  Original files were NOT deleted — remove them manually when ready.")
    else:
        print("  No changes made.")
    print()
    return 0


def _merge_into_claude_md(claude_md_path: Path, content: str, section: str, force: bool):
    """Merge imported content into CLAUDE.md under a labeled section."""
    marker_start = f"<!-- BRAINSTORMER IMPORT: {section} -->"
    marker_end = f"<!-- END BRAINSTORMER IMPORT: {section} -->"

    import_block = (
        f"\n\n{marker_start}\n"
        f"## {section}\n\n"
        f"*Imported by `brainstormer migrate` on {datetime.now().strftime('%Y-%m-%d')}*\n\n"
        f"{content.strip()}\n\n"
        f"{marker_end}\n"
    )

    if claude_md_path.exists():
        existing = claude_md_path.read_text(encoding="utf-8")

        # Check if this section was already imported
        if marker_start in existing:
            if force:
                # Replace existing import block
                pattern = re.escape(marker_start) + r".*?" + re.escape(marker_end)
                existing = re.sub(pattern, import_block.strip(), existing, flags=re.DOTALL)
                claude_md_path.write_text(existing, encoding="utf-8")
            # else: skip, already imported
            return

        # Append to end
        claude_md_path.write_text(existing + import_block, encoding="utf-8")
    else:
        # Create new CLAUDE.md with just the import
        header = (
            f"# Project Intelligence\n\n"
            f"*Created by `brainstormer migrate`*\n"
        )
        claude_md_path.write_text(header + import_block, encoding="utf-8")
