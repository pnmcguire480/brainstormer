# BrainStormer: Core Extraction — Product Improvements
**Idea:** Make BrainStormer's 4 skills excellent, then expand to universal AI knowledge layer
**Audience:** Solo devs and small teams using Claude Code, frustrated by context loss
**Date:** 2026-03-23

## Tier 1: Core Loop (9-10/10) — SELECTED

1. **Auto-Rule Proposals on Commit** [automation] — 10/10
   Git hook analyzes diffs, proposes rules automatically. Zero-effort knowledge capture.
   _Pairs with: #3, #5_

2. **Global Rules + Project Overrides** [framework] — 10/10
   `~/.brainstormer/rules.md` universal rules, per-project inherit/override.
   _Pairs with: #1, #8_

3. **Rule Confidence & Decay** [data-driven] — 9/10
   Hit/miss counters, confidence scoring, stale rule detection, auto-archive.
   _Pairs with: #1, #2_

4. **Walkthrough Generator from Git Diff** [automation] — 9/10
   `brainstormer learn walkthrough --from-diff` auto-generates CodeGlass walkthroughs.
   _Pairs with: #10_

5. **Pattern Detector** [automation] — 9/10
   `brainstormer learn scan --detect` surfaces recurring patterns from recent commits.
   _Pairs with: #1, #3_

## Tier 2: New Capabilities (7-8/10) — SELECTED

6. **Agent Pipelines** [framework] — 8/10
   Chain agents in YAML workflows. Sequential + parallel execution.
   _Pairs with: #7_

7. **Agent Builder SDK** [framework] — 8/10
   `brainstormer agent create` scaffolds, tests, publishes agents.
   _Pairs with: #6, #14_

9. **PALADIN GitHub Action** [ci-cd] — 8/10
   Quality gates on every PR. Configurable tier thresholds.
   _Pairs with: #17_

## Tier 2: New Capabilities — Future Build (Must Have)

8. **Team Rulesets** [team] — 8/10
10. **Learn-by-Example Engine** [educational] — 8/10
11. **Project Health Dashboard** [data-driven] — 7/10
12. **Smart Agent Recommendations** [educational] — 7/10
13. **Obsidian Bi-Directional Sync** [automation] — 7/10

## Tier 3: System Expansion — Future Build (Should Have)

14. **Agent Marketplace / Registry** [community] — 7/10
15. **Interactive Init Wizard** [beginner] — 7/10
16. **Telemetry-Driven Insights** [data-driven] — 6/10
17. **PALADIN Pre-Commit Hook** [ci-cd] — 6/10
18. **Rule Templates per Stack** [educational] — 6/10
19. **Diff-Aware Context Injection** [advanced] — 6/10

## Tier 4: Multi-AI Vision — Horizon (Nice to Have)

20. **Universal Config Sync** [multi-ai] — 6/10
21. **Tool-Agnostic Session Memory** [multi-ai] — 5/10
22. **Cross-Tool Agent Protocol** [multi-ai] — 5/10
23. **Knowledge Graph API (MCP)** [multi-ai] — 5/10
24. **AI Routing Layer** [multi-ai] — 5/10

## Added During Session

25. **Daily Summary Journal** [automation] — 9/10
    Auto-generated Obsidian journal with keyword taxonomy and retroactive wikilinks.
    Zero effort via Claude Code stop hook.

## Natural Series

- **Auto-Learn Loop:** #1 -> #3 -> #5
- **Knowledge Architecture:** #2 -> #8 -> #18
- **Agent Ecosystem:** #6 -> #7 -> #14
- **Quality Pipeline:** #9 -> #17 -> #11
- **Multi-AI Bridge:** #20 -> #21 -> #23 -> #24
