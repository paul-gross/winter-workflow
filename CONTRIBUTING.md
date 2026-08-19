# Contributing

## Commit messages

This repo follows the default conventions in
[`methodology/delivery/commit/conventions.md`](./methodology/delivery/commit/conventions.md) — Conventional Commits with
a scope. Scope here is the repo name or subsystem (e.g. `winter-workflow`, `agents`, `skills`). The `commit` skill
(shipped by this repo) generates commits in this format.

## Pre-push checks

Run the [verifiability matrix](./verifiability.md) methods the change class owes before pushing to `master`:

- `winter-workflow:lint` and `winter-workflow:lint-tests` — always.
- `winter-workflow:markdown-style` — always. Every `.md` file here is held to the mechanical style gates, and one of
  them writes its own fix:

  ```bash
  dprint check          # dprint fmt to apply
  rumdl check .         # rumdl check . --fix for the autofixable subset
  ```

- `winter-workflow:manual` — the cold-spawn behavioral eval, for any change `canon:cold-eval` names as owing one (new or
  reshaped rule, routing change, broadened trigger). An owed eval is a checklist item, not a remembered obligation.

## Delivery

- Default branch: `master`
- **Primary contributors** push directly to `master` whenever — no PR or review required. Allowed to rewrite history.
- **Outside contributors** are welcome — open a PR against `master` and I'll review and merge.
