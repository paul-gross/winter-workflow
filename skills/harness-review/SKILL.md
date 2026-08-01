---
description: Fresh-context review of the agentic harness against a change — agent context, verifier tooling, agent docs, recent agent mistakes — by a harness-reviewer subagent. Use when asked to review the harness.
argument-hint: "[inline] [uncommitted | <ref|range> | <paths>]"
allowed-tools: Bash, Read, Agent
---

# Harness Review

Run a **fresh** harness review — a fresh-context `harness-reviewer` subagent evaluates the change-set with zero prior conversation history. Where `cold-review` asks "is the code architecturally sound?", this axis asks "does the harness keep pace with the change, and is the application shaped so agents can develop it productively?" — the application↔harness seam. Run both for full coverage.

The mechanics — scope vocabulary, change-set discovery across the feature env, execution mode, model choice, the reviewer prompt scaffold (including the transcript-mining context this axis needs), and how to relay findings — are the single source in `winter-workflow:/context/review.md`. Read that engine doc and run the **harness** axis over the scope described by `$ARGUMENTS` (default: branch-vs-base; also `uncommitted`, a git `<ref|range>`, or a `<paths>` set). The engine is authoritative: pass `$ARGUMENTS` through unchanged, run it in the mode the engine selects — a fresh subagent by default, or in-context when `$ARGUMENTS` leads with `inline` (e.g. `inline main`) — and present the findings as it directs.
