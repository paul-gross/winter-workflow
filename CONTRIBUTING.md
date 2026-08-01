# Contributing

## Commit messages

This repo follows the default conventions in [`context/default-commit-conventions.md`](./context/default-commit-conventions.md) — Conventional Commits with a scope. Scope here is the repo name or subsystem (e.g. `winter-workflow`, `agents`, `skills`). The `commit` skill (shipped by this repo) generates commits in this format.

## Pre-push checks

Run before pushing to `master`:

- `winter lint winter-workflow` — runs this module's contributed checks. The agent-frontmatter check (`scripts/lint-agents.py`, wired via the `lint` field in `winter-ext.toml`) validates that every `agents/*.md` declares a non-empty `description`, a `tools` grant (non-empty list or the literal `*`), and a `model` of `haiku`, `sonnet`, or `opus`, failing with the file and offending key. The lint ships only through `winter lint` — there is no standalone task runner.
- `python3 tests/test_lint_agents.py` — exercises the check against the broken fixtures under `tests/fixtures/` (stdlib only, no dependencies).

## Delivery

- Default branch: `master`
- **Primary contributors** push directly to `master` whenever — no PR or review required. Allowed to rewrite history.
- **Outside contributors** are welcome — open a PR against `master` and I'll review and merge.
