#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# PALADIN BOOTSTRAP — Auto-Install Testing Infrastructure
#
# Detects what's missing and installs it. Designed for vibe coders
# who don't know what vitest or eslint are. They shouldn't have to.
#
# Usage: bash paladin-bootstrap.sh [project-root] [--dry-run] [--yes]
#
# Options:
#   --dry-run    Show what would be installed without doing it
#   --yes        Skip confirmation prompts (for CI/automation)
#   --minimal    Only install essentials (build + lint + test runner)
#   --full       Install everything including integration/a11y/perf tools
# ═══════════════════════════════════════════════════════════════

set -euo pipefail

# ─── Colors ───
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# ─── Config ───
PROJECT_ROOT="${1:-.}"
DRY_RUN=false
AUTO_YES=false
INSTALL_LEVEL="full"
CHANGES_MADE=()
ALREADY_PRESENT=()

for arg in "$@"; do
  case $arg in
    --dry-run) DRY_RUN=true ;;
    --yes) AUTO_YES=true ;;
    --minimal) INSTALL_LEVEL="minimal" ;;
    --full) INSTALL_LEVEL="full" ;;
  esac
done

cd "$PROJECT_ROOT"

# ─── Utility ───

log_install() {
  echo -e "  ${GREEN}+${NC} $1"
  CHANGES_MADE+=("$1")
}

log_skip() {
  echo -e "  ${BLUE}✓${NC} $1 (already present)"
  ALREADY_PRESENT+=("$1")
}

log_action() {
  echo -e "  ${YELLOW}→${NC} $1"
}

confirm() {
  if $AUTO_YES; then return 0; fi
  if $DRY_RUN; then return 0; fi
  echo ""
  echo -e "${BOLD}$1${NC}"
  read -p "  Proceed? (Y/n) " answer
  [[ -z "$answer" || "$answer" =~ ^[Yy] ]]
}

run_if_real() {
  if $DRY_RUN; then
    echo -e "  ${CYAN}[dry-run]${NC} $*"
  else
    "$@"
  fi
}

# ─── Project Detection (same as paladin-run.sh) ───

