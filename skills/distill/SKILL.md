---
description: Rewrite existing markdown — agent-facing or human-facing — into its smallest form that keeps every load-bearing fact. Use when asked to condense, distill, or de-bloat docs that already exist.
argument-hint: "[file | paths | directory | glob]"
allowed-tools: Bash, Read, Glob, Grep, Agent, AskUserQuestion
---

# Distill

Bind `$ARGUMENTS`, or the human caller's most recent concrete conversation request when it is empty, to the **target
set** input.

Read `winter-workflow:/methodology/distill/process.md` and execute every step exactly as written. The linked process is
authoritative; do not paraphrase, skip, or reorder its steps.
