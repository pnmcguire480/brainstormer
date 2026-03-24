"""brainstormer team — Team rulesets and shared configuration.

Usage:
    brainstormer team init              — Create a shared team ruleset in this repo
    brainstormer team status            — Show team ruleset info
    brainstormer team sync              — Sync personal rules with team rules
    brainstormer team templates         — List available starter rule templates
    brainstormer team apply <template>  — Apply a stack-specific rule template
"""

import re
from pathlib import Path
from datetime import datetime


# --- #18: Rule Templates per Stack ---

STACK_TEMPLATES = {
    "python": {
        "name": "Python/FastAPI",
        "rules": [
            ("Type Hints on All Public Functions", "Add type hints to all public function signatures", "Leave public functions untyped", "Untyped functions cause runtime surprises and break IDE autocomplete", "Python"),
            ("Use Pydantic for Validation", "Use Pydantic models for request/response validation", "Validate with manual dict checks", "Pydantic gives you automatic validation, serialization, and docs", "Python/FastAPI"),
            ("Async All the Way", "Keep the entire async chain unbroken", "Mix sync and async calls in the same chain", "One sync call blocks the entire event loop", "Python/FastAPI"),
            ("Virtual Environments Always", "Use venv or uv for every project", "Install packages globally", "Global installs cause dependency conflicts across projects", "Python"),
            ("Pin Dependencies", "Pin exact versions in requirements.txt or pyproject.toml", "Use >= or unpinned dependencies", "Unpinned deps break builds when upstream releases change", "Python"),
        ],
    },
    "react": {
        "name": "React/TypeScript",
        "rules": [
            ("No any Type", "Use proper TypeScript types instead of any", "Use 'any' to bypass type checking", "Every 'any' is a future runtime error hiding from the compiler", "TypeScript"),
            ("Guard Watch Returns", "Always include cleanup functions in useEffect", "Leave useEffect without cleanup", "Missing cleanup causes memory leaks and stale subscriptions", "React"),
            ("Component Single Responsibility", "Each component does one thing well", "Build mega-components with multiple concerns", "Large components are untestable and unreviewable", "React"),
            ("Controlled Inputs", "Use controlled components for form inputs", "Use uncontrolled inputs with refs for forms", "Uncontrolled inputs make validation and state sync unpredictable", "React"),
            ("Error Boundaries Required", "Wrap route-level components in error boundaries", "Let errors propagate to the root", "One bad component crashes the entire app", "React"),
        ],
    },
    "node": {
        "name": "Node.js/Express",
        "rules": [
            ("Handle Promise Rejections", "Always .catch() or try/await every promise", "Leave promises without error handling", "Unhandled rejections crash Node.js in production", "Node.js"),
            ("Validate All Input", "Validate and sanitize all user input at the API boundary", "Trust client-side validation", "Client validation is for UX; server validation is for security", "Node.js"),
            ("Environment Config", "Use environment variables for all config", "Hardcode config values or connection strings", "Hardcoded config causes deployment failures and security leaks", "Node.js"),
            ("Structured Logging", "Use structured JSON logging (not console.log)", "Use console.log in production code", "console.log is invisible in production log aggregators", "Node.js"),
            ("Graceful Shutdown", "Handle SIGTERM/SIGINT for clean process shutdown", "Let the process die on signals", "Ungraceful shutdown causes data loss and connection leaks", "Node.js"),
        ],
    },
    "go": {
        "name": "Go",
        "rules": [
            ("Handle Every Error", "Check and handle every returned error", "Use _ to discard errors", "Discarded errors cause silent data corruption", "Go"),
            ("Context Propagation", "Pass context.Context as the first parameter", "Use background context or skip context", "Missing context breaks cancellation, timeouts, and tracing", "Go"),
            ("No Goroutine Leaks", "Ensure every goroutine has a termination path", "Launch goroutines without lifecycle management", "Leaked goroutines consume memory and cause deadlocks", "Go"),
            ("Interface at Consumer", "Define interfaces where they're used, not where they're implemented", "Define interfaces next to implementations", "Consumer-side interfaces enable clean dependency injection", "Go"),
            ("Table-Driven Tests", "Use table-driven tests for function coverage", "Write one test case per function", "Table tests cover edge cases systematically with less code", "Go"),
        ],
    },
    "rust": {
        "name": "Rust",
        "rules": [
            ("Prefer Result Over Panic", "Use Result<T, E> for recoverable errors", "Use unwrap() or panic!() for error handling", "Panics crash the program; Result lets callers decide", "Rust"),
            ("Clippy Clean", "Run clippy with all warnings before committing", "Ignore clippy warnings", "Clippy catches common mistakes and non-idiomatic patterns", "Rust"),
            ("Own Your Data", "Prefer owned types in public APIs", "Return references from public functions", "References in APIs create lifetime coupling that limits reuse", "Rust"),
        ],
    },
    "universal": {
        "name": "Universal (Any Stack)",
        "rules": [
            ("Document All Env Vars", "List every env var in .env.example with descriptions", "Add env vars without documentation", "New team members can't run the project without documentation", "Universal"),
            ("Always Check .gitignore", "Review .gitignore before first commit", "Commit and then fix gitignore later", "Secrets and build artifacts in git history are permanent", "Universal"),
            ("Test Before Ship", "Run full test suite before pushing to main", "Push and let CI catch failures", "CI failures block the whole team; local runs catch your mistakes", "Universal"),
            ("Atomic Commits", "Each commit does one logical thing", "Bundle unrelated changes in a single commit", "Mixed commits make bisect useless and reverts dangerous", "Universal"),
            ("Review Your Own Diff", "Read your own diff before requesting review", "Submit PRs without self-review", "Self-review catches 50% of issues before bothering teammates", "Universal"),
        ],
    },
}


