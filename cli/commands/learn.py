"""brainstormer learn — The write side of the auto-research loop.

Captures rules, walkthroughs, and patterns from coding sessions and deposits
them back into the project's knowledge base so the next session starts smarter.

Usage:
    brainstormer learn rule       — Add a rule from a lesson learned
    brainstormer learn rule --global  — Add a global rule (applies to all projects)
    brainstormer learn rule --from-diff HEAD~1  — Auto-propose rules from git diff
    brainstormer learn walkthrough — Save a CodeGlass walkthrough
    brainstormer learn walkthrough --from-diff HEAD~1  — Generate walkthrough from diff
    brainstormer learn scan       — Scan Obsidian vault for new rules/walkthroughs to import
    brainstormer learn scan --detect  — Detect recurring patterns from recent commits
    brainstormer learn status     — Show what's been learned (rule/walkthrough counts)
    brainstormer learn prune      — Flag stale or low-confidence rules for review
"""

import re
import subprocess
from pathlib import Path
from datetime import datetime


GLOBAL_DIR = Path.home() / ".brainstormer"
GLOBAL_RULES = GLOBAL_DIR / "rules.md"


def _ensure_global_dir():
    """Create ~/.brainstormer/ and global rules.md if they don't exist."""
    GLOBAL_DIR.mkdir(parents=True, exist_ok=True)
    if not GLOBAL_RULES.exists():
        GLOBAL_RULES.write_text(
            "# BrainStormer — Global Rules\n\n"
            "Rules here apply to ALL projects unless overridden.\n"
            "Add rules with: brainstormer learn rule --global\n\n"
            "---\n\n## Rules\n",
            encoding="utf-8"
        )


def _get_global_rules() -> list:
    """Parse global rules into a list of (name, block) tuples."""
    if not GLOBAL_RULES.exists():
        return []
    return _parse_rules_from_file(GLOBAL_RULES)


def _get_project_rules(project_root: Path) -> list:
    """Parse project rules into a list of (name, block) tuples."""
    rules_file = project_root / "rules.md"
    if not rules_file.exists():
        return []
    return _parse_rules_from_file(rules_file)


def _parse_rules_from_file(filepath: Path) -> list:
    """Parse a rules.md file into a list of (name, full_block) tuples."""
    content = filepath.read_text(encoding="utf-8")
    rules = []
    for match in re.finditer(r'(### Rule: (.+?)\n(?:.*?\n)*?(?=### Rule:|\Z))', content, re.DOTALL):
        block = match.group(1).rstrip()
        name = match.group(2).strip()
        rules.append((name, block))
    return rules


def _get_merged_rules(project_root: Path) -> list:
    """Merge global + project rules. Project rules override global by name."""
    global_rules = _get_global_rules()
    project_rules = _get_project_rules(project_root)

    # Project rule names take precedence
    project_names = {name for name, _ in project_rules}
    merged = []
    for name, block in global_rules:
        if name not in project_names:
            merged.append(("global", name, block))
    for name, block in project_rules:
        merged.append(("project", name, block))

    return merged


def cmd_learn(opts: dict) -> int:
    """Execute the learn command."""
    positional = opts.get("positional", [])

    if not positional:
        return _learn_status(opts)

    action = positional[0]
    handlers = {
        "rule": _learn_rule,
        "walkthrough": _learn_walkthrough,
        "scan": _learn_scan,
        "status": _learn_status,
        "prune": _learn_prune,
    }

    handler = handlers.get(action)
    if not handler:
        print(f"\n  Unknown learn action: {action}")
        print("  Available: rule, walkthrough, scan, status, prune\n")
        return 1

    return handler(opts)


