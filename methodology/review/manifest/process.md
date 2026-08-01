# Review manifest — process

Generate a review manifest over a change-set through **classify → audit → render**, emitting a JSON sidecar and a concise review order. Any caller may execute this reusable process as a standalone operation or substep. Runtime operations follow [`../../runtime-ports.md`](../../runtime-ports.md).

The on-disk shape, the two invariants, hunk identity, and metrics are owned by [`format.md`](./format.md); tier semantics and classifier decisions by [`classification.md`](./classification.md); adversarial audit methodology and output by [`audit.md`](./audit.md). This doc owns only the **control flow**.

## What this is for

A manifest partitions every hunk of a diff into verification tiers so full human attention lands only on the hunks that hold actual decisions (`novel`), while a rename-heavy change collapses to a one-line list. **The reader is a human reviewing the change** — the rendered review order is for them; the agents in this pipeline only build it. It is **advisory** — it reorders a reviewer's attention, it gates nothing, and it never replaces the review itself. The same review order can also focus a later independent review.

The spine of the pipeline is a single rule: **every failure path demotes toward human review.** An unclassified hunk, a contested k-vote, and an audit hit all become `novel`. No path moves code away from human eyes on uncertainty.

## Inputs

A normalized **diff** scope from the engine's vocabulary ([`../process.md`](../process.md)): `branch-vs-base`, `uncommitted`, `unpushed`, or `{range: <verified-ref-or-range>}`. For `unpushed`, also carry its normalized `pinned_scope` and any documented `review_bases`. The manifest classifies hunks, so paths and remote scopes do not apply. The classifier is always a fresh-context runtime regardless of how the caller executes this process.

## Process

### 1. Discover the change-set

