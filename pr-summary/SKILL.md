---
name: pr-summary
description: >
  Summarizes all git changes between a target branch (default: main) and the
  current HEAD, then produces a structured PR/commit summary. Use this skill
  whenever the user asks to summarize their branch changes, wants a PR
  description, says things like "what changed from main", "summarize my
  branch", "diff summary", "changes since main", "changes against develop",
  "PR summary", "what did I change", "write a PR description", or types
  /pr-summary. Even if the user doesn't mention a branch explicitly but asks
  for a summary of their current work or branch, use this skill — it's the
  right tool whenever a concise human-readable summary of branch changes is needed.
argument-hint: [target-branch] [optional context...]
allowed-tools: Bash(git log:*), Bash(git diff:*), Bash(git rev-parse:*)
---

# PR Summary

Produce a clear, structured summary of everything that has changed between a
target branch (`main` unless the user names another) and the current HEAD,
then format it as a ready-to-use PR/commit description.

## Arguments

Arguments passed: `$ARGUMENTS`

Arguments are optional. The first word may be the target branch to compare
against; anything after it is extra context for the summary.

- If the first word resolves to a git ref (`git rev-parse --verify --quiet
  <word>` succeeds), use it as `<base>` and treat the rest as user context.
- Otherwise, treat all the arguments as user context and use the default base.
- If no branch is given in the arguments but the user named one in their
  message (e.g. "what changed since develop"), use that.

**Default base:** `main`. If `main` doesn't exist locally, fall back to
`origin/main`. If a named target branch doesn't exist locally, try
`origin/<branch>` before giving up. If no candidate resolves, say which refs
you tried and stop.

## Steps

1. **Gather the data** — with `<base>` resolved, run:

   **Commits on this branch:**
   ```
   git log <base>..HEAD --oneline --no-decorate
   ```

   **Files changed (stat):**
   ```
   git diff <base>...HEAD --stat
   ```

   **Full diff:**
   ```
   git diff <base>...HEAD
   ```

   The three-dot diff compares against the merge base, so changes that landed
   on `<base>` after the branch was cut don't show up — matching what a PR
   would show. If the branch has no commits ahead of `<base>`, say so clearly
   and stop.

2. **Analyze** — read the commits and diff to understand:
   - The overall theme/purpose of the changes (new feature, bug fix, refactor,
     dependency upgrade, config change, etc.)
   - Which files/areas of the codebase were touched
   - Any notable additions, deletions, or renames

3. **Output the summary** using the template below. Keep it concise but
   complete — enough for a reviewer who hasn't seen the branch to understand
   what changed and why.

## Output Template

```
## PR Title

<one-line title, ≤72 chars, Conventional Commits style: type(scope): summary>

## Summary

<2-4 sentence paragraph describing what the branch does and why>

## Changes

- <bullet point per meaningful change — group related changes onto one bullet>
- ...

## Files Modified

<short list of the most important files changed, with a one-phrase note on
what each one does — skip auto-generated files, lock files, and trivial edits>
```

## Style notes

- The PR title should follow Conventional Commits: `feat`, `fix`, `refactor`,
  `chore`, `docs`, `test`, `build`, `ci`. Include a scope in parentheses when
  it adds clarity (e.g., `feat(auth): ...`).
- Write the Summary paragraph as if explaining to a new team member — assume
  they know the codebase but not the context behind this change.
- Each bullet in "Changes" should describe a *what* and, where non-obvious, a
  *why*. Aim for 3–8 bullets. Avoid restating the PR title.
- For very large diffs (100+ files), focus on the high-signal changes and
  mention that minor/generated files were omitted.
- Do NOT include generic filler like "Various improvements" or "Multiple
  changes made". Be specific.

## Optional User Context

Any arguments left after the target branch (see **Arguments**) are extra
context from the user — use them to shape the summary.