def _learn_status(opts: dict) -> int:
    """Show what's been learned — global, project, and merged view."""
    project_root = Path.cwd()
    _ensure_global_dir()

    rules_file = project_root / "rules.md"
    codeglass_dir = project_root / "docs" / "codeglass"
    ruleset_file = project_root / "brainstormer" / "ruleset.md"

    print()
    print("  BrainStormer — Knowledge Status")
    print("  " + "=" * 50)
    print()

    # Global rules
    global_rules = _get_global_rules()
    print(f"  Global rules:  {len(global_rules)} in ~/.brainstormer/rules.md")

    # Project rules
    project_rules = _get_project_rules(project_root)
    print(f"  Project rules: {len(project_rules)} in rules.md")

    # Merged view
    merged = _get_merged_rules(project_root)
    overrides = sum(1 for scope, name, _ in merged if scope == "project"
                    and any(gn == name for gn, _ in global_rules))
    print(f"  Active rules:  {len(merged)} (merged, {overrides} overrides)")

    # Confidence breakdown
    confidence_counts = {"high": 0, "medium": 0, "emerging": 0, "unscored": 0}
    stale_count = 0
    for _, _, block in merged:
        conf = _extract_rule_metadata(block, "confidence")
        if conf in confidence_counts:
            confidence_counts[conf] += 1
        else:
            confidence_counts["unscored"] += 1
        last_fired = _extract_rule_metadata(block, "last_fired")
        if last_fired and last_fired != "never":
            try:
                fired_date = datetime.strptime(last_fired, "%Y-%m-%d")
                if (datetime.now() - fired_date).days > 90:
                    stale_count += 1
            except ValueError:
                pass

    if any(v > 0 for k, v in confidence_counts.items() if k != "unscored"):
        print(f"\n  Confidence: {confidence_counts['high']} high, "
              f"{confidence_counts['medium']} medium, "
              f"{confidence_counts['emerging']} emerging")
        if stale_count:
            print(f"  Stale (90+ days): {stale_count} — run 'brainstormer learn prune'")

    # Count walkthroughs
    wt_count = 0
    if codeglass_dir.exists():
        wt_count = len(list(codeglass_dir.glob("*.md")))
    print(f"\n  Walkthroughs: {wt_count} in docs/codeglass/")

    # Count ruleset entries
    rs_count = 0
    if ruleset_file.exists():
        content = ruleset_file.read_text(encoding="utf-8")
        rs_count = content.count("## Run:")
    print(f"  Ruleset runs: {rs_count} in brainstormer/ruleset.md")

    # Check Obsidian vault for unsynced knowledge
    vault_path = _get_vault_path()
    if vault_path:
        vault_rules = list((vault_path / "rules").glob("*.md")) if (vault_path / "rules").exists() else []
        print(f"\n  Obsidian vault: {vault_path}")
        print(f"  Vault rules:   {len(vault_rules)}")

        vault_wt_dirs = list((vault_path / "walkthroughs").iterdir()) if (vault_path / "walkthroughs").exists() else []
        vault_wt_count = sum(
            len(list(d.glob("*.md"))) for d in vault_wt_dirs if d.is_dir()
        )
        print(f"  Vault walkthroughs: {vault_wt_count}")
    else:
        print(f"\n  Obsidian vault: not configured")

    print()
    return 0


def _learn_rule(opts: dict) -> int:
    """Add a rule interactively, from file, or from git diff."""
    project_root = Path.cwd()
    positional = opts.get("positional", [])
    is_global = "--global" in positional

    # Determine target file
    if is_global:
        _ensure_global_dir()
        rules_file = GLOBAL_RULES
        scope_label = "global"
        positional = [p for p in positional if p != "--global"]
    else:
        rules_file = project_root / "rules.md"
        scope_label = "project"

    # --from-file: import from external file
    if "--from-file" in positional:
        idx = positional.index("--from-file")
        if idx + 1 < len(positional):
            return _import_rule_from_file(Path(positional[idx + 1]), rules_file)
        print("\n  Missing file path after --from-file\n")
        return 1

    # --from-diff: auto-propose rules from git diff
    if "--from-diff" in positional:
        idx = positional.index("--from-diff")
        ref = positional[idx + 1] if idx + 1 < len(positional) else "HEAD~1"
        return _propose_rules_from_diff(ref, rules_file, scope_label)

    # Interactive mode
    print()
    print(f"  Add a new {scope_label} rule")
    print("  " + "-" * 40)
    print()

    try:
        name = input("  Rule name: ").strip()
        if not name:
            print("  Cancelled — no name provided.")
            return 1

        do_this = input("  Do this: ").strip()
        dont_do = input("  Don't do this: ").strip()
        why = input("  Why (what breaks): ").strip()
        stack = input("  Stack (e.g. React, TypeScript): ").strip()
        source = input("  Source project/task: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\n  Cancelled.")
        return 1

    date = datetime.now().strftime("%Y-%m-%d")

    rule_block = _format_rule_block(
        name=name, do_this=do_this, dont_do=dont_do, why=why,
        stack=stack, source=source, date=date,
        confidence="emerging", hits=0, misses=0, last_fired="never",
    )

    _append_to_rules(rules_file, rule_block)
    print(f"\n  Added {scope_label} rule: {name}")
    print(f"  Total {scope_label} rules: {_count_rules(rules_file)}")
    print()
    return 0


