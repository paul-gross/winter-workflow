---
description: Fresh-context review of an implementation plan before building, judged against the target application's declared verifiability matrix and architecture guidance plus the plan's own planning specs, by a plan-reviewer subagent. Use when asked to review or gate an implementation plan. Runs against a refined work item's plan directory, plan files, or a plan stated in the conversation.
argument-hint: "[inline] [<plan-dir-or-file>...]"
allowed-tools: Bash, Read, Write, Agent, AskUserQuestion
---

The procedure for this skill is at `winter-workflow:/methodology/review/process.md`.

## Execute

Translate `$ARGUMENTS` into `{axis, scope, execution_mode, work_target}` before reading the procedure: bind
`axis: plan`; a leading `inline` binds `execution_mode: inline` and is removed, otherwise bind `fresh` — the token
selects only the execution mode, never where the plan comes from; discard an optional leading filler `against` or `vs`
from the remainder; map existing paths — a plan directory or plan files — to `{paths: [<values>]}`. When the remainder
is empty and the conversation supplies the plan itself, materialize it per the `plan` axis's Inputs
(`winter-workflow:/methodology/review/axes/plan.md`) and bind `{paths: [<materialized-file>]}`; when no plan is
available either way, ask the caller which plan to review rather than guessing. Reject any other remainder.

Bind `work_target` — the absolute path(s) of the repository or repositories the plan is judged against — from the
conversation or the plan's work-item context; ask the caller when it is not determinable. Read
`winter-workflow:/methodology/review/process.md` and execute every step with those semantic inputs.
