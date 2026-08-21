---
description: Coordinate parallel work across several targets — feature envs, repos, the workspace branch — by fanning conversational instructions out to teammate agents pinned to each. Use to drive multi-target work from one conversation.
argument-hint: "[initial instruction(s), optionally naming a work target]"
allowed-tools:
  - Bash
  - Read
  - Glob
  - Grep
  - Agent
  - TeamCreate
  - TeamDelete
  - TaskCreate
  - TaskUpdate
  - TaskList
  - TaskGet
  - SendMessage
  - TaskStop
  - AskUserQuestion
---

# Iceberg

Bind `$ARGUMENTS` together with the human caller's opening conversation input to the **opening instruction stream**
input. Bind any named or implied environment, repository, workspace branch, or path to its instruction's **work-target
hint**; leave ambiguous targets unresolved for the process to ask about.

Read `winter-workflow:/methodology/build/iceberg/process.md` and execute every step exactly as written, continuing to
accept subsequent conversation input as the **ongoing instruction stream** until the human caller ends the operation.
The linked process is authoritative; do not paraphrase, skip, or reorder its steps.
