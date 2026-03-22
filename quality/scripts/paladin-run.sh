#!/usr/bin/env bash
# paladin-run.sh — Main Paladin test runner
# Executes all enabled tiers sequentially, stops on failure
#
# Usage: bash paladin-run.sh [project-root] [--strict] [--skip=4,5] [--tier=2]
#
# Options:
#   project-root    Path to the project (default: current directory)
#   --strict        Treat warnings as errors
#   --skip=N,N      Skip specific tiers (comma-separated)
#   --tier=N        Run only a specific tier
#   --init          Generate paladin.config.json and exit
#   --report        Generate full report to paladin-reports/

set -euo pipefail

# ─── Configuration ───────────────────────────────────────────────

PROJECT_ROOT="${1:-.}"
STRICT_MODE=false
SKIP_TIERS=()
SINGLE_TIER=""
INIT_MODE=false
REPORT_MODE=false
VERDICT="PASS"
ISSUES_CRITICAL=0
ISSUES_HIGH=0
ISSUES_MEDIUM=0
ISSUES_LOW=0
START_TIME=$(date +%s)

# Parse arguments
for arg in "$@"; do
  case $arg in
    --strict) STRICT_MODE=true ;;
    --skip=*) IFS=',' read -ra SKIP_TIERS <<< "${arg#*=}" ;;
    --tier=*) SINGLE_TIER="${arg#*=}" ;;
    --init) INIT_MODE=true ;;
    --report) REPORT_MODE=true ;;
  esac
done

cd "$PROJECT_ROOT"

# ─── Project Detection ───────────────────────────────────────────

detect_project_type() {
  local types=()

  [ -f "package.json" ] && {
    if grep -q "vite" package.json 2>/dev/null; then
      types+=("react-vite")
    elif grep -q "next" package.json 2>/dev/null; then
      types+=("nextjs")
    else
      types+=("node")
    fi
  }

  [ -f "Cargo.toml" ] && types+=("rust")
  [ -f "pyproject.toml" ] || [ -f "requirements.txt" ] && types+=("python")
  [ -d "supabase" ] && types+=("supabase")

  # Static site: HTML files but no package.json
  if [ ${#types[@]} -eq 0 ] && ls *.html >/dev/null 2>&1; then
    types+=("static-site")
  fi

  if [ ${#types[@]} -eq 0 ]; then
    echo "unknown"
  else
    echo "${types[*]}"
  fi
}

PROJECT_TYPE=$(detect_project_type)
PROJECT_NAME=$(basename "$(pwd)")

echo "═══════════════════════════════════════════════"
echo "  PALADIN TESTING WALL"
echo "  Project: $PROJECT_NAME"
echo "  Stack:   $PROJECT_TYPE"
echo "  Strict:  $STRICT_MODE"
echo "  Date:    $(date -Iseconds)"
echo "═══════════════════════════════════════════════"
echo ""

# ─── Init Mode ───────────────────────────────────────────────────

if $INIT_MODE; then
  if [ -f "paladin.config.json" ]; then
    echo "paladin.config.json already exists. Overwrite? (y/N)"
    read -r answer
    [ "$answer" != "y" ] && exit 0
  fi

  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  SKILL_ROOT="$(dirname "$SCRIPT_DIR")"

  if [ -f "$SKILL_ROOT/templates/paladin-config-default.json" ]; then
    cp "$SKILL_ROOT/templates/paladin-config-default.json" paladin.config.json
    # Patch in project name and type
    sed -i "s/\"name\": \"\"/\"name\": \"$PROJECT_NAME\"/" paladin.config.json
    sed -i "s/\"type\": \"auto\"/\"type\": \"$PROJECT_TYPE\"/" paladin.config.json
    echo "Created paladin.config.json for $PROJECT_NAME ($PROJECT_TYPE)"
  else
    echo "ERROR: Default config template not found at $SKILL_ROOT/templates/"
    exit 1
  fi
  exit 0
fi

# ─── Auto-Bootstrap ─────────────────────────────────────────
# Run bootstrap to install any missing test infrastructure.
# This is what makes Paladin vibe-coder friendly — they don't
# need to know what vitest or eslint are.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ -f "$SCRIPT_DIR/paladin-bootstrap.sh" ]; then
  echo "Running bootstrap check..."
  bash "$SCRIPT_DIR/paladin-bootstrap.sh" "$(pwd)" --yes 2>&1
  echo ""
fi

# ─── Tier Execution ──────────────────────────────────────────────

should_skip() {
  local tier=$1
  for skip in "${SKIP_TIERS[@]}"; do
    [ "$skip" = "$tier" ] && return 0
  done
  return 1
}

run_tier() {
  local tier_num=$1
  local tier_name=$2
  local tier_start=$(date +%s)

  if should_skip "$tier_num"; then
    echo "  Tier $tier_num — $tier_name: SKIP (user requested)"
    return 0
  fi

  if [ -n "$SINGLE_TIER" ] && [ "$SINGLE_TIER" != "$tier_num" ]; then
    return 0
  fi

  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "  TIER $tier_num: $tier_name"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

  # The actual tier commands are run by the Claude skill reading
  # the reference files. This script provides the framework.
  # In automated mode, each tier's commands are piped through here.

  local tier_end=$(date +%s)
  local tier_duration=$((tier_end - tier_start))
  echo "  Duration: ${tier_duration}s"
  echo ""
}

# ─── Execute All Tiers ───────────────────────────────────────────

run_tier 1 "THE OBVIOUS"
run_tier 2 "THE STRUCTURAL"
run_tier 3 "THE BEHAVIORAL"
run_tier 4 "THE VISIBLE"
run_tier 5 "THE INVISIBLE"

# ─── Verdict ─────────────────────────────────────────────────────

END_TIME=$(date +%s)
TOTAL_TIME=$((END_TIME - START_TIME))

if [ "$ISSUES_CRITICAL" -gt 0 ]; then
  VERDICT="FAIL"
elif $STRICT_MODE && [ "$ISSUES_HIGH" -gt 0 ]; then
  VERDICT="FAIL"
elif [ "$ISSUES_HIGH" -gt 0 ]; then
  VERDICT="WARN"
fi

TOTAL_ISSUES=$((ISSUES_CRITICAL + ISSUES_HIGH + ISSUES_MEDIUM + ISSUES_LOW))

echo ""
echo "═══════════════════════════════════════════════"
echo "  PALADIN VERDICT: $VERDICT"
echo "  Project: $PROJECT_NAME"
echo "  Stack:   $PROJECT_TYPE"
echo "═══════════════════════════════════════════════"
echo "  Issues: $TOTAL_ISSUES (Critical: $ISSUES_CRITICAL | High: $ISSUES_HIGH | Medium: $ISSUES_MEDIUM | Low: $ISSUES_LOW)"
echo "  Total Time: ${TOTAL_TIME}s"
echo "═══════════════════════════════════════════════"

if [ "$VERDICT" = "PASS" ] || [ "$VERDICT" = "WARN" ]; then
  echo ""
  echo "  Tier 6 — The Human Wall: READY"
  echo "  Generate the human QA checklist and walk through it."
else
  echo ""
  echo "  Tier 6 — The Human Wall: BLOCKED"
  echo "  Fix the above issues and re-run Paladin."
fi

echo ""

# Exit code: 0 for PASS/WARN, 1 for FAIL
[ "$VERDICT" = "FAIL" ] && exit 1 || exit 0