def cmd_team(opts: dict) -> int:
    """Execute team subcommands."""
    positional = opts.get("positional", [])

    if not positional:
        return _team_status(opts)

    action = positional[0]

    # Gate Pro-only features (templates and status are free)
    PRO_ACTIONS = {"init", "sync", "apply"}
    if action in PRO_ACTIONS:
        try:
            from cli.core.license import require_pro
        except ImportError:
            from core.license import require_pro
        if not require_pro(f"Team {action}"):
            return 1

    handlers = {
        "init": _team_init,
        "status": _team_status,
        "sync": _team_sync,
        "templates": _team_templates,
        "apply": _team_apply_template,
    }

    handler = handlers.get(action)
    if not handler:
        print(f"\n  Unknown team action: {action}")
        print("  Available: init, status, sync, templates, apply\n")
        return 1

    return handler(opts)


def _team_init(opts: dict) -> int:
    """Create a shared team ruleset in this repo."""
    project_root = Path.cwd()
    team_rules = project_root / ".brainstormer" / "team-rules.md"

    if team_rules.exists():
        print(f"\n  Team ruleset already exists: {team_rules}")
        print("  Edit it directly or run 'brainstormer team sync'.\n")
        return 0

    team_rules.parent.mkdir(parents=True, exist_ok=True)

    content = f"""# Team Rules — {project_root.name}

Shared rules that apply to all team members. Committed to the repo.
Team rules take precedence over personal global rules.
Personal project rules can override team rules by using the same rule name.

Created: {datetime.now().strftime("%Y-%m-%d")}

---

## How This Works

1. Team rules live here: `.brainstormer/team-rules.md`
2. Committed to the repo — everyone gets them on pull
3. `brainstormer team sync` merges team rules with personal rules
4. Rule precedence: team > global, project > team

---

## Rules

<!-- Add team rules below. Same format as rules.md -->
"""

    team_rules.write_text(content, encoding="utf-8")

    # Add to .gitignore if not there
    gitignore = project_root / ".gitignore"
    if gitignore.exists():
        gi_content = gitignore.read_text(encoding="utf-8")
        if ".brainstormer/" not in gi_content:
            # Don't ignore — team rules should be committed
            pass

    print(f"\n  Team ruleset created: .brainstormer/team-rules.md")
    print()
    print("  Next steps:")
    print("    1. Add team rules to the file")
    print("    2. Or: brainstormer team apply <template> to start with a template")
    print("    3. Commit .brainstormer/team-rules.md to the repo")
    print("    4. Team members run: brainstormer team sync")
    print()
    return 0


def _team_status(opts: dict) -> int:
    """Show team ruleset info."""
    project_root = Path.cwd()
    team_rules = project_root / ".brainstormer" / "team-rules.md"

    print()
    print("  BrainStormer — Team Status")
    print("  " + "=" * 50)
    print()

    if team_rules.exists():
        content = team_rules.read_text(encoding="utf-8")
        rule_count = content.count("### Rule:")
        print(f"  Team ruleset: .brainstormer/team-rules.md")
        print(f"  Team rules:   {rule_count}")
    else:
        print("  No team ruleset found.")
        print("  Create one: brainstormer team init")

    # Check global rules
    global_rules = Path.home() / ".brainstormer" / "rules.md"
    if global_rules.exists():
        content = global_rules.read_text(encoding="utf-8")
        global_count = content.count("### Rule:")
        print(f"  Global rules: {global_count}")

    # Project rules
    project_rules = project_root / "rules.md"
    if project_rules.exists():
        content = project_rules.read_text(encoding="utf-8")
        project_count = content.count("### Rule:")
        print(f"  Project rules: {project_count}")

    print()
    print("  Precedence: project > team > global")
    print()
    return 0


