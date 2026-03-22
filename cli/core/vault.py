"""Obsidian vault sync for BrainStormer."""

import yaml
from pathlib import Path
from datetime import datetime


def get_config_path() -> Path:
    """Get the BrainStormer Obsidian config path."""
    current = Path(__file__).resolve()
    for parent in current.parents:
        config = parent / "obsidian" / "config.yaml"
        if config.exists():
            return config
    return Path(__file__).resolve().parent.parent.parent / "obsidian" / "config.yaml"


def load_config() -> dict:
    """Load Obsidian sync configuration."""
    config_path = get_config_path()
    if not config_path.exists():
        return {"vault_path": "", "sync_on_init": True, "projects": {}}

    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def save_config(config: dict):
    """Save Obsidian sync configuration."""
    config_path = get_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False)


def get_vault_path(config: dict = None) -> Path | None:
    """Get the configured Obsidian vault path."""
    if config is None:
        config = load_config()
    vault_str = config.get("vault_path", "")
    if not vault_str:
        return None
    vault = Path(vault_str)
    return vault if vault.exists() else None


def sync_project_to_vault(project_root: Path, project_name: str, vault_path: Path) -> dict:
    """Sync a project's state to the Obsidian vault.

    One-way sync: project files -> vault.
    Preserves <!-- USER NOTES --> blocks in vault files.
    Returns dict of {path: status}.
    """
    results = {}
    project_vault_dir = vault_path / "projects" / project_name

    # Create project directory in vault
    project_vault_dir.mkdir(parents=True, exist_ok=True)

    # Generate dashboard
    dashboard = _generate_dashboard(project_root, project_name)
    _write_preserving_user_notes(project_vault_dir / "dashboard.md", dashboard)
    results["dashboard.md"] = "synced"

    # Sync key files if they exist
    sync_map = {
        "spec.md": "SPEC.md",
        "architecture.md": "ARCHITECTURE.md",
        "context.md": "CONTEXT.md",
    }

    for vault_name, source_name in sync_map.items():
        source = project_root / source_name
        if source.exists():
            content = source.read_text(encoding="utf-8")
            dest = project_vault_dir / vault_name
            _write_preserving_user_notes(dest, content)
            results[vault_name] = "synced"

    # Sync ideation outputs
    ideation_dir = project_root / "brainstormer"
    if ideation_dir.exists():
        vault_ideation = project_vault_dir / "ideation"
        vault_ideation.mkdir(parents=True, exist_ok=True)
        for f in ideation_dir.glob("*.md"):
            content = f.read_text(encoding="utf-8")
            _write_preserving_user_notes(vault_ideation / f.name, content)
            results[f"ideation/{f.name}"] = "synced"

    # Sync codeglass walkthroughs
    codeglass_dir = project_root / "docs" / "codeglass"
    if codeglass_dir.exists():
        vault_comp = project_vault_dir / "comprehension"
        vault_comp.mkdir(parents=True, exist_ok=True)
        for f in codeglass_dir.glob("*.md"):
            content = f.read_text(encoding="utf-8")
            _write_preserving_user_notes(vault_comp / f.name, content)
            results[f"comprehension/{f.name}"] = "synced"

    # Update project index
    _update_project_index(vault_path, project_name)
    results["_index.md"] = "updated"

    # Register project in config
    config = load_config()
    config.setdefault("projects", {})[str(project_root)] = project_name
    save_config(config)

    return results


def _generate_dashboard(project_root: Path, project_name: str) -> str:
    """Generate a project dashboard page for Obsidian."""
    lines = [
        f"# {project_name}",
        "",
        f"**Last synced:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
    ]

    # Read CLAUDE.md for project state if it exists
    claude_md = project_root / "CLAUDE.md"
    if claude_md.exists():
        lines.append("## Project State")
        lines.append("")
        # Extract first few lines as summary
        content = claude_md.read_text(encoding="utf-8")
        summary_lines = content.split("\n")[:20]
        lines.extend(summary_lines)
        lines.append("")

    # Links to sub-pages
    lines.extend([
        "## Quick Links",
        "",
        f"- [[{project_name}/spec|Spec]]",
        f"- [[{project_name}/architecture|Architecture]]",
        f"- [[{project_name}/ideation/angles|Ideation — Angles]]",
        f"- [[{project_name}/comprehension|Comprehension Log]]",
        "",
    ])

    # Check what's configured
    lines.append("## Status")
    lines.append("")

    checks = [
        ("CLAUDE.md", project_root / "CLAUDE.md"),
        ("SPEC.md", project_root / "SPEC.md"),
        ("ARCHITECTURE.md", project_root / "ARCHITECTURE.md"),
        ("rules.md", project_root / "rules.md"),
        ("paladin.config.json", project_root / "paladin.config.json"),
        ("brainstormer/", project_root / "brainstormer"),
        ("docs/codeglass/", project_root / "docs" / "codeglass"),
    ]

    for label, path in checks:
        status = "x" if path.exists() else " "
        lines.append(f"- [{status}] {label}")

    lines.append("")
    return "\n".join(lines)


def _write_preserving_user_notes(path: Path, new_content: str):
    """Write content to a vault file, preserving <!-- USER NOTES --> blocks."""
    user_notes = ""
    if path.exists():
        existing = path.read_text(encoding="utf-8")
        # Extract user notes block
        start_marker = "<!-- USER NOTES -->"
        end_marker = "<!-- END USER NOTES -->"
        start_idx = existing.find(start_marker)
        if start_idx != -1:
            end_idx = existing.find(end_marker, start_idx)
            if end_idx != -1:
                user_notes = existing[start_idx:end_idx + len(end_marker)]

    content = new_content
    if user_notes:
        content += f"\n\n{user_notes}\n"

    path.write_text(content, encoding="utf-8")


def _update_project_index(vault_path: Path, project_name: str):
    """Update the projects/_index.md with current project list."""
    projects_dir = vault_path / "projects"
    projects_dir.mkdir(parents=True, exist_ok=True)
    index_path = projects_dir / "_index.md"

    # Gather all project folders
    project_names = sorted([
        d.name for d in projects_dir.iterdir()
        if d.is_dir() and not d.name.startswith("_")
    ])

    lines = [
        "# Projects",
        "",
        f"*Auto-generated by BrainStormer — {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
        "",
        "| Project | Dashboard |",
        "|---------|-----------|",
    ]

    for name in project_names:
        lines.append(f"| {name} | [[{name}/dashboard]] |")

    lines.append("")
    index_path.write_text("\n".join(lines), encoding="utf-8")
