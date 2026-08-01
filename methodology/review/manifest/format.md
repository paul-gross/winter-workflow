# Review manifest — format and invariants

A review manifest is **two files**: a **markdown review document** a human reads to walk the change tier by tier, and a **JSON facts file** the markdown is rendered from. The markdown is the deliverable — the thing a reviewer opens; the JSON is the data layer (per-hunk tiers, claims, metrics, the freshness binding) that the renderer and any consumer reads. Generate the JSON first (it holds the facts and the invariants), then render the markdown from it.

This doc is the single source for both files: the JSON schema, the markdown structure, the two hard invariants (total coverage, freshness binding), how a hunk is identified, and the per-change metrics. The process that produces a manifest is [`process.md`](./process.md); [`classification.md`](./classification.md) owns the closed tier vocabulary and its semantics. This doc only records those values in the schema and render.

A manifest describes **one change-set**, which may span several repos in one feature env (the same change-set unit the review engine uses — see [`../process.md`](../process.md) and [`../change-set.md`](../change-set.md)). Every hunk is keyed by its repo, so one manifest covers the whole set.

## Where it lives

Both files are **generated artifacts**, not repo deliverables. Resolve `<manifests-dir>` once under the `manifests` consumer policy in [`../../artifact-storage.md`](../../artifact-storage.md), then write the pair with one basename:

```
<manifests-dir>/<YYYY-MM-DD>-<slug>.md      ← the review document (what the human reads)
<manifests-dir>/<YYYY-MM-DD>-<slug>.json    ← the facts it was rendered from
```

`<slug>` identifies the change-set: the env name for an env-wide scope (`alpha`), or the repo name for a single-repo / standalone scope (`winter-workflow`). Same-day re-runs use the `<YYYY-MM-DD>-<HHMM>-<slug>` suffix. Neither file is written into a worktree. Report the **`.md` path** to the human — that is the manifest they review; the `.json` sits alongside for tooling and the freshness re-check.

## The markdown review document

The markdown is **a high-level reading guide for a human, not a diff dump.** Its job is to tell a reviewer *what to look at and why* and *what they can skip* — so it shrinks the change to a scannable map. The reviewer opens the actual diff in their own tool (editor, PR view); the manifest **points** them at the hunks that hold decisions and describes each in plain language. **Never paste raw hunk bodies into it** — a wall of inlined diff is the unreadable thing the manifest exists to replace. Aim for one to two screens; if a tier has many hunks, **cluster them by theme** rather than listing every one flat.

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
needs judgment**, then the file pointer(s). Lead with the highest-stakes group; flag contested hunks.

- **<theme>** — <plain description of the decision and what to check> · `path/one.md`, `path/two.md`
- **⚠️ <contested item>** — <why the classifiers split; what to confirm> · `path@@line`

## Conforms to a pattern (pattern · <count>)

- `<path>` — <claim> (exemplar `<exemplar-path>`)

## Mechanical — skip (<count>) · audit-verified ✓