def _learn_walkthrough(opts: dict) -> int:
    """Save a walkthrough to docs/codeglass/."""
    project_root = Path.cwd()
    codeglass_dir = project_root / "docs" / "codeglass"
    positional = opts.get("positional", [])

    # --from-diff: generate walkthrough from git diff
    if "--from-diff" in positional:
        idx = positional.index("--from-diff")
        ref = positional[idx + 1] if idx + 1 < len(positional) else "HEAD~1"
        return _generate_walkthrough_from_diff(ref, project_root)

    # --from-file: import an existing walkthrough file
    if len(positional) > 1 and positional[1] == "--from-file" and len(positional) > 2:
        src = Path(positional[2])
        if not src.exists():
            print(f"\n  File not found: {src}\n")
            return 1

        codeglass_dir.mkdir(parents=True, exist_ok=True)
        dest = codeglass_dir / src.name
        if dest.exists():
            print(f"\n  Already exists: {dest.name} (skipped)\n")
            return 0

        dest.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"\n  Imported walkthrough: {dest.name}")
        print(f"  Total walkthroughs: {len(list(codeglass_dir.glob('*.md')))}\n")
        return 0

    # Interactive mode
    print()
    print("  Save a CodeGlass walkthrough")
    print("  " + "-" * 40)
    print()

    try:
        task = input("  Task name: ").strip()
        if not task:
            print("  Cancelled — no task provided.")
            return 1
    except (EOFError, KeyboardInterrupt):
        print("\n  Cancelled.")
        return 1

    date = datetime.now().strftime("%Y-%m-%d")
    slug = re.sub(r'[^a-z0-9]+', '-', task.lower()).strip('-')
    filename = f"{date}-{slug}.md"

    codeglass_dir.mkdir(parents=True, exist_ok=True)
    dest = codeglass_dir / filename

    template = f"""---
project: "{project_root.name}"
task: "{task}"
date: {date}
patterns: []
level: standard
status: pending-review
---

## WHAT

<!-- What was built or changed? -->

## HOW

<!-- How does it work? Include data journey. -->

## WHERE

<!-- Key files and their purposes -->

## WHEN

<!-- When does this code run? What triggers it? -->

## WHY

<!-- Why these decisions? What are the alternatives? What breaks if changed? -->
"""

    dest.write_text(template, encoding="utf-8")
    print(f"\n  Created walkthrough template: docs/codeglass/{filename}")
    print(f"  Fill in the WHAT/HOW/WHERE/WHEN/WHY sections, then it's part of the loop.")
    print(f"  Total walkthroughs: {len(list(codeglass_dir.glob('*.md')))}\n")
    return 0