detect_project_type() {
  local types=()
  [ -f "package.json" ] && {
    if grep -q '"react"' package.json 2>/dev/null && grep -q "vite" package.json 2>/dev/null; then
      types+=("react-vite")
    elif grep -q '"next"' package.json 2>/dev/null; then
      types+=("nextjs")
    elif grep -q '"svelte"' package.json 2>/dev/null; then
      types+=("svelte")
    else
      types+=("node")
    fi
  }
  [ -f "Cargo.toml" ] && types+=("rust")
  [ -f "pyproject.toml" ] || [ -f "requirements.txt" ] && types+=("python")
  [ -d "supabase" ] && types+=("supabase")
  if [ ${#types[@]} -eq 0 ] && ls *.html >/dev/null 2>&1; then
    types+=("static-site")
  fi
  [ ${#types[@]} -eq 0 ] && echo "unknown" || echo "${types[*]}"
}

PROJECT_TYPE=$(detect_project_type)
PROJECT_NAME=$(basename "$(pwd)")

echo ""
echo -e "${BOLD}${CYAN}═══════════════════════════════════════════════${NC}"
echo -e "${BOLD}${CYAN}  PALADIN BOOTSTRAP${NC}"
echo -e "${BOLD}${CYAN}  Project: $PROJECT_NAME${NC}"
echo -e "${BOLD}${CYAN}  Stack:   $PROJECT_TYPE${NC}"
echo -e "${BOLD}${CYAN}  Level:   $INSTALL_LEVEL${NC}"
if $DRY_RUN; then
echo -e "${BOLD}${YELLOW}  Mode:    DRY RUN (no changes)${NC}"
fi
echo -e "${BOLD}${CYAN}═══════════════════════════════════════════════${NC}"
echo ""

# ═══════════════════════════════════════════════════════════════
# REACT + VITE + TYPESCRIPT BOOTSTRAP
# ═══════════════════════════════════════════════════════════════

bootstrap_react_vite() {
  echo -e "${BOLD}Checking React + Vite project...${NC}"
  echo ""

  # ─── Tier 1: Build & Lint Infrastructure ───
  echo -e "${BOLD}Tier 1 — Build & Lint:${NC}"

  # TypeScript
  if grep -q '"typescript"' package.json 2>/dev/null; then
    log_skip "TypeScript"
  else
    log_install "TypeScript (type checking)"
    run_if_real npm install -D typescript
  fi

  # tsconfig.json
  if [ -f "tsconfig.json" ]; then
    log_skip "tsconfig.json"
  else
    log_install "tsconfig.json (default config)"
    if ! $DRY_RUN; then
      cat > tsconfig.json << 'TSEOF'
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
TSEOF
    fi
  fi

  # ESLint
  if [ -f ".eslintrc.cjs" ] || [ -f ".eslintrc.js" ] || [ -f ".eslintrc.json" ] || [ -f "eslint.config.js" ] || [ -f "eslint.config.mjs" ]; then
    log_skip "ESLint config"
  else
    log_install "ESLint + React/TypeScript config"
    run_if_real npm install -D eslint @typescript-eslint/eslint-plugin @typescript-eslint/parser eslint-plugin-react-hooks eslint-plugin-react-refresh
    if ! $DRY_RUN; then
      cat > .eslintrc.cjs << 'ESLEOF'
module.exports = {
  root: true,
  env: { browser: true, es2020: true },
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:react-hooks/recommended',
  ],
  ignorePatterns: ['dist', '.eslintrc.cjs'],
  parser: '@typescript-eslint/parser',
  plugins: ['react-refresh'],
  rules: {
    'react-refresh/only-export-components': ['warn', { allowConstantExport: true }],
  },
};
ESLEOF
    fi
  fi

  # Prettier
  if [ -f ".prettierrc" ] || [ -f ".prettierrc.json" ] || [ -f "prettier.config.js" ] || [ -f ".prettierrc.js" ]; then
    log_skip "Prettier config"
  else
    log_install "Prettier (code formatter)"
    run_if_real npm install -D prettier
    if ! $DRY_RUN; then
      cat > .prettierrc << 'PEOF'
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5",
  "printWidth": 100
}
PEOF
    fi
  fi

  # .gitignore
  if [ -f ".gitignore" ]; then
    # Check if .env is in it
    if ! grep -q "\.env" .gitignore; then
      log_install ".env added to existing .gitignore"
      if ! $DRY_RUN; then
        echo -e "\n# Environment\n.env\n.env.local\n.env.production" >> .gitignore
      fi
    else
      log_skip ".gitignore (.env covered)"
    fi
  else
    log_install ".gitignore (full default)"
    if ! $DRY_RUN; then
      cat > .gitignore << 'GIEOF'
node_modules/
dist/
build/
.env
.env.local
.env.production
*.log
.DS_Store
coverage/
paladin-reports/
paladin-screenshots/
GIEOF
    fi
  fi

  echo ""

  # ─── Tier 2: Test Runner ───
  echo -e "${BOLD}Tier 2 — Test Runner:${NC}"

  # Vitest
  if grep -q '"vitest"' package.json 2>/dev/null; then
    log_skip "Vitest"
  else
    log_install "Vitest + Testing Library + jsdom"
    run_if_real npm install -D vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom @vitest/coverage-v8
  fi

  # Vitest config
  HAS_VITEST_CONFIG=false
  [ -f "vitest.config.ts" ] && HAS_VITEST_CONFIG=true
  if grep -q "test:" vite.config.ts 2>/dev/null; then HAS_VITEST_CONFIG=true; fi

  if $HAS_VITEST_CONFIG; then
    log_skip "Vitest config"
  else
    log_install "vitest.config.ts"
    if ! $DRY_RUN; then
      cat > vitest.config.ts << 'VTEOF'
/// <reference types="vitest" />
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
    css: true,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/test/',
        '**/*.d.ts',
        '**/*.config.*',
        '**/index.ts',
      ],
    },
  },
});
VTEOF
    fi
  fi

  # Test setup file
  if [ -f "src/test/setup.ts" ] || [ -f "src/setupTests.ts" ]; then
    log_skip "Test setup file"
  else
    log_install "src/test/setup.ts"
    if ! $DRY_RUN; then
      mkdir -p src/test
      cat > src/test/setup.ts << 'TSEOF'
