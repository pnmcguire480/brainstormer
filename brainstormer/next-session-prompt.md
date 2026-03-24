# Next Session Kickoff — Paste this into a new Claude Code chat

---

## Context

Read `c:\Dev\SKILLS\BrainStormer\brainstormer\session-summary-2026-03-24.md` for full context. TL;DR: BrainStormer is an AI Development Operating System — a pip-installable CLI at `c:\Dev\SKILLS\BrainStormer`. We just built Phases 1-4 (18 features) in one session. The CLI now has 25+ commands including auto-learning from diffs, agent pipelines, team rulesets, a health dashboard, and a daily Obsidian journal.

Nothing has been committed yet. All changes are unstaged.

## Task 1: Test BrainStormer on itself

Run these commands from `c:\Dev\SKILLS\BrainStormer` and verify they all work:

```bash
# Core
brainstormer status
brainstormer doctor

# Phase 1: Self-Learning Loop
brainstormer learn status
brainstormer learn rule --from-diff HEAD~1
brainstormer learn walkthrough --from-diff HEAD~1
brainstormer learn scan --detect
brainstormer learn prune
brainstormer summary
brainstormer summary status

# Phase 2: Agent Engine
brainstormer agent list
brainstormer agent search python
brainstormer agent test python-pro
brainstormer agent info python-pro

# Phase 3: Team Layer
brainstormer team templates
brainstormer team status

# Phase 4: Ecosystem
brainstormer hooks status
brainstormer hooks context
brainstormer sync
```

Fix anything that breaks. Then commit the working state.

## Task 2: Update all projects in c:\Dev with BrainStormer

Scan `c:\Dev\` for projects that have been initialized with BrainStormer (look for `.brainstormer-version` or `CLAUDE.md` files). For each project found:

1. `cd` into the project
2. Run `brainstormer init --update` to re-sync templates
3. Run `brainstormer learn scan` to import any vault rules
4. Run `brainstormer team apply universal` to give every project the universal starter rules
5. Run `brainstormer status` to verify health
6. Run `brainstormer sync` to push updated state to Obsidian

Known projects to check:
- `c:\Dev\SKILLS\BrainStormer` (this project)
- `c:\Dev\Ground Zero\ground-zero`
- `c:\Dev\Cort4Congress`

Report back: which projects updated successfully, which had issues, and the health score for each.

## Task 3: Verify Obsidian vault

After all syncs, check `c:\Dev\Anthropicer\` (the Obsidian vault):
- Verify `projects/_index.md` lists all synced projects
- Verify `summaries/` has today's entries
- Spot-check one project dashboard for accuracy

## Important

- Read CLAUDE.md first: `c:\Dev\SKILLS\BrainStormer\CLAUDE.md`
- Read the session summary: `c:\Dev\SKILLS\BrainStormer\brainstormer\session-summary-2026-03-24.md`
- Don't modify agents at `~/.claude/agents/` without approval
- The CLI is pip-installed — run `brainstormer` directly, not `python -m cli.brainstormer`
- If `brainstormer` command isn't found, run from the repo: `cd c:\Dev\SKILLS\BrainStormer && python -m cli.brainstormer`
