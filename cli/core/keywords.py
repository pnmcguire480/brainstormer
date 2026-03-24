"""Keyword taxonomy for auto-linking Obsidian wikilinks.

Manages a registry of crucial keywords across 6 sources:
  1. Projects — from obsidian/config.yaml
  2. Skills — hardcoded BrainStormer sub-skills
  3. Commands — from CLI command registry
  4. Concepts — from rules.md headings + pattern-library.md
  5. People — from git config
  6. Vault notes — filesystem scan of vault .md filenames
  + Custom — user-defined keywords

Registry stored at ~/.brainstormer/keywords.yml
"""

import re
import subprocess
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None


GLOBAL_DIR = Path.home() / ".brainstormer"
KEYWORDS_FILE = GLOBAL_DIR / "keywords.yml"

# Hardcoded skill names
SKILL_KEYWORDS = [
    "BrainStormer", "PALADIN", "CodeGlass", "Kernel",
    "Comprehension", "Ideation", "Quality",
]

# CLI commands
COMMAND_KEYWORDS = [
    "init", "status", "doctor", "sync", "update", "migrate",
    "learn", "summary", "agent", "license", "telemetry", "config",
]


def load_keywords() -> dict:
    """Load keyword registry from disk, auto-populating if needed."""
    keywords = {
        "projects": [],
        "skills": list(SKILL_KEYWORDS),
        "commands": list(COMMAND_KEYWORDS),
        "concepts": [],
        "people": [],
        "vault_notes": [],
        "custom": [],
    }

    if KEYWORDS_FILE.exists():
        try:
            if yaml:
                data = yaml.safe_load(KEYWORDS_FILE.read_text(encoding="utf-8"))
            else:
                data = _parse_simple_yaml(KEYWORDS_FILE.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                for key in keywords:
                    if key in data and isinstance(data[key], list):
                        keywords[key] = data[key]
        except Exception:
            pass

    return keywords


def save_keywords(keywords: dict):
    """Save keyword registry to disk."""
    GLOBAL_DIR.mkdir(parents=True, exist_ok=True)
    lines = ["# BrainStormer — Keyword Registry",
             "# Auto-generated + user-extensible", ""]
    for key, values in keywords.items():
        if values:
            items = ", ".join(f'"{v}"' if " " in str(v) else str(v)
                              for v in values)
            lines.append(f"{key}: [{items}]")
        else:
            lines.append(f"{key}: []")
    KEYWORDS_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def refresh_keywords(vault_path=None, project_root=None) -> dict:
    """Refresh keyword registry from all sources."""
    keywords = load_keywords()

    # 1. Projects from vault config
    if vault_path:
        try:
            config_path = _find_config()
            if config_path and config_path.exists():
                content = config_path.read_text(encoding="utf-8")
                if yaml:
                    config = yaml.safe_load(content)
                else:
                    config = {}
                projects = config.get("projects", {})
                if isinstance(projects, dict):
                    keywords["projects"] = list(set(projects.values()))
        except Exception:
            pass

    # 2. Skills — always hardcoded
    keywords["skills"] = list(SKILL_KEYWORDS)

    # 3. Commands — always hardcoded
    keywords["commands"] = list(COMMAND_KEYWORDS)

    # 4. Concepts from rules.md + pattern library
    if project_root:
        concepts = set(keywords.get("concepts", []))
        rules_file = project_root / "rules.md"
        if rules_file.exists():
            content = rules_file.read_text(encoding="utf-8")
            for match in re.finditer(r'### Rule: (.+)', content):
                name = match.group(1).strip()
                # Remove [auto-proposed] tag
                name = re.sub(r'\s*\[auto-proposed\]', '', name)
                if len(name) > 2:
                    concepts.add(name)

        # Add common concepts
        concepts.update([
            "rules", "patterns", "walkthroughs", "agents", "pipelines",
            "rulesets", "roadmap", "auto-learn", "confidence",
        ])
        keywords["concepts"] = sorted(concepts)

    # 5. People from git
    try:
        result = subprocess.run(
            ["git", "config", "user.name"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            people = set(keywords.get("people", []))
            people.add(result.stdout.strip())
            keywords["people"] = sorted(people)
    except Exception:
        pass

    # 6. Vault notes — scan filenames
    if vault_path:
        vault = Path(vault_path)
        if vault.exists():
            note_names = set()
            for md_file in vault.rglob("*.md"):
                name = md_file.stem
                if len(name) > 2 and not name.startswith("_"):
                    note_names.add(name)
            keywords["vault_notes"] = sorted(note_names)[:500]  # Cap at 500

    save_keywords(keywords)
    return keywords


def apply_wikilinks(text: str, keywords: dict = None) -> str:
    """Replace keyword occurrences with [[wikilinks]], skipping already-linked text."""
    if keywords is None:
        keywords = load_keywords()

    # Collect all keywords, longest first (to avoid partial matches)
    all_kw = set()
    for source, terms in keywords.items():
        for term in terms:
            if isinstance(term, str) and len(term) > 2:
                all_kw.add(term)

    # Sort longest first
    sorted_kw = sorted(all_kw, key=len, reverse=True)

    for kw in sorted_kw:
        # Match keyword NOT already inside [[ ]], NOT inside backticks, NOT in file paths
        # Skip lines that look like file paths (start with - ` or contain /)
        def _link_if_safe(match):
            # Check if the match is inside a backtick span or file path
            start = match.start()
            # Find the line containing this match
            line_start = text.rfind("\n", 0, start) + 1
            line = text[line_start:text.find("\n", start)]
            # Don't link inside backtick-wrapped content
            pre = text[line_start:start]
            if pre.count("`") % 2 == 1:  # Inside backticks
                return match.group(0)
            return f"[[{match.group(1)}]]"

        pattern = rf'(?<!\[\[)\b({re.escape(kw)})\b(?!\]\])'
        text = re.sub(pattern, _link_if_safe, text, count=1)

    return text


def retroactive_link(summaries_dir: Path, keywords: dict = None):
    """Scan existing summaries and add wikilinks for new keywords."""
    if keywords is None:
        keywords = load_keywords()

    if not summaries_dir.exists():
        return 0

    updated = 0
    for md_file in summaries_dir.rglob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        # Don't touch frontmatter
        parts = content.split("---", 2)
        if len(parts) >= 3:
            body = parts[2]
            new_body = apply_wikilinks(body, keywords)
            if new_body != body:
                md_file.write_text(parts[0] + "---" + parts[1] + "---" + new_body,
                                   encoding="utf-8")
                updated += 1
        else:
            new_content = apply_wikilinks(content, keywords)
            if new_content != content:
                md_file.write_text(new_content, encoding="utf-8")
                updated += 1

    return updated


def _find_config():
    """Find obsidian/config.yaml."""
    current = Path(__file__).resolve()
    for parent in current.parents:
        cfg = parent / "obsidian" / "config.yaml"
        if cfg.exists():
            return cfg
    return None


def _parse_simple_yaml(text: str) -> dict:
    """Minimal YAML parser for keyword files (no PyYAML dependency)."""
    result = {}
    for line in text.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        match = re.match(r'(\w+):\s*\[(.+)\]', line)
        if match:
            key = match.group(1)
            raw = match.group(2)
            items = [s.strip().strip('"').strip("'") for s in raw.split(",")]
            result[key] = [i for i in items if i]
    return result
