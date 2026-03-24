"""brainstormer agent — Agent management: create, test, list, run pipelines.

Usage:
    brainstormer agent list [--all]          — Show available agents
    brainstormer agent create <name>         — Scaffold a new agent
    brainstormer agent test <name>           — Validate an agent file
    brainstormer agent info <name>           — Show agent details
    brainstormer agent run <pipeline.yml>    — Run an agent pipeline
"""

import re
import subprocess
from pathlib import Path
from datetime import datetime

try:
    import yaml
except ImportError:
    yaml = None


def cmd_agent(opts: dict) -> int:
    """Execute agent subcommands."""
    positional = opts.get("positional", [])

    if not positional:
        print("\n  Usage: brainstormer agent <create|test|info|run|publish|search> [args]\n")
        return 1

    action = positional[0]
    handlers = {
        "create": _agent_create,
        "test": _agent_test,
        "info": _agent_info,
        "run": _agent_run_pipeline,
        "publish": _agent_publish,
        "search": _agent_search,
    }

    handler = handlers.get(action)
    if not handler:
        print(f"\n  Unknown agent action: {action}")
        print("  Available: create, test, info, run, publish, search\n")
        return 1

    return handler(opts)


# --- #7: Agent Builder SDK ---

AGENT_TEMPLATE = '''---
name: {name}
description: {description}
color: "#6366F1"
emoji: {emoji}
vibe: "{vibe}"
source: custom
---

# {name}

{description}

## Role

You are a specialized agent that {role_description}.

## Instructions

1. Always start by understanding the current context
2. Follow the project's existing patterns and conventions
3. Provide clear, actionable output

## When to use this agent

- {use_case_1}
- {use_case_2}
- {use_case_3}
'''


def _agent_create(opts: dict) -> int:
    """Scaffold a new agent with frontmatter template and test harness."""
    positional = opts.get("positional", [])

    if len(positional) < 2:
        print("\n  Usage: brainstormer agent create <name>")
        print("  Example: brainstormer agent create my-code-reviewer\n")
        return 1

    raw_name = positional[1]
    # Normalize to kebab-case filename
    slug = re.sub(r'[^a-z0-9]+', '-', raw_name.lower()).strip('-')
    display_name = raw_name.replace('-', ' ').title()

    try:
        from cli.core.registry import get_agents_dir
    except ImportError:
        from core.registry import get_agents_dir

    agents_dir = get_agents_dir()
    agent_file = agents_dir / f"{slug}.md"

    if agent_file.exists():
        print(f"\n  Agent already exists: {agent_file}")
        print(f"  Edit it directly or use a different name.\n")
        return 1

    # Interactive prompts with sensible defaults
    print()
    print(f"  Creating agent: {display_name}")
    print("  " + "-" * 40)
    print()

    try:
        description = input(f"  Description (1 line): ").strip()
        if not description:
            description = f"Specialized agent for {display_name.lower()} tasks"

        emoji = input("  Emoji (default: agent): ").strip()
        if not emoji:
            emoji = _suggest_emoji(slug)

        vibe = input("  Vibe/personality (1 sentence): ").strip()
        if not vibe:
            vibe = f"Thorough, precise, and focused on quality"

        role_desc = input("  What does this agent do? ").strip()
        if not role_desc:
            role_desc = f"helps with {display_name.lower()} tasks"

    except (EOFError, KeyboardInterrupt):
        print("\n  Cancelled.")
        return 1

    content = AGENT_TEMPLATE.format(
        name=display_name,
        description=description,
        emoji=emoji,
        vibe=vibe,
        role_description=role_desc,
        use_case_1=f"When you need help with {slug.replace('-', ' ')}",
        use_case_2="When the task matches this agent's specialty",
        use_case_3="When you want focused, expert-level guidance",
    )

    agents_dir.mkdir(parents=True, exist_ok=True)
    agent_file.write_text(content, encoding="utf-8")

    # Create test file alongside
    test_dir = agents_dir.parent / "agent-tests"
    test_dir.mkdir(parents=True, exist_ok=True)
    test_file = test_dir / f"test-{slug}.md"
    test_content = f"""# Test: {display_name}
**Agent:** {slug}.md
**Created:** {datetime.now().strftime("%Y-%m-%d")}

## Validation Checks
- [ ] Frontmatter is valid YAML
- [ ] Name field matches filename convention
- [ ] Description is clear and specific
- [ ] Instructions are actionable
- [ ] No placeholder text remaining

## Test Prompts
Try these prompts to verify the agent works:

1. "{description}"
2. "Help me with {slug.replace('-', ' ')} in my current project"
3. "What's the best approach for {slug.replace('-', ' ')}?"

## Notes
<!-- Add observations about agent behavior here -->
"""
    test_file.write_text(test_content, encoding="utf-8")

    print(f"\n  Agent created: {agent_file.name}")
    print(f"  Test file:     {test_file}")
    print()
    print(f"  Next steps:")
    print(f"    1. Edit {agent_file.name} to customize instructions")
    print(f"    2. Run: brainstormer agent test {slug}")
    print(f"    3. Try it: use the agent in Claude Code")
    print()
    return 0