def _learn_scan(opts: dict) -> int:
    """Scan Obsidian vault for rules/walkthroughs, or detect patterns."""
    positional = opts.get("positional", [])

    # --detect: pattern detection mode
    if "--detect" in positional:
        return _detect_patterns(opts)

    project_root = Path.cwd()
    project_name = project_root.name
    vault_path = _get_vault_path()

    if not vault_path:
        print("\n  No Obsidian vault configured. Run: brainstormer config set vault_path <path>\n")
        return 1

    print()
    print("  Scanning Obsidian vault for importable knowledge...")
    print("  " + "=" * 50)
    print()

    imported_rules = 0
    imported_wt = 0

    # --- Scan vault rules ---
    vault_rules_dir = vault_path / "rules"
    if vault_rules_dir.exists():
        rules_file = project_root / "rules.md"
        existing_content = ""
        if rules_file.exists():
            existing_content = rules_file.read_text(encoding="utf-8")

        for rule_file in sorted(vault_rules_dir.glob("*.md")):
            rule_content = rule_file.read_text(encoding="utf-8")
            rule_name = _extract_frontmatter_field(rule_content, "name")

            if not rule_name:
                continue

            # Check if rule already exists
            if f"### Rule: {rule_name}" in existing_content:
                continue

            # Convert vault format to rules.md format
            rule_block = _convert_vault_rule(rule_content, rule_name)
            if rule_block:
                _append_to_rules(rules_file, rule_block)
                imported_rules += 1
                print(f"  + Rule: {rule_name}")

    # --- Scan vault walkthroughs for this project ---
    vault_wt_dir = vault_path / "walkthroughs" / project_name
    if vault_wt_dir.exists():
        codeglass_dir = project_root / "docs" / "codeglass"
        codeglass_dir.mkdir(parents=True, exist_ok=True)
        existing_wt = {f.name for f in codeglass_dir.glob("*.md")}

        for wt_file in sorted(vault_wt_dir.glob("*.md")):
            if wt_file.name not in existing_wt:
                dest = codeglass_dir / wt_file.name
                dest.write_text(wt_file.read_text(encoding="utf-8"), encoding="utf-8")
                imported_wt += 1
                print(f"  + Walkthrough: {wt_file.name}")

    # --- Also scan example walkthroughs (generic, apply to any project) ---
    vault_examples_dir = vault_path / "walkthroughs" / "examples"
    if vault_examples_dir.exists():
        codeglass_dir = project_root / "docs" / "codeglass"
        codeglass_dir.mkdir(parents=True, exist_ok=True)
        existing_wt = {f.name for f in codeglass_dir.glob("*.md")}

        for wt_file in sorted(vault_examples_dir.glob("*.md")):
            if wt_file.name not in existing_wt:
                dest = codeglass_dir / wt_file.name
                dest.write_text(wt_file.read_text(encoding="utf-8"), encoding="utf-8")
                imported_wt += 1
                print(f"  + Example: {wt_file.name}")

    if imported_rules == 0 and imported_wt == 0:
        print("  Everything is already synced. No new knowledge to import.")
    else:
        print()
        print(f"  Imported: {imported_rules} rules, {imported_wt} walkthroughs")

    print()
    return 0


# --- #1: Auto-Rule Proposals from Diff ---

def _propose_rules_from_diff(ref: str, rules_file: Path, scope_label: str) -> int:
    """Analyze a git diff and propose rules based on patterns found."""
    diff = _run_git(["diff", ref])
    if diff is None:
        print(f"\n  Could not read git diff for {ref}")
        print("  Make sure you're in a git repo with commits.\n")
        return 1

    if not diff.strip():
        print(f"\n  No changes found in diff against {ref}\n")
        return 0

    stat = _run_git(["diff", "--stat", ref]) or ""
    proposals = _extract_proposals_from_diff(diff, stat)

    if not proposals:
        print(f"\n  No rule-worthy patterns detected in diff against {ref}\n")
        return 0

    date = datetime.now().strftime("%Y-%m-%d")
    project_name = Path.cwd().name

    print(f"\n  BrainStormer — Auto-Proposed Rules from {ref}")
    print("  " + "=" * 50)
    print()

    for i, (name, do_this, dont_do, why, stack) in enumerate(proposals, 1):
        print(f"  {i}. {name}")
        print(f"     Do: {do_this}")
        print(f"     Why: {why}")
        print()

    print(f"  {len(proposals)} rules proposed. They'll be added as [auto-proposed]")
    print(f"  with confidence: emerging. Review with 'brainstormer learn status'.")
    print()

    # Deduplicate: skip rules that already exist by name
    existing_content = rules_file.read_text(encoding="utf-8") if rules_file.exists() else ""
    added = 0
    for name, do_this, dont_do, why, stack in proposals:
        if f"### Rule: {name}" in existing_content:
            continue
        rule_block = _format_rule_block(
            name=f"{name} [auto-proposed]",
            do_this=do_this, dont_do=dont_do, why=why,
            stack=stack, source=f"git diff {ref} ({project_name})",
            date=date, confidence="emerging",
            hits=0, misses=0, last_fired="never",
        )
        _append_to_rules(rules_file, rule_block)
        added += 1

    print(f"  Added {added} {scope_label} rules ({len(proposals) - added} already existed).")
    print(f"  Total {scope_label} rules: {_count_rules(rules_file)}\n")
    return 0


