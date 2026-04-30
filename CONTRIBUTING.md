# Contributing

## Commit messages

Conventional Commits with a scope:

    <type>(<scope>): <description>

    [optional body]

- Types: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `perf`, `style`, `ai`
- Scope: repo name or subsystem (e.g. `winter-workflow`, `agents`, `skills`)
- The `/wf-commit` skill (shipped by this repo) generates commits in this format

## Pre-commit checks

None. No linters, formatters, or tests are wired in.

## Delivery

- Default branch: `master`
- **Primary contributors** push directly to `master` whenever — no PR or review required. Allowed to rewrite history.
- **Outside contributors** are welcome — open a PR against `master` and I'll review and merge.
