---
description: Use when the user says "review the diff/PR/branch" or asks about code correctness, architecture, or design quality — independent fresh-context code review by a code-reviewer subagent with no session history. Cold, one-shot. Different axis from the harness-review skill (which reviews the harness, not the code).
argument-hint: "[inline] [uncommitted | <ref|range> | <paths>]"
allowed-tools: Bash, Read, Agent
---

# Cold Review

Run a **cold** code review — a fresh-context `code-reviewer` subagent evaluates the change-set with zero prior conversation history.

The mechanics — scope vocabulary, change-set discovery across the feature env, execution mode, model choice, the reviewer prompt scaffold, and how to relay findings — are the single source in `winter-workflow:/ai/review.md`. Read that engine doc and run the **code** axis over the scope described by `$ARGUMENTS` (default: branch-vs-base; also `uncommitted`, a git `<ref|range>`, or a `<paths>` set). The engine is authoritative: pass `$ARGUMENTS` through unchanged, run it in the mode the engine selects — a cold subagent by default, or in-context when `$ARGUMENTS` leads with `inline` (e.g. `inline main`) — and present the findings as it directs.
