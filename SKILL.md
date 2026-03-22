---
name: BrainStormer
description: >
  The AI Development Operating System. Drop into any project, run init, and get the full
  pipeline wired — scaffolding, comprehension, ideation, quality gates, and a live Obsidian
  dashboard. Routes to four sub-skills based on context:

  1. KERNEL (Priority 1) — Project scaffolding with 10 template files + 5-tier LLM routing.
     Trigger on: "init", "scaffold", "new project", "set up project", "brainstormer init".

  2. COMPREHENSION (Priority 2) — Every code output gets a WHAT/HOW/WHERE/WHEN/WHY walkthrough.
     Auto-generates new rules as patterns emerge. NON-OPTIONAL for all coding tasks.
     Trigger on: "explain this", "walk me through", "how does this work", "codeglass", "glass this".

  3. IDEATION (Priority 3) — Idea multiplier chain. Takes one concept and grinds it into dozens
     of ranked angles, platform hooks, content calendars, outlines, and a compounding ruleset.
     Trigger on: "brainstorm this", "grind this idea", "expand this", "give me angles",
     "content calendar", "multiply this".

  4. QUALITY (Priority 4) — 6-tier testing wall before shipping. Catches dumb problems first
     so you never debug subtle issues when the real problem was a typo.
     Trigger on: "test", "QA", "ship it", "deploy", "is this ready", "paladin", "quality check".
---

# BrainStormer — The AI Development Operating System

## Overview

BrainStormer is a unified system that manages the full development lifecycle: idea to
polished deployable. It consolidates four sub-skills and routes tasks automatically.

## Sub-Skill Routing

When a task comes in, route to the appropriate sub-skill:

### Kernel (kernel/SKILL.md) — Priority 1
**When:** Project setup, scaffolding, new features requiring doc updates, scope changes.
**What:** Scaffolds 10 template files (CLAUDE.md, SPEC.md, SCENARIOS.md, ARCHITECTURE.md,
AGENTS.md, CODEGUIDE.md, ART.md, CONTEXT.md, SNIFFTEST.md, README.md) and configures
the 5-tier LLM routing system.
**Read:** `kernel/SKILL.md` for full instructions, `kernel/references/five-tier-system.md`
for tier definitions.

### Comprehension (comprehension/SKILL.md) — Priority 2
**When:** Every code generation, code review, or code explanation task. NON-OPTIONAL.
**What:** Produces WHAT/HOW/WHERE/WHEN/WHY walkthroughs at 3 depth levels (Quick Glass,
Standard Glass, Deep Glass). Auto-proposes new rules when patterns are detected.
**Read:** `comprehension/SKILL.md` for full instructions,
`comprehension/references/walkthrough-format.md` for the walkthrough structure,
`comprehension/references/pattern-library.md` for named patterns.

### Ideation (ideation/SKILL.md) — Priority 3
**When:** User wants to brainstorm, expand, or multiply an idea for content, launches,
campaigns, pitches, or any scenario where one concept needs many directions.
**What:** 6-step chain: Audience Lock → Core Extraction → Hook + Format Match →
Calendar Build → Outline Expansion → Skill Deposit.
**Read:** `ideation/SKILL.md` for overview, `ideation/chain-steps.md` for detailed
step-by-step instructions.

### Quality (quality/SKILL.md) — Priority 4
**When:** Before deploy, before merge, on-demand testing, or when code reaches a milestone.
**What:** 6-tier testing wall (Obvious → Structural → Behavioral → Visible → Invisible →
Human Wall). Auto-bootstraps missing test infrastructure.
**Read:** `quality/SKILL.md` for full instructions, `quality/references/` for stack-specific
test configurations.

## Shared Data Flow (Through-Points)

```
CLAUDE.md ──→ Read by ALL skills every session (project identity + rules)
SPEC.md  ──→ Feeds Ideation audience lock + Quality test generation
rules.md ──→ Comprehension accumulates patterns, fed back each session
Obsidian ──→ ALL skills sync outputs here for human visibility
```

### Learning Loop
```
Code output → Comprehension walkthrough → Pattern detected?
  YES → Propose new rule → User approves → Append to rules.md
       → Sync to Obsidian patterns/ library
       → Future sessions start smarter
  NO  → Walkthrough stored in docs/codeglass/ → Synced to vault
```

## Co-activation Rules

Skills can run simultaneously when triggers overlap:
- **Comprehension + Quality:** After code generation, Comprehension explains while
  Quality tests. Both outputs appear together.
- **Kernel + Ideation:** When starting a new product, SPEC.md drives Ideation's
  audience lock (Step 0 reads from SPEC.md user definitions).

## Init Command

Run `brainstormer init` from any project root to set up the full system:
1. Detects project type (Next.js, Python, Rust, etc.)
2. Scaffolds all template files (skips existing)
3. Configures comprehension, ideation, and quality layers
4. Syncs to Obsidian vault

## Agent Routing

156+ specialized agents are available at `~/.claude/agents/`. The registry
(`agents/registry.md`) maps each to a tier, category, and stack tags. During
init, only stack-relevant agents are surfaced. Progressive disclosure — new
users see 5-10 recommended agents, power users browse the full catalog.

The 5-tier system determines which agent handles a task:
- **Tier 1 (Autocomplete):** IDE completions — no agent needed
- **Tier 2 (Local Assist):** Ollama/local LLM — simple renames, formatting
- **Tier 3 (Specialist):** Single-file focused tasks
- **Tier 4 (Builder):** Multi-file features, agentic workflows
- **Tier 5 (Strategist):** Planning, architecture, code review
