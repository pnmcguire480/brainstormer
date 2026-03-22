# paladin.config.json — Schema Reference

Place `paladin.config.json` in the project root. All fields are optional;
defaults are applied for any missing field.

---

## Full Schema

```json
{
  "$schema": "paladin-config",
  "version": "1.0",

  "project": {
    "name": "my-project",
    "type": "auto",
    "description": "Optional project description for reports"
  },

  "tiers": {
    "skip": [],
    "strictMode": false,

    "tier1": {
      "enabled": true,
      "treatWarningsAsErrors": false,
      "ignorePaths": ["src/generated/**", "src/vendor/**"],
      "customLintRules": [],
      "allowedTodos": 5
    },

    "tier2": {
      "enabled": true,
      "coverageThreshold": {
        "statements": 80,
        "branches": 70,
        "functions": 80,
        "lines": 80
      },
      "testTimeout": 10000,
      "maxWeakAssertions": 10
    },

    "tier3": {
      "enabled": true,
      "apiMockRequired": true,
      "integrationTestDir": "src/__integration__",
      "supabaseChecks": "auto"
    },

    "tier4": {
      "enabled": true,
      "a11yLevel": "AA",
      "breakpoints": [320, 768, 1024, 1440],
      "maxConsoleLogs": 0,
      "screenshotDir": "paladin-screenshots"
    },

    "tier5": {
      "enabled": true,
      "lighthouseMinScore": {
        "performance": 80,
        "accessibility": 90,
        "bestPractices": 80,
        "seo": 80
      },
      "maxBundleSizeKb": 500,
      "secretPatterns": [
        "sk-[a-zA-Z0-9]{20,}",
        "ghp_[a-zA-Z0-9]{36,}",
        "AKIA[A-Z0-9]{16}",
        "eyJ[a-zA-Z0-9]{20,}"
      ]
    },

    "tier6": {
      "enabled": true,
      "humanTesters": ["Patrick"],
      "requireSignoff": true,
      "checklistTemplate": "default"
    }
  },

  "reporting": {
    "outputDir": "paladin-reports",
    "format": "markdown",
    "includeScreenshots": true,
    "includeTimings": true
  }
}
```

---

## Field Descriptions

### project.type
Auto-detected from project files. Override with:
`"react-vite"` | `"python"` | `"rust"` | `"static-site"` | `"composite"`

### tiers.skip
Array of tier numbers to skip entirely: `[4, 5]` skips visible and invisible.
Use sparingly. Skipped tiers show as `SKIP` in the verdict.

### tiers.strictMode
When `true`, HIGH-severity issues block shipping (not just CRITICAL).

### tier2.coverageThreshold
Per-metric minimums. Set any to `0` to disable that check.

### tier4.a11yLevel
WCAG level: `"A"`, `"AA"`, or `"AAA"`. Default `"AA"`.

### tier5.secretPatterns
Regex patterns for secret detection. Defaults cover common API key formats.
Add project-specific patterns as needed.

### tier6.humanTesters
Names shown in the Tier 6 checklist for sign-off accountability.
