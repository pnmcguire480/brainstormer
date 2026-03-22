#!/usr/bin/env python3
"""BrainStormer CLI — The AI Development Operating System.

Usage:
    brainstormer init [--name NAME] [--minimal] [--update] [--no-obsidian]
    brainstormer status
    brainstormer doctor
    brainstormer sync
    brainstormer update [--all]
    brainstormer quality run
    brainstormer quality bootstrap [--dry-run]
    brainstormer agent list [--all]
    brainstormer config set <key> <value>
    brainstormer config get <key>
    brainstormer help [<command>]
"""

import sys
import os
from pathlib import Path

# Fix console encoding for emoji output (all platforms)
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, OSError):
    pass

# Support both direct execution and installed package imports
try:
    from cli.commands.init import cmd_init
    from cli.commands.status import cmd_status
    from cli.commands.doctor import cmd_doctor
    from cli.commands.sync import cmd_sync
    from cli.commands.update import cmd_update
    from cli.commands.migrate import cmd_migrate
    from cli.commands.license_cmd import cmd_license
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from commands.init import cmd_init
    from commands.status import cmd_status
    from commands.doctor import cmd_doctor
    from commands.sync import cmd_sync
    from commands.update import cmd_update
    from commands.migrate import cmd_migrate
    from commands.license_cmd import cmd_license


HELP_TEXT = """
BrainStormer — The AI Development Operating System
Drop in. Init. Ship.

Commands:
  init          Set up BrainStormer in the current project
  status        Show what's configured and what's missing
  doctor        Validate setup, diagnose issues
  sync          Push project state to Obsidian vault
  update        Update BrainStormer and re-sync templates
  migrate       Import .cursorrules, .windsurfrules, existing configs
  quality run   Run PALADIN quality tiers 1-5
  quality bootstrap  Install missing test infrastructure
  agent list    Show available agents for this project
  license       Show, activate, or deactivate your license
  config        Get or set configuration values
  help          Show this help or command-specific help

Options:
  --name NAME       Set project name explicitly (default: folder name)
  --minimal         Kernel only (just the 10 docs)
  --update          Re-sync without overwriting customized files
  --no-obsidian     Skip Obsidian vault sync
  --all             Apply to all registered projects (for update)
  --dry-run         Show what would happen without doing it

Examples:
  brainstormer init
  brainstormer init --name "My Project" --minimal
  brainstormer status
  brainstormer doctor
  brainstormer sync
"""

COMMAND_HELP = {
    "init": """
brainstormer init — Set up BrainStormer in the current project

Phases:
  1. Detect    — Read project root, detect stack, check existing files
  2. Kernel    — Scaffold 10 template files (skip existing)
  3. Comprehension — Set up CodeGlass walkthroughs + rules
  4. Ideation  — Set up BrainStormer output directory + ruleset
  5. Quality   — Create PALADIN config, detect missing test tools
  6. Obsidian  — Sync project to your Obsidian vault

Options:
  --name NAME       Set project name (default: current folder name)
  --minimal         Only run Kernel phase (the 10 docs)
  --update          Re-sync templates without overwriting customized files
  --no-obsidian     Skip the Obsidian sync phase

Idempotent: Running init twice produces no changes on the second run.
""",
    "status": """
brainstormer status — Show what's configured and what's missing

Checks for:
  - Kernel files (10 templates)
  - Comprehension setup (rules.md, docs/codeglass/)
  - Ideation setup (brainstormer/ directory)
  - Quality setup (paladin.config.json)
  - Obsidian vault connection
""",
    "doctor": """
brainstormer doctor — Validate setup and diagnose issues

Checks:
  - All expected files exist
  - Config files are valid
  - Obsidian vault is accessible
  - Template versions match current BrainStormer version
  - No common misconfigurations
""",
    "sync": """
brainstormer sync — Push project state to Obsidian vault

One-way sync: project files -> Obsidian vault
User annotations in Obsidian (<!-- USER NOTES --> blocks) are preserved.
""",
    "migrate": """
brainstormer migrate — Import existing AI tool configurations

Detects and imports:
  .cursorrules        Cursor AI rules
  .windsurfrules      Windsurf rules
  .github/copilot-instructions.md  GitHub Copilot instructions
  .aider*             Aider config files
  CLAUDE.md           Existing Claude Code instructions (merges, doesn't overwrite)

Options:
  --dry-run           Show what would be imported without making changes
  --force             Overwrite existing files instead of merging
""",
    "license": """
brainstormer license — Manage your BrainStormer license

Usage:
  brainstormer license                  Show current license tier and status
  brainstormer license activate <key>   Activate a license key
  brainstormer license deactivate       Remove license, revert to free tier
  brainstormer license status           Show detailed license info

Tiers:
  Community (free)   1 project, 10 agents, no vault sync
  Pro                Unlimited projects/agents, vault sync, priority updates
  Team               Pro + shared configs, team agent library
  Enterprise         SSO, audit logging, air-gapped, custom agents
""",
    "agent": """
brainstormer agent list — Show available agents for this project

Detects your project stack and shows the most relevant agents.
Use --all to see the full catalog of 735+ agents.

Options:
  --all               Show all agents, not just stack-relevant ones
""",
}


