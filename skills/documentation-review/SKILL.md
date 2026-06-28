---
description: Fresh-context review of external-facing public documentation — docs site, guides, the user-facing README — against the code it describes, by a documentation-reviewer subagent. Use when asked to review the docs.
argument-hint: "[inline] [uncommitted | <ref|range> | <paths>]"
allowed-tools: Bash, Read, Agent
---

# Documentation Review

Run a **cold** documentation review — a fresh-context `documentation-reviewer` subagent evaluates the change-set with zero prior conversation history. Its axis is external-facing **public** documentation — the docs a human adopter or end-user reads. It does **not** review agent-facing markdown (`CLAUDE.md`, `.claude/`, `agents/`, `skills/`, `context/` — that's `context-reviewer`), harness markdown, or code. Run it when a change may have left a user-facing doc stale, wrong, or missing.

The mechanics — scope vocabulary, change-set discovery across the feature env, execution mode, model choice, the reviewer prompt scaffold, and how to relay findings — are the single source in `winter-workflow:/context/review.md`. Read that engine doc and run the **documentation** axis over the scope described by `$ARGUMENTS` (default: branch-vs-base; also `uncommitted`, a git `<ref|range>`, or a `<paths>` set). The engine is authoritative: pass `$ARGUMENTS` through unchanged, run it in the mode the engine selects — a cold subagent by default, or in-context when `$ARGUMENTS` leads with `inline` (e.g. `inline main`) — and present the findings as it directs.