def _extract_proposals_from_diff(diff: str, stat: str) -> list:
    """Extract rule-worthy patterns from a git diff.

    Returns list of (name, do_this, dont_do, why, stack) tuples.
    """
    proposals = []
    lines = diff.split("\n")
    added_lines = [l[1:] for l in lines if l.startswith("+") and not l.startswith("+++")]

    # Pattern: New error handling added
    error_patterns = [l for l in added_lines if re.search(
        r'(try|catch|except|\.catch|\.on\s*\(\s*["\']error)', l)]
    if len(error_patterns) >= 2:
        proposals.append((
            "Add Error Handling for New Code Paths",
            "Wrap new async/external calls in try/catch or error boundaries",
            "Leave new code paths without error handling",
            "Unhandled errors cause silent failures in production",
            _detect_stack_from_diff(diff),
        ))

    # Pattern: New environment variables
    env_refs = [l for l in added_lines if re.search(
        r'(process\.env\.|os\.environ|os\.getenv|env\(|ENV\[)', l)]
    if env_refs:
        proposals.append((
            "Document New Environment Variables",
            "Add new env vars to .env.example and document their purpose",
            "Add env var references without documentation",
            "Missing env vars cause confusing startup failures",
            _detect_stack_from_diff(diff),
        ))

    # Pattern: New dependencies imported
    new_imports = [l for l in added_lines if re.search(
        r'(^import |^from .+ import |require\(|import .+ from )', l)]
    if len(new_imports) >= 3:
        proposals.append((
            "Validate New Dependencies",
            "Check bundle size impact and license compatibility of new imports",
            "Add dependencies without checking their footprint",
            "Dependency bloat and license conflicts are hard to undo",
            _detect_stack_from_diff(diff),
        ))

    # Pattern: New API endpoints or routes
    route_patterns = [l for l in added_lines if re.search(
        r'(@app\.(get|post|put|delete|patch)|router\.(get|post|put|delete)|'
        r'@(Get|Post|Put|Delete|Patch)\(|path\(|url\()', l)]
    if route_patterns:
        proposals.append((
            "Test New API Endpoints",
            "Write integration tests for new routes before merging",
            "Ship new endpoints without test coverage",
            "Untested endpoints are the #1 source of production incidents",
            _detect_stack_from_diff(diff),
        ))

    # Pattern: Database schema changes
    db_patterns = [l for l in added_lines if re.search(
        r'(CREATE TABLE|ALTER TABLE|ADD COLUMN|DROP COLUMN|migration|\.migrate|'
        r'db\.|schema\.|Model\.|models\.)', l, re.IGNORECASE)]
    if db_patterns:
        proposals.append((
            "Review Database Changes for Reversibility",
            "Ensure schema changes have a rollback migration",
            "Make destructive schema changes without rollback plan",
            "Irreversible schema changes can cause data loss",
            _detect_stack_from_diff(diff),
        ))

    # Pattern: Config file changes
    config_patterns = [f for f in stat.split("\n") if re.search(
        r'(\.config\.|config\.ya?ml|\.env|settings\.|\.json)', f)]
    if config_patterns:
        proposals.append((
            "Validate Config Changes Across Environments",
            "Check that config changes work in dev, staging, and production",
            "Change config without verifying environment compatibility",
            "Config drift between environments causes deployment failures",
            _detect_stack_from_diff(diff),
        ))

    return proposals


def _detect_stack_from_diff(diff: str) -> str:
    """Detect tech stack from diff content."""
    if "import React" in diff or "from 'react'" in diff or 'from "react"' in diff:
        return "React"
    if "from fastapi" in diff or "from flask" in diff or "from django" in diff:
        return "Python"
    if "func " in diff and "package " in diff:
        return "Go"
    if "fn " in diff and "use " in diff:
        return "Rust"
    if "def " in diff or "import " in diff:
        return "Python"
    if "const " in diff or "function " in diff:
        return "JavaScript/TypeScript"
    return "General"


# --- #3: Rule Confidence & Decay ---

