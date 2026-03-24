# BrainStormer

[![PyPI](https://img.shields.io/pypi/v/brainstormer)](https://pypi.org/project/brainstormer/)
[![Python](https://img.shields.io/pypi/pyversions/brainstormer)](https://pypi.org/project/brainstormer/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**The AI Development Operating System**

Drop into any project. Run `init`. Ship.

Your AI assistant forgets everything between sessions. BrainStormer remembers. Rules compound. Patterns accumulate. Your 100th session is 10x faster than your first.

---

## Quick Start

```bash
pip install brainstormer
cd your-project
brainstormer init
```

That's it. BrainStormer detects your stack, scaffolds 10 project docs, wires up all 4 skills, and starts learning from your code.

```
Detecting project...          Next.js + TypeScript + Supabase
Scaffolding project docs...   10 created, 0 existing
Setting up comprehension...   CodeGlass ready
Setting up ideation...        BrainStormer ready
Setting up quality gates...   PALADIN ready
Syncing to Obsidian...        Done

Done! Project 'my-app' is ready.
```

## For Developers AND Vibe Coders

Never coded before? BrainStormer helps you understand what AI builds for you. Every code output gets a plain-English walkthrough. Rules accumulate so the AI stops making the same mistakes. You don't need to be a developer to use this.

## What It Does

BrainStormer consolidates 4 AI-assisted development skills into one system:

1. **Kernel** &mdash; 10 template files that give AI agents persistent context about your project
2. **Comprehension** &mdash; Every code output gets a WHAT/HOW/WHERE/WHEN/WHY walkthrough
3. **Ideation** &mdash; Turn one idea into 20+ ranked angles, hooks, calendars, and outlines
4. **Quality** &mdash; 6-tier testing wall that catches dumb problems before you debug subtle ones

Plus **374 curated agents**, **self-learning rules**, **team rulesets**, **git hooks**, and an **Obsidian dashboard** that shows everything across all your projects.

## Commands

### Core
```bash
brainstormer init              # Set up project (detects stack, scaffolds docs)
brainstormer status            # Health score, knowledge stats, recommendations
brainstormer doctor            # Validate setup, diagnose issues
brainstormer sync              # Sync project state to/from Obsidian vault
brainstormer help              # Full help
```

### Self-Learning (auto-compounds knowledge)
```bash
brainstormer learn status      # Show rules, confidence, hit/miss stats
brainstormer learn rule --from-diff HEAD~1   # Auto-propose rules from git diff
brainstormer learn walkthrough --from-diff   # Generate walkthrough from commits
brainstormer learn scan --detect             # Detect recurring patterns
brainstormer learn prune                     # Flag stale or low-confidence rules
brainstormer summary                         # Auto-generate daily Obsidian journal
```

### Agents
```bash
brainstormer agent list        # Show agents for your stack (374 total)
brainstormer agent search      # Search agents by keyword
brainstormer agent info        # Show agent details
brainstormer agent create      # Scaffold a custom agent (Pro)
brainstormer agent run         # Run a multi-agent pipeline (Pro)
```

### Team
```bash
brainstormer team templates    # List 6 starter rule templates
brainstormer team status       # Show team ruleset info
brainstormer team apply        # Apply a stack-specific template (Pro)
brainstormer team init         # Create shared team ruleset (Pro)
```

### Automation
```bash
brainstormer hooks install     # PALADIN pre-commit + auto-learn post-commit
brainstormer hooks context     # Show rules relevant to current changes
brainstormer hooks status      # Show hook installation status
```

### System
```bash
brainstormer update            # Check for updates + re-sync templates
brainstormer update channel    # View/set release channel (stable/preview)
brainstormer update rollback   # Revert to previous version
brainstormer migrate           # Import .cursorrules, .windsurfrules, etc.
brainstormer license           # Show/activate/deactivate license
brainstormer license buy       # Open Pro checkout page
brainstormer telemetry         # Toggle anonymous usage telemetry
```

## The Four Skills

### Kernel (Priority 1)
Scaffolds 10 markdown files that give AI agents persistent project context:

| File | Purpose |
|------|---------|
| CLAUDE.md | Project state, rules, session handoffs |
| SPEC.md | Users, stories, features, acceptance criteria |
| SCENARIOS.md | User flows with happy/sad paths |
| ARCHITECTURE.md | Tech stack, data model, APIs, deployment |
| AGENTS.md | 5-tier LLM routing and escalation rules |
| CODEGUIDE.md | Naming, style, git workflow, patterns |
| ART.md | Colors, typography, layout, components |
| CONTEXT.md | Domain background, stakeholders, constraints |
| SNIFFTEST.md | Human-only test prompts (never shown to AI) |
| README.md | Public project overview |

### Comprehension (Priority 2)
Every code output gets a walkthrough: **WHAT** (one sentence) &rarr; **HOW** (data flow) &rarr; **WHERE** (file map) &rarr; **WHEN** (triggers) &rarr; **WHY** (design choices)

### Ideation (Priority 3)
6-step chain: Audience Lock &rarr; Core Extraction &rarr; Hook + Format Match &rarr; Calendar Build &rarr; Outline Expansion &rarr; Skill Deposit

### Quality (Priority 4)
6-tier testing wall &mdash; catch the dumbest problems first:

| Tier | Name | What It Catches |
|------|------|----------------|
| 1 | The Obvious | Syntax errors, type mismatches, lint violations |
| 2 | The Structural | Logic errors, edge cases, coverage gaps |
| 3 | The Behavioral | Integration bugs, API contract violations |
| 4 | The Visible | Accessibility, responsive layout, visual regression |
| 5 | The Invisible | Bundle bloat, security holes, performance issues |
| 6 | The Human Wall | Happy path, destructive testing, first impressions |

## 374 Agents

Curated from 4 community sources. Smart surfacing shows relevant agents for your detected stack.

- **community** &mdash; Community-sourced collection
- **wshobson/agents** &mdash; Community collection
- **VoltAgent/awesome-claude-code-subagents** &mdash; Curated subagents
- **0xfurai/claude-code-subagents** &mdash; Production-ready agents

## Obsidian Integration

```
YourVault/
├── Home.md                    # All-projects dashboard
├── projects/
│   └── YourProject/
│       ├── dashboard.md       # One-page overview
│       ├── spec.md
│       ├── architecture.md
│       ├── ideation/
│       ├── comprehension/
│       └── quality/
├── journal/                   # Daily summaries with keyword linking
├── rules/                     # Cross-project rules
└── agents/                    # Agent catalog
```

Configure: `brainstormer config set vault_path /path/to/vault`

## Pricing

| | Community (Free) | Pro ($12/mo founding, $19/mo standard) |
|---|---|---|
| Projects | 3 | Unlimited |
| Agents | All 374 | All + custom creation + pipelines |
| Skills | All 4 | All 4 |
| Learning | Full | Full |
| Vault sync | One-way (push) | Bi-directional |
| Team features | View only | Full (init, sync, apply) |
| Updates | Stable channel | Stable + Preview |

**First 100 members get $12/mo locked forever.** [Get Pro](https://brainstormer.lemonsqueezy.com)

## Support

- [Discord](https://discord.gg/vrFcju9rBA) &mdash; questions, bugs, feature requests
- [GitHub Issues](https://github.com/pnmcguire480/brainstormer/issues) &mdash; bug reports

## License

MIT &mdash; Patrick McGuire
