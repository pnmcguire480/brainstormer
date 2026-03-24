# BrainStormer Agent Format

Every BrainStormer agent follows this structure. This is our IP — original prose, not copied from any source.

## Frontmatter

```yaml
---
name: Agent Name
description: One-line description — specific, actionable, starts with a verb or role noun
category: domain-slug (e.g., frontend, python, devops, security)
emoji: 🔧
source: brainstormer
version: 1.0
---
```

## Body Structure

```markdown
# {Agent Name}

You are **{Agent Name}**, a {role description in 1-2 sentences}. {What makes you distinct — your philosophy or approach in one sentence.}

## Your Expertise
- {3-6 bullet points of specific capabilities}
- {Be concrete — name technologies, patterns, techniques}

## How You Work

### {Primary Capability}
- {Specific actionable instructions}
- {What you do, not what you "can" do}

### {Secondary Capability}
- {More specific instructions}

## Rules
- {3-5 hard rules for quality/safety}
- {Things you always do or never do}

## Output Style
- {How you format responses}
- {What you include/exclude}
```

## Quality Requirements
- Minimum 250 words
- At least 3 `##` sections
- Concrete, actionable — not vague platitudes
- Written as instructions TO the agent, not ABOUT the agent
- No source attribution to external repos
- Every agent must earn its place — if it doesn't provide value beyond what a good prompt could do, it shouldn't exist
