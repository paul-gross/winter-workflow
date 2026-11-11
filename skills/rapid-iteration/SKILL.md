---
description: Coordinate interactive rapid iteration with a durable request queue and fast visible feedback. Use when the caller explicitly wants an ongoing build mode that defers tests, lint, and review gates.
argument-hint: "[initial requests, target, optional ledger path and preview URL]"
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, Agent, SendMessage, TaskStop, AskUserQuestion
---

# Rapid iteration

Bind `$ARGUMENTS` together with the human caller's conversation input to the **request stream**. Bind any named worktree,
ledger path, preview URL, and external worker ownership to the corresponding process inputs; leave ambiguous targets
unresolved.

## Execute

Read `winter-workflow:/methodology/build/rapid-iteration/process.md` and execute every step, accepting subsequent
conversation input until the caller pauses, stops, or explicitly switches modes. The linked process is authoritative.
