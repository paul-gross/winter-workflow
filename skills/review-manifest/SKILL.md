---
description: Use when the user says "build/generate a review manifest" or wants help reviewing a large diff — produces a reading guide for a human reviewer by classifying every hunk as mechanical, pattern, or novel and rendering a review order (novel first in full, pattern collapsed, mechanical as a one-line list) so the human's attention lands on the decisions. Advisory; gates nothing. Generate it to guide your own review of a big or rename-heavy diff, or before the cold-review/pre-push skill to also focus an agent review.
argument-hint: "[uncommitted | <ref|range>]"
allowed-tools: Bash, Read, Agent, Write
---

# Review Manifest

Generate a **review manifest** over the change-set — a reading guide that tells **a human reviewing this diff** where to spend attention. A fresh-context classifier walks the diff hunk-by-hunk and tiers every hunk (`mechanical` / `pattern` / `novel`), an adversarial auditor attacks the cheap tiers, and the result renders as a **review order** the human reads — `novel` first and in full, `pattern` collapsed behind their claims, `mechanical` as a one-line list. A JSON sidecar is written under `~/.claude/winter/review-manifests/`. The output is advisory; it reorders the reviewer's attention and gates nothing.

Read `winter-workflow:/ai/review-manifest/pipeline.md` and execute every step against the scope in `$ARGUMENTS` (default: branch-vs-base; also `uncommitted` or a git `<ref|range>` — the engine scope vocabulary). The pipeline doc is the source of truth: it discovers the change-set, spawns the k-voted [`diff-classifier`](../../agents/diff-classifier.md) fan-out and the [`manifest-auditor`](../../agents/manifest-auditor.md), enforces total coverage and the diff-SHA freshness binding ([`../../ai/review-manifest/format.md`](../../ai/review-manifest/format.md)), and renders the review order. Do not paraphrase or shortcut its steps. Pass `$ARGUMENTS` through unchanged.