import '@testing-library/jest-dom';
TSEOF
    fi
  fi

  # .env.example
  if [ -f ".env.example" ]; then
    log_skip ".env.example"
  else
    log_install ".env.example (env var documentation)"
    if ! $DRY_RUN; then
      # Scan for env var usage and create template
      echo "# Environment Variables" > .env.example
      echo "# Copy to .env.local and fill in values" >> .env.example
      echo "" >> .env.example
      grep -roh "VITE_[A-Z_]*" src/ 2>/dev/null | sort -u | while read var; do
        echo "$var=" >> .env.example
      done
    fi
  fi

  # Sample test file (only if NO test files exist at all)
  TEST_COUNT=$(find src/ -name "*.test.*" -o -name "*.spec.*" 2>/dev/null | wc -l)
  if [ "$TEST_COUNT" -eq 0 ]; then
    log_install "Sample test file (src/App.test.tsx)"
    if ! $DRY_RUN; then
      # Find the main component file
      if [ -f "src/App.tsx" ]; then
        cat > src/App.test.tsx << 'TESTEOF'
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import App from './App';

describe('App', () => {
  it('renders without crashing', () => {
    render(<App />);
    // This is your starter test. Replace this assertion with
    // something meaningful for your app:
    expect(document.body).toBeTruthy();
  });
});
TESTEOF
      fi
    fi
  else
    log_skip "Test files ($TEST_COUNT found)"
  fi

  echo ""

  # ─── Tier 3+: Integration & Advanced (full mode only) ───
  if [ "$INSTALL_LEVEL" = "full" ]; then
    echo -e "${BOLD}Tier 3+ — Integration & Advanced:${NC}"

    # MSW (API mocking)
    if grep -q '"msw"' package.json 2>/dev/null; then
      log_skip "MSW (API mocking)"
    else
      log_install "MSW (Mock Service Worker for API testing)"
      run_if_real npm install -D msw
    fi

    # MSW handler scaffold
    if [ -f "src/mocks/handlers.ts" ] || [ -f "src/mocks/handlers.js" ]; then
      log_skip "MSW handlers"
    else
      log_install "src/mocks/handlers.ts (API mock scaffold)"
      if ! $DRY_RUN; then
        mkdir -p src/mocks
        cat > src/mocks/handlers.ts << 'MSWEOF'
import { http, HttpResponse } from 'msw';

// Add your API mock handlers here.
// Example:
// http.get('/api/items', () => {
//   return HttpResponse.json([
//     { id: 1, name: 'Item 1' },
//     { id: 2, name: 'Item 2' },
//   ]);
// }),

export const handlers = [
  // Your handlers go here
];
MSWEOF
        cat > src/mocks/server.ts << 'SRVEOF'
import { setupServer } from 'msw/node';
import { handlers } from './handlers';

export const server = setupServer(...handlers);
SRVEOF
      fi
    fi

    echo ""
  fi

  # ─── NPM Scripts ───
  echo -e "${BOLD}NPM Scripts:${NC}"

  # Add test scripts to package.json if missing
  if ! grep -q '"test"' package.json 2>/dev/null; then
    log_install "npm scripts: test, test:coverage, lint, format, paladin"
    if ! $DRY_RUN; then
      # Use node to safely modify package.json
      node -e "
        const pkg = require('./package.json');
        pkg.scripts = pkg.scripts || {};
        if (!pkg.scripts.test) pkg.scripts.test = 'vitest run';
        if (!pkg.scripts['test:watch']) pkg.scripts['test:watch'] = 'vitest';
        if (!pkg.scripts['test:coverage']) pkg.scripts['test:coverage'] = 'vitest run --coverage';
        if (!pkg.scripts.lint) pkg.scripts.lint = 'eslint . --ext .ts,.tsx --max-warnings 0';
        if (!pkg.scripts.format) pkg.scripts.format = 'prettier --write \"src/**/*.{ts,tsx,css,json}\"';
        if (!pkg.scripts['format:check']) pkg.scripts['format:check'] = 'prettier --check \"src/**/*.{ts,tsx,css,json}\"';
        if (!pkg.scripts.typecheck) pkg.scripts.typecheck = 'tsc --noEmit';
        require('fs').writeFileSync('./package.json', JSON.stringify(pkg, null, 2) + '\n');
      "
    fi
  else
    log_skip "npm test script"
    # Still add missing paladin-related scripts
    if ! grep -q '"typecheck"' package.json 2>/dev/null; then
      log_install "npm script: typecheck"
      if ! $DRY_RUN; then
        node -e "
          const pkg = require('./package.json');
          pkg.scripts = pkg.scripts || {};
          if (!pkg.scripts.typecheck) pkg.scripts.typecheck = 'tsc --noEmit';
          if (!pkg.scripts['test:coverage']) pkg.scripts['test:coverage'] = 'vitest run --coverage';
          if (!pkg.scripts['format:check']) pkg.scripts['format:check'] = 'prettier --check \"src/**/*.{ts,tsx,css,json}\"';
          require('fs').writeFileSync('./package.json', JSON.stringify(pkg, null, 2) + '\n');
        "
      fi
    fi
  fi

  echo ""
}