def _format_rule_block(name, do_this, dont_do, why, stack, source, date,
                       confidence="emerging", hits=0, misses=0,
                       last_fired="never") -> str:
    """Format a rule block with confidence metadata."""
    return f"""
### Rule: {name}
- **Do this:** {do_this}
- **Don't do this:** {dont_do}
- **Why:** {why}
- **Stack:** {stack}
- **Source:** {source}
- **Date:** {date}
- **Confidence:** {confidence}
- **Hits:** {hits}
- **Misses:** {misses}
- **Last fired:** {last_fired}
"""


def _extract_rule_metadata(block: str, field: str) -> str:
    """Extract a metadata field from a rule block."""
    match = re.search(rf'\*\*{re.escape(field.title())}:\*\*\s*(.+)', block, re.IGNORECASE)
    if not match:
        # Try alternate format
        match = re.search(rf'\*\*{re.escape(field.replace("_", " ").title())}:\*\*\s*(.+)', block, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return ""


def _update_rule_confidence(rules_file: Path, rule_name: str, hit: bool = True):
    """Increment hit or miss counter for a rule and recalculate confidence."""
    if not rules_file.exists():
        return

    content = rules_file.read_text(encoding="utf-8")
    pattern = rf'(### Rule: {re.escape(rule_name)}\n(?:.*?\n)*?)(?=### Rule:|\Z)'
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        return

    block = match.group(1)
    hits = int(_extract_rule_metadata(block, "hits") or "0")
    misses = int(_extract_rule_metadata(block, "misses") or "0")

    if hit:
        hits += 1
    else:
        misses += 1

    # Recalculate confidence
    total = hits + misses
    if total >= 5:
        ratio = hits / total
        if ratio >= 0.7:
            confidence = "high"
        elif ratio >= 0.4:
            confidence = "medium"
        else:
            confidence = "emerging"
    else:
        confidence = "emerging"

    today = datetime.now().strftime("%Y-%m-%d")

    # Update the block
    new_block = block
    new_block = re.sub(r'\*\*Hits:\*\*\s*\d+', f'**Hits:** {hits}', new_block)
    new_block = re.sub(r'\*\*Misses:\*\*\s*\d+', f'**Misses:** {misses}', new_block)
    new_block = re.sub(r'\*\*Confidence:\*\*\s*\w+', f'**Confidence:** {confidence}', new_block)
    if hit:
        new_block = re.sub(r'\*\*Last fired:\*\*\s*.+', f'**Last fired:** {today}', new_block)

    content = content.replace(block, new_block)
    rules_file.write_text(content, encoding="utf-8")


def _learn_prune(opts: dict) -> int:
    """Flag stale or low-confidence rules for review."""
    project_root = Path.cwd()
    _ensure_global_dir()

    merged = _get_merged_rules(project_root)
    if not merged:
        print("\n  No rules to prune.\n")
        return 0

    stale = []
    low_conf = []
    today = datetime.now()

    for scope, name, block in merged:
        hits = int(_extract_rule_metadata(block, "hits") or "0")
        misses = int(_extract_rule_metadata(block, "misses") or "0")
        last_fired = _extract_rule_metadata(block, "last_fired")

        # Check staleness
        if last_fired and last_fired not in ("never", ""):
            try:
                fired_date = datetime.strptime(last_fired, "%Y-%m-%d")
                days_ago = (today - fired_date).days
                if days_ago > 90:
                    stale.append((scope, name, days_ago))
            except ValueError:
                pass
        elif last_fired == "never" or last_fired == "":
            # Rules that have never fired — check date added
            date_added = _extract_rule_metadata(block, "date")
            if date_added:
                try:
                    added = datetime.strptime(date_added, "%Y-%m-%d")
                    if (today - added).days > 90:
                        stale.append((scope, name, (today - added).days))
                except ValueError:
                    pass

        # Check low confidence
        total = hits + misses
        if total >= 5:
            ratio = hits / total
            if ratio < 0.3:
                low_conf.append((scope, name, hits, misses, ratio))

    print()
    print("  BrainStormer — Rule Pruning Review")
    print("  " + "=" * 50)
    print()

    if stale:
        print(f"  Stale rules (90+ days without firing):")
        for scope, name, days in stale:
            print(f"    [{scope}] {name} — {days} days")
        print()

    if low_conf:
        print(f"  Low confidence (< 30% hit rate, 5+ events):")
        for scope, name, hits, misses, ratio in low_conf:
            print(f"    [{scope}] {name} — {hits}/{hits+misses} hits ({ratio:.0%})")
        print()

    if not stale and not low_conf:
        print("  All rules are healthy. Nothing to prune.")
    else:
        total_flagged = len(stale) + len(low_conf)
        print(f"  {total_flagged} rules flagged for review.")
        print("  Remove with: brainstormer learn rule --remove <name>")

    print()
    return 0


# --- #5: Pattern Detector ---

def _detect_patterns(opts: dict) -> int:
    """Detect recurring patterns from recent commits."""
    n = 10  # Check last N commits
    positional = opts.get("positional", [])

    # Allow custom commit count: --detect 20
    for i, p in enumerate(positional):
        if p == "--detect" and i + 1 < len(positional):
            try:
                n = int(positional[i + 1])
            except ValueError:
                pass

    print(f"\n  Scanning last {n} commits for recurring patterns...")
    print("  " + "=" * 50)
    print()

    # Get file change frequency
    log = _run_git(["log", f"-{n}", "--pretty=format:", "--name-only"])
    if not log:
        print("  No git history found.\n")
        return 0

    file_counts = {}
    for line in log.strip().split("\n"):
        line = line.strip()
        if line:
            file_counts[line] = file_counts.get(line, 0) + 1

    # Files changed 3+ times = hot spots
    hotspots = [(f, c) for f, c in file_counts.items() if c >= 3]
    hotspots.sort(key=lambda x: -x[1])

    # Get added function/class patterns
    diff_all = _run_git(["log", f"-{n}", "-p", "--diff-filter=A"])
    func_patterns = {}
    if diff_all:
        for match in re.finditer(r'^\+\s*(def |function |class |const \w+ = |export (?:default )?(?:function|class) )(\w+)', diff_all, re.MULTILINE):
            kind = match.group(1).strip()
            name = match.group(2)
            func_patterns.setdefault(kind, []).append(name)

    # Report findings
    pattern_count = 0

    if hotspots:
        print("  Hot files (changed 3+ times):")
        for f, c in hotspots[:10]:
            print(f"    {c}x  {f}")
        print()
        pattern_count += len(hotspots)

    if func_patterns:
        print("  Recurring code patterns:")
        for kind, names in func_patterns.items():
            if len(names) >= 2:
                print(f"    {kind.strip()}: {len(names)} new ({', '.join(names[:5])})")
                pattern_count += 1
        print()

    if pattern_count == 0:
        print("  No strong patterns detected yet. Keep coding!")
    else:
        print(f"  {pattern_count} patterns detected.")
        print("  Consider adding rules for recurring patterns.")

    print()
    return 0


# --- #4: Walkthrough Generator from Diff ---

def _generate_walkthrough_from_diff(ref: str, project_root: Path) -> int:
    """Generate a CodeGlass walkthrough from a git diff."""
    diff = _run_git(["diff", ref])
    if not diff or not diff.strip():
        print(f"\n  No changes found in diff against {ref}\n")
        return 1

    stat = _run_git(["diff", "--stat", ref]) or ""
    log_msg = _run_git(["log", "-1", "--pretty=format:%s", ref]) or "Unknown change"

    # Parse the diff for key info
    files_changed = []
    for line in stat.strip().split("\n"):
        match = re.match(r'\s*(.+?)\s*\|', line)
        if match:
            files_changed.append(match.group(1).strip())

    added_funcs = []
    for match in re.finditer(r'^\+\s*(def |function |class |export )(\w+)', diff, re.MULTILINE):
        added_funcs.append(f"{match.group(1).strip()} {match.group(2)}")

    date = datetime.now().strftime("%Y-%m-%d")
    slug = re.sub(r'[^a-z0-9]+', '-', log_msg.lower()).strip('-')[:50]
    filename = f"{date}-{slug}.md"

    codeglass_dir = project_root / "docs" / "codeglass"
    codeglass_dir.mkdir(parents=True, exist_ok=True)
    dest = codeglass_dir / filename

    files_list = "\n".join(f"- `{f}`" for f in files_changed[:15]) or "- (see git diff)"
    funcs_list = "\n".join(f"- `{f}`" for f in added_funcs[:10]) if added_funcs else "- No new functions detected"

    template = f"""---
project: "{project_root.name}"
task: "{log_msg}"
date: {date}
ref: "{ref}"
patterns: []
level: standard
status: auto-generated
---

## WHAT

{log_msg}

Files changed:
{files_list}

## HOW

New functions/classes:
{funcs_list}

Key changes (from diff):
- {len(files_changed)} files modified
- Review `git diff {ref}` for full details

## WHERE

{files_list}

## WHEN

Generated from git ref: `{ref}`
Commit context: {log_msg}

## WHY

<!-- Why these decisions? What alternatives were considered? -->
<!-- Fill in the reasoning — the diff shows WHAT, this section captures WHY -->
"""

    dest.write_text(template, encoding="utf-8")
    wt_count = len(list(codeglass_dir.glob("*.md")))
    print(f"\n  Generated walkthrough: docs/codeglass/{filename}")
    print(f"  Status: auto-generated (review and fill in WHY section)")
    print(f"  Total walkthroughs: {wt_count}\n")
    return 0


# --- Git helpers ---

def _run_git(args: list) -> str:
    """Run a git command and return stdout, or None on failure."""
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True, text=True, timeout=30,
            encoding="utf-8", errors="replace",
        )
        if result.returncode == 0:
            return result.stdout
        return None
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None


