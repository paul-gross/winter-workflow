---
description: Fresh-context review of an implementation plan before building — the verifiability gate, the architecture gate, and planning-spec conformance — by a plan-reviewer subagent. Use when asked to review or gate a plan. Runs against a refined work item's plan directory, plan files, or a plan stated in the conversation.
argument-hint: "[inline] [<plan-dir-or-file>...]"
allowed-tools: Bash, Read, Write, Agent
---

The procedure for this skill is at `winter-workflow:/methodology/review/process.md`.

## Execute

Translate `$ARGUMENTS` into `{axis, scope, execution_mode}` before reading the procedure: bind `axis: plan`; a leading `inline` binds `execution_mode: inline` and is removed, otherwise bind `fresh` — the token selects only the execution mode, never where the plan comes from; discard an optional leading filler `against` or `vs` from the remainder; map existing paths — a plan directory or plan files — to `{paths: [<values>]}`. When the remainder is empty and the conversation supplies the plan itself, resolve `<workflows-dir>` through the artifact-directory runtime operation per `winter-workflow:/methodology/artifact-storage.md`, write the plan verbatim to `<workflows-dir>/<yyyy-mm-dd>-<name>/00-plan.md` (short kebab-case `<name>` from the plan), and bind `{paths: [<that-file>]}`; when no plan is available either way, ask the caller which plan to review rather than guessing. Reject any other remainder.

Also bind the axis's required work-target path(s) — the repository or repositories the plan is judged against — from the arguments, the conversation, or the plan's work-item context; ask the caller when they are not determinable. Read `winter-workflow:/methodology/review/process.md` and execute every step with those semantic inputs.
