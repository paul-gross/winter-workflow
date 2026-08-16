# Review manifest — classification

The canonical classification contract shared by every review-manifest producer and consumer — fresh classifiers, build-time authors, adversarial auditors, renderers, and human readers. Runtime agents are ports into this methodology; they do not own or redefine it.

## The closed tier vocabulary

Every hunk is exactly one of three values — there is no fourth, and "unsure" is not a tier. A tier is defined by **what it takes to verify the hunk**, not what it looks like:

| Tier | Claim | Verification | Human interpretation |
|------|-------|--------------|----------------------|
| `mechanical` | A rename / move / codemod with **no behavior change** — the same code, relocated or relabeled. | Unanimous classification, then the adversarial [`audit.md`](./audit.md) hunt for behavior riding along. | Skim the grouped summary; inspect any unaudited tag. |
| `pattern` | Conforms to a **named exemplar** — a new instance of an established pattern already in the codebase. | Unanimous classification, then the same audit, reading the exemplar and comparing. | Skim the one-line claim and exemplar; inspect any unaudited tag. |
| `novel` | A **new decision** — anything that introduces or changes behavior, structure, or intent. | A human, at full attention. | Read the real diff and judge the decision in full. |

Both cheap tiers are verified the same way today: the k classifiers must agree ([`process.md`](./process.md) fails any split closed to `novel`), and the audit then tries to refute what they agreed on.

`novel` is the default and the safe value: uncertainty, a hunk on the line, a claim that cannot be cleanly stated — all resolve to `novel`, with the reason said. The asymmetry is deliberate: a wrong cheap tier hides a decision from the human, while an over-cautious `novel` costs seconds of reading. **When in doubt, `novel`.**

**Target state — not built.** Each cheap tier is meant to earn a verification of its own: deterministic replay for `mechanical`, regenerating the change from the claim and byte-comparing; and for `pattern`, an LLM judge holding the exemplar in context over k votes. Neither exists, so read the table's Verification column as what runs today, not as a check you can assume happened.

### `mechanical` — only when behavior is provably unchanged

Grant `mechanical` only when the transformation can be named and asserted to change no behavior: a symbol renamed consistently, code moved between files unchanged, an import reordered, a formatter's output. Interrogate the claim skeptically — a "pure rename" that also changed a default, dropped a guard clause, flipped a comparison, or shifted an off-by-one is `novel`. A claim that cannot be stated as a verifiable transformation is not `mechanical`.

A **pure reference retarget** is mechanical: a link, import, or path string repointed at a moved or renamed target, where stripping the retargeted token leaves before and after byte-identical. The moment the retarget rides with any other edit — a reworded sentence, a reflowed paragraph, an added breadcrumb, a changed heading level, different anchor phrasing — it is `novel`: retargeting a reference is mechanical; editing around it is a decision. Likewise a relocated file that also gained or lost a line (a title, a breadcrumb) is moved-and-edited, hence `novel`.

### `pattern` — only with a named exemplar

Grant `pattern` only when the hunk mirrors a **specific existing file**, recorded as its `exemplar`. "Looks like other code" is not enough — without a named exemplar the hunk is `novel`. Classification only names the exemplar the hunk claims to follow; judging conformance is downstream.

## Classifier decision rules

These bind fresh classification and build-time self-classification alike:

1. Classify **per hunk, never per file** — one file can hold a mechanical rename and a novel decision in adjacent hunks.
2. Start at `novel`. Promote only for a named behavior-preserving transformation (`mechanical`) or conformance to a named exemplar (`pattern`).
3. Read surrounding code when needed to verify a rename, move, or exemplar claim; a hunk not fully understood stays `novel`.
4. Emit a one-line `claim` carrying the assertion the tier rests on — e.g. "renames `foo` to `bar` across 4 call sites, no behavior change" — and, for `pattern`, the `exemplar` path.

Build-time authors additionally record `source: "authored"` and `intent` per [`build-time.md`](./build-time.md); fresh classification records `source: "classified"` and no intent.

## Fresh-classification procedure

The caller supplies the in-scope targets (worktree path and base ref each), the exact `git diff` command, and the **canonical hunk-id list** enumerated by [`process.md`](./process.md) — ids keyed by the post-image start line per [`format.md#hunk-identity`](./format.md#hunk-identity).

1. Run the supplied diff command in each worktree and read the full diff, not only the `--stat`.
2. Classify each supplied canonical id. Do not invent, renumber, or re-derive ids; if a listed id has no matching hunk, report that rather than guessing.
3. Read surrounding code and any candidate exemplar needed to apply the decision rules.
4. Return the tier, one-line claim, and `pattern` exemplar for every supplied id — the caller reconciles independent votes by these exact ids, so omit none and add none.

## Fresh-classifier output

One record per supplied hunk id:

```text
<repo>/<file>@@<line>  <tier>  exemplar=<path|->
  claim: <one line>
```

Close with a one-line tally per tier and the ids the classification was on the line about — hesitation is signal to the caller. Name any listed id with no matching hunk and why; never silently drop or substitute one.
