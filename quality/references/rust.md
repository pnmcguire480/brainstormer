# Rust Project Testing Reference

Covers Rust projects including WASM builds (Stars 2026 pattern).

---

## Tier 1: The Obvious

```bash
# Compile check (fastest gate)
cargo check 2>&1

# Full build
cargo build 2>&1

# Clippy (lint)
cargo clippy -- -D warnings 2>&1

# Format check
cargo fmt -- --check 2>&1

# Dependency audit
cargo audit 2>/dev/null || echo "cargo-audit not installed: cargo install cargo-audit"

# WASM build (if applicable)
if grep -q "wasm" Cargo.toml; then
  wasm-pack build --target web 2>&1 || echo "wasm-pack build failed"
fi
```

---

## Tier 2: The Structural

```bash
# Run all tests
cargo test -- --nocapture 2>&1

# Run tests with output on failure only
cargo test 2>&1

# Check for untested public functions
# (heuristic: count pub fn vs #[test] fn)
PUB_FN=$(grep -rn "pub fn " src/ | wc -l)
TEST_FN=$(grep -rn "#\[test\]" src/ tests/ | wc -l)
echo "Public functions: $PUB_FN | Test functions: $TEST_FN"

# Doc tests
cargo test --doc 2>&1
```

---

## Tier 3: The Behavioral

```bash
# Integration tests (tests/ directory)
cargo test --test '*' 2>&1 || echo "No integration tests in tests/"

# If the project has a binary, smoke test it
if grep -q '\[\[bin\]\]' Cargo.toml || grep -q 'src/main.rs' Cargo.toml 2>/dev/null; then
  cargo run -- --help 2>&1 || echo "Binary --help check failed"
fi
```

---

## Tier 5: The Invisible

```bash
# Build in release mode and check size
cargo build --release 2>&1
ls -lh target/release/ | grep -v "\.d$\|deps\|build\|\.fingerprint" | head -10

# Check for unsafe code
grep -rn "unsafe " src/ | grep -v "// SAFETY:" || echo "No unsafe blocks (or all documented)"

# WASM size check
if [ -d pkg/ ]; then
  echo "=== WASM Bundle Size ==="
  ls -lh pkg/*.wasm 2>/dev/null
  ls -lh pkg/*.js 2>/dev/null
fi
```