def _agent_test(opts: dict) -> int:
    """Validate an agent file for correctness."""
    positional = opts.get("positional", [])

    if len(positional) < 2:
        print("\n  Usage: brainstormer agent test <name>\n")
        return 1

    name = positional[1]

    try:
        from cli.core.registry import get_agents_dir, parse_agent_frontmatter
    except ImportError:
        from core.registry import get_agents_dir, parse_agent_frontmatter

    agents_dir = get_agents_dir()

    # Find the agent file
    agent_file = agents_dir / f"{name}.md"
    if not agent_file.exists():
        # Try with .md already
        candidates = list(agents_dir.glob(f"*{name}*.md"))
        if candidates:
            agent_file = candidates[0]
        else:
            print(f"\n  Agent not found: {name}")
            print(f"  Searched in: {agents_dir}\n")
            return 1

    print()
    print(f"  Testing agent: {agent_file.name}")
    print("  " + "=" * 50)
    print()

    issues = []
    warnings = []

    # Read content
    content = agent_file.read_text(encoding="utf-8")

    # Check 1: Valid frontmatter
    if not content.startswith("---"):
        issues.append("Missing YAML frontmatter (must start with ---)")
    else:
        end = content.find("---", 3)
        if end == -1:
            issues.append("Unclosed frontmatter (missing closing ---)")

    # Check 2: Parse frontmatter
    agent = parse_agent_frontmatter(agent_file)
    if not agent:
        issues.append("Could not parse frontmatter")
    else:
        # Check required fields
        required = ["name", "description"]
        for field in required:
            if not agent.get(field):
                issues.append(f"Missing required field: {field}")

        # Check recommended fields
        recommended = ["emoji", "vibe", "source"]
        for field in recommended:
            if not agent.get(field):
                warnings.append(f"Missing recommended field: {field}")

        # Check name matches filename
        if agent.get("name"):
            print(f"  Name:        {agent['name']}")
        print(f"  Description: {agent.get('description', '(none)')}")
        print(f"  Source:      {agent.get('source', '(none)')}")
        print(f"  Category:    {agent.get('category', '(none)')}")
        print()

    # Check 3: Content quality
    body = content[content.find("---", 3) + 3:].strip() if content.startswith("---") else content
    if len(body) < 50:
        warnings.append("Agent body is very short (< 50 chars) — add more instructions")
    if "placeholder" in body.lower() or "TODO" in body:
        warnings.append("Contains placeholder text — customize before using")

    # Check 4: File size
    size_kb = agent_file.stat().st_size / 1024
    if size_kb > 50:
        warnings.append(f"Large file ({size_kb:.1f} KB) — consider trimming")

    # Report
    if issues:
        print(f"  FAIL — {len(issues)} issue(s):")
        for issue in issues:
            print(f"    x {issue}")
    else:
        print(f"  PASS — Frontmatter valid, required fields present")

    if warnings:
        print(f"\n  Warnings ({len(warnings)}):")
        for w in warnings:
            print(f"    ! {w}")

    print()
    return 1 if issues else 0


