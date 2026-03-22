# Python Project Testing Reference

---

## Tier 1: The Obvious

```bash
# Type checking
python -m mypy src/ --ignore-missing-imports 2>&1 || echo "mypy not installed"
# Alternative: pyright
npx pyright src/ 2>/dev/null || true

# Linting
python -m ruff check src/ 2>&1 || python -m flake8 src/ 2>&1 || echo "No linter found"

# Formatting
python -m ruff format --check src/ 2>&1 || python -m black --check src/ 2>&1 || echo "No formatter found"

# Import sorting
python -m isort --check-only src/ 2>&1 || true

# Security audit
pip audit 2>/dev/null || echo "pip-audit not installed"
python -m bandit -r src/ -ll 2>/dev/null || echo "bandit not installed"

# Build check (if pyproject.toml exists)
if [ -f pyproject.toml ]; then
  python -m build --no-isolation 2>&1 || echo "Build failed"
fi
```

---

## Tier 2: The Structural

```bash
# Run pytest with coverage
python -m pytest tests/ -v --tb=short 2>&1
python -m pytest tests/ --cov=src --cov-report=term-missing 2>&1

# Check test file existence for each source module
for f in $(find src/ -name "*.py" -not -name "__init__.py" -not -path "*/test*"); do
  basename=$(basename "$f" .py)
  if ! find tests/ -name "test_${basename}.py" -o -name "${basename}_test.py" | grep -q .; then
    echo "WARNING: No test file for $f"
  fi
done
```

---

## Tier 3: The Behavioral

```bash
# Integration tests (conventionally in tests/integration/)
python -m pytest tests/integration/ -v --tb=short 2>&1 || echo "No integration tests found"

# If FastAPI/Flask: endpoint testing
python -m pytest tests/ -v -k "test_api or test_endpoint or test_route" 2>&1 || true
```

---

## Tier 4: The Visible

```bash
# If CLI tool: verify help output
if grep -q "argparse\|click\|typer" src/**/*.py 2>/dev/null; then
  python -m src.main --help 2>&1 || echo "CLI help check failed"
fi

# If web app (FastAPI/Flask): basic response check
# Requires app to be running on localhost
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/ 2>/dev/null || true
```

---

## Tier 5: The Invisible

```bash
# Security scan
python -m bandit -r src/ -f json 2>/dev/null | python -c "
import json,sys
data=json.load(sys.stdin)
for r in data.get('results',[]):
    print(f\"{r['severity']}: {r['issue_text']} in {r['filename']}:{r['line_number']}\")
" 2>/dev/null || true

# Check for hardcoded secrets
grep -rn "password\|secret\|api_key\|token" src/ --include="*.py" \
  | grep -v "test\|mock\|fixture\|#\|environ\|getenv" || true
```
