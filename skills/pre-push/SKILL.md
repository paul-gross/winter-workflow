---
description: Multi-axis review of committed, unpushed work — code, context, and docs — against each selected worktree's upstream. Use before pushing.
argument-hint: "[blocking] [exclude-pinned|include-pinned|only-pinned]"
allowed-tools: Bash, Read, Agent, AskUserQuestion
---

The procedure for this skill is at `winter-workflow:/methodology/delivery/pre-push/process.md`.

## Execute

Translate `$ARGUMENTS` into semantic inputs, independent of token order:

- `blocking` binds `mode: blocking`; omission binds `mode: advisory`.
- `exclude-pinned`, `include-pinned`, or `only-pinned` binds `pinned_scope: exclude|include|only`; omission binds
  `pinned_scope: include`.
- Reject unknown tokens, repeated tokens, or more than one pinned-scope token.

Read `winter-workflow:/methodology/delivery/pre-push/process.md` and execute every step with those inputs. If an
upstream-less target needs an explicit review base, obtain and document it through the human-caller channel; do not
infer one.
