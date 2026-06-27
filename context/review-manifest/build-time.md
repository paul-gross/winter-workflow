# Review manifest — build-time intent capture

The **build-time producer**: instead of cold-classifying a finished diff after the fact ([`./pipeline.md`](./pipeline.md)), the agent *writing* the change records each hunk's tier, claim, and **intent as it builds** — so the manifest carries the author's real reasons, not a reconstruction. Use this when an agentic build skill (`glacier` per phase, a `blizzard` developer) is producing the change and a review manifest is wanted; reach for cold classification instead when reviewing a change you did not author or one built without a manifest.

This doc covers only what is *different* about authoring the entries. Everything downstream — the JSON facts shape, the markdown render, the two invariants, the metrics, and the adversarial audit — is shared with the cold flow and lives in [`./format.md`](./format.md) and [`./pipeline.md`](./pipeline.md). Read those for the tail; read this for the head.

## Why intent capture is worth it

A cold classifier is independent but blind: it reconstructs *what a hunk looks like* and can only guess *why*. The author knows. "Extracted the shared scope vocabulary into `patterns.md` so fetch/pull/push stop drifting" is an intent a cold reader cannot recover from the diff — and it is exactly what tells a human reviewer whether the extraction was the right call. Capturing it while building is higher-fidelity and free of a second classification pass.

The cost is that the author is **not independent** — left unchecked, an author marks their own work cheap ("just a rename") and buries decisions. So intent capture does **not** replace the adversarial audit; it feeds it. The author records high-recall claims; the [`manifest-auditor`](../../agents/manifest-auditor.md) then distrusts every cheap-tier one before it reaches the human. Author records, skeptic verifies — the fail-closed guarantee is unchanged.

## Accumulate as you build

As you write the change — per phase, per logical edit, however the build skill is structured — record an entry for each hunk you author. Append to the JSON facts file at `~/.claude/winter/review-manifests/<YYYY-MM-DD>-<slug>.json` (the [`./format.md`](./format.md) schema), each entry with:

- `source: "authored"` — this came from the builder, not a cold classifier.
- `tier` — your **honest** self-classification over the closed vocabulary (the [`diff-classifier`](../../agents/diff-classifier.md) body defines the tiers; apply the same bar to yourself). When a hunk is a real decision, mark it `novel` — that is not a failure, it is the manifest doing its job. **When in doubt, `novel`.**
- `claim` — the one-line assertion the tier rests on, same as the cold flow.
- `intent` — *why* you made the change, in your own words. This is the field cold classification cannot fill; it is the whole point of building the manifest this way.
- `exemplar` — for `pattern`, the named file the hunk conforms to.

Record against the **hunk identity** in [`./format.md#hunk-identity`](./format.md#hunk-identity), keyed off the post-image start line. Do not try to assign final line numbers mid-build while the file is still moving — record against the file and a stable anchor (the symbol or heading you changed), and let the **close** step below bind entries to the canonical hunk ids of the settled diff.

**Honesty discipline.** You are classifying your own work, so the failure mode is self-flattery: calling a decision `mechanical` because you are confident it is fine. The audit is built to catch exactly that, and every hit it scores against your entries increments `misclassification_count` — which, for an authored manifest, is a direct measure of *your* calibration. Mark honestly and the metric stays clean; mark cheap to look tidy and the skeptic exposes it.

## Close the manifest (audit + render)

When the change is settled (the feature is built, the phase is done — whenever the manifest is wanted for review), **close** it. This is the shared tail of [`./pipeline.md`](./pipeline.md), entered with the facts already populated instead of produced by the classifier:

1. **Settle the diff and bind ids.** Compute `diff_sha` and enumerate the canonical hunk-id set from the final change-set ([`./pipeline.md`](./pipeline.md) step 1). Bind each authored entry to its final `hunk_id`.
2. **Enforce total coverage.** Any final hunk with **no authored entry** is inserted as `novel` ([`./pipeline.md`](./pipeline.md) step 4, [`./format.md#invariant-1--total-coverage`](./format.md#invariant-1--total-coverage)). Forgetting to record a hunk fails closed toward human review, never away from it — the same backstop the cold flow relies on.
3. **Audit the cheap tiers.** Run the [`manifest-auditor`](../../agents/manifest-auditor.md) over the `authored` `mechanical` and `pattern` hunks exactly as in [`./pipeline.md`](./pipeline.md) step 3. The auditor is cold and adversarial; it does not get your intent as a free pass. Hits promote to `novel` and increment `misclassification_count`.
4. **Render and report.** Write the JSON facts and render the markdown review document ([`./pipeline.md`](./pipeline.md) steps 5–7). The render is identical, except `authored` entries carry richer claims — fold the captured `intent` into each `novel` entry's description so the human reads *why*, not just *what*.

## What's the same, what's different

| | Cold classification ([`pipeline.md`](./pipeline.md)) | Build-time intent capture (this doc) |
|---|---|---|
| Who sets the tier | a k-vote of fresh-context `diff-classifier`s | the building agent, as it writes |
| Sees the task / intent | no — coldness is the point | yes — intent is the point |
| `source` / `intent` fields | `classified` / `null` | `authored` / the author's reason |
| Reconciliation | k votes, any split → `novel` | single producer; no vote to reconcile |
| Adversarial audit | runs over cheap tiers | **runs over cheap tiers — unchanged** |
| Coverage + freshness invariants | enforced at close | **enforced at close — unchanged** |
| `misclassification_count` measures | classifier error caught by audit | **author self-flattery caught by audit** |

The producers are **mutually exclusive per hunk** — a hunk is either author-recorded or cold-classified, never both. A change built with this flow is closed with the author's entries; a change reviewed cold is classified from scratch. Either way the manifest a human opens is the same document, and the skeptic checked the cheap tiers before they got there.
