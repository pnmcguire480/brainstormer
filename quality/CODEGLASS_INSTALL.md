# Paladin → CodeGlass Installation Guide

Step-by-step instructions for wiring Paladin into CodeGlass as a testing phase.
This guide does NOT modify any CodeGlass files — it tells you exactly what to add
and where.

---

## Prerequisites

- CodeGlass skill is already installed and working
- Paladin skill directory is available at a known path
- Bash and Python 3.10+ available in your environment

---

## Step 1: Copy Paladin Into Your Skills Directory

Place the `paladin/` folder as a sibling to your CodeGlass skill:

```
your-skills/
├── codeglass/
│   ├── SKILL.md
│   └── ...
├── paladin/
│   ├── SKILL.md
│   ├── scripts/
│   │   └── paladin-run.sh
│   ├── references/
│   │   ├── universal.md
│   │   ├── react-vite.md
│   │   ├── python.md
│   │   ├── rust.md
│   │   ├── static-site.md
│   │   ├── supabase.md
│   │   ├── config-schema.md
│   │   └── codeglass-integration.md
│   ├── templates/
│   │   ├── paladin-config-default.json
│   │   ├── human-qa-checklist.md
│   │   └── test-report.md
│   └── evals/
│       └── evals.json
└── humanflow/
    └── ...
```

Make the gate script executable:

```bash
chmod +x paladin/scripts/paladin-run.sh
```

---

## Step 2: Add Paladin as a Phase Reference in CodeGlass

In your CodeGlass `SKILL.md`, add a reference to Paladin at the point where
CodeGlass finishes its code generation/analysis phase. The exact location depends
on your CodeGlass structure, but the pattern is:

**Find the section** in CodeGlass where it describes the workflow phases or pipeline
stages. Add a new phase entry:

```markdown
### Phase: Testing Wall (Paladin)

After code generation or modification is complete, invoke the Paladin testing skill.

1. Read the Paladin SKILL.md at `../paladin/SKILL.md`
2. Follow Paladin's Step 0 (detect project profile)
3. Follow Paladin's Step 2 (run automated Tiers 1–5)
4. If Paladin returns REJECT → stop, report failures, do not proceed
5. If Paladin returns HOLD → flag warnings for human review
6. If Paladin returns SHIP → proceed to deployment or delivery

Paladin handles its own profile detection, command selection, and reporting.
CodeGlass only needs to invoke it and respect the verdict.
```

---

## Step 3: Add Paladin Verdict Handling

Wherever CodeGlass makes its final "done" or "deliver" decision, add a gate check.
The concept:

```
IF paladin_verdict == "SHIP":
    proceed to delivery
ELIF paladin_verdict == "HOLD":
    present warnings to user
    ask: "Ship with warnings or fix first?"
ELIF paladin_verdict == "REJECT":
    present failures to user
    do NOT offer to ship
    say: "Fix these issues, then re-run Paladin"
```

If CodeGlass uses a structured pipeline config, add:

```yaml
phases:
  # ... existing phases ...
  - name: paladin-gate
    skill: paladin
    trigger: after-code-complete
    blocking: true
    on_fail: halt
    on_warn: prompt-user
```

---

## Step 4: Bootstrap Happens Automatically

You do NOT need to manually copy configs or install test dependencies.
When `paladin-run.sh` executes, it automatically runs `paladin-bootstrap.sh`
first, which:

- Detects what test infrastructure is missing
- Installs it (vitest, eslint, prettier, pytest, clippy, etc.)
- Scaffolds config files with sensible defaults
- Creates sample test files if none exist
- Adds npm scripts (test, lint, format, typecheck)
- Copies paladin.config.json into the project

This is designed for vibe coders who don't know what a test runner is.
They just run Paladin and it handles everything.

For manual bootstrapping (preview without changes):
```bash
bash /path/to/paladin/scripts/paladin-bootstrap.sh ./my-project --dry-run
```

---

## Step 5: Wire the Gate Script for CLI Usage

For projects where you want to run Paladin outside of Claude (CI/CD, local terminal):

```bash
# From your project root:
/path/to/paladin/scripts/paladin-run.sh --mode full

# Just run a single tier:
/path/to/paladin/scripts/paladin-run.sh --tier 1

# Hotfix mode (fast):
/path/to/paladin/scripts/paladin-run.sh --mode hotfix
```

Optional: add a convenience alias in each project's `package.json`:

```json
{
  "scripts": {
    "paladin": "/path/to/paladin/scripts/paladin-run.sh --mode full",
    "paladin:hotfix": "/path/to/paladin/scripts/paladin-run.sh --mode hotfix",
    "paladin:report": "python /path/to/paladin/scripts/report_generator.py"
  }
}
```

Or for Python projects, in `Makefile`:

```makefile
paladin:
	/path/to/paladin/scripts/paladin-run.sh --mode full

paladin-hotfix:
	/path/to/paladin/scripts/paladin-run.sh --mode hotfix
```

---

## Step 6: Update CodeGlass Description (Optional)

If CodeGlass has a description field that controls when it triggers, consider
adding awareness of Paladin so Claude knows they work together:

```
After completing code generation, CodeGlass invokes the Paladin testing skill
to run automated quality gates before delivering results. Paladin must pass
before any code is considered complete.
```

---

## How It Works at Runtime

```
User: "Build me a dashboard for [feature]"
         │
         ▼
   ┌─────────────┐
   │  CodeGlass   │  ← Analyzes request, generates code
   │  (phases     │
   │   1 through  │
   │   N)         │
   └──────┬──────┘
          │
          ▼
   ┌─────────────┐
   │  PALADIN     │  ← Reads project profile
   │  Tier 1      │  ← Build check
   │  Tier 2      │  ← Unit tests
   │  Tier 3      │  ← Integration
   │  Tier 4      │  ← Edge cases
   │  Tier 5      │  ← Perf & security
   └──────┬──────┘
          │
          ▼
     VERDICT?
    ╱    │    ╲
SHIP   HOLD   REJECT
  │      │       │
  ▼      ▼       ▼
Deliver  Ask     Stop.
to user  user    Fix.
         to      Re-run.
         decide
```

---

## Troubleshooting

**"Paladin skips most checks"**
→ Project profile detection probably failed. Set `profile` explicitly in
  `paladin.config.yaml` instead of using `"auto"`.

**"Gate script errors on npm ci"**
→ Make sure you're running from the project root, not the skill directory.
  `paladin-run.sh` expects to be invoked from where `package.json` lives.

**"Coverage check always skips"**
→ Coverage parsing is complex and profile-specific. The gate script marks it
  as SKIP by default. Run coverage manually and compare against thresholds
  in the config, or extend the script for your runner.

**"I want to add custom checks"**
→ Add them to `paladin-run.sh` in the appropriate tier section. Follow the
  `check_result` pattern: `check_result "X.X" "Name" "PASS|FAIL|WARN" "detail"`.

**"Can I run Paladin in CI/CD?"**
→ Yes. The gate script exits with code 1 on any FAIL. Use it as a GitHub
  Actions step or GitLab CI job. The JSON report can be parsed by CI tools.