def _agent_info(opts: dict) -> int:
    """Show detailed info about an agent."""
    positional = opts.get("positional", [])

    if len(positional) < 2:
        print("\n  Usage: brainstormer agent info <name>\n")
        return 1

    name = positional[1]

    try:
        from cli.core.registry import get_agents_dir, parse_agent_frontmatter
    except ImportError:
        from core.registry import get_agents_dir, parse_agent_frontmatter

    agents_dir = get_agents_dir()

    # Find agent (fuzzy match)
    candidates = list(agents_dir.glob(f"*{name}*.md"))
    if not candidates:
        print(f"\n  Agent not found: {name}\n")
        return 1

    agent_file = candidates[0]
    agent = parse_agent_frontmatter(agent_file)
    content = agent_file.read_text(encoding="utf-8")

    print()
    print(f"  {agent.get('emoji', '')} {agent.get('name', agent_file.stem)}")
    print("  " + "=" * 50)
    print()
    print(f"  Description: {agent.get('description', '(none)')}")
    print(f"  Category:    {agent.get('category', '(none)')}")
    print(f"  Source:      {agent.get('source', '(none)')}")
    print(f"  Vibe:        {agent.get('vibe', '(none)')}")
    print(f"  File:        {agent_file}")
    print(f"  Size:        {agent_file.stat().st_size / 1024:.1f} KB")

    # Count sections
    headings = re.findall(r'^#{1,3}\s+(.+)$', content, re.MULTILINE)
    print(f"  Sections:    {len(headings)}")

    print()
    return 0


# --- #6: Agent Pipelines ---

def _agent_run_pipeline(opts: dict) -> int:
    """Run an agent pipeline defined in YAML."""
    positional = opts.get("positional", [])

    if len(positional) < 2:
        print("\n  Usage: brainstormer agent run <pipeline.yml>")
        print("  Example: brainstormer agent run security-review.yml\n")
        return 1

    pipeline_path = Path(positional[1])
    if not pipeline_path.exists():
        # Check in .brainstormer/pipelines/
        alt = Path.home() / ".brainstormer" / "pipelines" / positional[1]
        if alt.exists():
            pipeline_path = alt
        else:
            print(f"\n  Pipeline not found: {positional[1]}")
            print(f"  Searched: ./{positional[1]} and ~/.brainstormer/pipelines/\n")
            return 1

    # Parse pipeline
    pipeline = _parse_pipeline(pipeline_path)
    if not pipeline:
        print(f"\n  Could not parse pipeline: {pipeline_path}\n")
        return 1

    name = pipeline.get("name", pipeline_path.stem)
    steps = pipeline.get("steps", [])

    if not steps:
        print(f"\n  Pipeline '{name}' has no steps.\n")
        return 1

    print()
    print(f"  Running pipeline: {name}")
    print(f"  Steps: {len(steps)}")
    print("  " + "=" * 50)
    print()

    # Validate all agents exist before running
    try:
        from cli.core.registry import get_agents_dir
    except ImportError:
        from core.registry import get_agents_dir

    agents_dir = get_agents_dir()
    for i, step in enumerate(steps):
        agent_name = step.get("agent", "")
        agent_file = agents_dir / f"{agent_name}.md"
        if not agent_file.exists():
            # Fuzzy match
            matches = list(agents_dir.glob(f"*{agent_name}*.md"))
            if not matches:
                print(f"  Step {i+1}: Agent not found: {agent_name}")
                print(f"  Pipeline aborted.\n")
                return 1
            step["_resolved_file"] = matches[0]
        else:
            step["_resolved_file"] = agent_file

    # Execute pipeline
    context = {}
    results = []

    for i, step in enumerate(steps):
        agent_name = step.get("agent", "unknown")
        agent_file = step["_resolved_file"]
        output_key = step.get("output", f"step_{i+1}")
        input_keys = step.get("input", [])
        if isinstance(input_keys, str):
            input_keys = [input_keys]

        print(f"  Step {i+1}/{len(steps)}: {agent_name}")

        # Build input context
        step_input = ""
        for key in input_keys:
            if key in context:
                step_input += f"\n--- Input from {key} ---\n{context[key]}\n"

        # Read agent instructions
        agent_content = agent_file.read_text(encoding="utf-8")
        # Strip frontmatter for the instruction body
        if agent_content.startswith("---"):
            end = agent_content.find("---", 3)
            if end != -1:
                agent_body = agent_content[end + 3:].strip()
            else:
                agent_body = agent_content
        else:
            agent_body = agent_content

        # For now, pipelines prepare the context but don't execute AI calls
        # They produce a structured prompt that can be fed to Claude Code
        output = f"[Agent: {agent_name}]\n"
        output += f"[Instructions: {len(agent_body)} chars]\n"
        if step_input:
            output += f"[Input context: {len(step_input)} chars from {', '.join(input_keys)}]\n"

        context[output_key] = output
        results.append({
            "step": i + 1,
            "agent": agent_name,
            "output_key": output_key,
            "agent_file": str(agent_file),
            "instruction_size": len(agent_body),
        })

        print(f"    -> {output_key} ({len(agent_body)} chars instructions)")

    # Write pipeline manifest
    print()
    print("  Pipeline complete. Results:")
    print()

    manifest_lines = [
        f"# Pipeline: {name}",
        f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"Steps: {len(steps)}",
        "",
    ]

    for r in results:
        manifest_lines.append(f"## Step {r['step']}: {r['agent']}")
        manifest_lines.append(f"- Agent file: `{r['agent_file']}`")
        manifest_lines.append(f"- Output key: `{r['output_key']}`")
        manifest_lines.append(f"- Instructions: {r['instruction_size']} chars")
        manifest_lines.append("")

    manifest_lines.append("## How to execute")
    manifest_lines.append("")
    manifest_lines.append("Use each agent in Claude Code with the context from previous steps:")
    manifest_lines.append("")
    for r in results:
        agent = r['agent']
        manifest_lines.append(f"{r['step']}. Invoke `{agent}` agent")

    manifest = "\n".join(manifest_lines)

    # Save manifest
    output_dir = Path.cwd() / "brainstormer"
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_file = output_dir / f"pipeline-{pipeline_path.stem}.md"
    manifest_file.write_text(manifest, encoding="utf-8")

    print(f"  Manifest saved: {manifest_file}")
    print(f"  Follow the steps to execute each agent in sequence.\n")
    return 0