<One line, or a terse grouped list — not per-hunk prose.> e.g. "8 pure link-retargets, all verified
to resolve: `README.md`, `setup.md` ×6, `worktree-ops.md`."
```

The discipline is **summarize and group, never transcribe**: a reviewer should be able to read the whole document in a minute and know the three things that need their judgment, then jump to those hunks in their own diff tool. `novel` gets prose because it carries the decisions; `pattern` collapses to one line per hunk behind its claim; `mechanical` collapses to a single skip-line for the whole tier.

## The closed tier vocabulary

The schema accepts exactly `mechanical`, `pattern`, or `novel`; there is no fourth value and no "unsure". [`classification.md`](./classification.md) owns what each value means, how uncertainty resolves, and how renderers and humans interpret it. The replay and exemplar-judging verifications remain out of scope for this cut; cheap tiers are checked through [`audit.md`](./audit.md).

## Hunk identity

A hunk is one `@@ -a,b +c,d @@` block within a file's diff. Its stable id is:

```
<repo>/<file>@@<new-start-line>
```

where `<new-start-line>` is the `c` (the post-image start line) from the `@@ -a,b +c,d @@` header — **not** the first changed line, which differs from `c` by the leading context lines. `<repo>` is the repo the worktree belongs to. The id is what total coverage is checked against and what every manifest entry, classifier vote, and audit result is keyed by.

**The orchestrator assigns these ids, once, from the diff — classifiers do not re-derive them.** Each fresh classifier reading the same diff independently would otherwise key the same hunk off a slightly different line number (the header `c` vs. the first `+`/`-` line), and the k votes would never line up for reconciliation. So the process parses the canonical `<repo>/<file>@@<c>` set from `git diff` up front and hands classifiers that enumerated list to classify *against*; a classifier returns `{hunk_id, tier, claim}` keyed by the ids it was given, never an id it invented. See [`./process.md`](./process.md) steps 1–2.

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

Keys, ordering, and types are stable across runs at this `schema_version`. The `tier` field records the **final** tier after the audit; `promoted_from` preserves what the classifier originally assigned so a reader can see what the audit caught.

`source` records **which producer** filled the entry: `classified` follows the fresh-classification [`process.md`](./process.md), while `authored` follows [`build-time.md`](./build-time.md). `intent` is the author's reason for the change in their own words (e.g. "extracted the shared scope vocab so fetch/pull/push stop drifting") — populated for `authored` entries, `null` for `classified` ones (a fresh classifier never saw the intent). `intent` enriches the render's claim; it never substitutes for the adversarial audit, which checks an `authored` cheap-tier claim exactly as it checks a `classified` one.

## Invariant 1 — total coverage

Every hunk of the diff is assigned **exactly one** tier; an unclassified hunk is `novel` by definition. Before a manifest is rendered or consumed, verify it mechanically:

1. Parse the diff's hunk-id set — every `@@` block across every target, as `<repo>/<file>@@<c>`.
2. Compare to the manifest's `hunks[].hunk_id` set.
3. Any diff hunk **missing** from the manifest is inserted as `novel` (it was never classified, so it fails closed). Any manifest hunk **absent** from the diff is a staleness signal — the diff changed under the manifest; treat the manifest as stale (invariant 2).

Coverage is a set equality, not a count — a manifest that classified 99 of 100 hunks does not "mostly" cover the diff; the 100th hunk is `novel` until proven otherwise.

## Invariant 2 — freshness binding

The manifest records the SHA of the diff it describes. A **stale manifest is mechanically rejected** — a consumer recomputes the SHA over the current change-set and refuses a manifest whose recorded `diff_sha` does not match.

### Computing `diff_sha`

Deterministic over the change-set. For each target in **repo-sorted order**, `cd` to its worktree and emit its diff; concatenate in that order; hash:

```bash
# branch-vs-base / unpushed:  git diff "<base>...HEAD"
# range:                      git diff "<range>"
# uncommitted:                git diff HEAD  AND each untracked file (see below)
for wt in <targets sorted by repo>; do
  ( cd "$wt" && git diff "<base>...HEAD" )
done | git hash-object --stdin
```

The repo-sort and the fixed diff command make the hash reproducible from the same change-set and different the moment any in-scope diff changes. Record each target's `head_sha` / `base_sha` in `targets[]` for diagnostics, but the **binding** is `diff_sha` — a rebased base or an amended commit both change the diff and therefore the hash.

**Untracked files (the `uncommitted` scope).** `git diff HEAD` shows only *tracked* changes — a new file the author has not yet `git add`ed is part of the uncommitted change-set but invisible to it. So for `uncommitted`, the per-target diff is `git diff HEAD` **plus** each untracked, non-ignored file rendered as a whole-file addition, in a stable order, with no index mutation:

```bash
( cd "$wt" && git diff HEAD
  git ls-files --others --exclude-standard -z | sort -z |
    while IFS= read -r -d '' f; do git diff --no-index --no-color -- /dev/null "$f"; done )
```

`git diff --no-index /dev/null <file>` emits a normal new-file diff (one `@@ … +1,N @@` hunk) read-only — no `git add -N`, no working-tree change. The untracked files join the tracked diff for **both** `diff_sha` and hunk enumeration, so an untracked new file becomes one hunk at `<repo>/<file>@@1` and is classified like any other rather than slipping through unreviewed. (Branch-vs-base, range, and unpushed scopes compare committed history and have no untracked dimension.)

### The staleness check

Any consumer of a manifest runs, before trusting it:

1. Rediscover the change-set for the manifest's `scope` (per `../change-set.md`), preserving its `pinned_scope`, target base kinds, and any documented explicit review bases.
2. Recompute `diff_sha` by the recipe above.
3. **Match** → the manifest describes the current diff; use it. **Mismatch** (or a target that no longer exists / a hunk-set that no longer matches) → **reject as stale**; regenerate the manifest, do not patch it. A stale manifest is never silently reused — a manifest that claims a hunk is `mechanical` for a diff that has since changed is exactly the false reassurance the binding exists to prevent.

## Metrics

Per change-set, emitted into `metrics` and surfaced in the render header:

| Metric | Definition |
|--------|------------|
| **% of diff lines per tier** | `lines_by_tier[t] / total_lines`, per tier. Lines = added + removed within the hunk. Reported on the **final** tiers (post-audit). |
| **contested-classification rate** | `contested_count / total_hunks` — hunks where the k classifiers disagreed and were failed closed to `novel`. |
| **audit promotion rate** | `audit_promotions / cheap_sampled` — sampled cheap-tier hunks the audit promoted to `novel`. Zero sampled → report `n/a`, not `0`. |
| **misclassification count** | total cheap-tier hunks the audit promoted (the per-change counter the audit increments). |

Lines are counted per hunk so the percentages answer the question the manifest exists for: *how much of this diff actually needs me?* A change that is 95% `mechanical` lines and 5% `novel` lines is the win condition — the human reads the 5%.
