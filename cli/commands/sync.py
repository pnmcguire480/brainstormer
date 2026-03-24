"""brainstormer sync — Bi-directional sync between project and Obsidian vault."""

from pathlib import Path

try:
    from core.detector import detect_project
    from core.vault import (load_config, get_vault_path,
                            sync_project_to_vault, sync_vault_to_project)
except ImportError:
    from cli.core.detector import detect_project
    from cli.core.vault import (load_config, get_vault_path,
                                sync_project_to_vault, sync_vault_to_project)


def cmd_sync(opts: dict) -> int:
    """Bi-directional sync: project <-> Obsidian vault."""
    project_root = Path.cwd()
    info = detect_project(project_root)
    reverse_only = opts.get("positional", []) == ["pull"]

    print()
    config = load_config()
    vault_path = get_vault_path(config)

    if not vault_path:
        vault_str = config.get("vault_path", "")
        if vault_str:
            print(f"  Vault not found: {vault_str}")
        else:
            print("  Vault not configured")
            print("  Run: brainstormer config set vault_path <path>")
        print()
        return 1

    # Step 1: Reverse sync (vault -> project) — Pro only (bi-directional)
    try:
        from cli.core.license import check_capability
    except ImportError:
        from core.license import check_capability

    can_pull = check_capability("bidirectional_sync")

    if can_pull:
        print(f"  Pulling from Obsidian vault...")
        reverse_results = sync_vault_to_project(project_root, info.name, vault_path)

        if reverse_results:
            print(f"  Pulled {len(reverse_results)} changes from vault:")
            for f, status in reverse_results.items():
                print(f"    <- {f} ({status})")
            print()

        if reverse_only:
            if not reverse_results:
                print("  No changes to pull from vault.")
            print()
            return 0
    else:
        if reverse_only:
            print("  Bi-directional sync requires Pro.")
            print("  Upgrade: https://brainstormer.lemonsqueezy.com")
            print()
            return 1
        # Community users skip pull phase silently, proceed to push

    # Step 2: Forward sync (project -> vault) — push to Obsidian
    print(f"  Pushing '{info.name}' to Obsidian...")
    results = sync_project_to_vault(project_root, info.name, vault_path)

    synced = [k for k, v in results.items() if v == "synced"]
    updated = [k for k, v in results.items() if v == "updated"]

    print(f"  Pushed {len(synced)} files to: {vault_path / 'projects' / info.name}")
    for f in synced:
        print(f"    -> {f}")
    if updated:
        for f in updated:
            print(f"    ~ {f}")

    print()
    return 0
