---
description: Review the un-pushed change-set before pushing — every repo in the feature env ahead of its upstream, reviewed together across the code, harness, context, and docs axes, synthesized into one advisory summary. Run before pushing completed work.
argument-hint: "[blocking]"
allowed-tools: Bash, Read, Agent, AskUserQuestion
---

Read [`winter-workflow:/context/pre-push/process.md`](winter-workflow:/context/pre-push/process.md) and execute the workflow it describes. Treat the doc as authoritative — every step, every reviewer prompt, every decision lives there. Pass `$ARGUMENTS` through unchanged.
