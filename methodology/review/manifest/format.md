# Review manifest — format and invariants

A review manifest is **two files**: a **markdown review document** a human reads to walk the change tier by tier, and the **JSON facts file** it is rendered from — the per-hunk tiers, claims, metrics, and freshness binding that the renderer and any later consumer read. Generate the JSON first, then render the markdown. This doc owns both shapes, the two hard invariants, hunk identity, and the metrics; [`classification.md`](./classification.md) owns what the tier values mean.

A manifest describes **one change-set**, which may span several repos in one feature env (the same unit the review engine uses — see [`../change-set.md`](../change-set.md)). Every hunk is keyed by its repo, so one manifest covers the whole set.

## Where it lives

Both files are generated artifacts, never written into a worktree. Resolve `<manifests-dir>` under the `manifests` consumer policy in [`../../artifact-storage.md`](../../artifact-storage.md), which also owns the `<YYYY-MM-DD>-<slug>.{md,json}` naming; the pair shares one basename. `<slug>` identifies the change-set: the env name for an env-wide scope (`alpha`), the repo name for a single-repo or standalone scope (`winter-workflow`). Report the **`.md` path** to the human — that is the manifest they review; the `.json` sits alongside for tooling and the freshness re-check.

## The markdown review document

The markdown is **a high-level reading guide for a human, not a diff dump**. It tells the reviewer what to look at, why, and what they can skip; the reviewer opens the actual diff in their own tool, so the manifest points at hunks and describes each decision in plain language. **Never paste raw hunk bodies** — a wall of inlined diff is the unreadable thing the manifest exists to replace. Aim for one to two screens; when a tier has many hunks, cluster them by theme rather than listing every one flat.

Structure:

```markdown
# Review manifest — <slug>

<one sentence: what this change is>

**<N> hunks, <L> lines** · novel <p>% · pattern <p>% · mechanical <p>%
contested <c>/<N> · audit: <sampled> sampled, <promoted> promoted

> **Where to spend your attention.** <2–3 sentences orienting the reviewer: the shape of the
> change, which tier holds the real decisions, what the cheap tiers cover and that they're verified.>

## Decisions — read these (novel · <count>)

Grouped by theme, not one flat row per hunk. Each entry: a plain-language **what changed and why it
needs judgment**, then the file pointer(s). Lead with the highest-stakes group; surface promoted and
contested hunks first — the audit and the vote flagged them.

- **<theme>** — <plain description of the decision and what to check> · `path/one.md`, `path/two.md`
- **⚠️ <contested item>** — <why the classifiers split; what to confirm> · `path@@line`

## Conforms to a pattern (pattern · <count>)

- `<path>` — <claim> (exemplar `<exemplar-path>`)

## Mechanical — skip (<count>) · audit-verified ✓

<One line, or a terse grouped list — not per-hunk prose.> e.g. "8 pure link-retargets, all verified
to resolve: `README.md`, `setup.md` ×6, `worktree-ops.md`." Tag any hunk the audit did not sample.
```

`novel` carries prose because it holds the decisions; `pattern` collapses to one line per hunk behind its claim and exemplar; `mechanical` collapses to a single skip-line for the whole tier. The header carries the metrics, led by the line percentages — they answer *how much of this change actually needs me?*

## Hunk identity

A hunk is one `@@ -a,b +c,d @@` block within a file's diff. Its stable id is:

```
<repo>/<file>@@<new-start-line>
```

where `<new-start-line>` is `c`, the post-image start line from the `@@` header — **not** the first changed line, which differs from `c` by the leading context lines — and `<repo>` is the repo the worktree belongs to. Every manifest entry, classifier vote, audit result, and coverage check is keyed by this id.

**The orchestrator assigns these ids, once, from the diff — classifiers never re-derive them.** Independent classifiers reading the same diff would otherwise key the same hunk off slightly different line numbers and the k votes would never line up for reconciliation. So [`./process.md`](./process.md) parses the canonical id set from `git diff` up front and hands classifiers that enumerated list to classify against; a classifier returns `{hunk_id, tier, claim}` keyed by the ids it was given, never an id it invented.

## Schema

```json
{
  "schema_version": 1,
  "skill_version": "v1",
  "generated_at": "<ISO-8601 timestamp>",
  "scope": "branch-vs-base | uncommitted | range | unpushed",
  "pinned_scope": "exclude | include | only | null",
  "slug": "<env-or-repo>",
  "diff_sha": "<hash binding the manifest to the diff it describes>",
  "targets": [
    {
      "repo": "<repo name>",
      "worktree": "<absolute worktree path>",
      "base": "<base ref>",
      "base_kind": "integration | upstream | explicit | head",
      "head_sha": "<HEAD sha, for diagnostics>",
      "base_sha": "<resolved base sha, for diagnostics>"
    }
  ],
  "hunks": [
    {
      "hunk_id": "<repo>/<file>@@<new-start-line>",
      "tier": "mechanical | pattern | novel",
      "claim": "<one-line assertion the tier rests on>",
      "exemplar": "<path|null>",
      "source": "classified | authored",
      "intent": "<author's reason for the change, or null>",
      "lines": <added + removed line count in this hunk>,
      "contested": false,
      "audit": "unaudited | survives | promoted",
      "promoted_from": "<original tier if audit promoted it, else null>"
    }
  ],
  "metrics": {
    "total_hunks": 0,
    "total_lines": 0,
    "lines_by_tier": { "mechanical": 0, "pattern": 0, "novel": 0 },
    "pct_lines_by_tier": { "mechanical": 0.0, "pattern": 0.0, "novel": 0.0 },
    "contested_count": 0,
    "contested_rate": 0.0,
    "cheap_sampled": 0,
    "audit_promotions": 0,
    "audit_promotion_rate": 0.0,
    "misclassification_count": 0
  }
}
```

