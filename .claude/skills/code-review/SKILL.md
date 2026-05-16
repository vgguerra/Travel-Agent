---
name: code-review
description: "Team code review checklist and standard. Use this when reviewing a colleague's PR or self-reviewing before opening a PR."
---

# Code Review — A&M standard

Checklist applicable to any PR. Goal: catch real problems before production without turning review into style theater.

---

## Priority order (most important first)

1. **Correctness** — Does the code do what it says? Any bug?
2. **Security** — Any risk of SQL injection, XSS, data leak, wrong permission?
3. **Performance** — Any query in a loop, N+1, expensive operation in a hot path?
4. **Readability** — Will a colleague understand this code in 6 months?
5. **Tests** — Does a critical change have a test? Do existing tests still hold?
6. **Consistency** — Does it follow project standards (AGENTS.md, local skills)?
7. **Style** — Only if documented; linter handles the rest.

Focusing heavily on 5-7 before 1-4 is a bad review smell.

---

## Questions by category

### Correctness
- Does the code actually fix the bug / implement the feature described in the PR?
- Are the most obvious edge cases handled? (empty list, null input, unauthenticated user)
- Any behavior that only changes in production (race condition, ordering)?

### Security
- Do user inputs reach SQL/HTML without escaping?
- Does a new endpoint have the correct auth/role guard?
- Are secrets (tokens, passwords) in env vars, not hardcoded?
- Do logs/errors avoid leaking sensitive data?
- Are CORS, CSP, rate limits affected?

### Performance
- Any `SELECT *` on a large table?
- Loop calling an internal endpoint N times (N+1)?
- `await` in series when `Promise.all` would do?
- Did the frontend bundle blow up because of an unnecessary lib?

### Readability
- Do variable and function names explain the purpose without a comment?
- Do functions have 1 clear responsibility?
- Does complex logic have a comment explaining the **why** (not the **what**)?
- Does the file have reasonable size, or has it become a "god file"?

### Tests
- Does a behavior change have a test that would fail if the logic were removed?
- Does the test use fixtures/mocks consistent with the rest of the project?
- No flaky tests (time-dependent, order-dependent, network-dependent)?

### Consistency
- Does it follow standards documented in `CLAUDE.md` / `AGENTS.md` / project skills?
- Does it use the primitives the project already defined (e.g., `apiFetch` instead of raw `fetch`)?
- No new library introduced when there's already a similar one in the project?

---

## Leaving comments

Use these prefixes to make severity clear:

| Prefix | Meaning |
|--------|---------|
| `nit:` | Detail, optional, can ignore |
| `suggestion:` | Improvement that may or may not be accepted |
| `question:` | Needs clarification before approval |
| `issue:` | Real problem — must change before merge |
| `blocker:` | Cannot merge as-is |

Examples:
```
nit: could use an f-string here
suggestion: extracting this logic into a helper reduces duplication
issue: this endpoint is missing an auth check — any user can hit it
blocker: credentials hardcoded in the code, must move to an env var before merge
```

---

## Self-review before asking a colleague

Before marking the PR as "ready for review":

- [ ] I read my own diff from top to bottom
- [ ] I ran tests locally (`pytest` / `npm test` / `tsc --noEmit`)
- [ ] I ran the feature in practice (not just reading code)
- [ ] PR description explains **what** changes and **why**
- [ ] Screenshots/GIFs if there was a visual change
- [ ] Test checklist if the feature has a complex flow
- [ ] CI is green

---

## Approving or requesting changes

- **Approve** — if the code is correct, secure, readable, and tested. Standalone `nit:` comments should not block approval.
- **Comment** — to leave feedback without approving or blocking. Use when you have open questions.
- **Request changes** — when there are `issue:` or `blocker:` items to resolve. Objectively explain what needs to change.

---

## Receiving feedback

- Every comment deserves a reply, even if it's "yes, will change" or "I disagree because X"
- Only resolve threads once you applied the change or reached consensus
- If you disagree, argue with data — not just "I prefer it this way"

---

## Reviewer antipatterns

- Asking for a full rewrite instead of targeted suggestions
- Only commenting on style/tabs/semicolons (the linter should catch those)
- "I wouldn't do it this way" with no reasoning
- Rubber-stamp approve without reading

## Author antipatterns

- Giant 2000+ line PR mixing 5 features
- Merge commit from main in the middle of the PR
- "I'll fix it in the next PR" for security/correctness comments
- Ignoring a red CI

---

## References

- Conventional Commits (used on commits inside the PR): [../conventional-commits](../conventional-commits/SKILL.md)
- Google eng-practices: https://google.github.io/eng-practices/review/
