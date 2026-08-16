# Review manifest — process

Generate a review manifest over a change-set through **classify → audit → render**, emitting the JSON facts file and the markdown review document owned by [`format.md`](./format.md). Any caller may execute this reusable process as a standalone operation or a substep; runtime operations follow [`../../runtime-ports.md`](../../runtime-ports.md). This doc owns only the control flow.

A manifest partitions every hunk into verification tiers so full human attention lands only on the hunks that hold actual decisions (`novel`), while a rename-heavy change collapses to a one-line list. The rendered review order is for the **human reviewing the change** — the agents in this pipeline only build it — and it is **advisory**: it reorders attention, gates nothing, and never replaces the review. The pipeline's spine is one rule: **every failure path demotes toward human review.** An unclassified hunk, a contested k-vote, and an audit hit all become `novel`.

## Inputs

A normalized **diff** scope from the review engine's vocabulary ([`../process.md`](../process.md)): `branch-vs-base`, `uncommitted`, `unpushed`, or `{range: <verified-ref-or-range>}`; for `unpushed`, also the normalized `pinned_scope` and any documented `review_bases`. Paths and remote scopes do not apply — the manifest classifies hunks. The classifier is always a fresh-context runtime regardless of how the caller executes this process.

## Process

### 1. Discover the change-set

Follow [`../change-set.md`](../change-set.md) for the env-wide scopes, passing `pinned_scope` and `review_bases` for `unpushed`; an explicit ref or range is the change-set in the current repo. Preserve any delivery blockers in the result — a manifest never makes an upstream-less target pushable. For `uncommitted`, the per-target diff includes untracked, non-ignored files as whole-file additions per [`./format.md#computing-diff_sha`](./format.md#computing-diff_sha) — a new file not yet `git add`ed is classified, not silently skipped. Zero hunks and no blockers → report "nothing to classify" and stop; spawn nothing.

**Enumerate the canonical hunk-id set now.** Parse `git diff` for every target and assign each hunk its `<repo>/<file>@@<c>` id per [`./format.md#hunk-identity`](./format.md#hunk-identity); an untracked whole-file addition is one hunk at `@@1`. This enumerated list is **authoritative**: classifiers classify against it (step 2) and total coverage checks against it (step 4).

Compute `diff_sha` now, by the recipe in [`./format.md#computing-diff_sha`](./format.md#computing-diff_sha), and resolve each target's `head_sha` / `base_sha` — captured before classification so a diff that shifts mid-run is caught by the checks at render.

### 2. Classify — k-voted, fail closed

Spawn **k = 3** canonical `diff-classifier` roles as one concurrent group of fresh isolated runs, each executing [`classification.md`](./classification.md) with judgment model intent (downgrade only for a deliberately trivial scope, and say so). Each run is **fresh and identical**: the diff targets (worktree paths, base refs, the `git diff` command) and the enumerated hunk-id list from step 1, with the instruction to classify each listed hunk by its given id. **Do not pass the task prompt, the PR description, or this session's design discussion** — the classifier's value is that it never saw why the change was made. Await all three results.

**Reconcile per canonical hunk-id** — walk the step-1 list and gather the three votes for each id:

- All three agree → that tier, with the `claim` (and `exemplar`) from any concurring classifier.
- **Any disagreement → `novel`**, marked `contested: true`. Do not average and do not take a 2-of-3 majority: a hunk three fresh readers cannot agree is cheap is, by definition, not safe to skim.
- An id one or more classifiers failed to vote on is a disagreement → `novel`, `contested: true`; an id missed by all three is backstopped by the step-4 coverage insert. Ignore any returned id not on the list.

Record each hunk's `lines` (added + removed) from the diff for the metrics.

### 3. Audit — adversarially refute the cheap tiers

Spawn the canonical `manifest-auditor` role in a fresh isolated context, with judgment model intent, over the reconciled **`mechanical` and `pattern`** hunks (`novel` is never audited — it already has the human). It executes [`audit.md`](./audit.md) and returns one result before this process continues.

Give it the cheap-tier hunk list and a **sampling budget**: audit all cheap-tier hunks when there are ≤ 20; above that, the hardest 20 first (largest hunks, control-flow- or default-touching, classifier-flagged on-the-line), with the rest declared out of budget so the auditor lists them rather than implying they were cleared.

Apply the results:

- **Hit** → `tier: novel`, `audit: "promoted"`, `promoted_from: <old tier>`, increment `misclassification_count`.
- **Survives** → `audit: "survives"`, tier unchanged.
- Not sampled → `audit: "unaudited"` — tier kept, but named in the render so partial audit coverage is never implied clean.

### 4. Enforce total coverage, then compute metrics

Run the coverage check from [`./format.md#invariant-1--total-coverage`](./format.md#invariant-1--total-coverage), inserting any missing hunk as `novel`. A manifest hunk absent from the current diff makes the manifest stale under that invariant — stop and tell the caller to re-run on a settled diff rather than emit a manifest bound to a diff that no longer exists. Then compute the `metrics` block per [`./format.md#metrics`](./format.md#metrics) on the **final**, post-audit tiers.

### 5. Write the JSON facts file

Resolve `<manifests-dir>` once through the artifact-directory runtime operation under the consumer policy in [`../../artifact-storage.md`](../../artifact-storage.md), then write the facts file there per the [`format.md`](./format.md) schema and naming.

### 6. Render and write the markdown review document

Render the markdown review document from the facts — to the structure and discipline owned by [`./format.md#the-markdown-review-document`](./format.md#the-markdown-review-document) — and write it next to the JSON with the same basename. This file, not the JSON and not an inline dump, is the manifest the human reviews.

### 7. Report

Tell the caller the **`.md` path** (noting the `.json` alongside) and a one-line headline: hunk count, tier split, promotions. Point at the document rather than re-pasting it — it exists so the reply does not carry the review. When a caller generated the manifest as a review pre-step, hand the document back to that caller to order its own attention; do not also run the fresh review here.
