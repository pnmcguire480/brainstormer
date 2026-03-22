---
name: paladin
description: >
  Lawful Good testing and evaluation gatekeeper. Enforces a six-tier testing wall
  that code must pass through before shipping — from the most obvious failures down
  to the faintest defects. Use this skill whenever the user mentions "test", "testing",
  "QA", "quality", "eval", "evaluation", "ship it", "deploy", "release", "launch",
  "is this ready", "check this", "review this code", "paladin", "testing wall",
  "run tests", "automated tests", "manual QA", or any variation of wanting to verify
  code quality before shipping. Also trigger when a project reaches a milestone and
  needs validation, when the user says "let's make sure this works", or when finishing
  any BabyTierOS chunk that produces working code. This skill applies to ALL project
  types — React apps, CLI tools, APIs, static sites, games, PWAs, scripts, libraries.
  If code exists and it might ship, Paladin guards the gate.
---

# Paladin — Lawful Good Testing Wall

## The Oath

Nothing ships unexamined. Every project passes through the wall — six tiers of
escalating scrutiny, from the obvious to the invisible. Automated gates run first.
Humans inspect only what the machines have already blessed. The wall does not bend.

## Philosophy

Testing follows **the funnel principle**: catch the dumbest problems first so you
never waste time debugging a subtle race condition when the real issue was a typo.
Each tier is a gate. If a gate fails, you stop, fix, and re-run from that gate.
You do NOT skip ahead.

---

## THE SIX TIERS

```
┌─────────────────────────────────────────────┐
│  TIER 1: THE OBVIOUS          [Automated]   │
│  Static analysis, linting, type checking    │
├─────────────────────────────────────────────┤
│  TIER 2: THE STRUCTURAL       [Automated]   │
│  Unit tests — function-level correctness    │
├─────────────────────────────────────────────┤
│  TIER 3: THE BEHAVIORAL       [Automated]   │
│  Integration tests — components together    │
├─────────────────────────────────────────────┤
│  TIER 4: THE VISIBLE          [Automated]   │
│  UI/UX, accessibility, visual regression    │
├─────────────────────────────────────────────┤
│  TIER 5: THE INVISIBLE        [Automated]   │
│  Performance, security, bundle analysis     │
├─────────────────────────────────────────────┤
│  TIER 6: THE HUMAN WALL       [Manual]      │
│  Walkthroughs, checklists, gut checks       │
└─────────────────────────────────────────────┘
```

**Rule: Tiers 1–5 are automated. Tier 6 is human. Never skip to Tier 6 until 1–5 pass.**

---

## HOW TO USE THIS SKILL

### Step 1: Detect the project type

Read the project root. Look for:
- `package.json` → Node/React/Vite project
- `Cargo.toml` → Rust project
- `pyproject.toml` / `requirements.txt` → Python project
- `index.html` (standalone) → Static site
- `supabase/` directory → Supabase backend
- Multiple indicators → composite project (test each layer)

Load the appropriate reference file from `references/` for stack-specific commands:
- `references/react-vite.md` — React + Vite + TypeScript + Tailwind
- `references/python.md` — Python projects
- `references/rust.md` — Rust projects
- `references/static-site.md` — HTML/CSS/JS static sites
- `references/supabase.md` — Supabase backend layer
- `references/universal.md` — Stack-agnostic checks (always load this too)

### Step 2: Run the Gauntlet

Execute tiers sequentially. Stop at first failure. Report results using the
verdict format (see below). For each tier, the reference files contain the
exact commands. The universal reference contains checks that apply regardless
of stack.

**Before running any tier, Paladin auto-bootstraps missing infrastructure.**
This is critical for vibe coders and newcomers. If the project has no test
runner, no linter, no config — Paladin installs everything automatically
via `scripts/paladin-bootstrap.sh`. The bootstrap:

- Detects what's missing (vitest, eslint, prettier, pytest, clippy, etc.)
- Installs it with sensible defaults
- Scaffolds config files (vitest.config.ts, .eslintrc, pytest.ini, etc.)
- Creates a sample test file if zero tests exist
- Adds npm scripts (test, lint, format, typecheck)
- Creates .env.example from env var usage in code
- Sets up .gitignore with proper exclusions
- Copies in paladin.config.json

This runs automatically inside `paladin-run.sh`. For manual use:

```bash
# See what would be installed (no changes):
bash paladin/scripts/paladin-bootstrap.sh /path/to/project --dry-run

# Install everything automatically:
bash paladin/scripts/paladin-bootstrap.sh /path/to/project --yes

# Minimal install (just build + lint + test runner):
bash paladin/scripts/paladin-bootstrap.sh /path/to/project --minimal --yes
```

The bootstrap is idempotent — running it twice does nothing new. It only
adds what's missing and never overwrites existing configuration.

### Step 3: Generate the Verdict

After all tiers pass (or one fails), output the Paladin Verdict:

```
═══════════════════════════════════════════════
  PALADIN VERDICT: [PASS | FAIL | WARN]
  Project: [name]
  Stack: [detected stack]
  Date: [timestamp]
═══════════════════════════════════════════════
  Tier 1 — The Obvious:      [PASS|FAIL|SKIP]
  Tier 2 — The Structural:   [PASS|FAIL|SKIP]
  Tier 3 — The Behavioral:   [PASS|FAIL|SKIP]
  Tier 4 — The Visible:      [PASS|FAIL|SKIP]
  Tier 5 — The Invisible:    [PASS|FAIL|SKIP]
  Tier 6 — The Human Wall:   [READY|BLOCKED]
═══════════════════════════════════════════════
  Issues Found: [count]
  Critical: [count]  |  Warning: [count]  |  Info: [count]

  [If FAIL: list every issue, grouped by tier, severity-sorted]
  [If PASS: list any warnings/info, then Tier 6 human checklist]
═══════════════════════════════════════════════
```