def _team_sync(opts: dict) -> int:
    """Sync team rules into the project."""
    project_root = Path.cwd()
    team_rules_path = project_root / ".brainstormer" / "team-rules.md"

    if not team_rules_path.exists():
        print("\n  No team ruleset found. Run: brainstormer team init\n")
        return 1

    # Parse team rules
    content = team_rules_path.read_text(encoding="utf-8")
    team_rules = []
    for match in re.finditer(r'(### Rule: (.+?)\n(?:.*?\n)*?(?=### Rule:|\Z))', content, re.DOTALL):
        block = match.group(1).rstrip()
        name = match.group(2).strip()
        team_rules.append((name, block))

    if not team_rules:
        print("\n  Team ruleset is empty. Add rules first.\n")
        return 0

    # Check project rules.md for conflicts
    rules_file = project_root / "rules.md"
    existing_names = set()
    if rules_file.exists():
        proj_content = rules_file.read_text(encoding="utf-8")
        for match in re.finditer(r'### Rule: (.+)', proj_content):
            existing_names.add(match.group(1).strip())

    synced = 0
    skipped = 0
    for name, block in team_rules:
        if name in existing_names:
            skipped += 1
        else:
            # Append team rule to project rules
            try:
                from cli.commands.learn import _append_to_rules
            except ImportError:
                from commands.learn import _append_to_rules
            _append_to_rules(rules_file, "\n" + block + "\n")
            synced += 1

    print(f"\n  Team sync complete:")
    print(f"    Synced: {synced} new rules")
    print(f"    Skipped: {skipped} (already in project rules)")
    print(f"    Total team rules: {len(team_rules)}\n")
    return 0


def _team_templates(opts: dict) -> int:
    """List available starter rule templates."""
    print()
    print("  BrainStormer — Rule Templates")
    print("  " + "=" * 50)
    print()

    for key, template in STACK_TEMPLATES.items():
        print(f"  {key:<12s}  {template['name']} ({len(template['rules'])} rules)")

    print()
    print("  Apply: brainstormer team apply <template>")
    print("  Example: brainstormer team apply python")
    print("  Combine: brainstormer team apply python universal")
    print()
    return 0


def _team_apply_template(opts: dict) -> int:
    """Apply a stack-specific rule template."""
    positional = opts.get("positional", [])

    if len(positional) < 2:
        print("\n  Usage: brainstormer team apply <template> [template2 ...]")
        print("  Available templates:")
        for key in STACK_TEMPLATES:
            print(f"    {key}")
        print()
        return 1

    templates_to_apply = positional[1:]
    project_root = Path.cwd()

    # Determine target: team rules if team init'd, else project rules
    team_rules_path = project_root / ".brainstormer" / "team-rules.md"
    if team_rules_path.exists():
        target = team_rules_path
        target_label = "team rules"
    else:
        target = project_root / "rules.md"
        target_label = "project rules"

    total_added = 0

    for template_name in templates_to_apply:
        template = STACK_TEMPLATES.get(template_name)
        if not template:
            print(f"  Unknown template: {template_name}")
            continue

        # Check existing rules
        existing = ""
        if target.exists():
            existing = target.read_text(encoding="utf-8")

        added = 0
        for name, do_this, dont_do, why, stack in template["rules"]:
            if f"### Rule: {name}" in existing:
                continue

            try:
                from cli.commands.learn import _format_rule_block, _append_to_rules
            except ImportError:
                from commands.learn import _format_rule_block, _append_to_rules

            block = _format_rule_block(
                name=name, do_this=do_this, dont_do=dont_do, why=why,
                stack=stack, source=f"template:{template_name}",
                date=datetime.now().strftime("%Y-%m-%d"),
                confidence="high", hits=0, misses=0, last_fired="never",
            )
            _append_to_rules(target, block)
            added += 1

        print(f"  Applied: {template['name']} — {added} new rules")
        total_added += added

    print(f"\n  Total: {total_added} rules added to {target_label}")
    print()
    return 0
