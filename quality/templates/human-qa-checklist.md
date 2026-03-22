# Tier 6: Human QA Checklist

**Project:** {{PROJECT_NAME}}
**Stack:** {{STACK}}
**Date:** {{DATE}}
**Tester:** {{TESTER_NAME}}

> This checklist is generated ONLY after Tiers 1–5 have passed.
> Walk through each item. Check the box when verified. If ANY item
> fails, log the issue and send it back through the appropriate tier.

---

## A. Happy Path Walkthrough

Walk through the primary user flow from start to finish. Do the thing
the app is supposed to do.

- [ ] **First load**: Does the app load without errors? How long does it take?
- [ ] **Primary action**: Can you complete the main task the app exists for?
- [ ] **Data persistence**: Does saved data actually persist after refresh?
- [ ] **Navigation**: Can you reach every page/screen from the expected entry points?
- [ ] **Authentication** (if applicable): Can you sign up, log in, log out, and log back in?
- [ ] **Core feature 1**: {{FEATURE_1}} — works as expected? Y/N
- [ ] **Core feature 2**: {{FEATURE_2}} — works as expected? Y/N
- [ ] **Core feature 3**: {{FEATURE_3}} — works as expected? Y/N

**Notes:**
```
[Write observations here]
```

---

## B. Destructive Testing

Try to break it. Be a hostile user.

- [ ] **Empty inputs**: Submit forms with nothing filled in. What happens?
- [ ] **Giant inputs**: Paste a novel into text fields. Does it handle overflow?
- [ ] **Special characters**: Try `<script>alert('xss')</script>`, emoji, unicode, SQL injection strings
- [ ] **Rapid clicking**: Spam the submit button. Does it double-submit?
- [ ] **Back button**: Hit back during a multi-step flow. Does it recover?
- [ ] **Offline**: Turn off network. Does the app fail gracefully?
- [ ] **Stale tab**: Leave the tab open for 30 minutes. Come back. Does it still work?
- [ ] **Multiple tabs**: Open the app in two tabs. Do they conflict?

**Notes:**
```
[Write observations here]
```

---

## C. Device Testing

Test on actual hardware, not just dev tools emulation.

- [ ] **Desktop Chrome**: Full walkthrough
- [ ] **Desktop Firefox**: Quick check of layout and main flow
- [ ] **Mobile Safari (iPhone)**: Full walkthrough on actual phone
- [ ] **Mobile Chrome (Android)**: Quick check if available
- [ ] **Tablet** (if applicable): Layout and readability check

**Notes:**
```
[Write observations here]
```

---

## D. Copy & Content Review

Read every word on every screen.

- [ ] **No placeholder text**: No "Lorem ipsum", no "TODO", no "CHANGEME"
- [ ] **No typos**: Read everything. Out loud if needed.
- [ ] **Consistent terminology**: Same thing called the same name everywhere
- [ ] **Error messages make sense**: Trigger errors on purpose. Are messages helpful?
- [ ] **Empty states**: What does the app show when there's no data? Is it helpful?
- [ ] **Loading states**: Are there loading indicators? Do they appear and disappear correctly?

**Notes:**
```
[Write observations here]
```

---

## E. First Impression Test

Pretend you've never seen this app before.

- [ ] **5-second test**: Look at the landing page for 5 seconds. Can you tell what it does?
- [ ] **Would you use this?**: Honestly — does this feel like a finished product?
- [ ] **Professional quality**: Does it look like someone cared about the details?
- [ ] **Obvious next step**: Is it always clear what the user should do next?
- [ ] **Trust factor**: Would you enter your email/data into this? Why or why not?

**Notes:**
```
[Write observations here]
```

---

## F. Edge Case Exploration

Think about users who aren't you.

- [ ] **New user**: No account, no data, first visit. Is the experience clear?
- [ ] **Power user**: Lots of data, many interactions. Does performance hold?
- [ ] **Accessibility user**: Navigate with keyboard only. Use a screen reader if possible.
- [ ] **Slow connection**: Throttle to 3G in dev tools. Is it usable?
- [ ] **Wrong browser**: Try a browser you don't normally test in.

**Notes:**
```
[Write observations here]
```

---

## Sign-Off

| Tester | Verdict | Date | Signature |
|--------|---------|------|-----------|
| {{TESTER_NAME}} | PASS / FAIL / CONDITIONAL | {{DATE}} | _________ |

**If FAIL:** List every issue below with the tier it should route back to:

| Issue | Severity | Route to Tier | Notes |
|-------|----------|--------------|-------|
| | | | |

---

**Paladin Tier 6 complete. The wall has been walked.**
