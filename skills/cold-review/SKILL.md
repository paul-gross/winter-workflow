---
description: Independent, fresh-context review of code changes for correctness, architecture, and design quality, by a cold-reviewer subagent with no session history. Use when asked to review a diff, PR, or branch, or to assess code quality.
argument-hint: "[inline] [uncommitted | <ref|range> | <paths>]"
allowed-tools: Bash, Read, Agent
---

# Fresh Review

Run a **fresh** code review — a fresh-context `cold-reviewer` subagent evaluates the change-set with zero prior conversation history.

The mechanics — scope vocabulary, change-set discovery across the feature env, execution mode, model choice, the reviewer prompt scaffold, and how to relay findings — are the single source in `winter-workflow:/context/review.md`. Read that engine doc and run the **code** axis over the scope described by `$ARGUMENTS` (default: branch-vs-base; also `uncommitted`, a git `<ref|range>`, or a `<paths>` set). The engine is authoritative: pass `$ARGUMENTS` through unchanged, run it in the mode the engine selects — a fresh subagent by default, or in-context when `$ARGUMENTS` leads with `inline` (e.g. `inline main`) — and present the findings as it directs.

On a large or mechanical-heavy diff, consider generating a [review manifest](winter-workflow:/context/review-manifest/index.md) first (the `review-manifest` skill) — it tiers every hunk and renders a review order (`novel` first in full, `pattern`/`mechanical` collapsed) that a human reads to focus their own review, and that can also order this fresh review's attention onto the decisions instead of every line equally. Optional and advisory; skip it on a small diff.
