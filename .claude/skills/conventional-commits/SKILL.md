---
name: conventional-commits
description: "Alvarez & Marsal commit convention — Conventional Commits in English, imperative, small and frequent. Use this whenever committing in any team project."
---

# Conventional Commits (A&M standard)

Commit rules applicable to **any project** the team works on. Specific projects (e.g., Cortex) may have additional rules — read the local `CLAUDE.md`/`AGENTS.md` if one exists.

---

## Structure

```
<type>(<optional scope>): <short imperative description in English>

<optional body — why, context, links>

<optional footer — breaking changes, issue refs>
```

Examples:

```
feat(auth): add password reset flow

Sends a 1-hour token via email and lets the user pick a new password
from a dedicated page.
```

```
fix(api): reject empty slug on plugin upload
```

```
refactor(frontend): extract SelectDropdown shared component
```

---

## Types

| Type | When |
|------|------|
| `feat` | New user-facing feature |
| `fix` | Bug fix |
| `docs` | Docs only |
| `refactor` | Reorganization without behavior change |
| `chore` | Config, dependencies, .gitignore |
| `test` | Tests (new or adjusted) |
| `ci` | Pipeline/workflow |
| `style` | Formatting, lint (no logic) |
| `perf` | Performance improvement |
| `build` | Build system (Dockerfile, webpack, vite, etc) |

Avoid `misc`, `update`, `stuff`, `wip`.

---

## 5 key rules

1. **English, imperative mood**
   - OK: `Add user search`, `Fix race condition in sync`
   - NOT: `Added user search`, `Arrumando bug`

2. **Short title** — aim for 50 chars, max 72. If you need more, use the body.

3. **Small and focused** — 1 commit = 1 logical change. If the diff mixes subjects, split.

4. **No Co-Authored-By for Claude**
   - Team-wide preference — never add this footer

5. **No `--no-verify`** — if the hook failed, investigate the cause

---

## When to use a scope

Use `(scope)` when the project has well-separated areas. Examples:
- `feat(backend): ...`
- `fix(ui): ...`
- `refactor(auth): ...`

Do not invent one-off scopes — match the ones the project already uses. If there's no pattern, omit.

---

## Breaking changes

Add `!` before the colon and/or a `BREAKING CHANGE:` note in the footer:

```
feat(api)!: rename /users to /accounts

BREAKING CHANGE: All clients must update their endpoint path.
Old /users redirects are removed.
```

---

## Recommended flow

1. `git status` + `git diff` — understand staged vs unstaged
2. Split into logical commits (`git add -p` is useful to split hunks)
3. Pick type + scope
4. Write a short imperative title
5. If the change is not obvious, write 1-3 body lines explaining the **why**
6. Use HEREDOC to preserve formatting:
   ```bash
   git commit -m "$(cat <<'EOF'
   feat(module): title

   Body explaining why.
   EOF
   )"
   ```

---

## Antipatterns (do not do)

- `update stuff` — says nothing
- `WIP` — use stash or a branch instead
- Giant commit with several unrelated subjects
- Message in Portuguese or past tense
- `git add -A` / `git add .` — can include `.env`, caches, binaries
- Amending a commit already pushed to a shared branch

---

## References

- Conventional Commits: https://www.conventionalcommits.org/
- Git book (recording changes): https://git-scm.com/book/en/v2/Git-Basics-Recording-Changes-to-the-Repository
