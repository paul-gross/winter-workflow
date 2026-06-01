---
description: Use before pushing completed work to surface review findings over the un-pushed change-set — every repo in the feature env ahead of its upstream, reviewed together. Fans out code-reviewer plus, conditionally on the in-scope repos' surfaces, harness-reviewer, context-reviewer, and documentation-reviewer in parallel (one per axis, spanning all in-scope repos over origin/master..HEAD), then synthesizes a single advisory summary with a cross-repo consistency pass. Run before `git push` or `/ws-push`.
argument-hint: "[blocking]"
allowed-tools: Bash, Read, Agent, AskUserQuestion
---

Read the sibling [pre-push-review.md](./pre-push-review.md) and execute the workflow it describes. Treat the doc as authoritative — every step, every reviewer prompt, every decision lives there. Pass `$ARGUMENTS` through unchanged.
