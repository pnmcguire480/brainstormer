# Static Site Testing Reference

For HTML/CSS/JS sites without a build step (campaign sites, landing pages,
portfolio sites like Flock Performance, Minnie Sweet's, etc.).

---

## Tier 1: The Obvious

```bash
# HTML validation
npx html-validate "*.html" "**/*.html" 2>/dev/null \
  || echo "html-validate not available — install globally: npm i -g html-validate"

# Check for broken local links
grep -rohn 'href="[^"]*"\|src="[^"]*"' *.html **/*.html 2>/dev/null \
  | grep -v "http\|https\|mailto\|tel\|#\|javascript:" \
  | sed 's/.*="\(.*\)"/\1/' | sort -u | while read -r link; do
    if [ ! -f "$link" ]; then
      echo "BROKEN LINK: $link"
    fi
  done

# CSS validation (basic)
npx stylelint "**/*.css" 2>/dev/null || echo "stylelint not available"

# Check for TODO/FIXME/placeholder content
grep -rn "TODO\|FIXME\|lorem ipsum\|placeholder\|CHANGEME\|example\.com" \
  *.html **/*.html **/*.css **/*.js 2>/dev/null || true
```

---

## Tier 4: The Visible

```bash
# Accessibility check
npx pa11y index.html 2>/dev/null || echo "pa11y not available"

# Check all images have alt text
grep -rn "<img " *.html **/*.html 2>/dev/null | grep -v "alt=" || true

# Check meta tags exist
for f in *.html; do
  echo "=== $f ==="
  grep -c "<title>" "$f" || echo "  MISSING: <title>"
  grep -c "meta.*description" "$f" || echo "  MISSING: meta description"
  grep -c "meta.*viewport" "$f" || echo "  MISSING: viewport meta"
  grep -c "og:title\|og:description\|og:image" "$f" || echo "  MISSING: Open Graph tags"
done

# Check favicon exists
if [ ! -f favicon.ico ] && [ ! -f favicon.svg ]; then
  echo "WARNING: No favicon found"
fi
```

---

## Tier 5: The Invisible

```bash
# Total page weight
echo "=== Page Weight ==="
du -sh .
find . -name "*.jpg" -o -name "*.png" -o -name "*.gif" -o -name "*.webp" \
  | xargs du -ch 2>/dev/null | tail -1

# Check for uncompressed images > 500KB
find . -name "*.jpg" -o -name "*.png" -size +500k 2>/dev/null | while read -r img; do
  echo "LARGE IMAGE: $img ($(du -h "$img" | cut -f1))"
done

# Check for mixed content (http:// in an https site)
grep -rn "http://" *.html **/*.html **/*.css **/*.js 2>/dev/null \
  | grep -v "localhost\|127.0.0.1\|http://www.w3.org" || true

# SSL/HTTPS readiness
grep -rn "http://" *.html **/*.html 2>/dev/null \
  | grep -v "localhost\|127\.0\|<!--" | head -10 || true
```
