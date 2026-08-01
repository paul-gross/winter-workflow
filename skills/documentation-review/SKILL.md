---
description: Fresh-context review of external-facing public documentation — docs site, guides, the user-facing README — against the code it describes, by a documentation-reviewer subagent. Use when asked to review the docs.
argument-hint: "[inline] [uncommitted | <ref|range> | <paths> | <PR|MR>]"
allowed-tools: Bash, Read, Agent
---

The procedure for this skill is at `winter-workflow:/methodology/review/process.md`.

## Execute

Translate `$ARGUMENTS` into `{axis, scope, execution_mode}` before reading the procedure: bind `axis: documentation`; a leading `inline` binds `execution_mode: inline` and is removed, otherwise bind `fresh`; discard an optional leading filler `against` or `vs` from the remainder; map an empty remainder to `branch-vs-base`, literal `uncommitted` to that scope, existing paths to `{paths: [<values>]}`, a forge PR/MR locator to `{remote: <locator>, feedback: default}`, and a verified git ref or range to `{range: <value>}`. Reject any other remainder. Read `winter-workflow:/methodology/review/process.md` and execute every step with those semantic inputs.
