# React + Vite + TypeScript + Tailwind — Testing Reference

Patrick's primary stack. This is the most detailed reference because it covers
the majority of projects (ChoreGate, Triangulate, SwarmCast, campaign sites, etc.).

---

## Required Dev Dependencies

Before running any tier, ensure these are installed. The `paladin-init.sh` script
can install missing ones.

```bash
# Tier 1: Static analysis
npm ls typescript eslint prettier || echo "Missing Tier 1 deps"

# Tier 2: Unit testing
npm ls vitest @testing-library/react @testing-library/jest-dom || echo "Missing Tier 2 deps"

# Tier 3: Integration testing
npm ls @testing-library/user-event msw || echo "Missing Tier 3 deps"

# Tier 4: Visual/a11y
npm ls @axe-core/react || echo "Missing Tier 4 deps"

# Tier 5: Performance/security
npm ls vite-plugin-inspect || echo "Missing Tier 5 deps"
```

### Quick Install (all test deps at once)
```bash
npm install -D vitest @testing-library/react @testing-library/jest-dom \
  @testing-library/user-event jsdom msw @axe-core/cli happy-dom
```

---

## Tier 1: The Obvious

### 1.1 — TypeScript Compilation
```bash
npx tsc --noEmit
# Expected: zero errors
# Common failures:
#   - Missing type imports
#   - Implicit 'any' with strict mode
#   - Null/undefined not handled
```

### 1.2 — ESLint
```bash
npx eslint src/ --ext .ts,.tsx --max-warnings 0
# Expected: zero errors, zero warnings
# If eslint config doesn't exist, flag as CRITICAL
```

### 1.3 — Prettier Check
```bash
npx prettier --check "src/**/*.{ts,tsx,css,json}"
# Expected: all files formatted
# Fix: npx prettier --write "src/**/*.{ts,tsx,css,json}"
```

### 1.4 — Vite Build
```bash
npx vite build 2>&1
# Expected: successful build with no errors
# Watch for:
#   - Import resolution failures
#   - Circular dependency warnings
#   - Missing environment variables
```

### 1.5 — Dependency Audit
```bash
npm audit --audit-level=high
# Expected: no high or critical vulnerabilities
```

---

## Tier 2: The Structural

### 2.1 — Vitest Configuration Check
```bash
# Verify vitest is configured
if ! grep -q "vitest" vite.config.ts 2>/dev/null && \
   ! [ -f vitest.config.ts ]; then
  echo "CRITICAL: Vitest not configured"
  echo "Add to vite.config.ts:"
  echo '  test: { globals: true, environment: "jsdom", setupFiles: "./src/test/setup.ts" }'
fi
```

### 2.2 — Run Unit Tests
```bash
npx vitest run --reporter=verbose
# Expected: all tests pass
# Coverage report:
npx vitest run --coverage
# Expected: coverage >= threshold (default 80%)
```

### 2.3 — Test Quality Audit
```bash
# Check for weak assertions (tests that can't actually fail)
grep -rn "expect(true)" src/ --include="*.test.*" || true
grep -rn "expect(1)" src/ --include="*.test.*" || true
grep -rn "\.toBeDefined()" src/ --include="*.test.*" | wc -l
# Flag if >50% of assertions are just .toBeDefined()
```

### 2.4 — Coverage Gaps
```bash
npx vitest run --coverage --coverage.reporter=text 2>&1 | tail -40
# Look for files with <50% coverage — these need attention
# Look for 0% coverage — these are untested entirely
```

### Minimum Test Patterns for React Components

Every component should have at minimum:
```typescript
// 1. Renders without crashing
it('renders without crashing', () => {
  render(<Component />);
});

// 2. Renders expected content
it('renders expected content', () => {
  render(<Component />);
  expect(screen.getByText('Expected Text')).toBeInTheDocument();
});

// 3. Handles empty/missing props gracefully
it('handles missing optional props', () => {
  render(<Component />);
  // Should not throw
});

// 4. User interaction works
it('responds to user interaction', async () => {
  const user = userEvent.setup();
  render(<Component />);
  await user.click(screen.getByRole('button'));
  // Assert state change
});
```

---

## Tier 3: The Behavioral

### 3.1 — Component Integration Tests
```bash
# Run integration test suite (conventionally in src/__integration__/ or *.integration.test.*)
npx vitest run --reporter=verbose "**/*.integration.test.*"
```

### 3.2 — API Mocking with MSW
```typescript
// Ensure MSW handlers exist for every API endpoint the app uses
// Check: src/mocks/handlers.ts should exist
// Check: every fetch/axios call in src/ has a corresponding mock handler
```

```bash
# Verify MSW is set up
if [ ! -f src/mocks/handlers.ts ] && [ ! -f src/mocks/handlers.js ]; then
  echo "WARNING: No MSW handlers found — API integration tests may not be isolated"
fi
```

### 3.3 — Router Testing
```bash
# If using React Router, verify all routes render
grep -rn "path=" src/ --include="*.{ts,tsx}" | \
  sed 's/.*path=["'"'"']\([^"'"'"']*\).*/\1/' | sort -u
# Each extracted path should have a corresponding test
```

### 3.4 — Supabase Integration (if applicable)
```bash
# Check if Supabase client is properly typed
grep -rn "supabase\." src/ --include="*.{ts,tsx}" | \
  grep -v "node_modules\|test\|mock\|spec" | head -20
# Every Supabase call should have error handling
# Every Supabase call should have a corresponding mock in tests
```

---

## Tier 4: The Visible

