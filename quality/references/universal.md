# Universal Checks — Stack-Agnostic

Always load this file alongside any stack-specific reference. These checks
apply to every project regardless of language or framework.

---

## Tier 1 Universal Checks

### 1.1 — File Hygiene
```bash
# Check for debug artifacts
grep -rn "console\.log\|debugger\|TODO\|FIXME\|HACK\|XXX" src/ --include="*.{ts,tsx,js,jsx,py,rs}" || true

# Check for hardcoded secrets / credentials
grep -rn "password\|secret\|api_key\|apikey\|token\|SUPABASE_SERVICE_ROLE" src/ \
  --include="*.{ts,tsx,js,jsx,py,rs,json,env}" \
  --exclude-dir=node_modules --exclude-dir=.git || true

# Check for .env files accidentally committed
git ls-files | grep -E "\.env$|\.env\.local$|\.env\.production$" || true

# Check .gitignore exists and covers basics
if [ ! -f .gitignore ]; then
  echo "CRITICAL: No .gitignore found"
fi
```

### 1.2 — Dependency Health
```bash
# Check for lockfile consistency (npm)
if [ -f package-lock.json ]; then
  npm ci --dry-run 2>&1 | head -20
fi

# Check for outdated deps with known vulnerabilities
npm audit --audit-level=high 2>/dev/null || true
pip audit 2>/dev/null || true
cargo audit 2>/dev/null || true
```

### 1.3 — Git State
```bash
# Check for uncommitted changes
git status --porcelain

# Check for untracked files that should probably be tracked
git ls-files --others --exclude-standard

# Check branch is clean
git diff --stat HEAD
```

---

## Tier 2 Universal Checks

### 2.1 — Test File Existence
```bash
# Verify test files actually exist
find . -name "*.test.*" -o -name "*.spec.*" -o -name "test_*" \
  | grep -v node_modules | head -20

# Count: how many source files vs how many test files?
SRC_COUNT=$(find src/ -name "*.ts" -o -name "*.tsx" -o -name "*.py" -o -name "*.rs" \
  | grep -v test | grep -v spec | wc -l)
TEST_COUNT=$(find . -name "*.test.*" -o -name "*.spec.*" -o -name "test_*" \
  | grep -v node_modules | wc -l)
echo "Source files: $SRC_COUNT | Test files: $TEST_COUNT | Ratio: $(echo "scale=1; $TEST_COUNT * 100 / $SRC_COUNT" | bc)%"
```

### 2.2 — Error Handling Audit
```bash
# Find async functions without try/catch or .catch()
# (heuristic — flags potential issues for manual review)
grep -rn "async " src/ --include="*.{ts,tsx,js,jsx}" \
  | grep -v "try\|catch\|\.catch\|test\|spec" || true

# Find fetch calls without error handling
grep -rn "fetch(" src/ --include="*.{ts,tsx,js,jsx}" \
  | grep -v "catch\|try\|test\|spec" || true
```

---

## Tier 3 Universal Checks

### 3.1 — Environment Consistency
```bash
# Verify all env vars referenced in code are documented
grep -rohn "process\.env\.\w\+\|import\.meta\.env\.\w\+" src/ \
  --include="*.{ts,tsx,js,jsx}" | sort -u > /tmp/env-used.txt

if [ -f .env.example ]; then
  cat .env.example | grep -v "^#" | cut -d= -f1 | sort -u > /tmp/env-documented.txt
  echo "=== Env vars used but NOT in .env.example ==="
  comm -23 /tmp/env-used.txt /tmp/env-documented.txt
fi
```

### 3.2 — Route/Endpoint Inventory
```bash
# List all route definitions (React Router, Express, etc.)
grep -rn "path=\|Route\|router\.\(get\|post\|put\|delete\|patch\)" src/ \
  --include="*.{ts,tsx,js,jsx}" | head -30
```

---

## Tier 4 Universal Checks

### 4.1 — Accessibility Baseline
```bash
# If pa11y is available
npx pa11y http://localhost:5173 2>/dev/null || echo "pa11y not available — install for a11y checks"

# Manual check: all img tags have alt attributes
grep -rn "<img " src/ --include="*.{tsx,jsx,html}" | grep -v "alt=" || true

# Manual check: all form inputs have labels
grep -rn "<input\|<select\|<textarea" src/ --include="*.{tsx,jsx,html}" \
  | grep -v "aria-label\|aria-labelledby\|id=.*label" || true
```

### 4.2 — Console Pollution
```bash
# Count console statements (should be zero in production code)
CONSOLE_COUNT=$(grep -rn "console\.\(log\|warn\|error\|debug\|info\)" src/ \
  --include="*.{ts,tsx,js,jsx}" | grep -v "test\|spec\|__test__" | wc -l)
echo "Console statements in production code: $CONSOLE_COUNT"
```

---

## Tier 5 Universal Checks

### 5.1 — Secret Scanning
```bash
# Deep scan for secrets patterns
grep -rn \
  -e "['\"]sk-[a-zA-Z0-9]\{20,\}['\"]" \
  -e "['\"]ghp_[a-zA-Z0-9]\{36,\}['\"]" \
  -e "['\"]eyJ[a-zA-Z0-9]\{20,\}['\"]" \
  -e "AKIA[A-Z0-9]\{16\}" \
  -e "['\"]supabase['\"].*['\"]eyJ" \
  src/ --include="*.{ts,tsx,js,jsx,py,rs,json}" \
  --exclude-dir=node_modules --exclude-dir=.git || true
```

### 5.2 — Build Output Analysis
```bash
# Check build output size
if [ -d dist ]; then
  echo "=== Build output size ==="
  du -sh dist/
  find dist/ -name "*.js" -exec du -h {} \; | sort -rh | head -10
  echo ""
  echo "=== Largest assets ==="
  find dist/ -type f -exec du -h {} \; | sort -rh | head -10
fi
```

### 5.3 — License Compliance
```bash
# Check for copyleft licenses in dependencies (potential issue for commercial projects)
npx license-checker --failOn "GPL-2.0;GPL-3.0;AGPL-1.0;AGPL-3.0" 2>/dev/null \
  || echo "license-checker not available"
```

---

## Severity Classification

All issues found by Paladin are classified:

| Severity | Meaning | Blocks ship? |
|----------|---------|-------------|
| **CRITICAL** | App broken, security hole, data loss risk | YES — always |
| **HIGH** | Feature broken, a11y violation, performance regression | YES — in strict mode |
| **MEDIUM** | Warning, minor UI issue, code smell | NO — logged |
| **LOW** | Style nit, optimization opportunity, info | NO — logged |
| **INFO** | Observation, suggestion, metric | NO — logged |

---

## Verdict Decision Logic

```
IF any CRITICAL issue exists → VERDICT: FAIL
ELSE IF strict_mode AND any HIGH issue exists → VERDICT: FAIL
ELSE IF any HIGH issue exists → VERDICT: WARN
ELSE → VERDICT: PASS (proceed to Tier 6)
```
