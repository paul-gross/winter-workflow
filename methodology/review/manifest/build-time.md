# Review manifest — build-time intent capture

The **build-time producer**: instead of fresh-classifying a finished diff ([`./process.md`](./process.md)), the agent *writing* the change records each hunk's tier, claim, and **intent** as it builds. Use this when an agentic build skill is producing the change and a manifest is wanted; fresh-classify instead when reviewing a change you did not author or one built without a manifest. Only the authoring of entries differs — the JSON shape, the render, the invariants, the metrics, and the audit are shared with the fresh flow and owned by [`./format.md`](./format.md) and [`./process.md`](./process.md).

The author knows *why* each hunk exists — "extracted the shared scope vocabulary so fetch/pull/push stop drifting" is exactly what tells a reviewer whether the change was the right call, and no fresh reader can recover it from the diff. The cost is that the author is **not independent**: left unchecked, an author marks their own work cheap and buries decisions. So intent capture feeds the adversarial audit rather than replacing it — the author records high-recall claims, and [`audit.md`](./audit.md) distrusts every cheap-tier one before it reaches the human.

## Accumulate as you build

As you write the change — per phase, per logical edit, however the build is structured — resolve and retain `<manifests-dir>` under the consumer policy in [`../../artifact-storage.md`](../../artifact-storage.md), and append an entry per authored hunk to the manifest's JSON facts file there, using the [`./format.md`](./format.md) schema:

- `source: "authored"`.
- `tier` — your **honest** self-classification under [`classification.md`](./classification.md), by the same decision rules as a fresh classifier. Marking a real decision `novel` is the manifest doing its job; **when in doubt, `novel`**.
- `claim` — the one-line assertion the tier rests on.
- `intent` — *why* you made the change, in your own words: the field fresh classification cannot fill.
- `exemplar` — for `pattern`, the named file the hunk conforms to.

Do not assign final line numbers while the files are still moving: record against the file and a stable anchor (the symbol or heading you changed), and let the close step bind entries to the canonical hunk ids ([`./format.md#hunk-identity`](./format.md#hunk-identity)) of the settled diff.

You are classifying your own work, so the failure mode is self-flattery — calling a decision `mechanical` because you are confident it is fine. Every audit hit against your entries increments `misclassification_count`, which for an authored manifest is a direct measure of your calibration.

## Close the manifest (audit + render)

When the change is settled — the feature is built, the phase is done, the manifest is wanted for review — **close** it: the shared tail of [`./process.md`](./process.md), entered with the facts already populated.

1. **Settle the diff and bind ids.** Compute `diff_sha` and enumerate the canonical hunk-id set from the final change-set (process step 1); bind each authored entry to its final `hunk_id`.
2. **Enforce total coverage.** Any final hunk with no authored entry is inserted as `novel` ([`./format.md#invariant-1--total-coverage`](./format.md#invariant-1--total-coverage)) — a forgotten hunk fails closed toward human review.
3. **Audit the cheap tiers.** Run the `manifest-auditor` over the authored `mechanical` and `pattern` hunks exactly as in process step 3; intent is not a free pass, and hits promote to `novel` and increment `misclassification_count`.
4. **Render and report.** Write the facts and render the review document (process steps 5–7), folding each captured `intent` into its `novel` entry's description so the human reads *why*, not just *what*.

The producers are mutually exclusive per hunk — a hunk is either author-recorded or fresh-classified, never both, and the authored path has no k-vote to reconcile. Either way the human opens the same document, and the skeptic checked the cheap tiers before they got there.
