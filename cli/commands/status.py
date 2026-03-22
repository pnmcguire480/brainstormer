"""brainstormer status — Show what's configured and what's missing."""

from pathlib import Path
from core.detector import detect_project, BRAINSTORMER_FILES
from core.registry import count_agents
from core.vault import load_config, get_vault_path


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

    print()
    return 0
