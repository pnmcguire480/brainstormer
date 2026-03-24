"""brainstormer summary — Auto-generated daily journal in Obsidian.

Captures session summaries with auto-linked keywords and drops them
into the Obsidian vault's summaries/ folder organized by date.

Usage:
    brainstormer summary          — Generate a summary for the current session
    brainstormer summary --auto   — Fully automatic (for use in Claude Code hooks)
    brainstormer summary rollup   — Generate/update today's daily rollup
    brainstormer summary status   — Show summary stats
"""

import re
import subprocess
from pathlib import Path
from datetime import datetime


def cmd_summary(opts: dict) -> int:
    """Execute the summary command."""
    positional = opts.get("positional", [])
    is_auto = "--auto" in positional

    if not positional or is_auto:
        return _generate_summary(opts, auto=is_auto)

    action = positional[0]
    if action == "rollup":
        return _generate_rollup(opts)
    elif action == "status":
        return _summary_status(opts)
    else:
        print(f"\n  Unknown summary action: {action}")
        print("  Available: (default), rollup, status\n")
        return 1


def _generate_summary(opts: dict, auto: bool = False) -> int:
    """Generate a session summary and write to vault."""
    vault_path = _get_vault_path()
    if not vault_path:
        if not auto:
            print("\n  No Obsidian vault configured. Run: brainstormer config set vault_path <path>\n")
        return 1

    project_root = Path.cwd()
    project_name = project_root.name
    today = datetime.now().strftime("%Y-%m-%d")
    time_now = datetime.now().strftime("%H:%M")

    # Create summaries directory
    summaries_dir = Path(vault_path) / "summaries" / today
    summaries_dir.mkdir(parents=True, exist_ok=True)

    # Determine session number
    existing = sorted(summaries_dir.glob("*.md"))
    # Filter out daily-rollup.md
    session_files = [f for f in existing if not f.name.startswith("daily-rollup")]
    session_num = len(session_files) + 1

    # Gather context
    diff_stat = _run_git(["diff", "--stat", "HEAD~1"]) or ""
    recent_log = _run_git(["log", "-3", "--pretty=format:%s"]) or ""
    changed_files = _get_changed_files()

    # Build summary content
    commit_msgs = [l.strip() for l in recent_log.strip().split("\n") if l.strip()]
    what_done = "\n".join(f"- {msg}" for msg in commit_msgs[:5]) if commit_msgs else "- (no recent commits)"

    files_section = "\n".join(f"- `{f}`" for f in changed_files[:15]) if changed_files else "- (no files tracked)"

    # Load and apply keywords
    try:
        from cli.core.keywords import refresh_keywords, apply_wikilinks
    except ImportError:
        try:
            from core.keywords import refresh_keywords, apply_wikilinks
        except ImportError:
            refresh_keywords = None
            apply_wikilinks = None

    keywords = None
    keywords_linked = 0
    if refresh_keywords:
        keywords = refresh_keywords(vault_path=vault_path, project_root=project_root)

    # Build the summary body (before wikilinks)
    slug = re.sub(r'[^a-z0-9]+', '-', project_name.lower()).strip('-')
    topic = commit_msgs[0][:30] if commit_msgs else "session"
    topic_slug = re.sub(r'[^a-z0-9]+', '-', topic.lower()).strip('-')[:20]
    filename = f"{session_num:03d}-{slug}-{topic_slug}.md"

    body = f"""## What was done
{what_done}

## Files changed
{files_section}

## What was learned
<!-- Key decisions, patterns, or rules from this session -->

## Links
<!-- Auto-linked by BrainStormer keyword engine -->
"""

    # Apply wikilinks
    if apply_wikilinks and keywords:
        linked_body = apply_wikilinks(body, keywords)
        # Count links added
        keywords_linked = linked_body.count("[[") - body.count("[[")
        body = linked_body

    # Also wikilink the project name in the header
    header_project = f"[[{project_name}]]" if apply_wikilinks else project_name

    # Detect tags from content
    tags = _detect_tags(diff_stat, commit_msgs, changed_files)

    content = f"""---
date: {today}
time: "{time_now}"
project: {project_name}
session: {session_num}
tags: [{', '.join(tags)}]
keywords_linked: {keywords_linked}
---
# Session Summary \u2014 {header_project}

{body}"""

    dest = summaries_dir / filename
    dest.write_text(content, encoding="utf-8")

    if not auto:
        print(f"\n  Summary saved: summaries/{today}/{filename}")
        print(f"  Keywords linked: {keywords_linked}")
        print(f"  Session {session_num} for today")
        print()

    # Retroactive linking of previous summaries
    if apply_wikilinks and keywords:
        try:
            from cli.core.keywords import retroactive_link
        except ImportError:
            try:
                from core.keywords import retroactive_link
            except ImportError:
                retroactive_link = None

        if retroactive_link:
            parent_summaries = Path(vault_path) / "summaries"
            updated = retroactive_link(parent_summaries, keywords)
            if updated and not auto:
                print(f"  Retroactively linked {updated} previous summaries")
                print()

    return 0


