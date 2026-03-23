#!/usr/bin/env python3
"""Audit 780 agents for redundancy, overlap, and quality."""

import os
import sys
import re
from pathlib import Path
from collections import defaultdict

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, OSError):
    pass

AGENTS_DIR = Path.home() / ".claude" / "agents"


def parse_agent(path: Path) -> dict:
    """Parse an agent file into structured data."""
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None

    agent = {"path": path, "filename": path.stem, "size": len(content)}

    # Parse frontmatter
    if content.startswith("---"):
        end = content.find("---", 3)
        if end != -1:
            fm = content[3:end]
            body = content[end + 3:].strip()
            for line in fm.split("\n"):
                line = line.strip()
                if ":" in line and not line.startswith(" "):
                    key, _, val = line.partition(":")
                    agent[key.strip()] = val.strip().strip('"').strip("'")
            agent["body"] = body
        else:
            agent["body"] = content
    else:
        agent["body"] = content

    # Extract key terms from body for similarity matching
    body_lower = agent.get("body", "").lower()
    agent["has_tools"] = "tools:" in content[:500]
    agent["has_sections"] = body_lower.count("##") > 2
    agent["word_count"] = len(body_lower.split())

    return agent


def normalize(name: str) -> str:
    """Normalize name for grouping."""
    name = name.lower().strip()
    name = re.sub(r'[^a-z0-9\s]', '', name)
    # Remove common filler words
    for word in ["expert", "specialist", "agent", "pro", "the", "a", "an",
                 "senior", "lead", "chief", "master", "guru"]:
        name = re.sub(rf'\b{word}\b', '', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name


def extract_keywords(agent: dict) -> set:
    """Extract meaningful keywords from agent description and body."""
    text = (agent.get("description", "") + " " + agent.get("name", "")).lower()
    # Get significant words (length > 3, not common)
    stop_words = {"that", "this", "with", "from", "your", "have", "will",
                  "been", "they", "their", "about", "would", "could", "should",
                  "into", "also", "more", "most", "than", "then", "when",
                  "what", "which", "where", "while", "each", "every",
                  "expert", "specialist", "specializing", "focused",
                  "development", "developer", "engineering", "engineer"}
    words = set(re.findall(r'[a-z]{4,}', text))
    return words - stop_words


def find_duplicates(agents: list) -> list:
    """Find groups of agents that are likely duplicates or redundant."""
    # Group by normalized name
    name_groups = defaultdict(list)
    for a in agents:
        norm = normalize(a.get("name", a["filename"]))
        name_groups[norm].append(a)

    # Find groups with > 1 agent (exact name dupes)
    exact_dupes = {k: v for k, v in name_groups.items() if len(v) > 1}

    # Find keyword-based overlaps
    keyword_groups = defaultdict(list)
    for a in agents:
        kw = extract_keywords(a)
        # Create a signature from top keywords
        sig = frozenset(sorted(kw)[:8])
        if len(sig) >= 3:
            keyword_groups[sig].append(a)

    keyword_dupes = {k: v for k, v in keyword_groups.items()
                     if len(v) > 1 and k not in exact_dupes}

    return exact_dupes, keyword_dupes


def score_agent(agent: dict) -> int:
    """Score agent quality (higher = better, keep this one)."""
    score = 0

    # Prefer community-curated agents
    if agent.get("source") == "community":
        score += 50

    # Prefer agents with more content
    wc = agent.get("word_count", 0)
    if wc > 500:
        score += 30
    elif wc > 200:
        score += 20
    elif wc > 100:
        score += 10

    # Prefer agents with proper frontmatter
    if agent.get("name"):
        score += 10
    if agent.get("description"):
        score += 10
    if agent.get("emoji"):
        score += 5
    if agent.get("vibe"):
        score += 5

    # Prefer agents with structured content
    if agent.get("has_sections"):
        score += 15

    # Prefer agents with tool definitions
    if agent.get("has_tools"):
        score += 10

    return score


def main():
    print("=" * 60)
    print("  BrainStormer Agent Audit")
    print("=" * 60)
    print()

    # Load all agents
    agents = []
    for f in sorted(AGENTS_DIR.glob("*.md")):
        a = parse_agent(f)
        if a:
            agents.append(a)

    print(f"  Total agents: {len(agents)}")
    print()

    # Source breakdown
    sources = defaultdict(int)
    for a in agents:
        sources[a.get("source", "unknown")] += 1

    print("  By source:")
    for src, count in sorted(sources.items(), key=lambda x: -x[1]):
        print(f"    {src}: {count}")
    print()

    # Size analysis
    tiny = [a for a in agents if a["word_count"] < 50]
    small = [a for a in agents if 50 <= a["word_count"] < 150]
    medium = [a for a in agents if 150 <= a["word_count"] < 500]
    large = [a for a in agents if a["word_count"] >= 500]

    print("  By content depth:")
    print(f"    Tiny (<50 words):     {len(tiny)} — likely stubs")
    print(f"    Small (50-150):       {len(small)} — basic definitions")
    print(f"    Medium (150-500):     {len(medium)} — decent agents")
    print(f"    Large (500+ words):   {len(large)} — comprehensive agents")
    print()

    # Find duplicates
    exact_dupes, keyword_dupes = find_duplicates(agents)

    print(f"  Exact name duplicates: {len(exact_dupes)} groups")
    print(f"  Keyword overlaps: {len(keyword_dupes)} groups")
    print()

    # === REPORT: Exact duplicates ===
    remove_list = []

    if exact_dupes:
        print("-" * 60)
        print("  EXACT DUPLICATES (same normalized name)")
        print("-" * 60)
        for norm_name, group in sorted(exact_dupes.items()):
            print(f"\n  '{norm_name}' — {len(group)} versions:")
            scored = [(score_agent(a), a) for a in group]
            scored.sort(key=lambda x: -x[0])

            best = scored[0]
            print(f"    KEEP:   {best[1]['filename']}.md (score: {best[0]}, "
                  f"source: {best[1].get('source', '?')}, "
                  f"{best[1]['word_count']} words)")

            for score, a in scored[1:]:
                print(f"    REMOVE: {a['filename']}.md (score: {score}, "
                      f"source: {a.get('source', '?')}, "
                      f"{a['word_count']} words)")
                remove_list.append(a)

    # === REPORT: Stubs (too small to be useful) ===
    print()
    print("-" * 60)
    print(f"  STUBS — {len(tiny)} agents with <50 words (likely not useful)")
    print("-" * 60)
    for a in sorted(tiny, key=lambda x: x["word_count"]):
        print(f"    {a['filename']}.md — {a['word_count']} words, "
              f"source: {a.get('source', '?')}")
        remove_list.append(a)

    # === Summary ===
    print()
    print("=" * 60)
    print("  AUDIT SUMMARY")
    print("=" * 60)
    print(f"  Total agents:           {len(agents)}")
    print(f"  Exact duplicates:       {sum(len(g) - 1 for g in exact_dupes.values())} to remove")
    print(f"  Stubs (<50 words):      {len(tiny)} to remove")
    print(f"  Total to remove:        {len(remove_list)}")
    print(f"  After cleanup:          {len(agents) - len(remove_list)}")
    print()

    # Write removal list
    removal_file = AGENTS_DIR.parent / "agent-audit-removals.txt"
    with open(removal_file, "w", encoding="utf-8") as f:
        f.write("# BrainStormer Agent Audit — Files to Remove\n")
        f.write(f"# Generated: {__import__('datetime').datetime.now().isoformat()}\n")
        f.write(f"# Total: {len(remove_list)} files\n\n")
        for a in sorted(remove_list, key=lambda x: x["filename"]):
            f.write(f"{a['filename']}.md  # {a.get('source', '?')}, "
                    f"{a['word_count']} words\n")

    print(f"  Removal list saved to: {removal_file}")
    print(f"  Review and run: brainstormer agent prune")
    print()

    return remove_list


if __name__ == "__main__":
    removals = main()

    if removals and "--apply" in sys.argv:
        print("  Applying removals...")
        removed = 0
        for a in removals:
            try:
                a["path"].unlink()
                removed += 1
            except OSError as e:
                print(f"    Error removing {a['filename']}: {e}")
        print(f"  Removed {removed} files.")
        print(f"  Remaining: {len(list(AGENTS_DIR.glob('*.md')))} agents")
