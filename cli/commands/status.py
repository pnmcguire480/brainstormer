"""brainstormer status — Project health dashboard."""

from pathlib import Path
from datetime import datetime

try:
    from core.detector import detect_project, BRAINSTORMER_FILES
    from core.registry import count_agents, get_top_agents
    from core.vault import load_config, get_vault_path
    from core.license import format_license_status
except ImportError:
    from cli.core.detector import detect_project, BRAINSTORMER_FILES
    from cli.core.registry import count_agents, get_top_agents
    from cli.core.vault import load_config, get_vault_path
    from cli.core.license import format_license_status


def cmd_status(opts: dict) -> int:
    """Show project status."""
    project_root = Path.cwd()
    info = detect_project(project_root)

    print()
    print(f"  Project: {info.name}")
    print(f"  Stack:   {info.summary}")
    print(f"  Root:    {project_root}")
    print()

    # Kernel files
    print("  Kernel (10 template files):")
    for fname in BRAINSTORMER_FILES:
        exists = (project_root / fname).exists()
        icon = "✅" if exists else "❌"
        print(f"    {icon} {fname}")

    print()

    # Comprehension
    print("  Comprehension (CodeGlass):")
    checks = [
        ("rules.md", project_root / "rules.md"),
        ("docs/codeglass/", project_root / "docs" / "codeglass"),
        ("scripts/eval.sh", project_root / "scripts" / "eval.sh"),
    ]
    for label, path in checks:
        icon = "✅" if path.exists() else "❌"
        print(f"    {icon} {label}")

    print()

    # Ideation
    print("  Ideation (BrainStormer):")
    checks = [
        ("brainstormer/", project_root / "brainstormer"),
        ("brainstormer/ruleset.md", project_root / "brainstormer" / "ruleset.md"),
        ("brainstormer/angles.md", project_root / "brainstormer" / "angles.md"),
    ]
    for label, path in checks:
        icon = "✅" if path.exists() else "❌"
        print(f"    {icon} {label}")

    print()

    # Quality
    print("  Quality (PALADIN):")
    checks = [
        ("paladin.config.json", project_root / "paladin.config.json"),
    ]
    for label, path in checks:
        icon = "✅" if path.exists() else "❌"
        print(f"    {icon} {label}")

    print()

    # Obsidian
    config = load_config()
    vault_path = get_vault_path(config)
    print("  Obsidian Vault:")
    if vault_path:
        print(f"    ✅ Connected: {vault_path}")
        project_in_vault = vault_path / "projects" / info.name / "dashboard.md"
        if project_in_vault.exists():
            print(f"    ✅ Project synced")
        else:
            print(f"    ❌ Project not synced (run: brainstormer sync)")
    else:
        vault_str = config.get("vault_path", "")
        if vault_str:
            print(f"    ❌ Vault not found: {vault_str}")
        else:
            print(f"    ❌ Not configured (run: brainstormer config set vault_path <path>)")

    print()

    # Agents
    agent_count = count_agents()
    print(f"  Agents: {agent_count} available")

    # #12: Smart Agent Recommendations
    stack = info.framework or info.stack or "general"
    recommended = get_top_agents(stack, limit=5)
    if recommended:
        print(f"\n  Recommended for {info.summary}:")
        for a in recommended:
            emoji = a.get("emoji", "")
            name = a.get("name", a["filename"])
            print(f"    {emoji} {name}")

    print()

    # #11: Project Health Dashboard
    print("  Knowledge Health:")
    health_score = 0
    health_max = 0

    # Rules
    rules_file = project_root / "rules.md"
    rule_count = 0
    if rules_file.exists():
        content = rules_file.read_text(encoding="utf-8")
        rule_count = content.count("### Rule:")
    health_max += 3
    if rule_count >= 10:
        health_score += 3
        print(f"    ✅ Rules: {rule_count} (strong)")
    elif rule_count >= 3:
        health_score += 2
        print(f"    🟡 Rules: {rule_count} (growing)")
    elif rule_count > 0:
        health_score += 1
        print(f"    🟠 Rules: {rule_count} (needs more)")
    else:
        print(f"    ❌ Rules: 0 (run: brainstormer learn rule)")

    # Walkthroughs
    codeglass_dir = project_root / "docs" / "codeglass"
    wt_count = len(list(codeglass_dir.glob("*.md"))) if codeglass_dir.exists() else 0
    health_max += 2
    if wt_count >= 5:
        health_score += 2
        print(f"    ✅ Walkthroughs: {wt_count}")
    elif wt_count > 0:
        health_score += 1
        print(f"    🟡 Walkthroughs: {wt_count}")
    else:
        print(f"    ❌ Walkthroughs: 0 (run: brainstormer learn walkthrough)")

    # Team rules
    team_rules = project_root / ".brainstormer" / "team-rules.md"
    health_max += 1
    if team_rules.exists():
        health_score += 1
        print(f"    ✅ Team rules: configured")
    else:
        print(f"    ⬜ Team rules: not set up (run: brainstormer team init)")

    # Git hooks
    git_dir = project_root / ".git" / "hooks"
    hooks_installed = False
    if git_dir.exists():
        for hook in ("pre-commit", "post-commit"):
            hook_path = git_dir / hook
            if hook_path.exists():
                try:
                    content = hook_path.read_text(encoding="utf-8", errors="replace")
                    if "BrainStormer" in content:
                        hooks_installed = True
                except OSError:
                    pass
    health_max += 1
    if hooks_installed:
        health_score += 1
        print(f"    ✅ Git hooks: installed")
    else:
        print(f"    ⬜ Git hooks: not installed (run: brainstormer hooks install)")

    # Health score
    pct = (health_score / health_max * 100) if health_max > 0 else 0
    bar_filled = int(pct / 10)
    bar = "█" * bar_filled + "░" * (10 - bar_filled)
    print(f"\n  Health: [{bar}] {pct:.0f}%")

    print()

    # License
    print(format_license_status())

    print()
    return 0