Follow [`../change-set.md`](../change-set.md) for the env-wide scopes (`branch-vs-base`, `uncommitted`, `unpushed`); for an explicit `<ref|range>` the change-set is that range in the current repo. Pass `pinned_scope` and any documented `review_bases` for `unpushed`. The result is a set of reviewable `(repo, worktree-path, base-ref, review-base-kind)` entries, any delivery blockers, and the per-target `git diff` command (per the engine's scope table). Preserve blockers in the result; a manifest never makes an upstream-less target pushable. For the `uncommitted` scope, the per-target diff includes **untracked, non-ignored files** as whole-file additions — see [`./format.md#computing-diff_sha`](./format.md#computing-diff_sha); a new file an author has not yet `git add`ed is part of the change and must be classified, not silently skipped. Zero hunks and no blockers → report "nothing to classify" and stop; spawn nothing.

**Enumerate the canonical hunk-id set now.** Parse `git diff` for every target and assign each `@@ -a,b +c,d @@` block its id `<repo>/<file>@@<c>` (the post-image start line `c`, per [`./format.md#hunk-identity`](./format.md#hunk-identity)); an untracked whole-file addition is one hunk at `@@1`. This enumerated list is **authoritative** — it is what classifiers classify against (step 2) and what total coverage checks against (step 4). Deriving ids once here, rather than letting each classifier re-derive them, is what makes the k votes reconcilable: independent classifiers otherwise key the same hunk off slightly different line numbers and the votes never line up.

Compute `diff_sha` now, by the recipe in [`./format.md#computing-diff_sha`](./format.md#computing-diff_sha), and resolve each target's `head_sha` / `base_sha`. This is the binding the whole manifest hangs off — capture it before classification so a diff that shifts mid-run is caught by the coverage and staleness checks at render.

### 2. Classify — k-voted, fail closed

Spawn **k = 3** canonical `diff-classifier` roles as one concurrent group of fresh isolated runs. They are independent and concurrency avoids additive wall time. Each executes the canonical [`classification.md`](./classification.md) methodology.

Each run is **fresh and identical**: it carries the diff target (worktree paths, base refs, the `git diff` command) **and the enumerated hunk-id list from step 1**, with the instruction to classify each listed hunk by its given id. **Do not pass the task prompt, the PR description, or this session's design discussion** — the classifier's value is that it never saw why the change was made.

Require each classifier to run without resident peers or a shared assignment queue, avoid seeking the task or design history, return one per-hunk report through the isolated-result channel, perform no follow-on work, and stop. Await all three results before reconciliation.

Use **judgment model intent** (Opus/Sol class) for every classifier because classification is judgment-heavy. Downgrade only for a deliberately trivial scope, and say so.

**Reconcile per canonical hunk-id** once all three report — walk the step-1 enumerated list, gather the three votes for each id:

- All three agree on the tier → that tier. Take the `claim` (and `exemplar`) from the majority; any classifier's claim is fine when they concur.
- **Any disagreement → `novel`**, marked `contested: true`. This is the fail-closed core: a hunk three fresh readers cannot agree is cheap is, by definition, not safe to skim. Do not average, do not take a 2-of-3 majority — *any* split fails closed.
- A canonical id one or more classifiers **failed to vote on** is treated as a disagreement on that id → `novel`, `contested: true`. A hunk missing from *all* three is still backstopped by the coverage check in step 4 (inserted as `novel`). Ignore any id a classifier returns that is not in the enumerated list.

Record each hunk's `lines` (added + removed) from the diff for the metrics.

### 3. Audit — adversarially refute the cheap tiers

Spawn the canonical `manifest-auditor` role in a fresh isolated context over the reconciled manifest's **`mechanical` and `pattern`** hunks (the cheap tiers; `novel` is never audited — it already has the human). It executes [`audit.md`](./audit.md), uses judgment model intent, carries the same one-shot restrictions, and returns one result before this process continues.

Give it the cheap-tier hunk list and a **sampling budget**. Default budget: audit **all** cheap-tier hunks when there are ≤ 20; above that, sample the hardest 20 first (largest hunks, control-flow/default-touching, classifier-flagged-on-the-line) and tell the auditor the rest are out of budget so it lists them rather than implying they were cleared. The auditor reports **hits** (claim refuted), **survives**, and **not audited (budget)**.

Apply the results:

- Each **hit** → set the hunk's `tier` to `novel`, `audit: "promoted"`, `promoted_from: <old tier>`, and **increment `misclassification_count`**.
- Each **survives** → `audit: "survives"` (tier unchanged).
- Cheap-tier hunks not sampled → `audit: "unaudited"`. They keep their classified tier but are **named in the render** as audited-not, so the human knows the audit's coverage was partial.

### 4. Enforce total coverage, then compute metrics

Before rendering, run the coverage check from [`./format.md#invariant-1--total-coverage`](./format.md#invariant-1--total-coverage): parse the diff's hunk-id set, compare to the manifest's, insert any missing hunk as `novel`. If a manifest hunk is **absent** from the current diff, the diff moved under you — recompute `diff_sha`; if it no longer matches step 1's, the change-set is mid-flight: stop and tell the caller to re-run on a settled diff rather than emit a manifest bound to a diff that no longer exists.

Then compute the `metrics` block per [`./format.md#metrics`](./format.md#metrics) — on the **final** (post-audit) tiers.

### 5. Write the JSON facts file

Resolve `<manifests-dir>` once through the artifact-directory runtime operation, following [`../../artifact-storage.md`](../../artifact-storage.md). Stop before writing if resolution fails or is empty. Write the classification facts to `<manifests-dir>/<YYYY-MM-DD>-<slug>.json` per the [`./format.md`](./format.md) schema and naming. `<slug>` is the env name (env-wide scope) or the repo name (single-repo/standalone). This is the data layer — the per-hunk tiers, claims, metrics, and the `diff_sha` binding — that the markdown is rendered from and that a later consumer freshness-checks.

### 6. Render and write the markdown review document

Render the **markdown review document** from the facts and write it next to the JSON, sharing the basename: `<manifests-dir>/<YYYY-MM-DD>-<slug>.md`. This file — not the JSON, and not an inline dump — is the manifest the human reviews.

Build it to the structure and discipline in [`./format.md#the-markdown-review-document`](./format.md#the-markdown-review-document). The essentials, so they are not missed:

- **It is a high-level reading guide, never a diff dump.** Do **not** paste hunk bodies. Describe each decision in plain language and point at the file/hunk; the reviewer opens the real diff in their own tool. A wall of inlined diff is exactly the unreadable artifact the manifest replaces.
- **`novel` carries prose, grouped by theme.** These are the decisions — lead with the highest-stakes group, describe *what changed and why it needs judgment*, and surface promoted/contested hunks first (the audit and the vote flagged them, so they are the highest-signal reads). Cluster many related hunks into one themed entry rather than listing every hunk flat.
- **`pattern` collapses to one line per hunk** behind its claim and exemplar.
- **`mechanical` collapses to a single skip-line for the whole tier** — count plus the files, marked audit-verified; tag any cheap-tier hunk the audit did not sample so partial coverage is never implied-clean.
- The header carries the metrics from step 4; lead with the line percentages — they answer *how much of this change actually needs me?*

Keep it to one or two screens. If a tier is large, cluster harder; the manifest fails the moment it stops being scannable.

### 7. Report

Tell the caller the **`.md` path** (the document they read) with the `.json` noted alongside, and a one-line headline (the tier split). Example:

> Manifest at `<manifests-dir>/2026-06-14-alpha.md` (facts in the `.json` alongside) — 41 hunks, 78% `novel` lines, 1 audit promotion.

Do not re-paste the document into the reply — point at it; it exists so the reply does not have to carry the review. When a caller generated the manifest as a review pre-step, hand the document back to that caller to order its own attention; do not also run the fresh review here.

## Why fresh, why k-voted, why adversarial

- **Fresh** — the classifier never saw the task, so it cannot be told "it's just a rename." It reads the code and judges the claim without author framing.
- **k-voted, fail closed** — three independent reads, and *any* disagreement demotes to `novel`. One classifier's blind spot cannot quietly bury a decision in a cheap tier; it takes unanimity to earn a skim.
- **Adversarial audit** — even a unanimous cheap classification is then attacked by a reader whose only job is to refute it. The `mechanical`/`pattern` tiers are trustworthy precisely because something tried to break them and failed.

Every layer points the same direction: **toward the human, never away.** The manifest can only ever *save* reviewer attention by proving a hunk safe through replay/exemplar/audit — never by assuming it.
