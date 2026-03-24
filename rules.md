# CodeGlass — Rules File

Rules are added after coding sessions surface them.
Never delete rules — the value is in the accumulation.

---

## Rules

### Rule: Add Error Handling for New Code Paths [auto-proposed]
- **Do this:** Wrap new async/external calls in try/catch or error boundaries
- **Don't do this:** Leave new code paths without error handling
- **Why:** Unhandled errors cause silent failures in production
- **Stack:** Python
- **Source:** git diff HEAD~1 (BrainStormer)
- **Date:** 2026-03-23
- **Confidence:** emerging
- **Hits:** 0
- **Misses:** 0
- **Last fired:** never

### Rule: Document New Environment Variables [auto-proposed]
- **Do this:** Add new env vars to .env.example and document their purpose
- **Don't do this:** Add env var references without documentation
- **Why:** Missing env vars cause confusing startup failures
- **Stack:** Python
- **Source:** git diff HEAD~1 (BrainStormer)
- **Date:** 2026-03-23
- **Confidence:** emerging
- **Hits:** 0
- **Misses:** 0
- **Last fired:** never

### Rule: Review Database Changes for Reversibility [auto-proposed]
- **Do this:** Ensure schema changes have a rollback migration
- **Don't do this:** Make destructive schema changes without rollback plan
- **Why:** Irreversible schema changes can cause data loss
- **Stack:** Python
- **Source:** git diff HEAD~1 (BrainStormer)
- **Date:** 2026-03-23
- **Confidence:** emerging
- **Hits:** 0
- **Misses:** 0
- **Last fired:** never

### Rule: Test New API Endpoints [auto-proposed]
- **Do this:** Write integration tests for new routes before merging
- **Don't do this:** Ship new endpoints without test coverage
- **Why:** Untested endpoints are the #1 source of production incidents
- **Stack:** Python
- **Source:** git diff HEAD~1 (BrainStormer)
- **Date:** 2026-03-24
- **Confidence:** emerging
- **Hits:** 0
- **Misses:** 0
- **Last fired:** never


### Rule: Document All Env Vars
- **Do this:** List every env var in .env.example with descriptions
- **Don't do this:** Add env vars without documentation
- **Why:** New team members can't run the project without documentation
- **Stack:** Universal
- **Source:** template:universal
- **Date:** 2026-03-24
- **Confidence:** high
- **Hits:** 0
- **Misses:** 0
- **Last fired:** never

### Rule: Always Check .gitignore
- **Do this:** Review .gitignore before first commit
- **Don't do this:** Commit and then fix gitignore later
- **Why:** Secrets and build artifacts in git history are permanent
- **Stack:** Universal
- **Source:** template:universal
- **Date:** 2026-03-24
- **Confidence:** high
- **Hits:** 0
- **Misses:** 0
- **Last fired:** never

### Rule: Test Before Ship
- **Do this:** Run full test suite before pushing to main
- **Don't do this:** Push and let CI catch failures
- **Why:** CI failures block the whole team; local runs catch your mistakes
- **Stack:** Universal
- **Source:** template:universal
- **Date:** 2026-03-24
- **Confidence:** high
- **Hits:** 0
- **Misses:** 0
- **Last fired:** never

### Rule: Atomic Commits
- **Do this:** Each commit does one logical thing
- **Don't do this:** Bundle unrelated changes in a single commit
- **Why:** Mixed commits make bisect useless and reverts dangerous
- **Stack:** Universal
- **Source:** template:universal
- **Date:** 2026-03-24
- **Confidence:** high
- **Hits:** 0
- **Misses:** 0
- **Last fired:** never

### Rule: Review Your Own Diff
- **Do this:** Read your own diff before requesting review
- **Don't do this:** Submit PRs without self-review
- **Why:** Self-review catches 50% of issues before bothering teammates
- **Stack:** Universal
- **Source:** template:universal
- **Date:** 2026-03-24
- **Confidence:** high
- **Hits:** 0
- **Misses:** 0
- **Last fired:** never