# --- Helpers ---

def _get_vault_path():
    """Get the Obsidian vault path from config."""
    try:
        from core.vault import load_config, get_vault_path
    except ImportError:
        try:
            from cli.core.vault import load_config, get_vault_path
        except ImportError:
            return None

    config = load_config()
    return get_vault_path(config)


def _append_to_rules(rules_file: Path, rule_block: str):
    """Append a rule block to rules.md, creating if needed."""
    if not rules_file.exists():
        rules_file.write_text(
            "# CodeGlass — Rules File\n\n"
            "Rules are added after coding sessions surface them.\n"
            "Never delete rules — the value is in the accumulation.\n\n"
            "---\n\n## Rules\n",
            encoding="utf-8"
        )

    content = rules_file.read_text(encoding="utf-8")
    # Ensure trailing newline before appending
    if not content.endswith("\n"):
        content += "\n"
    content += rule_block
    rules_file.write_text(content, encoding="utf-8")


def _count_rules(rules_file: Path) -> int:
    """Count rules in rules.md."""
    if not rules_file.exists():
        return 0
    return rules_file.read_text(encoding="utf-8").count("### Rule:")


def _extract_frontmatter_field(content: str, field: str) -> str:
    """Extract a field from YAML frontmatter."""
    match = re.search(rf'^{field}:\s*(.+)$', content, re.MULTILINE)
    if match:
        return match.group(1).strip().strip('"').strip("'")
    return ""


