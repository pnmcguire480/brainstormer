---
project: "BrainStormer"
task: "Add Discord invite link to landing page, README, and CLI error output"
date: 2026-03-24
ref: "HEAD~1"
patterns: []
level: standard
status: auto-generated
---

## WHAT

Add Discord invite link to landing page, README, and CLI error output

Files changed:
- `.github/workflows/release.yml`
- `cli/brainstormer.py`
- `cli/commands/status.py`
- `cli/commands/sync.py`
- `cli/core/telemetry.py`
- `cli/core/vault.py`
- `comprehension/references/pattern-library.md`
- `comprehension/templates/rules.md`
- `ruleset.md`

## HOW

New functions/classes:
- `def _cmd_telemetry_insights`
- `def main`
- `def get_insights`
- `def format_telemetry_status`
- `def sync_vault_to_project`
- `def _strip_user_notes`
- `def _update_project_index`

Key changes (from diff):
- 9 files modified
- Review `git diff HEAD~1` for full details

## WHERE

- `.github/workflows/release.yml`
- `cli/brainstormer.py`
- `cli/commands/status.py`
- `cli/commands/sync.py`
- `cli/core/telemetry.py`
- `cli/core/vault.py`
- `comprehension/references/pattern-library.md`
- `comprehension/templates/rules.md`
- `ruleset.md`

## WHEN

Generated from git ref: `HEAD~1`
Commit context: Add Discord invite link to landing page, README, and CLI error output

## WHY

<!-- Why these decisions? What alternatives were considered? -->
<!-- Fill in the reasoning — the diff shows WHAT, this section captures WHY -->