def _parse_pipeline(path: Path) -> dict:
    """Parse a pipeline YAML file."""
    content = path.read_text(encoding="utf-8")

    if yaml:
        try:
            return yaml.safe_load(content)
        except Exception:
            pass

    # Minimal YAML parser for pipeline files
    pipeline = {"name": path.stem, "steps": []}

    current_step = None
    for line in content.split("\n"):
        line_stripped = line.strip()

        if line_stripped.startswith("name:"):
            pipeline["name"] = line_stripped.split(":", 1)[1].strip().strip('"').strip("'")
        elif line_stripped.startswith("- agent:"):
            if current_step:
                pipeline["steps"].append(current_step)
            current_step = {"agent": line_stripped.split(":", 1)[1].strip()}
        elif current_step and line_stripped.startswith("output:"):
            current_step["output"] = line_stripped.split(":", 1)[1].strip()
        elif current_step and line_stripped.startswith("input:"):
            val = line_stripped.split(":", 1)[1].strip()
            # Handle list or string
            if val.startswith("["):
                current_step["input"] = [
                    s.strip().strip('"').strip("'")
                    for s in val.strip("[]").split(",")
                ]
            else:
                current_step["input"] = val

    if current_step:
        pipeline["steps"].append(current_step)

    return pipeline


# --- #14: Agent Marketplace ---

MARKETPLACE_DIR = Path.home() / ".brainstormer" / "marketplace"
MARKETPLACE_INDEX = MARKETPLACE_DIR / "index.json"


