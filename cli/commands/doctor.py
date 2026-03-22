"""brainstormer doctor — Validate setup and diagnose issues."""

from pathlib import Path
from core.detector import detect_project, BRAINSTORMER_FILES
from core.scaffold import get_brainstormer_root
from core.vault import load_config, get_vault_path


def cmd_doctor(opts: dict) -> int:
    """Validate BrainStormer setup."""
    project_root = Path.cwd()
    info = detect_project(project_root)
    issues = []
    warnings = []

    print()
    print("  BrainStormer Doctor")
    print("  " + "=" * 50)
    print()
    print(f"  Project: {info.name}")
    print(f"  Stack:   {info.summary}")
    print()

    # Check BrainStormer installation
    bs_root = get_brainstormer_root()
    if not (bs_root / "SKILL.md").exists():
        issues.append("BrainStormer installation not found")
    else:
        print("  ✅ BrainStormer installed")

    # Check version marker
    if not info.has_brainstormer:
        issues.append("Project not initialized (run: brainstormer init)")
    else:
        print("  ✅ Project initialized")

    # Check kernel files
    missing_kernel = [f for f in BRAINSTORMER_FILES if not (project_root / f).exists()]
    if missing_kernel:
        warnings.append(f"Missing kernel files: {', '.join(missing_kernel)}")
    else:
        print("  ✅ All 10 kernel files present")

    # Check comprehension
    if not (project_root / "rules.md").exists():
        warnings.append("Missing rules.md (comprehension layer)")
    if not (project_root / "docs" / "codeglass").exists():
        warnings.append("Missing docs/codeglass/ directory")

    # Check ideation
    if not (project_root / "brainstormer").exists():
        warnings.append("Missing brainstormer/ directory (ideation layer)")

    # Check quality
    if not (project_root / "paladin.config.json").exists():
        warnings.append("Missing paladin.config.json (quality layer)")

    # Check Obsidian
    config = load_config()
    vault_path = get_vault_path(config)
    if vault_path:
        print(f"  ✅ Obsidian vault: {vault_path}")
        project_dir = vault_path / "projects" / info.name
        if not project_dir.exists():
            warnings.append("Project not synced to vault (run: brainstormer sync)")
        else:
            print("  ✅ Project synced to vault")
    else:
        warnings.append("Obsidian vault not configured")

    # Check agents directory
    agents_dir = Path.home() / ".claude" / "agents"
    if agents_dir.exists():
        agent_count = len(list(agents_dir.glob("*.md")))
        print(f"  ✅ {agent_count} agents available")
    else:
        warnings.append("No agents directory found at ~/.claude/agents/")

    # Print issues and warnings
    print()
    if issues:
        print("  Issues (must fix):")
        for issue in issues:
            print(f"    ❌ {issue}")
        print()

    if warnings:
        print("  Warnings:")
        for warning in warnings:
            print(f"    ⚠️  {warning}")
        print()

    if not issues and not warnings:
        print("  ✅ Everything looks good!")
        print()

    # Verdict
    if issues:
        print("  Verdict: NEEDS ATTENTION")
    elif warnings:
        print(f"  Verdict: OK ({len(warnings)} warning{'s' if len(warnings) != 1 else ''})")
    else:
        print("  Verdict: HEALTHY")

    print()
    return 1 if issues else 0