# ═══════════════════════════════════════════════════════════════
# PYTHON BOOTSTRAP
# ═══════════════════════════════════════════════════════════════

bootstrap_python() {
  echo -e "${BOLD}Checking Python project...${NC}"
  echo ""

  echo -e "${BOLD}Tier 1 — Lint & Format:${NC}"

  # Ruff (replaces flake8 + isort + black in one tool)
  if pip show ruff &>/dev/null || grep -q "ruff" requirements*.txt pyproject.toml 2>/dev/null; then
    log_skip "Ruff (linter/formatter)"
  else
    log_install "Ruff (linter + formatter, replaces flake8/black/isort)"
    run_if_real pip install ruff --break-system-packages 2>/dev/null || run_if_real pip install ruff
  fi

  # ruff.toml
  if [ -f "ruff.toml" ] || [ -f ".ruff.toml" ] || grep -q "\[tool.ruff\]" pyproject.toml 2>/dev/null; then
    log_skip "Ruff config"
  else
    log_install "ruff.toml"
    if ! $DRY_RUN; then
      cat > ruff.toml << 'REOF'
line-length = 100
target-version = "py310"

[lint]
select = ["E", "F", "W", "I", "N", "UP", "B", "A", "SIM", "TCH"]
ignore = ["E501"]  # line length handled by formatter

[format]
quote-style = "double"
REOF
    fi
  fi

  # mypy
  if pip show mypy &>/dev/null; then
    log_skip "mypy"
  else
    log_install "mypy (type checking)"
    run_if_real pip install mypy --break-system-packages 2>/dev/null || run_if_real pip install mypy
  fi

  echo ""
  echo -e "${BOLD}Tier 2 — Test Runner:${NC}"

  # pytest
  if pip show pytest &>/dev/null; then
    log_skip "pytest"
  else
    log_install "pytest + pytest-cov"
    run_if_real pip install pytest pytest-cov --break-system-packages 2>/dev/null || run_if_real pip install pytest pytest-cov
  fi

  # pytest config
  if [ -f "pytest.ini" ] || [ -f "setup.cfg" ] || grep -q "\[tool.pytest\]" pyproject.toml 2>/dev/null; then
    log_skip "pytest config"
  else
    log_install "pyproject.toml pytest config"
    if ! $DRY_RUN; then
      if [ -f "pyproject.toml" ]; then
        cat >> pyproject.toml << 'PTEOF'

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
addopts = "-v --tb=short"
PTEOF
      else
        cat > pytest.ini << 'PIEOF'
[pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
addopts = -v --tb=short
PIEOF
      fi
    fi
  fi

  # tests directory
  if [ -d "tests" ]; then
    log_skip "tests/ directory"
  else
    log_install "tests/ directory with sample test"
    if ! $DRY_RUN; then
      mkdir -p tests
      cat > tests/__init__.py << 'EOF'
EOF
      cat > tests/test_smoke.py << 'STEOF'
"""Smoke test — proves the test runner works."""


def test_sanity():
    """If this fails, your test setup is broken."""
    assert True


def test_imports():
    """Verify the main package can be imported."""
    # Replace 'your_package' with your actual package name:
    # import your_package
    pass
STEOF
    fi
  fi

  # .gitignore additions
  if [ -f ".gitignore" ]; then
    if ! grep -q "__pycache__" .gitignore; then
      log_install "Python entries added to .gitignore"
      if ! $DRY_RUN; then
        cat >> .gitignore << 'GIEOF'

# Python
__pycache__/
*.pyc
.mypy_cache/
.ruff_cache/
.pytest_cache/
htmlcov/
.coverage
.env
dist/
*.egg-info/
GIEOF
      fi
    fi
  fi

  echo ""
}

# ═══════════════════════════════════════════════════════════════
# RUST BOOTSTRAP
# ═══════════════════════════════════════════════════════════════

bootstrap_rust() {
  echo -e "${BOLD}Checking Rust project...${NC}"
  echo ""

  echo -e "${BOLD}Tier 1 — Lint & Format:${NC}"

  # Clippy (comes with rustup, just verify)
  if rustup component list 2>/dev/null | grep -q "clippy.*installed"; then
    log_skip "clippy"
  else
    log_install "clippy (Rust linter)"
    run_if_real rustup component add clippy
  fi

  # rustfmt
  if rustup component list 2>/dev/null | grep -q "rustfmt.*installed"; then
    log_skip "rustfmt"
  else
    log_install "rustfmt (Rust formatter)"
    run_if_real rustup component add rustfmt
  fi

  # cargo-audit
  if command -v cargo-audit &>/dev/null; then
    log_skip "cargo-audit"
  else
    log_install "cargo-audit (dependency vulnerability scanner)"
    run_if_real cargo install cargo-audit
  fi

  echo ""
  echo -e "${BOLD}Tier 2 — Tests:${NC}"

  # Check for any #[test] in src/
  TEST_COUNT=$(grep -rn "#\[test\]" src/ tests/ 2>/dev/null | wc -l)
  if [ "$TEST_COUNT" -gt 0 ]; then
    log_skip "Test functions ($TEST_COUNT found)"
  else
    log_install "tests/ directory with sample integration test"
    if ! $DRY_RUN; then
      mkdir -p tests
      cat > tests/smoke_test.rs << 'RTEOF'
//! Smoke test — proves the test harness works.

#[test]
fn sanity_check() {
    assert_eq!(2 + 2, 4);
}
RTEOF
    fi
  fi

  echo ""
}

# ═══════════════════════════════════════════════════════════════
# STATIC SITE BOOTSTRAP
# ═══════════════════════════════════════════════════════════════

bootstrap_static_site() {
  echo -e "${BOLD}Checking static site...${NC}"
  echo ""

  echo -e "${BOLD}Tier 1 — Validation:${NC}"

  # If no package.json, there's not much to install automatically.
  # Suggest what they should add.
  if [ ! -f "package.json" ]; then
    log_action "No package.json found. Consider initializing with: npm init -y"
    log_action "Then install: npm install -D html-validate prettier"
  else
    # Prettier
    if grep -q '"prettier"' package.json 2>/dev/null; then
      log_skip "Prettier"
    else
      log_install "Prettier (HTML/CSS/JS formatter)"
      run_if_real npm install -D prettier
    fi

    # html-validate
    if grep -q '"html-validate"' package.json 2>/dev/null; then
      log_skip "html-validate"
    else
      log_install "html-validate (HTML validation)"
      run_if_real npm install -D html-validate
    fi
  fi

  # .gitignore
  if [ ! -f ".gitignore" ]; then
    log_install ".gitignore"
    if ! $DRY_RUN; then
      echo -e "node_modules/\n.env\n.DS_Store" > .gitignore
    fi
  fi

  echo ""
}

# ═══════════════════════════════════════════════════════════════
# SUPABASE OVERLAY BOOTSTRAP
# ═══════════════════════════════════════════════════════════════

bootstrap_supabase() {
  echo -e "${BOLD}Supabase overlay checks...${NC}"
  echo ""

  # Check Supabase CLI
  if command -v supabase &>/dev/null; then
    log_skip "Supabase CLI"
  else
    log_action "Supabase CLI not found. Install: npm install -g supabase"
  fi

  # Check for types file
  TYPES_FILE=$(find src/ -name "supabase.ts" -o -name "database.types.ts" 2>/dev/null | head -1)
  if [ -n "$TYPES_FILE" ]; then
    log_skip "Supabase types ($TYPES_FILE)"
  else
    log_action "No Supabase types file. Generate with: supabase gen types typescript --local > src/types/supabase.ts"
  fi

  # Check .env has Supabase vars documented
  if [ -f ".env.example" ]; then
    if grep -q "SUPABASE" .env.example; then
      log_skip "Supabase env vars in .env.example"
    else
      log_install "Supabase env vars added to .env.example"
      if ! $DRY_RUN; then
        echo -e "\n# Supabase\nVITE_SUPABASE_URL=\nVITE_SUPABASE_ANON_KEY=" >> .env.example
      fi
    fi
  fi

  echo ""
}

# ═══════════════════════════════════════════════════════════════
# PALADIN CONFIG BOOTSTRAP (all projects)
# ═══════════════════════════════════════════════════════════════

bootstrap_paladin_config() {
  echo -e "${BOLD}Paladin Config:${NC}"

  if [ -f "paladin.config.json" ]; then
    log_skip "paladin.config.json"
  else
    log_install "paladin.config.json (testing wall config)"
    if ! $DRY_RUN; then
      SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
      SKILL_ROOT="$(dirname "$SCRIPT_DIR")"
      if [ -f "$SKILL_ROOT/templates/paladin-config-default.json" ]; then
        cp "$SKILL_ROOT/templates/paladin-config-default.json" paladin.config.json
        # Patch in project details
        node -e "
          const cfg = require('./paladin.config.json');
          cfg.project = cfg.project || {};
          cfg.project.name = '$PROJECT_NAME';
          cfg.project.type = '$PROJECT_TYPE';
          require('fs').writeFileSync('./paladin.config.json', JSON.stringify(cfg, null, 2) + '\n');
        " 2>/dev/null || true
      else
        # Create minimal config inline
        cat > paladin.config.json << CFEOF
{
  "project": {
    "name": "$PROJECT_NAME",
    "type": "$PROJECT_TYPE"
  },
  "tiers": {
    "skip": [],
    "strictMode": false,
    "tier2": {
      "coverageThreshold": {
        "statements": 80,
        "branches": 70,
        "functions": 80,
        "lines": 80
      }
    }
  }
}
CFEOF
      fi
    fi
  fi
  echo ""
}

# ═══════════════════════════════════════════════════════════════
# MAIN — Route to appropriate bootstrap
# ═══════════════════════════════════════════════════════════════

echo -e "${BOLD}Scanning for missing test infrastructure...${NC}"
echo ""

# Run project-specific bootstrap
for ptype in $PROJECT_TYPE; do
  case $ptype in
    react-vite) bootstrap_react_vite ;;
    nextjs)     bootstrap_react_vite ;;  # Same tooling, minor differences
    svelte)     bootstrap_react_vite ;;  # Similar enough
    node)       bootstrap_react_vite ;;
    python)     bootstrap_python ;;
    rust)       bootstrap_rust ;;
    static-site) bootstrap_static_site ;;
    supabase)   bootstrap_supabase ;;
    *)          echo -e "${YELLOW}Unknown project type: $ptype — skipping${NC}" ;;
  esac
