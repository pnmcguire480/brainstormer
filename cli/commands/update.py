"""brainstormer update — Update BrainStormer and re-sync templates."""

from pathlib import Path
from core.detector import detect_project
from core.scaffold import get_brainstormer_root


def cmd_update(opts: dict) -> int:
    """Update BrainStormer and re-sync."""
    try:
        from core.channels import (
            get_channel, set_channel, get_current_version,
            check_for_update, format_channel_status, CHANNELS,
        )
    except ImportError:
        from cli.core.channels import (
            get_channel, set_channel, get_current_version,
            check_for_update, format_channel_status, CHANNELS,
        )

    project_root = Path.cwd()
    update_all = opts.get("all", False)
    positional = opts.get("positional", [])

    # Handle subcommands: update channel, update rollback
    if positional:
        subcmd = positional[0]

        if subcmd == "channel":
            if len(positional) > 1:
                new_channel = positional[1]
                if set_channel(new_channel):
                    print(f"\n  Release channel set to: {CHANNELS[new_channel]['label']}")
                    print(f"  {CHANNELS[new_channel]['description']}")
                    print()
                else:
                    print(f"\n  Unknown channel: {new_channel}")
                    print(f"  Available: {', '.join(CHANNELS.keys())}")
                    print()
                    return 1
            else:
                print()
                print(format_channel_status())
                print()
                print("  Set channel:")
                for name, info in CHANNELS.items():
                    marker = " (current)" if name == get_channel() else ""
                    print(f"    brainstormer update channel {name}{marker}")
                print()
            return 0

        if subcmd == "rollback":
            return _rollback(project_root)

        if subcmd == "check":
            return _check_update()

    print()
    print("  BrainStormer Update")
    print("  " + "=" * 50)
    print()

    bs_root = get_brainstormer_root()
    print(f"  Installation: {bs_root}")
    print(f"  Version:      {get_current_version()}")
    print(f"  Channel:      {CHANNELS[get_channel()]['label']}")

    # Read current version
    version_file = project_root / ".brainstormer-version"
    if version_file.exists():
        content = version_file.read_text(encoding="utf-8")
        for line in content.split("\n"):
            if line.startswith("initialized:"):
                print(f"  Initialized:  {line.split(':', 1)[1].strip()}")
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
            if template.stat().st_mtime > project_file.stat().st_mtime:
                print(f"    📝 {template.name} — template updated (project file untouched)")
                updated += 1

    if updated == 0:
        print("  ✅ All templates are current")
    else:
        print(f"\n  {updated} template(s) have updates. Your project files were NOT overwritten.")
        print("  To see diffs, compare your files against the templates in:")
        print(f"    {template_dir}")

    # Check for new version
    print()
    print("  Checking for new releases...")
    update_info = check_for_update()
    if update_info:
        print(f"  📦 New version available: {update_info['latest']} (you have {update_info['current']})")
        print(f"     pip install --upgrade brainstormer")
        if update_info.get("url"):
            print(f"     Release notes: {update_info['url']}")
    else:
        print("  ✅ You're on the latest version")

    print()
    print("  Commands:")
    print("    brainstormer update check       Check for updates")
    print("    brainstormer update channel      View/set release channel")
    print("    brainstormer update rollback     Revert to previous version")
    print()
    return 0


def _check_update() -> int:
    """Check for updates without doing anything else."""
    try:
        from core.channels import check_for_update, get_current_version, get_channel
    except ImportError:
        from cli.core.channels import check_for_update, get_current_version, get_channel

    print()
    print(f"  Current version: {get_current_version()}")
    print(f"  Channel: {get_channel()}")
    print()

    update_info = check_for_update()
    if update_info:
        print(f"  📦 Update available: {update_info['latest']}")
        print(f"     Run: pip install brainstormer=={update_info['latest']}")
        if update_info.get("body"):
            print()
            print("  What's new:")
            for line in update_info["body"].splitlines()[:10]:
                print(f"    {line}")
    else:
        print("  ✅ Up to date")

    print()
    return 0


def _rollback(project_root: Path) -> int:
    """Rollback BrainStormer to the previous pip-installed version.

    Strategy: pip install the previous version from PyPI.
    We find it by listing available versions.
    """
    try:
        from core.channels import get_current_version
    except ImportError:
        from cli.core.channels import get_current_version

    current = get_current_version()

    print()
    print("  BrainStormer Rollback")
    print("  " + "=" * 50)
    print()
    print(f"  Current version: {current}")
    print()

    # Find available versions from PyPI
    previous = _find_previous_version(current)

    if previous:
        print(f"  Previous version: {previous}")
        print()
        print(f"  To rollback, run:")
        print(f"    pip install brainstormer=={previous}")
        print()
        print("  After rollback, run 'brainstormer doctor' to verify.")
    else:
        print("  Could not determine previous version.")
        print("  You can manually install a specific version:")
        print("    pip install brainstormer==YYYY.WW.PATCH")

    print()
    return 0


def _find_previous_version(current: str) -> str:
    """Query PyPI for the version before the current one."""
    try:
        import json
        import urllib.request
        import ssl

        url = "https://pypi.org/pypi/brainstormer/json"
        ctx = ssl.create_default_context()
        req = urllib.request.Request(url, headers={"User-Agent": "brainstormer-cli"})
        with urllib.request.urlopen(req, timeout=5, context=ctx) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        versions = sorted(data.get("releases", {}).keys())
        if current in versions:
            idx = versions.index(current)
            if idx > 0:
                return versions[idx - 1]

        # If current not on PyPI yet, return the latest available
        if versions:
            return versions[-1]
    except Exception:
        pass

    return ""
