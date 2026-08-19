# Review manifest — the markdown review document

The markdown review document is the manifest a human actually reads. It is rendered from the completed JSON facts file
owned by [`format.md`](./format.md), and both producers close by rendering it: fresh classification through
[`process.md`](./process.md), build-time capture through [`build-time.md`](./build-time.md).

The markdown is **a high-level reading guide for a human, not a diff dump**. It tells the reviewer what to look at, why,
and what they can skip; the reviewer opens the actual diff in their own tool, so the manifest points at hunks and
describes each decision in plain language. **Never paste raw hunk bodies** — a wall of inlined diff is the unreadable
thing the manifest exists to replace. Aim for one to two screens; when a tier has many hunks, cluster them by theme
rather than listing every one flat.

## Structure

```markdown
# Review manifest — <slug>

<one sentence: what this change is>

**<N> hunks, <L> lines** · novel <p>% · pattern <p>% · mechanical <p>% contested <c>/<N> · audit: <sampled> sampled,
<promoted> promoted

> **Where to spend your attention.** <2–3 sentences orienting the reviewer: the shape of the change, which tier holds
> the real decisions, what the cheap tiers cover and that they're verified.>

## Decisions — read these (novel · <count>)

Grouped by theme, not one flat row per hunk. Each entry: a plain-language **what changed and why it needs judgment**,
then the file pointer(s). Lead with the highest-stakes group; surface promoted and contested hunks first — the audit and
the vote flagged them.

- **<theme>** — <plain description of the decision and what to check> · `path/one.md`, `path/two.md`
- **⚠️ <contested item>** — <why the classifiers split; what to confirm> · `path@@line`

## Conforms to a pattern (pattern · <count>)

- `<path>` — <claim> (exemplar `<exemplar-path>`)

## Mechanical — skip (<count>) · audit-verified ✓

<One line, or a terse grouped list — not per-hunk prose.> e.g. "8 pure link-retargets, all verified to resolve:
`README.md`, `setup.md` ×6, `worktree-ops.md`." Tag any hunk the audit did not sample.
```

`novel` carries prose because it holds the decisions; `pattern` collapses to one line per hunk behind its claim and
exemplar; `mechanical` collapses to a single skip-line for the whole tier. The header carries the
[metrics](./format.md#metrics), led by the line percentages — they answer *how much of this change actually needs me?*
