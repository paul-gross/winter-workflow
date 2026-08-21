---
description: Audit a codebase's standing agent-context cost — memory files, agent definitions, skill descriptions — against real invocation counts. Use to find unused skills or subagents, or when a session's always-loaded context feels bloated.
argument-hint: "[target path]"
allowed-tools: Bash, Read, AskUserQuestion
disable-model-invocation: true
---

The procedure for this skill is at `winter-workflow:/methodology/optimize-context/process.md`.

## Execute

Bind `$ARGUMENTS`, or `$PWD` when empty, to the **target_path** input. Read
`winter-workflow:/methodology/optimize-context/process.md` and execute every step exactly as written against it. The
linked process is authoritative; do not paraphrase, skip, or reorder its steps.
