"""brainstormer sync — Push project state to Obsidian vault."""

from pathlib import Path
from core.detector import detect_project
from core.vault import load_config, get_vault_path, sync_project_to_vault


def cmd_sync(opts: dict) -> int:
    """Sync project to Obsidian vault."""
    project_root = Path.cwd()
    info = detect_project(project_root)

    print()
    print(f"  Syncing '{info.name}' to Obsidian...")
    print()

    config = load_config()
    vault_path = get_vault_path(config)

    if not vault_path:
        vault_str = config.get("vault_path", "")
        if vault_str:
            print(f"  ❌ Vault not found: {vault_str}")
        else:
            print("  ❌ Vault not configured")
            print("  Run: brainstormer config set vault_path <path>")
        print()
        return 1

    results = sync_project_to_vault(project_root, info.name, vault_path)

    synced = [k for k, v in results.items() if v == "synced"]
    updated = [k for k, v in results.items() if v == "updated"]

    print(f"  ✅ Synced {len(synced)} files to: {vault_path / 'projects' / info.name}")
    for f in synced:
        print(f"    → {f}")
    if updated:
        for f in updated:
            print(f"    ↻ {f}")

    print()
    return 0
