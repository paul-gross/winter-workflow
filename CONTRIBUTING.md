# Contributing

## Commit messages

This repo follows the default conventions in [`methodology/delivery/commit/conventions.md`](./methodology/delivery/commit/conventions.md) — Conventional Commits with a scope. Scope here is the repo name or subsystem (e.g. `winter-workflow`, `agents`, `skills`). The `commit` skill (shipped by this repo) generates commits in this format.

## Pre-push checks

Run before pushing to `master`:

- `winter lint winter-workflow` — runs this module's contributed checks. The agent-frontmatter check (`scripts/lint-agents.py`) validates required agent metadata. The methodology-boundary check (`scripts/lint-methodology.py`) rejects `$ARGUMENTS` and Markdown links, `@` imports, inline-code paths, or canonical references from `methodology/` back to top-level `skills/` or `agents/`. Fenced code and lines marked `<!-- winter-lint:example -->` are treated as illustrative examples. Both checks are wired through the `lint` field in `winter-ext.toml` and emit findings through `winter lint`.
- `python3 tests/test_lint_agents.py` and `python3 tests/test_lint_methodology.py` — exercise both checks with stdlib-only fixtures or temporary repositories.

## Delivery

- Default branch: `master`
- **Primary contributors** push directly to `master` whenever — no PR or review required. Allowed to rewrite history.
- **Outside contributors** are welcome — open a PR against `master` and I'll review and merge.
