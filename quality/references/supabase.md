# Supabase Backend Testing Reference

For projects using Supabase (ChoreGate, SwarmCast, Triangulate patterns).
Run these checks IN ADDITION to the frontend stack reference.

---

## Tier 1: The Obvious

```bash
# Check Supabase CLI is available
supabase --version 2>/dev/null || echo "CRITICAL: Supabase CLI not installed"

# Validate migration files exist and are sequential
if [ -d supabase/migrations ]; then
  echo "=== Migration Files ==="
  ls -1 supabase/migrations/
  # Check for gaps in numbering
  ls supabase/migrations/ | sort -n
else
  echo "WARNING: No supabase/migrations directory"
fi

# Check types are generated and up to date
if [ -f src/types/supabase.ts ] || [ -f src/lib/database.types.ts ]; then
  echo "Supabase types file found"
  # Regenerate and diff
  supabase gen types typescript --local > /tmp/supabase-types-fresh.ts 2>/dev/null
  if [ $? -eq 0 ]; then
    TYPES_FILE=$(find src/ -name "supabase.ts" -o -name "database.types.ts" | head -1)
    diff "$TYPES_FILE" /tmp/supabase-types-fresh.ts > /dev/null 2>&1 \
      || echo "WARNING: Supabase types may be out of date — run supabase gen types"
  fi
else
  echo "WARNING: No Supabase types file found"
fi

# Check .env has required Supabase vars
for var in VITE_SUPABASE_URL VITE_SUPABASE_ANON_KEY; do
  grep -q "$var" .env.local 2>/dev/null || grep -q "$var" .env 2>/dev/null \
    || echo "MISSING ENV: $var"
done
```

---

## Tier 2: The Structural

```bash
# Test migrations apply cleanly
supabase db reset --debug 2>&1 || echo "Migration reset failed"

# Test RLS policies exist for each table
supabase db dump --data-only=false 2>/dev/null | grep -A5 "CREATE POLICY" || true

# Check that no table is missing RLS
supabase db dump --data-only=false 2>/dev/null \
  | grep "ALTER TABLE.*ENABLE ROW LEVEL SECURITY" || true
```

---

## Tier 3: The Behavioral

```bash
# Test Supabase Edge Functions (if any)
if [ -d supabase/functions ]; then
  echo "=== Edge Functions ==="
  ls supabase/functions/
  # Serve and test each function
  for fn in supabase/functions/*/; do
    fn_name=$(basename "$fn")
    echo "Testing function: $fn_name"
    # Check it has an index.ts
    if [ ! -f "$fn/index.ts" ]; then
      echo "  CRITICAL: No index.ts in $fn_name"
    fi
  done
fi

# Test realtime subscriptions (if used)
grep -rn "supabase.*channel\|supabase.*on(" src/ --include="*.{ts,tsx}" \
  | grep -v "node_modules\|test" || echo "No realtime subscriptions found"
```

---

## Tier 5: The Invisible

```bash
# Check for service role key in client code (CRITICAL security issue)
grep -rn "service_role\|SERVICE_ROLE\|supabase_service" src/ \
  --include="*.{ts,tsx,js,jsx}" | grep -v test || true
# If found: CRITICAL — service role key must never be in client code

# Check RLS is enabled on all public tables
supabase db dump --data-only=false 2>/dev/null \
  | grep -B2 "ENABLE ROW LEVEL SECURITY" | grep "ALTER TABLE" || true

# Check for overly permissive RLS policies
supabase db dump --data-only=false 2>/dev/null \
  | grep -A3 "CREATE POLICY" | grep "true" || true
# Policies with just "true" as the check are wide open
```
