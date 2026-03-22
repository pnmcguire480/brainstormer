# Getting Started with BrainStormer

## 5-Minute Onboarding

### Step 1: Install

```bash
cd /path/to/BrainStormer/cli
pip install -e .
```

### Step 2: Configure Obsidian (optional)

```bash
brainstormer config set vault_path /path/to/your/obsidian/vault
```

### Step 3: Initialize Your Project

```bash
cd /path/to/your/project
brainstormer init
```

That's it. BrainStormer will:
- Detect your stack (Node, Python, Rust, etc.)
- Create 10 project documentation files
- Set up comprehension tracking
- Set up ideation workspace
- Configure quality gates
- Sync to your Obsidian vault

### Step 4: Check Status

```bash
brainstormer status
```

See what's configured and what needs attention.

### Step 5: Validate

```bash
brainstormer doctor
```

Make sure everything is wired up correctly.

---

## What Just Happened?

When you ran `brainstormer init`, these files were created in your project:

### Root Directory
```
CLAUDE.md        ← Start here. Project identity, rules, session state.
SPEC.md          ← Define your users, features, acceptance criteria.
ARCHITECTURE.md  ← Tech stack, data model, APIs.
CONTEXT.md       ← Domain background, stakeholders, constraints.
SCENARIOS.md     ← User flows with happy/sad paths.
AGENTS.md        ← Which AI tier handles which tasks.
CODEGUIDE.md     ← Code style, naming, git workflow.
ART.md           ← Visual design direction.
SNIFFTEST.md     ← Human-only test prompts (AI never reads this).
README.md        ← Public project overview.
```

### Additional Directories
```
.claude/              ← Claude Code configuration
brainstormer/         ← Ideation outputs (angles, hooks, calendar)
docs/codeglass/       ← Code walkthrough archives
rules.md              ← Accumulated coding patterns
paladin.config.json   ← Quality gate configuration
```

---

## Recommended First Steps

1. **Fill in CONTEXT.md** — Brain dump everything about your project
2. **Fill in SPEC.md** — Define who your users are and what features they need
3. **Fill in ARCHITECTURE.md** — Document your tech stack choices
4. **Start coding** — CodeGlass walkthroughs happen automatically
5. **Before shipping** — Run `brainstormer quality run` to hit the testing wall

---

## For Existing Projects

BrainStormer is safe for existing projects:
- **Never overwrites** existing files
- Only creates files that don't exist yet
- Running `init` twice does nothing on the second run
- Use `--update` to re-sync templates while preserving your customizations

---

## Common Workflows

### Starting a new project
```bash
mkdir my-project && cd my-project
npm init -y  # or cargo init, or whatever
brainstormer init
```

### Adding to an existing project
```bash
cd existing-project
brainstormer init  # skips files that already exist
```

### After making changes
```bash
brainstormer sync  # push latest state to Obsidian
```

### Before deploying
```bash
brainstormer quality run  # run all automated quality checks
```
