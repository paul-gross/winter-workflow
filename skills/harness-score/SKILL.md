---
description: "Score a codebase against the harness model maturity matrix. Produces an HTML report (YYYY-MM-DD-<project>.html) plus a JSON sidecar in the winter space's scores directory, with per-dimension stages (1-5), evidence citations, and (if prior reports exist) a delta section comparing against the most recent score. Use weekly to track progress or divergence."
allowed-tools: Bash, Read, Glob, Grep, Write, Agent
---

# Harness Score

`harness-score` is the user-invocable entry point for the **codebase-scoped** maturity scoring procedure documented at `winter-workflow:/context/harness-score/process.md`. The procedure lives in `context/` so other agents (e.g., a `blizzard` snowflake doing a multi-step initiative) can `Read` and execute it as a substep without going through this slash command.

## Execute

Read `winter-workflow:/context/harness-score/process.md` and execute every step against the current working directory. The skill takes no arguments — the only target is `$PWD`.

In short, the linked process: loads the frozen rubric at `winter-workflow:/context/harness-score/rubric.md`, spawns an `explorer` to gather evidence, applies the rubric, and writes an HTML report plus JSON sidecar into the winter space's `scores` directory (`winter space scores`; see `winter-workflow:/context/winter-space.md`). If a prior report at the same rubric version exists for the same project, a deltas section is included.

Do not paraphrase or shortcut the steps from this file. The process doc is the source of truth.
