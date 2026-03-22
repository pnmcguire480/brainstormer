"""brainstormer update — Update BrainStormer and re-sync templates."""

from pathlib import Path
from core.detector import detect_project
from core.scaffold import get_brainstormer_root


def cmd_update(opts: dict) -> int:
    """Update BrainStormer and re-sync."""
    project_root = Path.cwd()
    info = detect_project(project_root)
    update_all = opts.get("all", False)

    print()
    print("  BrainStormer Update")
    print("  " + "=" * 50)
    print()

    bs_root = get_brainstormer_root()
    print(f"  Installation: {bs_root}")

    # Read current version
    version_file = project_root / ".brainstormer-version"
    if version_file.exists():
        content = version_file.read_text(encoding="utf-8")
        for line in content.split("\n"):
            if line.startswith("version:"):
                print(f"  Installed version: {line.split(':')[1].strip()}")
            if line.startswith("initialized:"):
                print(f"  Initialized: {line.split(':', 1)[1].strip()}")
    else:
        print("  ⚠️  Project not initialized (run: brainstormer init)")
        print()
        return 1

    print()
    print("  Checking for template updates...")
    print()

    # Compare template files
    template_dir = bs_root / "kernel" / "templates"
    updated = 0
    for template in template_dir.glob("*.md"):
        project_file = project_root / template.name
        if project_file.exists():
            # Don't overwrite — just report if template is newer
            if template.stat().st_mtime > project_file.stat().st_mtime:
                print(f"    📝 {template.name} — template updated (project file untouched)")
                updated += 1

    if updated == 0:
        print("  ✅ All templates are current")
    else:
        print(f"\n  {updated} template(s) have updates. Your project files were NOT overwritten.")
        print("  To see diffs, compare your files against the templates in:")
        print(f"    {template_dir}")

    print()
    return 0
