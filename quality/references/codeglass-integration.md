# CodeGlass Integration Guide

How to wire Paladin into CodeGlass as a post-analysis testing module.

---

## Architecture

```
┌──────────────────────────────────────────────┐
│                  CodeGlass                    │
│                                              │
│  1. Code Review (existing)                   │
│  2. Understanding Report (existing)          │
│     │                                        │
│     ▼                                        │
│  3. ── PALADIN GATE ──────────────────────   │
│     │  Triggers after code review completes  │
│     │  Runs Tiers 1-5 automatically          │
│     │  Blocks if any tier fails              │
│     │                                        │
│     ▼                                        │
│  4. Combined Verdict                         │
│     │  CodeGlass review + Paladin results    │
│     │                                        │
│     ▼                                        │
│  5. Tier 6 Human Checklist (if Tiers 1-5    │
│     pass)                                    │
│                                              │
└──────────────────────────────────────────────┘
```

---

## Integration Steps (Manual Wiring)

### Step 1: Copy Paladin into your skills directory

```bash
# From your skills root (wherever CodeGlass lives)
cp -r /path/to/paladin /mnt/skills/user/paladin
```

Your skills directory should look like:
```
/mnt/skills/user/
├── codeglass/
│   └── SKILL.md          ← existing CodeGlass skill
├── paladin/
│   ├── SKILL.md          ← Paladin skill (new)
│   ├── references/       ← stack-specific test references
│   ├── scripts/          ← automation scripts
│   └── templates/        ← report and checklist templates
└── humanflow/
    └── SKILL.md          ← existing HumanFlow skill
```

### Step 2: Add Paladin trigger to CodeGlass SKILL.md

Find the section in CodeGlass where it generates its final output/report.
Add the following block AFTER the code review section but BEFORE the
final summary:

```markdown
## Post-Review: Paladin Testing Gate

After completing the code review, trigger the Paladin testing skill:

1. Read `/mnt/skills/user/paladin/SKILL.md`
2. Detect the project type from the codebase being reviewed
3. Load the appropriate reference file(s) from `paladin/references/`
4. Execute Tiers 1–5 sequentially (automated checks)
5. Append the Paladin Verdict to the CodeGlass report
6. If all tiers pass, generate and append the Tier 6 Human Checklist

The Paladin verdict determines the final CodeGlass recommendation:
- Paladin PASS → CodeGlass can recommend shipping
- Paladin WARN → CodeGlass recommends shipping with noted warnings
- Paladin FAIL → CodeGlass recommends fixing before shipping

CodeGlass should NEVER recommend shipping code that fails Paladin.
```

### Step 3: Add the cross-reference in CodeGlass description

In the CodeGlass SKILL.md YAML frontmatter `description` field, append:

```
Integrates with Paladin testing skill for automated quality verification.
When Paladin is available, always run the testing wall after code review.
```

### Step 4: Wire the verdict format

Add this to CodeGlass's output template section so the two reports merge
into a single document:

```markdown
## CodeGlass + Paladin Combined Report

### Code Review Summary
[existing CodeGlass output]

### Testing Verdict
[Paladin verdict block — see SKILL.md for format]

### Human QA Checklist
[Paladin Tier 6 checklist — only if Tiers 1-5 passed]

### Final Recommendation
- Code Quality: [CodeGlass grade]
- Test Status: [Paladin verdict]
- Ship Ready: [YES / NO / WITH WARNINGS]
```

---

## Trigger Conditions

Paladin should activate in CodeGlass when ANY of these are true:
- User says "review and test" or "is this ready to ship"
- CodeGlass finishes a code review and Paladin skill is available
- User explicitly says "run paladin" or "testing wall"
- A BabyTierOS chunk is marked as complete

Paladin should NOT activate when:
- User says "just review, don't test" or "skip tests"
- The project has no testable code (pure documentation, design files)
- User is in planning/architecture phase (no code to test yet)

---

## Data Flow Between Skills

CodeGlass passes to Paladin:
- Project root path
- Detected stack/framework
- List of files changed (if reviewing a diff)
- Any existing test configuration found

Paladin returns to CodeGlass:
- Verdict (PASS / FAIL / WARN)
- Issue list with severity classifications
- Tier-by-tier pass/fail status
- Tier 6 human checklist (if applicable)
- Timing data (how long each tier took)

---

## Fallback Behavior

If Paladin encounters a tier it can't run (missing tools, no test framework
installed, etc.), it:

1. Marks that tier as `SKIP` with reason
2. Logs a WARNING: "Tier X skipped: [reason]"
3. Continues to the next tier
4. In the verdict, notes skipped tiers and recommends installing missing deps

A fully skipped run (all tiers skipped) results in:
```
VERDICT: INCOMPLETE — No tiers could execute.
Recommendation: Install testing dependencies before review.
```

---

## Example: Full CodeGlass + Paladin Flow

```
User: "Review this project and tell me if it's ready to ship"

CodeGlass activates:
  1. Reads codebase
  2. Generates code review (architecture, patterns, issues)
  3. Detects paladin skill is available

Paladin activates:
  4. Detects: React + Vite + TypeScript + Supabase
  5. Loads: react-vite.md + supabase.md + universal.md
  6. Tier 1: tsc --noEmit → PASS
  7. Tier 1: eslint → 2 warnings → PASS (not strict mode)
  8. Tier 2: vitest run → 47/47 pass, 83% coverage → PASS
  9. Tier 3: integration tests → 12/12 pass → PASS
  10. Tier 4: a11y scan → 1 minor → PASS
  11. Tier 5: lighthouse 87, no secrets → PASS
  12. Verdict: PASS (2 warnings, 1 info)
  13. Generates Tier 6 human checklist

Combined output:
  14. CodeGlass review + Paladin verdict + Human checklist
  15. Final: "Ship Ready: YES (with 2 minor warnings)"
```
