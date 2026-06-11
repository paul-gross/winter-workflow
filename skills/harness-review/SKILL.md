---
description: Use when the user says "review the harness" or asks about agent context, verifier tooling, agent docs, or recent agent mistakes — checks whether the agentic harness keeps pace with application change and whether the application is shaped for agent productivity. Cold, one-shot harness-reviewer subagent. Different axis from the cold-review skill (which reviews the code, not the harness).
argument-hint: "[inline] [uncommitted | <ref|range> | <paths>]"
allowed-tools: Bash, Read, Agent
---

# Harness Review

Run a **cold** harness review — a fresh-context `harness-reviewer` subagent evaluates the change-set with zero prior conversation history. Where `cold-review` asks "is the code architecturally sound?", this axis asks "does the harness keep pace with the change, and is the application shaped so agents can develop it productively?" — the application↔harness seam. Run both for full coverage.

The mechanics — scope vocabulary, change-set discovery across the feature env, execution mode, model choice, the reviewer prompt scaffold (including the transcript-mining context this axis needs), and how to relay findings — are the single source in `winter-workflow:/ai/review.md`. Read that engine doc and run the **harness** axis over the scope described by `$ARGUMENTS` (default: branch-vs-base; also `uncommitted`, a git `<ref|range>`, or a `<paths>` set). The engine is authoritative: pass `$ARGUMENTS` through unchanged, run it in the mode the engine selects — a cold subagent by default, or in-context when `$ARGUMENTS` leads with `inline` (e.g. `inline main`) — and present the findings as it directs.