def _agent_publish(opts: dict) -> int:
    """Publish an agent to the local marketplace registry."""
    positional = opts.get("positional", [])

    if len(positional) < 2:
        print("\n  Usage: brainstormer agent publish <name>")
        print("  Publishes your custom agent to the marketplace registry.\n")
        return 1

    name = positional[1]

    try:
        from cli.core.registry import get_agents_dir, parse_agent_frontmatter
    except ImportError:
        from core.registry import get_agents_dir, parse_agent_frontmatter

    agents_dir = get_agents_dir()

    # Find agent
    agent_file = agents_dir / f"{name}.md"
    if not agent_file.exists():
        candidates = list(agents_dir.glob(f"*{name}*.md"))
        if candidates:
            agent_file = candidates[0]
        else:
            print(f"\n  Agent not found: {name}\n")
            return 1

    # Validate first
    agent = parse_agent_frontmatter(agent_file)
    if not agent:
        print(f"\n  Could not parse agent: {agent_file.name}")
        print("  Run 'brainstormer agent test' first.\n")
        return 1

    if agent.get("source") != "custom":
        print(f"\n  Can only publish custom agents (source: custom).")
        print(f"  This agent's source is: {agent.get('source', 'unknown')}\n")
        return 1

    # Copy to marketplace
    MARKETPLACE_DIR.mkdir(parents=True, exist_ok=True)
    dest = MARKETPLACE_DIR / agent_file.name
    content = agent_file.read_text(encoding="utf-8")
    dest.write_text(content, encoding="utf-8")

    # Update index
    index = _load_marketplace_index()
    index[agent_file.stem] = {
        "name": agent.get("name", agent_file.stem),
        "description": agent.get("description", ""),
        "emoji": agent.get("emoji", ""),
        "category": agent.get("category", "custom"),
        "published": datetime.now().isoformat(),
        "filename": agent_file.name,
    }
    _save_marketplace_index(index)

    print(f"\n  Published: {agent.get('name', agent_file.stem)}")
    print(f"  Registry: ~/.brainstormer/marketplace/")
    print(f"  Total published: {len(index)} agents")
    print()
    print(f"  Share the file: {dest}")
    print(f"  Others can install: copy to ~/.claude/agents/\n")
    return 0


def _agent_search(opts: dict) -> int:
    """Search installed agents by keyword."""
    positional = opts.get("positional", [])

    if len(positional) < 2:
        print("\n  Usage: brainstormer agent search <keyword>")
        print("  Example: brainstormer agent search security\n")
        return 1

    query = " ".join(positional[1:]).lower()

    try:
        from cli.core.registry import list_agents
    except ImportError:
        from core.registry import list_agents

    all_agents = list_agents(show_all=True)
    matches = []

    for a in all_agents:
        searchable = " ".join([
            a.get("name", ""),
            a.get("description", ""),
            a.get("category", ""),
            a.get("vibe", ""),
        ]).lower()

        if query in searchable:
            matches.append(a)

    if not matches:
        print(f"\n  No agents found matching: {query}\n")
        return 0

    print(f"\n  Search results for: {query}")
    print(f"  Found: {len(matches)} agents")
    print("  " + "=" * 50)
    print()

    for a in matches[:25]:
        emoji = a.get("emoji", "")
        name = a.get("name", a["filename"])
        desc = a.get("description", "")[:55]
        source = a.get("source", "")
        print(f"  {emoji} {name:<30s} {desc}")
        if source:
            print(f"    {'':30s} [{source}]")

    if len(matches) > 25:
        print(f"\n  ... and {len(matches) - 25} more. Refine your search.")

    print()
    return 0


def _load_marketplace_index() -> dict:
    """Load the marketplace index."""
    if not MARKETPLACE_INDEX.exists():
        return {}
    try:
        import json
        return json.loads(MARKETPLACE_INDEX.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_marketplace_index(index: dict):
    """Save the marketplace index."""
    import json
    MARKETPLACE_DIR.mkdir(parents=True, exist_ok=True)
    MARKETPLACE_INDEX.write_text(
        json.dumps(index, indent=2), encoding="utf-8"
    )


def _suggest_emoji(slug: str) -> str:
    """Suggest an emoji based on agent name."""
    emoji_map = {
        "review": "🔍", "test": "🧪", "security": "🔒", "debug": "🐛",
        "deploy": "🚀", "docs": "📝", "design": "🎨", "data": "📊",
        "api": "🔌", "database": "🗄️", "performance": "⚡", "build": "🔨",
        "lint": "✨", "format": "📐", "migrate": "🔄", "monitor": "📡",
    }
    for key, emoji in emoji_map.items():
        if key in slug:
            return emoji
    return "🤖"
