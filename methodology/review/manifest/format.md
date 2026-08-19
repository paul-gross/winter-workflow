# Review manifest — format and invariants

A review manifest is **two files**: a **markdown review document** a human reads to walk the change tier by tier, and
the **JSON facts file** it is rendered from — the per-hunk tiers, claims, metrics, and freshness binding that the
renderer and any later consumer read. Generate the JSON first, then render the markdown. This doc owns the facts file —
its schema, hunk identity, the two hard invariants, and the metrics. [`render.md`](./render.md) owns the markdown
document's shape and discipline; [`classification.md`](./classification.md) owns what the tier values mean.

A manifest describes **one change-set**, which may span several repos in one feature env (the same unit the review
engine uses — see [`../change-set.md`](../change-set.md)). Every hunk is keyed by its repo, so one manifest covers the
whole set.

## Where it lives

Both files are generated artifacts, never written into a worktree. Resolve `<manifests-dir>` and name the pair under the
`manifests` consumer policy in [`../../artifact-storage.md`](../../artifact-storage.md), which owns the naming pattern
and its same-day variant; the `.md` and `.json` share one basename. `<slug>` identifies the change-set: the env name for
an env-wide scope (`alpha`), the repo name for a single-repo or standalone scope (`winter-workflow`). Report the **`.md`
path** to the human — that is the manifest they review; the `.json` sits alongside for tooling and the freshness
re-check.

## Hunk identity

A hunk is one `@@ -a,b +c,d @@` block within a file's diff. Its stable id is:

```text
<repo>/<file>@@<new-start-line>
```

where `<new-start-line>` is `c`, the post-image start line from the `@@` header — **not** the first changed line, which
differs from `c` by the leading context lines — and `<repo>` is the repo the worktree belongs to. Every manifest entry,
classifier vote, audit result, and coverage check is keyed by this id.

**The orchestrator assigns these ids, once, from the diff — classifiers never re-derive them.** Independent classifiers
reading the same diff would otherwise key the same hunk off slightly different line numbers and the k votes would never
line up for reconciliation. So [`./process.md`](./process.md) parses the canonical id set from `git diff` up front and
hands classifiers that enumerated list to classify against; a classifier returns `{hunk_id, tier, claim}` keyed by the
ids it was given, never an id it invented.

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

Keys, ordering, and types are stable across runs at this `schema_version`. `tier` takes exactly the three values owned
by [`classification.md`](./classification.md) and records the **final** tier after the audit; `promoted_from` preserves
what the classifier originally assigned so a reader can see what the audit caught. `base_kind` takes the review-base
kinds owned by [`../change-set.md`](../change-set.md), which names the kind it returns for each scope.

`source` records which producer filled the entry: `classified` follows [`process.md`](./process.md), `authored` follows
[`build-time.md`](./build-time.md). `intent` is the author's reason for the change in their own words — populated for
`authored` entries, `null` for `classified` ones (a fresh classifier never saw the intent). Intent enriches the render's
claim; it never substitutes for the adversarial audit, which checks an `authored` cheap-tier claim exactly as it checks
a `classified` one.

### Fail-closed entries

Two entry kinds reach the schema with no concurring classifier behind them. Both are `tier: "novel"`, `exemplar: null`,
`audit: "unaudited"` (`novel` is never audited), `promoted_from: null`, and `lines` counted from the diff like any other
hunk; `source` records whichever producer path ran, and `intent` is `null` unless a build-time author recorded one. They
differ in the two fields that carry why the entry exists:

| Entry                                                                                              | `contested` | `claim`                                                                    |
| -------------------------------------------------------------------------------------------------- | ----------- | -------------------------------------------------------------------------- |
| **Contested** — the k classifiers split ([`process.md`](./process.md))                             | `true`      | The split itself and the tiers voted, since no assertion survived the vote |
| **Coverage-inserted** — the hunk reached [invariant 1](#invariant-1--total-coverage) with no entry | `false`     | That no classifier vote exists for the hunk                                |

A coverage-inserted hunk is not contested: nothing was voted on to disagree about. Fixing these two shapes here is what
keeps `contested_rate` and the tier percentages comparable across runs.

## Invariant 1 — total coverage

Every hunk of the diff carries **exactly one** tier; an unclassified hunk is `novel` by definition. Verify mechanically
before a manifest is rendered or consumed:

1. Parse the diff's hunk-id set — every `@@` block across every target, as `<repo>/<file>@@<c>`.
2. Compare to the manifest's `hunks[].hunk_id` set.
3. Insert any diff hunk **missing** from the manifest as `novel` — never classified, so it fails closed. Any manifest
   hunk **absent** from the diff means the diff changed under the manifest; treat the manifest as stale (invariant 2).

Coverage is set equality, not a count: a manifest that classified 99 of 100 hunks does not "mostly" cover the diff — the
100th hunk is `novel` until proven otherwise.

## Invariant 2 — freshness binding

The manifest records the SHA of the diff it describes, and a **stale manifest is mechanically rejected**: a consumer
recomputes the SHA over the current change-set and refuses a manifest whose recorded `diff_sha` does not match.

### Computing `diff_sha`

Deterministic over the change-set: for each target in **repo-sorted order**, emit its diff from its worktree;
concatenate in that order; hash:

```bash
# branch-vs-base / unpushed:  git diff "<base>...HEAD"
# range:                      git diff "<range>"
# uncommitted:                git diff HEAD  AND each untracked file (see below)
for wt in <targets sorted by repo>; do
  ( cd "$wt" && git diff "<base>...HEAD" )
done | git hash-object --stdin
```

The repo-sort and the fixed diff command make the hash reproducible from the same change-set and different the moment
any in-scope diff changes — a rebased base and an amended commit both change it. `targets[].head_sha` / `base_sha` are
diagnostics; the binding is `diff_sha`.

**Untracked files (the `uncommitted` scope).** `git diff HEAD` shows only *tracked* changes, but a new file the author
has not yet `git add`ed is part of the uncommitted change-set. So for `uncommitted`, the per-target diff is
`git diff HEAD` **plus** each untracked, non-ignored file rendered as a whole-file addition, in a stable order, with no
index mutation:

```bash
( cd "$wt" && git diff HEAD
  git ls-files --others --exclude-standard -z | sort -z |
    while IFS= read -r -d '' f; do git diff --no-index --no-color -- /dev/null "$f"; done )
```

`git diff --no-index /dev/null <file>` emits a normal new-file diff (one `@@ … +1,N @@` hunk) read-only — no
`git add -N`, no working-tree change. Untracked files join the tracked diff for **both** `diff_sha` and hunk
enumeration, so a new file becomes one classifiable hunk at `<repo>/<file>@@1` rather than slipping through unreviewed.
(The committed-history scopes have no untracked dimension.)

### The staleness check

Before trusting a manifest, a consumer:

1. Rediscovers the change-set for the manifest's `scope` (per [`../change-set.md`](../change-set.md)), preserving its
   `pinned_scope`, target base kinds, and any documented explicit review bases.
2. Recomputes `diff_sha` by the recipe above.
3. **Match** → the manifest describes the current diff; use it. **Mismatch** — or a target that no longer exists, or a
   hunk-set that no longer matches — → **reject as stale** and regenerate; never patch or silently reuse. A manifest
   claiming a hunk is `mechanical` for a diff that has since changed is exactly the false reassurance the binding exists
   to prevent.

### Amending a rendered manifest

A manifest whose `diff_sha` still matches may be amended in **one direction only: toward human review.** A review
finding proving a cheap-tier hunk carried a decision promotes that hunk in place; nothing moves a hunk to a cheaper
tier, and no other in-place edit is permitted. A manifest needing any other correction is regenerated, which is also the
only remedy once `diff_sha` stops matching.

A promotion obliges the full set, or it is a lie the metrics inherit: set `tier: "novel"`, `audit: "promoted"`, and
`promoted_from` to the tier it left; increment `misclassification_count`; recompute the `metrics` block; and re-render
the markdown so the document a human reads agrees with the facts file.

## Metrics

Per change-set, emitted into `metrics` and surfaced in the render header:

| Metric                            | Definition                                                                                                                                                    |
| --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **% of diff lines per tier**      | `lines_by_tier[t] / total_lines`, per tier. Lines = added + removed within the hunk. Reported on the **final** tiers (post-audit).                            |
| **contested-classification rate** | `contested_count / total_hunks` — hunks where the k classifiers disagreed and were failed closed to `novel`.                                                  |
| **audit promotion rate**          | `audit_promotions / cheap_sampled` — sampled cheap-tier hunks the audit promoted to `novel`. Zero sampled → report `n/a`, not `0`.                            |
| **misclassification count**       | total cheap-tier hunks promoted out of a cheap tier. The step applying an audit result or a review finding increments it; the audit itself only reports hits. |