### 4.1 — Accessibility Scan
```bash
# Automated a11y audit (requires dev server running)
npx vite preview --port 4173 &
PREVIEW_PID=$!
sleep 3

npx @axe-core/cli http://localhost:4173 --exit 2>/dev/null
AXE_EXIT=$?

kill $PREVIEW_PID 2>/dev/null
exit $AXE_EXIT
```

### 4.2 — Responsive Layout Check
```bash
# Screenshot at key breakpoints (requires Playwright)
npx playwright install chromium 2>/dev/null

cat > /tmp/responsive-check.ts << 'EOF'
import { chromium } from 'playwright';
const BREAKPOINTS = [
  { name: 'mobile', width: 320, height: 568 },
  { name: 'mobile-lg', width: 375, height: 812 },
  { name: 'tablet', width: 768, height: 1024 },
  { name: 'desktop', width: 1024, height: 768 },
  { name: 'desktop-lg', width: 1440, height: 900 },
];
(async () => {
  const browser = await chromium.launch();
  for (const bp of BREAKPOINTS) {
    const page = await browser.newPage({ viewport: { width: bp.width, height: bp.height } });
    await page.goto('http://localhost:4173');
    await page.screenshot({ path: `paladin-screenshots/${bp.name}.png`, fullPage: true });
    await page.close();
  }
  await browser.close();
})();
EOF
```

### 4.3 — Tailwind Purge Verification
```bash
# Build and check if unused CSS is purged
npx vite build
CSS_SIZE=$(find dist/ -name "*.css" -exec du -b {} + | awk '{sum += $1} END {print sum}')
echo "Total CSS in build: ${CSS_SIZE} bytes"
# Flag if CSS > 50KB (indicates purge not working)
if [ "$CSS_SIZE" -gt 51200 ]; then
  echo "WARNING: CSS bundle > 50KB — check Tailwind purge config"
fi
```

### 4.4 — Console Cleanliness in Browser
```bash
# Run the app and capture console output
cat > /tmp/console-check.ts << 'EOF'
import { chromium } from 'playwright';
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  const logs: string[] = [];
  page.on('console', msg => logs.push(`[${msg.type()}] ${msg.text()}`));
  page.on('pageerror', err => logs.push(`[ERROR] ${err.message}`));
  await page.goto('http://localhost:4173');
  await page.waitForTimeout(3000);
  await browser.close();
  if (logs.length > 0) {
    console.log('=== Browser Console Output ===');
    logs.forEach(l => console.log(l));
    const errors = logs.filter(l => l.startsWith('[error]') || l.startsWith('[ERROR]'));
    if (errors.length > 0) process.exit(1);
  } else {
    console.log('Console clean — no output');
  }
})();
EOF
```

---

## Tier 5: The Invisible

### 5.1 — Bundle Analysis
```bash
# Vite bundle visualization
npx vite build
npx vite-bundle-visualizer 2>/dev/null || echo "Install vite-bundle-visualizer for detailed analysis"

# Quick size check
echo "=== JS Bundle Sizes ==="
find dist/assets/ -name "*.js" -exec du -h {} \; | sort -rh
echo ""
echo "=== Total build size ==="
du -sh dist/
```

### 5.2 — Lighthouse CI
```bash
# Requires Chrome and lighthouse
npx vite preview --port 4173 &
PREVIEW_PID=$!
sleep 3

npx lighthouse http://localhost:4173 \
  --output=json \
  --output-path=./paladin-lighthouse.json \
  --chrome-flags="--headless --no-sandbox" \
  --only-categories=performance,accessibility,best-practices,seo \
  2>/dev/null

kill $PREVIEW_PID 2>/dev/null

# Parse scores
node -e "
const r = require('./paladin-lighthouse.json');
const cats = r.categories;
console.log('Performance:', Math.round(cats.performance.score * 100));
console.log('Accessibility:', Math.round(cats.accessibility.score * 100));
console.log('Best Practices:', Math.round(cats['best-practices'].score * 100));
console.log('SEO:', Math.round(cats.seo.score * 100));
if (cats.performance.score < 0.8) process.exit(1);
"
```

### 5.3 — Security Checks
```bash
# Check for exposed environment variables in build output
grep -rn "VITE_\|SUPABASE_\|API_KEY\|SECRET" dist/ 2>/dev/null || true

# Check for eval() usage
grep -rn "eval(" src/ --include="*.{ts,tsx,js,jsx}" \
  | grep -v node_modules | grep -v test || true

# Check for innerHTML usage (XSS vector)
grep -rn "dangerouslySetInnerHTML\|innerHTML" src/ --include="*.{ts,tsx,js,jsx}" \
  | grep -v node_modules | grep -v test || true
```

### 5.4 — Environment Variable Safety
```bash
# Ensure no server-only secrets are exposed to the client
# In Vite, only VITE_ prefixed vars are exposed
grep -rn "process\.env\." src/ --include="*.{ts,tsx}" \
  | grep -v "node_modules\|test\|spec" || true
# If any process.env (without VITE_) found in client code, flag CRITICAL
```

---

## Test File Conventions

```
src/
  components/
    Button/
      Button.tsx
      Button.test.tsx          ← unit test (Tier 2)
      Button.integration.test.tsx  ← integration (Tier 3)
  hooks/
    useAuth.ts
    useAuth.test.ts            ← unit test (Tier 2)
  utils/
    formatDate.ts
    formatDate.test.ts         ← unit test (Tier 2)
  __integration__/
    auth-flow.test.tsx         ← integration (Tier 3)
    navigation.test.tsx        ← integration (Tier 3)
  mocks/
    handlers.ts                ← MSW API mocks
    server.ts                  ← MSW server setup
  test/
    setup.ts                   ← Vitest setup file
```