Keys, ordering, and types are stable across runs at this `schema_version`. `tier` takes exactly the three values owned by [`classification.md`](./classification.md) and records the **final** tier after the audit; `promoted_from` preserves what the classifier originally assigned so a reader can see what the audit caught.

`source` records which producer filled the entry: `classified` follows [`process.md`](./process.md), `authored` follows [`build-time.md`](./build-time.md). `intent` is the author's reason for the change in their own words — populated for `authored` entries, `null` for `classified` ones (a fresh classifier never saw the intent). Intent enriches the render's claim; it never substitutes for the adversarial audit, which checks an `authored` cheap-tier claim exactly as it checks a `classified` one.

## Invariant 1 — total coverage

Every hunk of the diff carries **exactly one** tier; an unclassified hunk is `novel` by definition. Verify mechanically before a manifest is rendered or consumed:

1. Parse the diff's hunk-id set — every `@@` block across every target, as `<repo>/<file>@@<c>`.
2. Compare to the manifest's `hunks[].hunk_id` set.
3. Insert any diff hunk **missing** from the manifest as `novel` — never classified, so it fails closed. Any manifest hunk **absent** from the diff means the diff changed under the manifest; treat the manifest as stale (invariant 2).

Coverage is set equality, not a count: a manifest that classified 99 of 100 hunks does not "mostly" cover the diff — the 100th hunk is `novel` until proven otherwise.

## Invariant 2 — freshness binding

The manifest records the SHA of the diff it describes, and a **stale manifest is mechanically rejected**: a consumer recomputes the SHA over the current change-set and refuses a manifest whose recorded `diff_sha` does not match.

### Computing `diff_sha`

Deterministic over the change-set: for each target in **repo-sorted order**, emit its diff from its worktree; concatenate in that order; hash:

```bash
# branch-vs-base / unpushed:  git diff "<base>...HEAD"
# range:                      git diff "<range>"
# uncommitted:                git diff HEAD  AND each untracked file (see below)
for wt in <targets sorted by repo>; do
  ( cd "$wt" && git diff "<base>...HEAD" )
done | git hash-object --stdin
```

The repo-sort and the fixed diff command make the hash reproducible from the same change-set and different the moment any in-scope diff changes — a rebased base and an amended commit both change it. `targets[].head_sha` / `base_sha` are diagnostics; the binding is `diff_sha`.

**Untracked files (the `uncommitted` scope).** `git diff HEAD` shows only *tracked* changes, but a new file the author has not yet `git add`ed is part of the uncommitted change-set. So for `uncommitted`, the per-target diff is `git diff HEAD` **plus** each untracked, non-ignored file rendered as a whole-file addition, in a stable order, with no index mutation:

```bash
( cd "$wt" && git diff HEAD
  git ls-files --others --exclude-standard -z | sort -z |
    while IFS= read -r -d '' f; do git diff --no-index --no-color -- /dev/null "$f"; done )
```

`git diff --no-index /dev/null <file>` emits a normal new-file diff (one `@@ … +1,N @@` hunk) read-only — no `git add -N`, no working-tree change. Untracked files join the tracked diff for **both** `diff_sha` and hunk enumeration, so a new file becomes one classifiable hunk at `<repo>/<file>@@1` rather than slipping through unreviewed. (The committed-history scopes have no untracked dimension.)

### The staleness check

Before trusting a manifest, a consumer:

1. Rediscovers the change-set for the manifest's `scope` (per [`../change-set.md`](../change-set.md)), preserving its `pinned_scope`, target base kinds, and any documented explicit review bases.
2. Recomputes `diff_sha` by the recipe above.
3. **Match** → the manifest describes the current diff; use it. **Mismatch** — or a target that no longer exists, or a hunk-set that no longer matches — → **reject as stale** and regenerate; never patch or silently reuse. A manifest claiming a hunk is `mechanical` for a diff that has since changed is exactly the false reassurance the binding exists to prevent.

## Metrics

Per change-set, emitted into `metrics` and surfaced in the render header:

| Metric | Definition |
|--------|------------|
| **% of diff lines per tier** | `lines_by_tier[t] / total_lines`, per tier. Lines = added + removed within the hunk. Reported on the **final** tiers (post-audit). |
| **contested-classification rate** | `contested_count / total_hunks` — hunks where the k classifiers disagreed and were failed closed to `novel`. |
| **audit promotion rate** | `audit_promotions / cheap_sampled` — sampled cheap-tier hunks the audit promoted to `novel`. Zero sampled → report `n/a`, not `0`. |
| **misclassification count** | total cheap-tier hunks the audit promoted (the per-change counter the audit increments). |