def _convert_vault_rule(content: str, name: str) -> str:
    """Convert an Obsidian vault rule (frontmatter + sections) to rules.md format."""
    stack = _extract_frontmatter_field(content, "stack")
    source = _extract_frontmatter_field(content, "source-project")
    confidence = _extract_frontmatter_field(content, "confidence")
    date = _extract_frontmatter_field(content, "date")

    # Extract sections
    pattern = _extract_section(content, "Pattern") or _extract_section(content, "How to Apply")
    reason = _extract_section(content, "Reason")

    if not pattern:
        return ""

    date_str = date or datetime.now().strftime("%Y-%m-%d")
    source_str = source or "Obsidian vault"

    return f"""
### Rule: {name}
- **Do this:** {pattern}
- **Don't do this:** (see reason)
- **Why:** {reason or 'Imported from vault'}
- **Stack:** {stack or 'General'}
- **Source:** {source_str}
- **Date:** {date_str}
"""


def _extract_section(content: str, heading: str) -> str:
    """Extract text under a markdown heading."""
    pattern = rf'##\s+{re.escape(heading)}\s*\n(.*?)(?=\n##|\Z)'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        text = match.group(1).strip()
        # Collapse to single line for rule format
        return re.sub(r'\s+', ' ', text)
    return ""