done

# Always run paladin config bootstrap
bootstrap_paladin_config

# ═══════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════

echo ""
echo -e "${BOLD}${CYAN}═══════════════════════════════════════════════${NC}"
echo -e "${BOLD}${CYAN}  BOOTSTRAP SUMMARY${NC}"
echo -e "${BOLD}${CYAN}═══════════════════════════════════════════════${NC}"

if [ ${#CHANGES_MADE[@]} -eq 0 ]; then
  echo -e "  ${GREEN}All test infrastructure already present.${NC}"
  echo -e "  ${GREEN}Ready to run: paladin-run.sh${NC}"
else
  echo -e "  ${GREEN}Installed ${#CHANGES_MADE[@]} items:${NC}"
  for change in "${CHANGES_MADE[@]}"; do
    echo -e "    ${GREEN}+${NC} $change"
  done
fi

if [ ${#ALREADY_PRESENT[@]} -gt 0 ]; then
  echo ""
  echo -e "  ${BLUE}Already present: ${#ALREADY_PRESENT[@]} items${NC}"
fi

if $DRY_RUN; then
  echo ""
  echo -e "  ${YELLOW}This was a dry run. No changes were made.${NC}"
  echo -e "  ${YELLOW}Run without --dry-run to apply.${NC}"
fi

echo ""
echo -e "${BOLD}${CYAN}═══════════════════════════════════════════════${NC}"
echo ""
