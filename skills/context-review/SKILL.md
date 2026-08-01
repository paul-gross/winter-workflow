---
description: Fresh-context review of agent-facing markdown — agents, skills, commands, CLAUDE.md, context/ docs — against the workspace's authoring conventions, by a context-reviewer subagent. Use when asked to review the agent docs/context. Reviews the change-set by default; also takes uncommitted, a ref/range, or paths.
argument-hint: "[inline] [uncommitted | <ref|range> | <paths>]"
allowed-tools: Bash, Read, Agent
---

# Context Review

Run a **fresh** context review — a fresh-context `context-reviewer` subagent evaluates the change-set with zero prior conversation history. Its axis is agent-facing markdown — agents, skills, commands, `CLAUDE.md` files, and `context/` docs — against the workspace's documented conventions for clarity, single-source-of-truth, and non-duplication. It does **not** review code, the application↔harness seam, or external-facing public documentation.

The mechanics — scope vocabulary, change-set discovery across the feature env, execution mode, model choice, the reviewer prompt scaffold, and how to relay findings — are the single source in `winter-workflow:/context/review.md`. Read that engine doc and run the **context** axis over the scope described by `$ARGUMENTS` (default: branch-vs-base; also `uncommitted`, a git `<ref|range>`, or a `<paths>` set — the path set reviews agent-facing markdown in its current state). The engine is authoritative: pass `$ARGUMENTS` through unchanged, run it in the mode the engine selects — a fresh subagent by default, or in-context when `$ARGUMENTS` leads with `inline` (e.g. `inline main`) — and present the findings as it directs.
