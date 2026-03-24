"""brainstormer hooks — Install git hooks and manage context injection.

Usage:
    brainstormer hooks install          — Install PALADIN pre-commit + auto-learn hooks
    brainstormer hooks remove           — Remove BrainStormer git hooks
    brainstormer hooks status           — Show installed hooks
    brainstormer hooks context          — Inject relevant rules/patterns for staged files
"""

import re
import subprocess
from pathlib import Path


PRECOMMIT_HOOK = '''#!/bin/sh
# BrainStormer — PALADIN pre-commit hook
# Runs quick quality checks (tiers 1-2) before each commit.
# Full 6-tier check runs in CI.

# Skip if BRAINSTORMER_SKIP_HOOKS is set
if [ -n "$BRAINSTORMER_SKIP_HOOKS" ]; then
    exit 0
fi

# Find PALADIN script
PALADIN_SCRIPT=""
for dir in $(python -c "from pathlib import Path; p = Path.home() / '.brainstormer'; print(p)" 2>/dev/null) \\
           $(python -c "import cli.core.scaffold as s; print(s.get_brainstormer_root())" 2>/dev/null); do
    if [ -f "$dir/quality/scripts/paladin-run.sh" ]; then
        PALADIN_SCRIPT="$dir/quality/scripts/paladin-run.sh"
        break
    fi
done

if [ -z "$PALADIN_SCRIPT" ]; then
    # PALADIN not found — skip silently (don't block commits)
    exit 0
fi

echo "BrainStormer: Running PALADIN quick check (tiers 1-2)..."
bash "$PALADIN_SCRIPT" --tier=1 --tier=2 2>/dev/null

RESULT=$?
if [ $RESULT -ne 0 ]; then
    echo ""
    echo "PALADIN: Quality issues detected. Fix before committing."
    echo "Skip with: BRAINSTORMER_SKIP_HOOKS=1 git commit"
    echo ""
    exit 1
fi

exit 0
'''

POST_COMMIT_HOOK = '''#!/bin/sh
# BrainStormer — post-commit hook
# Auto-proposes rules from the commit diff.

# Skip if BRAINSTORMER_SKIP_HOOKS is set
if [ -n "$BRAINSTORMER_SKIP_HOOKS" ]; then
    exit 0
fi

# Run in background to not slow down commits
(brainstormer learn rule --from-diff HEAD~1 > /dev/null 2>&1 &)
exit 0
'''


def cmd_hooks(opts: dict) -> int:
    """Manage git hooks."""
    positional = opts.get("positional", [])

    if not positional:
        return _hooks_status(opts)

    action = positional[0]
    handlers = {
        "install": _hooks_install,
        "remove": _hooks_remove,
        "status": _hooks_status,
        "context": _hooks_context,
    }

    handler = handlers.get(action)
    if not handler:
        print(f"\n  Unknown hooks action: {action}")
        print("  Available: install, remove, status, context\n")
        return 1

    return handler(opts)


def _hooks_install(opts: dict) -> int:
    """Install BrainStormer git hooks."""
    git_dir = _find_git_dir()
    if not git_dir:
        print("\n  Not a git repository. Run from a git project root.\n")
        return 1

    hooks_dir = git_dir / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)

    installed = []

    # Install pre-commit hook
    precommit_path = hooks_dir / "pre-commit"
    if precommit_path.exists():
        existing = precommit_path.read_text(encoding="utf-8", errors="replace")
        if "BrainStormer" in existing:
            print("  Pre-commit hook already installed.")
        else:
            # Append to existing hook
            with open(precommit_path, "a", encoding="utf-8") as f:
                f.write("\n\n" + PRECOMMIT_HOOK)
            installed.append("pre-commit (appended)")
    else:
        precommit_path.write_text(PRECOMMIT_HOOK, encoding="utf-8")
        _make_executable(precommit_path)
        installed.append("pre-commit")

    # Install post-commit hook
    postcommit_path = hooks_dir / "post-commit"
    if postcommit_path.exists():
        existing = postcommit_path.read_text(encoding="utf-8", errors="replace")
        if "BrainStormer" in existing:
            print("  Post-commit hook already installed.")
        else:
            with open(postcommit_path, "a", encoding="utf-8") as f:
                f.write("\n\n" + POST_COMMIT_HOOK)
            installed.append("post-commit (appended)")
    else:
        postcommit_path.write_text(POST_COMMIT_HOOK, encoding="utf-8")
        _make_executable(postcommit_path)
        installed.append("post-commit")

    if installed:
        print()
        print("  BrainStormer hooks installed:")
        for h in installed:
            print(f"    + {h}")
        print()
        print("  Pre-commit:  PALADIN quick check (tiers 1-2)")
        print("  Post-commit: Auto-propose rules from diff")
        print()
        print("  Skip hooks: BRAINSTORMER_SKIP_HOOKS=1 git commit")
        print("  Remove:      brainstormer hooks remove")
    else:
        print("\n  All hooks already installed.\n")

    print()
    return 0


