# BrainStormer — Big Vision Roadmap
**Date:** 2026-03-23
**Vision:** The AI Development Operating System — the persistent knowledge layer that makes every AI tool smarter.

## The Arc

```
Phase 0 (DONE)     -> "It works"
Phase 1 (NEXT)     -> "It learns"
Phase 2            -> "It composes"
Phase 3            -> "It scales to teams"
Phase 4            -> "It's a platform"
Phase 5 (HORIZON)  -> "It's the universal AI brain"
```

---

## Phase 0: Foundation (DONE)
_"The OS boots"_

- [x] 4 sub-skills: Kernel, Comprehension, Ideation, Quality
- [x] 735 curated agents
- [x] 13 CLI commands
- [x] `brainstormer learn` command (auto-research write side)
- [x] License tiers, release channels, telemetry, landing page
- [x] Obsidian vault sync, GitHub CI/CD
- [x] rules.md seeded with 12 rules, pattern library with 30+ patterns

---

## Phase 1: The Self-Learning Loop (P2a — NEXT)
_"The OS gets smarter every session without you doing anything"_

**Theme:** Close every gap in the auto-learn cycle.

| # | Feature | Effort | Depends On | Status |
|---|---------|--------|-----------|--------|
| 2 | Global Rules + Project Overrides | 1-2 sessions | rules.md (done) | [ ] |
| 1 | Auto-Rule Proposals on Commit | 2-3 sessions | learn rule (done) | [ ] |
| 3 | Rule Confidence & Decay | 1-2 sessions | rules.md (done) | [ ] |
| 5 | Pattern Detector | 2-3 sessions | #3 | [ ] |
| 4 | Walkthrough Generator from Diff | 2-3 sessions | CodeGlass (done) | [ ] |
| 25 | Daily Summary Journal | 2-3 sessions | Obsidian sync (done) | [ ] |

**Build order:** #2 first -> #1 + #3 parallel -> #5 -> #4. #25 independent.

**Success:** Code for a week. `brainstormer learn status` shows 5+ auto-proposed rules with confidence scores, 3+ auto-walkthroughs. Obsidian vault has daily journal with auto-linked keywords. Zero manual effort.

---

## Phase 2: The Agent Engine (P2b)
_"Agents stop being a list and start being a system"_

**Theme:** Composable, testable, user-extensible agents.

| # | Feature | Effort | Depends On | Status |
|---|---------|--------|-----------|--------|
| 7 | Agent Builder SDK | 2-3 sessions | registry (done) | [ ] |
| 6 | Agent Pipelines (Composition) | 3-4 sessions | #7 | [ ] |
| 9 | PALADIN GitHub Action | 2-3 sessions | PALADIN scripts (done) | [ ] |

**Success:** `brainstormer agent create` -> write agent -> test locally -> chain in pipeline YAML -> run with one command.

---

## Phase 3: The Team Layer (P3a)
_"One developer's knowledge becomes the whole team's"_

| # | Feature | Priority | Effort |
|---|---------|----------|--------|
| 8 | Team Rulesets | Must have | 2-3 sessions |
| 18 | Rule Templates per Stack | Must have | 1-2 sessions |
| 10 | Learn-by-Example Engine | Should have | 2-3 sessions |
| 12 | Smart Agent Recommendations | Should have | 1-2 sessions |
| 11 | Project Health Dashboard | Should have | 2-3 sessions |
| 15 | Interactive Init Wizard | Nice to have | 1-2 sessions |

**Success:** New team member runs `brainstormer init`, gets team rulesets + recommended agents + stack-specific rules. First AI session already knows "how we build here."

---

## Phase 4: The Ecosystem (P3b)
_"BrainStormer becomes a platform, not just a tool"_

| # | Feature | Priority | Effort |
|---|---------|----------|--------|
| 14 | Agent Marketplace / Registry | Must have | 3-4 sessions |
| 13 | Obsidian Bi-Directional Sync | Should have | 2-3 sessions |
| 17 | PALADIN Pre-Commit Hook | Should have | 1-2 sessions |
| 16 | Telemetry-Driven Insights | Nice to have | 2-3 sessions |
| 19 | Diff-Aware Context Injection | Nice to have | 2-3 sessions |

**Success:** Community agents published and discoverable. Knowledge grows from contributions, not just personal sessions.

---

## Phase 5: The Universal Second Brain (Horizon)
_"Every AI tool you use gets smarter because they all share the same brain"_

| # | Feature | Priority | Effort |
|---|---------|----------|--------|
| 20 | Universal Config Sync | Must have | 2-3 sessions |
| 23 | Knowledge Graph API (MCP Server) | Must have | 3-4 sessions |
| 21 | Tool-Agnostic Session Memory | Should have | 3-4 sessions |
| 22 | Cross-Tool Agent Protocol | Should have | 3-4 sessions |
| 24 | AI Routing Layer | Nice to have | 4-5 sessions |

**Success:** Switch from Claude Code to Cursor mid-project. BrainStormer syncs everything automatically. The new tool starts with full knowledge. Routing layer sends simple tasks to cheap models, complex tasks to Opus.

---

## Strategic Position

**The moat deepens at every phase:**
- Phase 1: Personal knowledge accumulates (individual switching cost)
- Phase 3: Team knowledge accumulates (organizational switching cost)
- Phase 4: Community knowledge accumulates (ecosystem switching cost)
- Phase 5: Cross-tool knowledge accumulates (you can switch AI tools, but BrainStormer is the one thing that persists)

**The fast-moving AI market is the advantage:** Every time someone adopts a new AI tool, they need something to carry their knowledge forward. That's BrainStormer.
