# Review manifest — pipeline

The process that generates a review manifest over a change-set: **classify → audit → render**, emitting a JSON sidecar and an inline review order. Designed to be executed by any agent — reached via the [`review-manifest`](../../skills/review-manifest/SKILL.md) skill, or invoked directly by another agent (an `iceberg` foreman, the `cold-review` or `pre-push` skill) that wants a tiered review order as a substep.

The on-disk shape, the closed tier vocabulary, the two invariants, hunk identity, and the metrics are owned by [`./format.md`](./format.md); the tier *semantics* by the [`diff-classifier`](../../agents/diff-classifier.md) and [`manifest-auditor`](../../agents/manifest-auditor.md) agents. This doc is the **control flow** — it does not restate any of those.

## What this is for

A manifest partitions every hunk of a diff into verification tiers so full human attention lands only on the hunks that hold actual decisions (`novel`), while a rename-heavy change collapses to a one-line list. **The reader is a human reviewing the change** — the rendered review order is for them; the agents in this pipeline only build it. It is **advisory** — it reorders a reviewer's attention, it gates nothing, and it never replaces the review itself. The same review order can *also* focus an agent review (`cold-review`, `pre-push`) run afterward.

The spine of the pipeline is a single rule: **every failure path demotes toward human review.** An unclassified hunk, a contested k-vote, and an audit hit all become `novel`. No path moves code away from human eyes on uncertainty.

## Inputs

A **diff** scope from the engine's vocabulary ([`../review.md`](../review.md)) — the manifest classifies hunks, so the engine's `paths` scope (current state, no diff) does not apply. Reached via the slash command, `$ARGUMENTS` resolves exactly as the engine resolves it: empty → branch-vs-base (default), `uncommitted`, or a git `<ref|range>`. The `unpushed` scope is — as in the engine — **not** a typeable `$ARGUMENTS` token; a caller selects it directly when invoking this pipeline (today, `pre-push`, generating a manifest over the un-pushed change-set). A leading `inline` token, if present, is stripped and ignored: the manifest pipeline has no fresh/warm split of its own — the classifier is always a fresh-context subagent — so `inline` affects only how the *caller* runs, not the classify stage.

## Process

### 1. Discover the change-set

