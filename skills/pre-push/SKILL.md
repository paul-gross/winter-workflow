---
description: Use before pushing completed work to surface review findings over the un-pushed range. Fans out code-reviewer plus, conditionally on the project's surfaces, harness-reviewer, context-reviewer, and documentation-reviewer in parallel against origin/master..HEAD, then synthesizes a single advisory summary. Run before `git push` or `/ws-push`.
model: opus
argument-hint: "[blocking]"
allowed-tools: Bash, Read, Agent, AskUserQuestion
---

Read the sibling [pre-push-review.md](./pre-push-review.md) and execute the workflow it describes. Treat the doc as authoritative — every step, every reviewer prompt, every decision lives there. Pass `$ARGUMENTS` through unchanged.