def _hooks_remove(opts: dict) -> int:
    """Remove BrainStormer git hooks."""
    git_dir = _find_git_dir()
    if not git_dir:
        print("\n  Not a git repository.\n")
        return 1

    hooks_dir = git_dir / "hooks"
    removed = []

    for hook_name in ("pre-commit", "post-commit"):
        hook_path = hooks_dir / hook_name
        if hook_path.exists():
            content = hook_path.read_text(encoding="utf-8", errors="replace")
            if "BrainStormer" in content:
                # If it's ONLY our hook, remove the file
                # If mixed, just remove our section
                lines = content.split("\n")
                our_start = None
                our_end = None
                for i, line in enumerate(lines):
                    if "BrainStormer" in line and our_start is None:
                        # Find the #!/bin/sh before this
                        our_start = max(0, i - 1)
                    if our_start is not None and line.strip() == "exit 0":
                        our_end = i + 1
                        break

                if our_start == 0 or our_start == 1:
                    # Entire file is ours
                    hook_path.unlink()
                    removed.append(f"{hook_name} (removed)")
                elif our_start is not None and our_end is not None:
                    new_content = "\n".join(lines[:our_start] + lines[our_end:])
                    hook_path.write_text(new_content.strip() + "\n", encoding="utf-8")
                    removed.append(f"{hook_name} (cleaned)")

    if removed:
        print()
        print("  BrainStormer hooks removed:")
        for h in removed:
            print(f"    - {h}")
    else:
        print("\n  No BrainStormer hooks found.")

    print()
    return 0


def _hooks_status(opts: dict) -> int:
    """Show installed hook status."""
    git_dir = _find_git_dir()

    print()
    print("  BrainStormer — Hook Status")
    print("  " + "=" * 50)
    print()

    if not git_dir:
        print("  Not a git repository.")
        print()
        return 0

    hooks_dir = git_dir / "hooks"

    for hook_name, desc in [
        ("pre-commit", "PALADIN quick check (tiers 1-2)"),
        ("post-commit", "Auto-propose rules from diff"),
    ]:
        hook_path = hooks_dir / hook_name
        if hook_path.exists():
            content = hook_path.read_text(encoding="utf-8", errors="replace")
            if "BrainStormer" in content:
                print(f"  {hook_name}: installed — {desc}")
            else:
                print(f"  {hook_name}: exists (not BrainStormer)")
        else:
            print(f"  {hook_name}: not installed")

    print()
    print("  Install: brainstormer hooks install")
    print("  Remove:  brainstormer hooks remove")
    print()
    return 0


# --- #19: Diff-Aware Context Injection ---

def _hooks_context(opts: dict) -> int:
    """Inject relevant rules and patterns based on staged/modified files."""
    project_root = Path.cwd()

    # Get staged + modified files
    staged = _run_git(["diff", "--name-only", "--cached"])
    modified = _run_git(["diff", "--name-only"])
    all_files = set()
    if staged:
        all_files.update(f.strip() for f in staged.strip().split("\n") if f.strip())
    if modified:
        all_files.update(f.strip() for f in modified.strip().split("\n") if f.strip())

    if not all_files:
        print("\n  No staged or modified files. Nothing to inject.\n")
        return 0

    print()
    print("  BrainStormer — Context Injection")
    print("  " + "=" * 50)
    print(f"\n  Files in play: {len(all_files)}")
    for f in sorted(all_files)[:10]:
        print(f"    {f}")
    if len(all_files) > 10:
        print(f"    ... and {len(all_files) - 10} more")
    print()

    # Detect file types
    extensions = set()
    for f in all_files:
        ext = Path(f).suffix.lower()
        if ext:
            extensions.add(ext)

    # Map extensions to stacks
    ext_stack_map = {
        ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
        ".tsx": "React/TypeScript", ".jsx": "React", ".rs": "Rust",
        ".go": "Go", ".rb": "Ruby", ".java": "Java", ".cs": "C#",
        ".vue": "Vue", ".svelte": "Svelte", ".sql": "SQL",
        ".yml": "Config", ".yaml": "Config", ".json": "Config",
        ".sh": "Shell", ".bash": "Shell", ".css": "CSS",
        ".html": "HTML", ".md": "Markdown",
    }

    stacks = set()
    for ext in extensions:
        if ext in ext_stack_map:
            stacks.add(ext_stack_map[ext])

    # Load rules and filter by relevant stacks
    try:
        from cli.commands.learn import _get_merged_rules, _extract_rule_metadata
    except ImportError:
        from commands.learn import _get_merged_rules, _extract_rule_metadata

    merged = _get_merged_rules(project_root)

    relevant_rules = []
    for scope, name, block in merged:
        rule_stack = _extract_rule_metadata(block, "stack").lower()
        # Match if rule stack overlaps with file stacks, or is "general"/"universal"
        if rule_stack in ("general", "universal", ""):
            relevant_rules.append((scope, name, block))
        else:
            for s in stacks:
                if s.lower() in rule_stack or rule_stack in s.lower():
                    relevant_rules.append((scope, name, block))
                    break

    if relevant_rules:
        print(f"  Relevant rules ({len(relevant_rules)} of {len(merged)}):")
        print()
        for scope, name, block in relevant_rules:
            do_this = _extract_rule_metadata(block, "do this")
            confidence = _extract_rule_metadata(block, "confidence")
            conf_tag = f" [{confidence}]" if confidence else ""
            print(f"  [{scope}] {name}{conf_tag}")
            if do_this:
                print(f"          {do_this[:70]}")
            print()
    else:
        print("  No rules match the current file set.")

    # Summary
    print(f"  Stacks detected: {', '.join(sorted(stacks)) if stacks else 'unknown'}")
    print(f"  Rules injected: {len(relevant_rules)}")
    print()
    return 0


# --- Helpers ---

def _find_git_dir() -> Path:
    """Find the .git directory."""
    current = Path.cwd()
    while current != current.parent:
        git = current / ".git"
        if git.exists():
            return git
        current = current.parent
    return None


def _make_executable(path: Path):
    """Make a file executable (Unix only, no-op on Windows)."""
    try:
        import stat
        path.chmod(path.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    except (OSError, AttributeError):
        pass


def _run_git(args: list) -> str:
    """Run a git command and return stdout."""
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True, text=True, timeout=10,
            encoding="utf-8", errors="replace",
        )
        return result.stdout if result.returncode == 0 else None
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None
