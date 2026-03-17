---
name: commit
description: Generates a Conventional Commits-style commit message from staged and/or unstaged git changes, without running git commit. Use this skill whenever the user wants a commit message, asks to "prepare a commit", says "what should I commit?", types /commit, or asks for help writing a git commit message based on their current changes.
argument-hint: [optional context...]
allowed-tools: Bash(git diff:*), Bash(git diff --cached:*)
---

# Prepare a Conventional Commit Message

Read the staged and unstaged changes below, then output a single commit message following the [Conventional Commits](https://www.conventionalcommits.org/) specification.

## Rules

- Output **only** the commit message itself — no preamble, no explanation, no markdown fences.
- Do **not** run `git commit`, `git add`, or any other git write command. This skill is read-only.
- Follow the format: `<type>(<optional scope>): <short summary>` with an optional body separated by a blank line.
- Choose the type that best describes the primary change: `feat`, `fix`, `refactor`, `chore`, `docs`, `style`, `perf`, `test`, `build`, `ci`.
- **Focus on the essence.** Describe the core change (the fix, feature, or refactor). If tests or linting were also added, do not call them out — they are expected, not noteworthy.
- **Frontend changes:** if the diff touches UI components, briefly note the visual or UX difference (e.g., "button was red, now blue" or "modal now shows inline error instead of alert").
- Do **not** include "Generated with Claude Code", "Co-Authored-By", or test-run counts (e.g., "All 2594 tests passing").
- **Summary line must be 72 characters or fewer** — count carefully before outputting. If your first draft is too long, shorten it: drop filler words, use a shorter synonym, or omit the scope. Move extra detail to the body. Add a body only when extra context genuinely helps readers understand *why* the change was made.

## Staged Changes

```
!git diff --cached
```

## Unstaged Changes

```
!git diff
```

## Optional User Context

$ARGUMENTS