Follow [`../changeset-scope.md`](../changeset-scope.md) for the env-wide scopes (`branch-vs-base`, `uncommitted`, `unpushed`); for an explicit `<ref|range>` the change-set is that range in the current repo. The result is a set of `(repo, worktree-path, base-ref)` entries and the per-target `git diff` command (per the engine's scope table). For the `uncommitted` scope, the per-target diff includes **untracked, non-ignored files** as whole-file additions — see [`./format.md#computing-diff_sha`](./format.md#computing-diff_sha); a new file an author has not yet `git add`ed is part of the change and must be classified, not silently skipped. Zero hunks in scope → report "nothing to classify" and stop; spawn nothing.

**Enumerate the canonical hunk-id set now.** Parse `git diff` for every target and assign each `@@ -a,b +c,d @@` block its id `<repo>/<file>@@<c>` (the post-image start line `c`, per [`./format.md#hunk-identity`](./format.md#hunk-identity)); an untracked whole-file addition is one hunk at `@@1`. This enumerated list is **authoritative** — it is what classifiers classify against (step 2) and what total coverage checks against (step 4). Deriving ids once here, rather than letting each classifier re-derive them, is what makes the k votes reconcilable: independent classifiers otherwise key the same hunk off slightly different line numbers and the votes never line up.

Compute `diff_sha` now, by the recipe in [`./format.md#computing-diff_sha`](./format.md#computing-diff_sha), and resolve each target's `head_sha` / `base_sha`. This is the binding the whole manifest hangs off — capture it before classification so a diff that shifts mid-run is caught by the coverage and staleness checks at render.

### 2. Classify — k-voted, fail closed

Spawn **k = 3** [`diff-classifier`](../../agents/diff-classifier.md) subagents **in parallel** (one message, three `Agent` calls — they are independent and concurrency is free wall-time).

Each spawn is **fresh and identical**: it carries the diff target (worktree paths, base refs, the `git diff` command) **and the enumerated hunk-id list from step 1**, with the instruction to classify each listed hunk by its given id. **Do not pass the task prompt, the PR description, or this session's design discussion** — the classifier's value is that it never saw why the change was made. Prepend the standard one-shot/no-team preamble (verbatim):

> This is a one-shot standalone classification. Read the diff, classify every hunk, and stop. There is no team coordinating you — do not call `SendMessage`, `TaskCreate`, or `TaskUpdate`, and do not attempt follow-on work. You did not see the task that produced this diff; do not go looking for it. When your per-hunk report is done, stop.

Run on **`opus`**, passed explicitly (`Agent(subagent_type: "diff-classifier", model: "opus", …)`) — classification is judgment-heavy. Downgrade only for a deliberately trivial scope, and say so.

**Reconcile per canonical hunk-id** once all three report — walk the step-1 enumerated list, gather the three votes for each id:

- All three agree on the tier → that tier. Take the `claim` (and `exemplar`) from the majority; any classifier's claim is fine when they concur.
- **Any disagreement → `novel`**, marked `contested: true`. This is the fail-closed core: a hunk three fresh readers cannot agree is cheap is, by definition, not safe to skim. Do not average, do not take a 2-of-3 majority — *any* split fails closed.
- A canonical id one or more classifiers **failed to vote on** is treated as a disagreement on that id → `novel`, `contested: true`. A hunk missing from *all* three is still backstopped by the coverage check in step 4 (inserted as `novel`). Ignore any id a classifier returns that is not in the enumerated list.

Record each hunk's `lines` (added + removed) from the diff for the metrics.

### 3. Audit — adversarially refute the cheap tiers

Spawn one [`manifest-auditor`](../../agents/manifest-auditor.md) over the reconciled manifest's **`mechanical` and `pattern`** hunks (the cheap tiers; `novel` is never audited — it already has the human). Same one-shot/no-team preamble, `opus`, foreground.

Give it the cheap-tier hunk list and a **sampling budget**. Default budget: audit **all** cheap-tier hunks when there are ≤ 20; above that, sample the hardest 20 first (largest hunks, control-flow/default-touching, classifier-flagged-on-the-line) and tell the auditor the rest are out of budget so it lists them rather than implying they were cleared. The auditor reports **hits** (claim refuted), **survives**, and **not audited (budget)**.

Apply the results:

- Each **hit** → set the hunk's `tier` to `novel`, `audit: "promoted"`, `promoted_from: <old tier>`, and **increment `misclassification_count`**.
- Each **survives** → `audit: "survives"` (tier unchanged).
- Cheap-tier hunks not sampled → `audit: "unaudited"`. They keep their classified tier but are **named in the render** as audited-not, so the human knows the audit's coverage was partial.

### 4. Enforce total coverage, then compute metrics

Before rendering, run the coverage check from [`./format.md#invariant-1--total-coverage`](./format.md#invariant-1--total-coverage): parse the diff's hunk-id set, compare to the manifest's, insert any missing hunk as `novel`. If a manifest hunk is **absent** from the current diff, the diff moved under you — recompute `diff_sha`; if it no longer matches step 1's, the change-set is mid-flight: stop and tell the caller to re-run on a settled diff rather than emit a manifest bound to a diff that no longer exists.

Then compute the `metrics` block per [`./format.md#metrics`](./format.md#metrics) — on the **final** (post-audit) tiers.

### 5. Write the JSON facts file

Write the classification facts to `$(winter space manifests)/<YYYY-MM-DD>-<slug>.json` per the [`./format.md`](./format.md) schema and naming (the [`../winter-space.md`](../winter-space.md) contract; default `workspace:/.winter/manifests/`). `<slug>` is the env name (env-wide scope) or the repo name (single-repo/standalone). This is the data layer — the per-hunk tiers, claims, metrics, and the `diff_sha` binding — that the markdown is rendered from and that a later consumer freshness-checks.

### 6. Render and write the markdown review document

Render the **markdown review document** from the facts and write it next to the JSON, sharing the basename: `$(winter space manifests)/<YYYY-MM-DD>-<slug>.md`. This file — not the JSON, and not an inline dump — is the manifest the human reviews.

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

Do not re-paste the document into the reply — point at it; it exists so the reply does not have to carry the review. When the manifest is generated as a pre-step for the `cold-review` or `pre-push` skill, hand the document back to that caller to order its own attention; do not also run the fresh review here.

## Why fresh, why k-voted, why adversarial

- **Fresh** — the classifier never saw the task, so it cannot be told "it's just a rename." It reads the code and judges the claim, the same freshness the `cold-review` skill relies on.
- **k-voted, fail closed** — three independent reads, and *any* disagreement demotes to `novel`. One classifier's blind spot cannot quietly bury a decision in a cheap tier; it takes unanimity to earn a skim.
- **Adversarial audit** — even a unanimous cheap classification is then attacked by a reader whose only job is to refute it. The `mechanical`/`pattern` tiers are trustworthy precisely because something tried to break them and failed.

Every layer points the same direction: **toward the human, never away.** The manifest can only ever *save* reviewer attention by proving a hunk safe through replay/exemplar/audit — never by assuming it.
