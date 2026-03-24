# BrainStormer: Implementation Briefs
**Date:** 2026-03-23

## Brief 1: Auto-Rule Proposals on Commit (#1)

**Pitch:** "Your AI remembers what it learned — automatically"
**Files:** `cli/commands/learn.py`, `cli/brainstormer.py`, `comprehension/templates/rules.md`

**Approach:**
1. `brainstormer learn rule --from-diff HEAD~1` reads diff, extracts patterns
2. Proposes rules with `[auto-proposed]` tag, `confidence: emerging`
3. Appends to rules.md "pending review" section
4. `brainstormer hooks install` adds git post-commit hook for full automation

**Done:** Commit -> seconds later -> "BrainStormer proposes 2 new rules"

---

## Brief 2: Global Rules + Project Overrides (#2)

**Pitch:** "Write a rule once, apply it everywhere"
**Files:** `cli/commands/learn.py`, `cli/core/scaffold.py`, `comprehension/templates/rules.md`

**Approach:**
1. `~/.brainstormer/rules.md` = global rules
2. Project rules.md gets `inherits: global` frontmatter (default on)
3. `--global` flag saves to global; default saves to project
4. Merge on read, project overrides global by rule ID

**Done:** Rule in one project auto-available in all projects

---

## Brief 3: Rule Confidence & Decay (#3)

**Pitch:** "Rules that prove themselves survive; the rest fade"
**Files:** `comprehension/templates/rules.md`, `cli/commands/learn.py`

**Approach:**
1. YAML metadata per rule: hits, misses, last_fired, confidence
2. `--from-diff` matching increments hits; user override increments misses
3. Confidence = hits / (hits + misses), floor of 5 events
4. `brainstormer learn prune` flags confidence < 0.3 or 90 days stale

**Done:** After 2 weeks, `learn status` shows rules ranked by confidence

---

## Brief 4: Agent Pipelines (#6)

**Pitch:** "Chain agents like Unix pipes"
**Files:** `cli/commands/agent.py`, `cli/core/pipeline.py` (new), agent frontmatter

**Approach:**
1. Pipeline YAML: steps with agent, input, output fields
2. `brainstormer agent run pipeline.yml` executes sequentially
3. Output captured and passed as context to next agent
4. Results aggregated into summary

**Done:** 3-agent pipeline in YAML, one command, unified output

---

## Brief 5: PALADIN GitHub Action (#9)

**Pitch:** "Quality gates that actually gate"
**Files:** `.github/workflows/paladin.yml`, `quality/scripts/paladin-run.sh`, `quality/templates/paladin-config.yml`

**Approach:**
1. GitHub Action installs BrainStormer, runs paladin-run.sh in CI mode
2. Configurable tier threshold (default: fail below tier 3)
3. PR annotations with findings
4. Ship as reusable action: `uses: pnmcguire480/brainstormer-paladin@v1`

**Done:** PR opened -> PALADIN runs -> check pass/fail based on quality tier

---

## Brief 6: Daily Summary Journal (#25)

**Pitch:** "Your Obsidian vault writes itself"
**Files:** `cli/commands/summary.py` (new), `cli/core/vault.py`, `cli/core/keywords.py` (new), `obsidian/vault-templates/summary.md` (new)

**Approach:**
1. Claude Code `stop` hook fires `brainstormer summary --auto`
2. Reads git diff + CLAUDE.md context, generates summary
3. Writes to `summaries/YYYY-MM-DD/NNN-project-topic.md` in vault
4. Auto-links keywords from 6-source taxonomy (projects, skills, commands, concepts, people, vault notes)
5. Retroactive linking: scans previous summaries for newly linkable keywords
6. Daily rollup aggregates all sessions

**Keyword registry:** `~/.brainstormer/keywords.yml` — auto-populated + user-extensible

**Done:** Code all day, never run summary. Vault has complete journal with wikilinked graph.
