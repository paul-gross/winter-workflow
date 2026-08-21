---
description: Produce a reading guide for a large diff — every hunk classified by how it is verified, ordered so attention lands on the decisions. Use when asked for a review manifest or a reading order for a big or rename-heavy diff.
argument-hint: "[uncommitted | <ref|range>]"
allowed-tools: Bash, Read, Agent, Write
---

The procedure for this skill is at `winter-workflow:/methodology/review/manifest/process.md`.

## Execute

Translate `$ARGUMENTS` into a semantic diff scope before reading the procedure: map an empty value to `branch-vs-base`,
literal `uncommitted` to that scope, and a verified git ref or range to `{range: <value>}`. Reject any other value. Read
`winter-workflow:/methodology/review/manifest/process.md` and execute every step with that scope.