def parse_args(argv):
    """Parse command-line arguments into command + options."""
    if not argv:
        return "help", {}

    command = argv[0]
    opts = {}

    # Handle subcommands
    if command == "quality" and len(argv) > 1:
        command = f"quality-{argv[1]}"
        argv = argv[2:]
    elif command == "agent" and len(argv) > 1:
        command = f"agent-{argv[1]}"
        argv = argv[2:]
    elif command == "config" and len(argv) > 1:
        command = f"config-{argv[1]}"
        argv = argv[2:]
    elif command == "license":
        # license keeps its subcommand as a positional arg
        argv = argv[1:]
    else:
        argv = argv[1:]

    # Parse flags
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--name" and i + 1 < len(argv):
            opts["name"] = argv[i + 1]
            i += 2
        elif arg == "--minimal":
            opts["minimal"] = True
            i += 1
        elif arg == "--update":
            opts["update"] = True
            i += 1
        elif arg == "--no-obsidian":
            opts["no_obsidian"] = True
            i += 1
        elif arg == "--all":
            opts["all"] = True
            i += 1
        elif arg == "--dry-run":
            opts["dry_run"] = True
            i += 1
        elif arg == "--json":
            opts["json"] = True
            i += 1
        elif arg == "--force":
            opts["force"] = True
            i += 1
        else:
            opts.setdefault("positional", []).append(arg)
            i += 1

    return command, opts


def run(argv=None):
    """Main entry point."""
    if argv is None:
        argv = sys.argv[1:]

    command, opts = parse_args(argv)

    if command == "help":
        positional = opts.get("positional", [])
        if positional and positional[0] in COMMAND_HELP:
            print(COMMAND_HELP[positional[0]])
        else:
            print(HELP_TEXT)
        return 0

    commands = {
        "init": cmd_init,
        "status": cmd_status,
        "doctor": cmd_doctor,
        "sync": cmd_sync,
        "update": cmd_update,
        "migrate": cmd_migrate,
        "license": cmd_license,
        "agent-list": lambda opts: _cmd_agent_list(opts),
    }

    handler = commands.get(command)
    if not handler:
        print(f"Unknown command: {command}")
        print("Run 'brainstormer help' for usage.")
        return 1

    return handler(opts)


def _cmd_agent_list(opts: dict) -> int:
    """Show available agents with progressive disclosure."""
    try:
        from cli.core.detector import detect_project
        from cli.core.registry import list_agents, count_agents, get_top_agents
        from cli.core.license import get_tier_capabilities
    except ImportError:
        from core.detector import detect_project
        from core.registry import list_agents, count_agents, get_top_agents
        from core.license import get_tier_capabilities

    project_root = Path.cwd()
    info = detect_project(project_root)
    show_all = opts.get("all", False)
    total = count_agents()
    caps = get_tier_capabilities()
    agent_limit = caps["max_agents"]

    print()
    print(f"  Agents for: {info.name} ({info.summary})")
    print("  " + "=" * 50)
    print()

    if show_all:
        if agent_limit != -1:
            print(f"  Community tier: showing up to {agent_limit} agents.")
            print(f"  Upgrade to Pro for the full catalog of {total}.")
            print()

        agents = list_agents(show_all=True)
        if agent_limit != -1:
            agents = agents[:agent_limit]

        # Group by category
        categories = {}
        for a in agents:
            cat = a.get("category", "general")
            categories.setdefault(cat, []).append(a)

        for cat in sorted(categories):
            print(f"  [{cat}]")
            for a in categories[cat][:20]:
                emoji = a.get("emoji", "")
                name = a.get("name", a["filename"])
                desc = a.get("description", "")[:60]
                print(f"    {emoji} {name:<30s} {desc}")
            if len(categories[cat]) > 20:
                print(f"    ... and {len(categories[cat]) - 20} more")
            print()

        print(f"  Total: {len(agents)} agents")
    else:
        # Progressive disclosure: show top 10 for this stack
        stack = info.framework or info.stack or "general"
        limit = min(10, agent_limit) if agent_limit != -1 else 10
        top = get_top_agents(stack, limit=limit)

        if top:
            print("  Recommended for your stack:")
            print()
            for a in top:
                emoji = a.get("emoji", "")
                name = a.get("name", a["filename"])
                desc = a.get("description", "")[:60]
                print(f"    {emoji} {name:<30s} {desc}")
            print()
            print(f"  Showing {len(top)} of {total} agents.")
        else:
            print(f"  {total} agents available (no stack-specific recommendations).")

        print(f"  Run 'brainstormer agent list --all' to see the full catalog.")

    print()
    return 0


def main():
    try:
        sys.exit(run())
    except KeyboardInterrupt:
        print("\n  Cancelled.")
        sys.exit(130)
    except Exception as e:
        _handle_error(e)
        sys.exit(1)


def _handle_error(e: Exception):
    """Print a user-friendly error message without tracebacks."""
    error_type = type(e).__name__

    # Categorize errors into user-fixable vs system issues
    if isinstance(e, FileNotFoundError):
        print(f"\n  ❌ File not found: {e.filename or e}")
        print("  Check that the path exists and you have permission to access it.")
    elif isinstance(e, PermissionError):
        print(f"\n  ❌ Permission denied: {e.filename or e}")
        print("  Try running with elevated permissions or check file ownership.")
    elif isinstance(e, (IsADirectoryError, NotADirectoryError)):
        print(f"\n  ❌ Path error: {e}")
    elif isinstance(e, OSError) and hasattr(e, 'errno'):
        print(f"\n  ❌ System error: {e}")
        print("  This may be a disk, network, or permission issue.")
    elif isinstance(e, UnicodeDecodeError):
        print(f"\n  ❌ Encoding error: Could not read file (not UTF-8)")
        print("  BrainStormer expects UTF-8 encoded files.")
    elif isinstance(e, ImportError):
        print(f"\n  ❌ Missing dependency: {e.name or e}")
        print("  Try: pip install brainstormer --upgrade")
    else:
        print(f"\n  ❌ Unexpected error: {e}")
        print(f"  ({error_type})")

    # Always show where to get help
    print()
    print("  Run 'brainstormer doctor' to diagnose issues.")
    print("  Report bugs: https://github.com/brainstormer-dev/brainstormer/issues")


if __name__ == "__main__":
    main()