def _generate_rollup(opts: dict) -> int:
    """Generate or update today's daily rollup."""
    vault_path = _get_vault_path()
    if not vault_path:
        print("\n  No Obsidian vault configured.\n")
        return 1

    today = datetime.now().strftime("%Y-%m-%d")
    summaries_dir = Path(vault_path) / "summaries" / today

    if not summaries_dir.exists():
        print(f"\n  No summaries found for {today}\n")
        return 0

    session_files = sorted(
        f for f in summaries_dir.glob("*.md")
        if not f.name.startswith("daily-rollup")
    )

    if not session_files:
        print(f"\n  No session summaries for {today}\n")
        return 0

    # Parse each summary
    sessions = []
    projects = set()
    total_keywords = 0

    for sf in session_files:
        content = sf.read_text(encoding="utf-8")
        project = _extract_frontmatter(content, "project")
        kw_count = _extract_frontmatter(content, "keywords_linked")
        if project:
            projects.add(project)
        try:
            total_keywords += int(kw_count)
        except (ValueError, TypeError):
            pass

        # Extract first line of "What was done"
        what_match = re.search(r'## What was done\s*\n-\s*(.+)', content)
        summary_line = what_match.group(1).strip() if what_match else sf.stem

        sessions.append((sf.stem, summary_line))

    session_list = "\n".join(
        f"{i}. [[{name}]] \u2014 {desc}"
        for i, (name, desc) in enumerate(sessions, 1)
    )
    project_list = ", ".join(sorted(projects))

    rollup = f"""---
date: {today}
sessions: {len(sessions)}
projects: [{project_list}]
total_keywords_linked: {total_keywords}
---
# Daily Rollup \u2014 {today}

## Sessions
{session_list}

## Knowledge growth
- {total_keywords} keywords linked across {len(sessions)} sessions
- Projects touched: {project_list}
"""

    dest = summaries_dir / "daily-rollup.md"
    dest.write_text(rollup, encoding="utf-8")

    print(f"\n  Daily rollup saved: summaries/{today}/daily-rollup.md")
    print(f"  {len(sessions)} sessions, {len(projects)} projects, {total_keywords} keywords linked\n")
    return 0


def _summary_status(opts: dict) -> int:
    """Show summary statistics."""
    vault_path = _get_vault_path()
    if not vault_path:
        print("\n  No Obsidian vault configured.\n")
        return 1

    summaries_dir = Path(vault_path) / "summaries"
    if not summaries_dir.exists():
        print("\n  No summaries yet. Run: brainstormer summary\n")
        return 0

    days = sorted(d for d in summaries_dir.iterdir() if d.is_dir())
    total_summaries = 0
    total_rollups = 0

    for day in days:
        sessions = [f for f in day.glob("*.md") if not f.name.startswith("daily-rollup")]
        rollups = list(day.glob("daily-rollup.md"))
        total_summaries += len(sessions)
        total_rollups += len(rollups)

    print()
    print("  BrainStormer \u2014 Summary Journal Status")
    print("  " + "=" * 50)
    print()
    print(f"  Days tracked:    {len(days)}")
    print(f"  Total summaries: {total_summaries}")
    print(f"  Daily rollups:   {total_rollups}")

    if days:
        print(f"  First day:       {days[0].name}")
        print(f"  Latest day:      {days[-1].name}")

    # Keyword registry
    try:
        from cli.core.keywords import load_keywords
    except ImportError:
        try:
            from core.keywords import load_keywords
        except ImportError:
            load_keywords = None

    if load_keywords:
        kw = load_keywords()
        total_kw = sum(len(v) for v in kw.values())
        print(f"\n  Keyword registry: {total_kw} keywords across {len(kw)} categories")

    print()
    return 0


# --- Helpers ---

def _get_vault_path():
    """Get Obsidian vault path from config."""
    try:
        from cli.core.vault import load_config, get_vault_path
    except ImportError:
        try:
            from core.vault import load_config, get_vault_path
        except ImportError:
            return None
    config = load_config()
    return get_vault_path(config)


def _run_git(args: list) -> str:
    """Run a git command and return stdout."""
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True, text=True, timeout=30,
            encoding="utf-8", errors="replace",
        )
        return result.stdout if result.returncode == 0 else None
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None


def _get_changed_files() -> list:
    """Get recently changed files from git."""
    result = _run_git(["diff", "--name-only", "HEAD~1"])
    if not result:
        # Fallback: staged + unstaged
        result = _run_git(["diff", "--name-only"]) or ""
        staged = _run_git(["diff", "--name-only", "--cached"]) or ""
        result = result + "\n" + staged

    return [f.strip() for f in result.strip().split("\n") if f.strip()]


def _detect_tags(stat: str, commits: list, files: list) -> list:
    """Auto-detect tags from session content."""
    tags = set()
    all_text = " ".join([stat] + commits + files).lower()

    tag_patterns = {
        "bugfix": r"fix|bug|patch|hotfix",
        "feature": r"add|new|implement|create",
        "refactor": r"refactor|clean|reorganize|rename",
        "docs": r"doc|readme|comment|changelog",
        "test": r"test|spec|assert|coverage",
        "ci": r"ci|workflow|action|deploy|release",
        "ideation": r"angle|hook|calendar|brainstorm|roadmap",
        "config": r"config|setting|env|yaml|json",
    }

    for tag, pattern in tag_patterns.items():
        if re.search(pattern, all_text):
            tags.add(tag)

    return sorted(tags) if tags else ["general"]


def _extract_frontmatter(content: str, field: str) -> str:
    """Extract a field from YAML frontmatter."""
    match = re.search(rf'^{field}:\s*(.+)$', content, re.MULTILINE)
    if match:
        return match.group(1).strip().strip('"').strip("'")
    return ""
