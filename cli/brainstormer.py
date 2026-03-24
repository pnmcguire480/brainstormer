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
    brainstormer learn [rule|walkthrough|scan|status]
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
    from cli.commands.learn import cmd_learn
    from cli.commands.summary import cmd_summary
    from cli.commands.agent import cmd_agent
    from cli.commands.hooks import cmd_hooks
    from cli.commands.team import cmd_team
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from commands.init import cmd_init
    from commands.status import cmd_status
    from commands.doctor import cmd_doctor
    from commands.sync import cmd_sync
    from commands.update import cmd_update
    from commands.migrate import cmd_migrate
    from commands.license_cmd import cmd_license
    from commands.learn import cmd_learn
    from commands.summary import cmd_summary
    from commands.agent import cmd_agent
    from commands.hooks import cmd_hooks
    from commands.team import cmd_team


HELP_TEXT = """
BrainStormer — The AI Development Operating System
Drop in. Init. Ship.

Commands:
  init              Set up BrainStormer in the current project
  status            Show what's configured and what's missing
  doctor            Validate setup, diagnose issues
  sync              Push project state to Obsidian vault
  update            Update BrainStormer and re-sync templates
  update check      Check for new releases
  update channel    View or set release channel (stable/preview)
  update rollback   Show how to revert to previous version
  migrate           Import .cursorrules, .windsurfrules, existing configs
  quality run       Run PALADIN quality tiers 1-5
  quality bootstrap Install missing test infrastructure
  agent list        Show available agents for this project
  agent create      Scaffold a new custom agent
  agent test        Validate an agent file
  agent info        Show agent details
  agent run         Run an agent pipeline (YAML)
  license           Show, activate, or deactivate your license
  learn             Auto-learn: rules from diffs, pattern detection, confidence tracking
  summary           Auto-generate daily journal in Obsidian with keyword linking
  hooks             Install git hooks (PALADIN pre-commit, auto-learn post-commit)
  team              Team rulesets, rule templates, and shared configuration
  telemetry         View or toggle anonymous usage telemetry
  config            Get or set configuration values
  help              Show this help or command-specific help

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
  Community (free)   3 projects, all agents, one-way vault sync
  Pro ($12/mo)       Unlimited projects, agent creation, pipelines,
                     bi-directional sync, team features, preview channel
  Team               Pro + shared configs, team agent library
  Enterprise         SSO, audit logging, air-gapped, custom agents
""",
    "update": """
brainstormer update — Update BrainStormer and re-sync templates

Subcommands:
  brainstormer update                Check templates + new releases
  brainstormer update check          Check for new releases only
  brainstormer update channel        View current release channel
  brainstormer update channel stable  Set channel to stable (weekly GA)
  brainstormer update channel preview Set channel to preview (next-week builds)
  brainstormer update rollback       Show how to revert to previous version
""",
    "telemetry": """
brainstormer telemetry — Manage anonymous usage telemetry

Usage:
  brainstormer telemetry             Show current status
  brainstormer telemetry on          Enable anonymous telemetry
  brainstormer telemetry off         Disable and delete stored events

Telemetry is OFF by default. When enabled, collects:
  - Command names (e.g., "init", "status")
  - Success/failure and error types
  - OS, Python version, BrainStormer version
  - Anonymous machine ID

NEVER collects: code, file contents, paths, API keys, or project names.
""",
    "learn": """
brainstormer learn — Capture knowledge from coding sessions

The write side of the auto-research loop. Every correction, lesson, and
walkthrough gets deposited so the next session starts smarter.

Subcommands:
  brainstormer learn              Show knowledge status (global + project rules)
  brainstormer learn rule         Add a rule interactively (to project)
  brainstormer learn rule --global        Add a rule to global rules (~/.brainstormer/)
  brainstormer learn rule --from-diff HEAD~1  Auto-propose rules from git diff
  brainstormer learn walkthrough          Create a walkthrough template
  brainstormer learn walkthrough --from-diff HEAD~1  Generate walkthrough from diff
  brainstormer learn scan                 Import rules/walkthroughs from Obsidian vault
  brainstormer learn scan --detect        Detect recurring patterns from recent commits
  brainstormer learn prune                Flag stale or low-confidence rules
  brainstormer learn status               Same as 'brainstormer learn' (default)

Global rules (~/.brainstormer/rules.md) apply to ALL projects.
Project rules (./rules.md) can override global rules by name.

The compounding loop:
  Code → Diff analyzed → Rules auto-proposed → Confidence tracked
  → Stale rules pruned → Patterns detected → Knowledge compounds
""",
    "summary": """
brainstormer summary — Auto-generated daily journal in Obsidian

Captures session summaries with auto-linked keywords organized by date.
Zero-effort mode with Claude Code stop hook.

Subcommands:
  brainstormer summary              Generate a summary for this session
  brainstormer summary --auto       Fully automatic (for Claude Code hooks)
  brainstormer summary rollup       Generate today's daily rollup
  brainstormer summary status       Show summary journal stats

Hook setup (zero effort):
  Add to .claude/settings.json:
  { "hooks": { "stop": [{ "command": "brainstormer summary --auto" }] } }

Keywords are auto-linked from 6 sources:
  Projects, Skills, Commands, Concepts, People, Vault notes
""",
    "agent": """
brainstormer agent — Agent management

Subcommands:
  brainstormer agent list [--all]       Show available agents (stack-filtered)
  brainstormer agent create <name>      Scaffold a new custom agent
  brainstormer agent test <name>        Validate agent frontmatter and content
  brainstormer agent info <name>        Show agent details
  brainstormer agent run <pipeline.yml> Run a multi-agent pipeline

Agent Builder SDK:
  1. brainstormer agent create my-reviewer   — scaffold agent + test file
  2. Edit ~/.claude/agents/my-reviewer.md    — customize instructions
  3. brainstormer agent test my-reviewer     — validate
  4. Use in Claude Code as a subagent

Agent Pipelines:
  Define multi-agent workflows in YAML:
    name: security-review
    steps:
      - agent: security-engineer
        output: security_report
      - agent: test-automator
        input: security_report
        output: test_plan
  Run: brainstormer agent run security-review.yml
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
        subcmd = argv[1]
        if subcmd in ("create", "test", "info", "run", "publish", "search"):
            # Route to new agent command module with subcommand as positional
            command = "agent"
            argv = argv[1:]  # keep subcommand + args as positional
        else:
            command = f"agent-{subcmd}"
            argv = argv[2:]
    elif command == "config" and len(argv) > 1:
        command = f"config-{argv[1]}"
        argv = argv[2:]
    elif command == "license":
        # license keeps its subcommand as a positional arg
        argv = argv[1:]
    elif command == "learn":
        # learn keeps its subcommand as a positional arg
        argv = argv[1:]
    elif command == "summary":
        # summary keeps its subcommand as a positional arg
        argv = argv[1:]
    elif command == "hooks":
        # hooks keeps its subcommand as a positional arg
        argv = argv[1:]
    elif command == "team":
        # team keeps its subcommand as a positional arg
        argv = argv[1:]
    elif command == "telemetry":
        # telemetry keeps its subcommand as a positional arg
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
        "learn": cmd_learn,
        "summary": cmd_summary,
        "agent": cmd_agent,
        "hooks": cmd_hooks,
        "team": cmd_team,
        "telemetry": lambda opts: _cmd_telemetry(opts),
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
    except ImportError:
        from core.detector import detect_project
        from core.registry import list_agents, count_agents, get_top_agents

    project_root = Path.cwd()
    info = detect_project(project_root)
    show_all = opts.get("all", False)
    total = count_agents()

    print()
    print(f"  Agents for: {info.name} ({info.summary})")
    print("  " + "=" * 50)
    print()

    if show_all:
        agents = list_agents(show_all=True)

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
        top = get_top_agents(stack, limit=10)

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


def _cmd_telemetry(opts: dict) -> int:
    """Handle telemetry subcommands."""
    try:
        from core.telemetry import (
            is_enabled, opt_in, opt_out, format_telemetry_status, flush_events,
        )
    except ImportError:
        from cli.core.telemetry import (
            is_enabled, opt_in, opt_out, format_telemetry_status, flush_events,
        )

    positional = opts.get("positional", [])

    if not positional:
        print()
        print("  BrainStormer Telemetry")
        print("  " + "=" * 50)
        print()
        print(format_telemetry_status())
        print()
        return 0

    action = positional[0]

    if action == "on":
        opt_in()
        print("\n  Telemetry enabled. Thank you for helping improve BrainStormer!")
        print("  Only anonymous usage data is collected. Never code or file contents.")
        print("  Disable anytime: brainstormer telemetry off\n")
        return 0

    if action == "off":
        opt_out()
        print("\n  Telemetry disabled. All stored events deleted.\n")
        return 0

    if action == "flush":
        count = flush_events()
        print(f"\n  Sent {count} events.\n")
        return 0

    if action == "insights":
        return _cmd_telemetry_insights()

    print("\n  Usage:")
    print("    brainstormer telemetry           Show status")
    print("    brainstormer telemetry on        Enable")
    print("    brainstormer telemetry off       Disable")
    print("    brainstormer telemetry insights  Personal usage insights\n")
    return 1


def _cmd_telemetry_insights() -> int:
    """Show personal usage insights from telemetry data."""
    try:
        from core.telemetry import get_insights, is_enabled
    except ImportError:
        from cli.core.telemetry import get_insights, is_enabled

    if not is_enabled():
        print("\n  Telemetry is disabled. Enable first: brainstormer telemetry on\n")
        return 0

    insights = get_insights()
    if not insights:
        print("\n  No telemetry data yet. Use BrainStormer for a while first.\n")
        return 0

    print()
    print("  BrainStormer — Personal Usage Insights")
    print("  " + "=" * 50)
    print()
    print(f"  Total commands:  {insights['total_events']}")
    print(f"  Success rate:    {insights['success_rate']:.0%}")
    print(f"  Days active:     {insights['days_active']}")
    print(f"  Avg per day:     {insights['avg_per_day']:.1f}")
    print()

    if insights.get("top_commands"):
        print("  Most used commands:")
        for cmd, count in insights["top_commands"]:
            bar = "#" * min(count, 30)
            print(f"    {cmd:<15s} {count:>4d}  {bar}")
        print()

    if insights.get("top_errors"):
        print("  Common errors:")
        for err, count in insights["top_errors"]:
            print(f"    {err:<25s} {count}x")
        print()

    if insights.get("busiest_days"):
        print("  Busiest days:")
        for day, count in insights["busiest_days"]:
            print(f"    {day}  {count} commands")
        print()

    # Privacy note
    print("  All data is LOCAL. Nothing is sent unless you run 'telemetry flush'.")
    print()
    return 0


def main():
    try:
        result = run()

        # Record telemetry (non-blocking, silently fails)
        try:
            from core.telemetry import record_event
        except ImportError:
            try:
                from cli.core.telemetry import record_event
            except ImportError:
                record_event = None

        if record_event and len(sys.argv) > 1:
            cmd = sys.argv[1]
            record_event(cmd, success=(result == 0))

        sys.exit(result)
    except KeyboardInterrupt:
        print("\n  Cancelled.")
        sys.exit(130)
    except Exception as e:
        # Record error telemetry
        try:
            from core.telemetry import record_event
        except ImportError:
            try:
                from cli.core.telemetry import record_event
            except ImportError:
                record_event = None

        if record_event and len(sys.argv) > 1:
            record_event(sys.argv[1], success=False, error_type=type(e).__name__)

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
    print("  Get help: https://discord.gg/vrFcju9rBA")
    print("  Report bugs: https://github.com/pnmcguire480/brainstormer/issues")


if __name__ == "__main__":
    main()
