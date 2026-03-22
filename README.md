# BrainStormer

**The AI Development Operating System**

Drop into any project. Run `init`. Ship.

---

## What Is This?

BrainStormer consolidates your entire AI-assisted development workflow into one system:

1. **Kernel** — 10 template files that give AI agents persistent context about your project
2. **Comprehension** — Every code output gets a WHAT/HOW/WHERE/WHEN/WHY walkthrough
3. **Ideation** — Turn one idea into 20+ ranked angles, platform hooks, calendars, and outlines
4. **Quality** — 6-tier testing wall that catches dumb problems before you debug subtle ones

Plus **780+ specialized agents** and an **Obsidian dashboard** that shows you everything happening across all your projects.

## Quick Start

```bash
# From any project root:
brainstormer init
```

That's it. BrainStormer detects your stack, scaffolds everything, and connects to your Obsidian vault.

```
🔍 Detecting project...          Next.js + TypeScript + Supabase
📁 Scaffolding project docs...   10 files created
🧠 Setting up comprehension...   CodeGlass ready
💡 Setting up ideation...        BrainStormer ready
🛡️ Setting up quality gates...   PALADIN ready
📔 Syncing to Obsidian...        → ~/Vault/projects/MyProject/
✅ Done! Open Obsidian to see your project dashboard.
```

## Commands

```bash
brainstormer init              # Set up project
brainstormer status            # What's configured, what's missing
brainstormer doctor            # Validate setup, diagnose issues
brainstormer sync              # Push project state to Obsidian vault
brainstormer update            # Update BrainStormer + re-sync templates
brainstormer quality run       # Run PALADIN quality tiers 1-5
brainstormer agent list        # Show agents for your stack
brainstormer help              # Full help
```

## The Four Skills

### Kernel (Priority 1)
Scaffolds 10 markdown files that give AI agents everything they need to understand your project:

| File | Purpose | Update Frequency |
|------|---------|-----------------|
| CLAUDE.md | Project state, rules, session handoffs | Every session |
| SPEC.md | Users, stories, features, acceptance criteria | Every feature |
| SCENARIOS.md | User flows with happy/sad paths | Major features |
| ARCHITECTURE.md | Tech stack, data model, APIs, deployment | Architecture changes |
| AGENTS.md | 5-tier LLM routing and escalation rules | When scope shifts |
| CODEGUIDE.md | Naming, style, git workflow, patterns | Set once |
| ART.md | Colors, typography, layout, components | Set once |
| CONTEXT.md | Domain background, stakeholders, constraints | As needed |
| SNIFFTEST.md | Human-only test prompts (never shown to AI) | Human only |
| README.md | Public project overview | At milestones |

### Comprehension (Priority 2)
Every code output gets a walkthrough answering five questions:
- **WHAT** — One sentence, no jargon
- **HOW** — Trace the data flow end-to-end
- **WHERE** — File map showing what lives where
- **WHEN** — What runs on load, click, data change, route change
- **WHY** — Design choices and alternatives

Rules compound over time — each session starts smarter than the last.

### Ideation (Priority 3)
6-step chain that turns one idea into dozens of directions:
1. **Audience Lock** — Profile your target
2. **Core Extraction** — 20+ ranked angles
3. **Hook + Format Match** — Platform-specific hooks
4. **Calendar Build** — 30-day publishing calendar
5. **Outline Expansion** — Full content outlines
6. **Skill Deposit** — Reusable rules that compound across runs

### Quality (Priority 4)
6-tier testing wall — catch the dumbest problems first:

| Tier | Name | What It Catches |
|------|------|----------------|
| 1 | The Obvious | Syntax errors, type mismatches, lint violations |
| 2 | The Structural | Logic errors, edge cases, coverage gaps |
| 3 | The Behavioral | Integration bugs, API contract violations |
| 4 | The Visible | Accessibility, responsive layout, visual regression |
| 5 | The Invisible | Bundle bloat, security holes, performance issues |
| 6 | The Human Wall | Happy path, destructive testing, first impressions |

## 780+ Agents

Specialized agents for every task — engineering, marketing, design, testing, sales, game dev, XR, and more. BrainStormer surfaces only the agents relevant to your project's stack.

Agents are sourced from:
- **Original** — Patrick McGuire's handcrafted 156
- **wshobson/agents** — Community collection
- **VoltAgent/awesome-claude-code-subagents** — Curated subagents
- **0xfurai/claude-code-subagents** — Production-ready agents

Every agent is tagged with its source to credit creators.

## Obsidian Integration

BrainStormer syncs your project state to an Obsidian vault:

```
YourVault/
├── Home.md                    # All-projects dashboard
├── projects/
│   └── YourProject/
│       ├── dashboard.md       # One-page overview
│       ├── spec.md            # ← from SPEC.md
│       ├── architecture.md    # ← from ARCHITECTURE.md
│       ├── ideation/          # ← angles, hooks, calendar
│       ├── comprehension/     # ← CodeGlass walkthroughs
│       └── quality/           # ← PALADIN verdicts
├── patterns/                  # Global pattern library
└── agents/                    # Agent catalog
```

Configure your vault: `brainstormer config set vault_path /path/to/vault`

## Installation

```bash
# Clone or download
git clone <repo-url> ~/.brainstormer

# Install CLI
cd ~/.brainstormer/cli
pip install -e .

# Verify
brainstormer help
```

## License

MIT — Patrick McGuire
