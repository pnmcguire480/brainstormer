"""brainstormer init — Set up BrainStormer in the current project."""

import sys
from pathlib import Path

from core.detector import detect_project
from core.scaffold import (
    scaffold_kernel,
    scaffold_comprehension,
    scaffold_ideation,
    scaffold_quality,
    write_version_marker,
)
from core.vault import load_config, get_vault_path, sync_project_to_vault


def _print_phase(emoji: str, label: str, detail: str):
    """Print a phase progress line."""
    print(f"  {emoji} {label:<30s} {detail}")


def _print_results(results: dict):
    """Print file creation results."""
    created = [k for k, v in results.items() if v == "created"]
    skipped = [k for k, v in results.items() if v == "skipped"]
    errors = [k for k, v in results.items() if isinstance(v, str) and v.startswith("error")]

    if created:
        for f in created:
            print(f"    + {f}")
    if errors:
        for f in errors:
            print(f"    ! {f}: {results[f]}", file=sys.stderr)


def cmd_init(opts: dict) -> int:
    """Execute the init command."""
    project_root = Path.cwd()
    minimal = opts.get("minimal", False)
    update = opts.get("update", False)
    no_obsidian = opts.get("no_obsidian", False)

    print()
    print("  BrainStormer — The AI Development Operating System")
    print("  " + "=" * 50)
    print()

    # Phase 1: Detect
    info = detect_project(project_root)
    project_name = opts.get("name", info.name)

    if info.has_brainstormer and not update:
        _print_phase("✅", "Already initialized", f"Use --update to re-sync")
        print()
        print(f"  Project: {project_name}")
        print(f"  Stack:   {info.summary}")
        print(f"  Existing files: {len(info.existing_files)}")
        print()
        return 0

    _print_phase("🔍", "Detecting project...", info.summary)

    # Phase 2: Kernel
    results = scaffold_kernel(project_root, project_name)
    created_count = sum(1 for v in results.values() if v == "created")
    skipped_count = sum(1 for v in results.values() if v == "skipped")
    _print_phase("📁", "Scaffolding project docs...",
                 f"{created_count} created, {skipped_count} existing")
    _print_results(results)

    if not minimal:
        # Phase 3: Comprehension
        results = scaffold_comprehension(project_root)
        detail = ", ".join(f"{k}" for k, v in results.items() if v == "created")
        _print_phase("🧠", "Setting up comprehension...",
                     detail if detail else "already configured")
        _print_results(results)

        # Phase 4: Ideation
        results = scaffold_ideation(project_root)
        detail = ", ".join(f"{k}" for k, v in results.items() if v == "created")
        _print_phase("💡", "Setting up ideation...",
                     detail if detail else "already configured")
        _print_results(results)

        # Phase 5: Quality
        results = scaffold_quality(project_root)
        detail = ", ".join(f"{k}" for k, v in results.items() if v == "created")
        _print_phase("🛡️", "Setting up quality gates...",
                     detail if detail else "already configured")
        _print_results(results)

    # Phase 6: Obsidian Sync
    if not no_obsidian:
        config = load_config()
        vault_path = get_vault_path(config)

        if vault_path:
            results = sync_project_to_vault(project_root, project_name, vault_path)
            _print_phase("📔", "Syncing to Obsidian...",
                         f"→ {vault_path / 'projects' / project_name}")
        else:
            vault_str = config.get("vault_path", "")
            if vault_str:
                _print_phase("⚠️", "Obsidian vault not found",
                             f"Path: {vault_str}")
            else:
                _print_phase("📔", "Obsidian not configured",
                             "Run: brainstormer config set vault_path <path>")

    # Write version marker
    write_version_marker(project_root)

    # Done
    print()
    print(f"  ✅ Done! Project '{project_name}' is ready.")
    print()
    print("  Next steps:")
    print("    brainstormer status     — see what's set up")
    print("    brainstormer doctor     — check for issues")
    print("    brainstormer help       — see all commands")
    print()

    return 0