### Step 4: The Human Wall (Tier 6)

Only reached when Tiers 1–5 pass. Generate a project-specific human QA
checklist from `templates/human-qa-checklist.md`. This checklist is what
the developer physically walks through — device testing, user flow
walkthroughs, and the "does this feel right" gut check.

---

## TIER DETAILS

### Tier 1: The Obvious (Static Analysis)

The cheapest, fastest checks. If these fail, nothing else matters.

| Check | What it catches |
|-------|----------------|
| **Build** | Syntax errors, import failures, missing deps |
| **Type check** | Type mismatches, null safety violations |
| **Lint** | Style violations, dead code, suspicious patterns |
| **Format** | Inconsistent formatting |
| **Dependency audit** | Known vulnerabilities in deps |

**Gate rule:** Zero errors. Warnings logged but don't block unless strict mode.

### Tier 2: The Structural (Unit Tests)

Every exported function, every utility, every hook — tested in isolation.

| Check | What it catches |
|-------|----------------|
| **Unit test suite** | Logic errors, wrong return values |
| **Edge cases** | Boundary conditions, empty inputs, overflow |
| **Error paths** | Missing try/catch, unhandled rejections |
| **Coverage gate** | Untested code paths |

**Gate rule:** All tests pass. Coverage >= threshold (default 80%).

### Tier 3: The Behavioral (Integration Tests)

Components working together. API calls resolving. State flowing correctly.

| Check | What it catches |
|-------|----------------|
| **Component integration** | Props not flowing, context breaking |
| **API contract tests** | Response shape changes, status codes |
| **State management** | Race conditions, stale state |
| **Route testing** | Dead links, wrong redirects, 404s |
| **Database operations** | CRUD correctness, constraint violations |

**Gate rule:** All integration tests pass. Zero unhandled promise rejections.

### Tier 4: The Visible (UI/UX Verification)

What the user actually sees.

| Check | What it catches |
|-------|----------------|
| **Accessibility (a11y)** | Missing labels, bad contrast, no keyboard nav |
| **Responsive snapshots** | Layout breaks at breakpoints |
| **Visual regression** | Unintended visual changes |
| **Cross-browser compat** | Browser-specific rendering bugs |
| **Console cleanliness** | Leftover console.logs, React warnings |

**Gate rule:** Zero a11y violations at "serious" or above. No layout
breaks at standard breakpoints (320, 768, 1024, 1440).

### Tier 5: The Invisible (Performance & Security)

The stuff users feel but can't name.

| Check | What it catches |
|-------|----------------|
| **Bundle analysis** | Bloated bundles, tree-shaking failures |
| **Lighthouse audit** | Performance, SEO, best practices |
| **Security scan** | XSS vectors, injection points, exposed secrets |
| **Environment check** | Leaked env vars, hardcoded credentials |
| **Load testing** | Slowdowns under concurrent requests |

**Gate rule:** Lighthouse performance > 80. No critical/high security
findings. No secrets in codebase.

### Tier 6: The Human Wall (Manual QA)

The machine says it works. Now a human confirms it *feels* right.

| Check | What it catches |
|-------|----------------|
| **Happy path walkthrough** | "Does the main flow actually work?" |
| **Destructive testing** | "What breaks if I do something dumb?" |
| **Device testing** | "Does it work on my actual phone?" |
| **Copy/content review** | Typos, awkward phrasing, placeholder text |
| **First-impression test** | "Would I use this? Does it feel done?" |
| **Edge case exploration** | "What happens with weird data?" |

**Gate rule:** All checklist items signed off. Any "feels wrong" goes back.

---

## CONFIGURATION

Paladin looks for `paladin.config.json` in the project root. If absent,
defaults are used. Run `scripts/paladin-init.sh` to generate one.

See `references/config-schema.md` for full schema. Key settings:
- `strictMode`: Treat warnings as errors (default: false)
- `coverageThreshold`: Minimum code coverage % (default: 80)
- `lighthouseMinScore`: Minimum Lighthouse perf score (default: 80)
- `skipTiers`: Array of tier numbers to skip (default: [])
- `projectType`: Override auto-detection
- `humanTesters`: Array of names for Tier 6 sign-off

---

## CODEGLASS INTEGRATION

Paladin plugs into CodeGlass as a post-analysis module. See
`references/codeglass-integration.md` for full wiring instructions.

Integration points:
1. **CodeGlass triggers Paladin** after code review completes
2. **Paladin reports back** with the verdict
3. **CodeGlass displays** combined review + test results
4. **Tier 6 checklist** appended to CodeGlass output

Paladin does NOT replace CodeGlass. CodeGlass reads and understands code.
Paladin verifies it actually works.

---

## REFERENCE FILES

- `references/universal.md` — Stack-agnostic checks (always loaded)
- `references/react-vite.md` — React + Vite + TypeScript + Tailwind
- `references/python.md` — Python project testing
- `references/rust.md` — Rust project testing
- `references/static-site.md` — Static HTML/CSS/JS testing
- `references/supabase.md` — Supabase backend testing
- `references/config-schema.md` — paladin.config.json schema
- `references/codeglass-integration.md` — CodeGlass wiring guide

## TEMPLATES

- `templates/human-qa-checklist.md` — Tier 6 checklist generator
- `templates/paladin-config-default.json` — Default config
- `templates/test-report.md` — Full report template

## SCRIPTS

- `scripts/paladin-run.sh` — Main runner, all tiers sequential
- `scripts/paladin-init.sh` — Config generator
