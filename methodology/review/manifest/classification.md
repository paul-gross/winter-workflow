# Review manifest — classification

The canonical classification contract for every review-manifest producer and consumer. Fresh classifiers, build-time authors, adversarial auditors, renderers, and human reviewers all use these tier meanings and decision rules. Runtime agents are ports into this methodology; they do not own or redefine it.

## The closed tier vocabulary

Every hunk is exactly one of these three values — there is no fourth, and "unsure" is not a tier. The tier is defined by **how the hunk is verified**, not what it looks like:

| Tier | Claim | How it would be verified | Human interpretation |
|------|-------|--------------------|----------------------|
| `mechanical` | A rename / move / codemod with **no behavior change** — the same code, relocated or relabeled. | Deterministic replay: regenerate the change from the claim and byte-compare. | Skim the grouped summary; inspect any unaudited tag. |
| `pattern` | **Conforms to a named exemplar** — a new instance of an established, named pattern already in the codebase. | An LLM judge with the exemplar in context, k votes. | Skim the one-line claim and named exemplar; inspect any unaudited tag. |
| `novel` | A **new decision** — anything that introduces or changes behavior, structure, or intent. | A human, at full attention. | Read the real diff and judge the decision in full. |

`novel` is the **default and the safe value**. When a hunk does not cleanly satisfy the `mechanical` or `pattern` claim — when the classifier is weighing it, when it is on a line — classify it `novel` and say why. Demoting a real decision to a cheap tier hides it from the human; promoting a trivial change to `novel` only costs a few seconds of reading. The asymmetry is deliberate: **when in doubt, `novel`.**

The replay and exemplar-judging verifications are follow-ups in the current implementation. Until they exist, both cheap tiers are checked by the adversarial [`audit.md`](./audit.md) methodology before rendering.

### `mechanical` — only when behavior is provably unchanged

A hunk is `mechanical` only when the classifier can name the transformation and assert it changed no behavior: a symbol renamed consistently, code moved between files unchanged, an import reordered, or a formatter's output. Interrogate it skeptically before granting the tier. A "pure rename" that also **changed a default, dropped a guard clause, flipped a comparison, or shifted an off-by-one** is `novel`, not `mechanical`. If the claim cannot be stated as a verifiable transformation, the hunk is not `mechanical`.

A **pure reference retarget** is mechanical: a link, import, or path string repointed to a moved or renamed target — `[usage.md]` → `[usage/dashboard.md]`, `from a.b import x` → `from a.c import x`, or a docstring's file path updated — **where the only change in the hunk is the reference token and the surrounding prose or code is otherwise byte-identical**. The test is strict and verifiable: strip the retargeted token and the before/after are the same. The moment the retarget rides with any other edit — a reworded sentence, a reflowed paragraph, an added breadcrumb, a changed heading level, or different anchor phrasing — it is no longer pure; it is `novel`. Retargeting a reference is mechanical; editing around the reference is a decision. Do not stretch this to whole-file moves that also gained or lost a line: a relocated file with an added title or breadcrumb is moved-and-edited, hence `novel`.

### `pattern` — only with a named exemplar

A hunk is `pattern` only when the classifier can point to a **specific existing file** it mirrors (`exemplar`). "Looks like other code" is not enough. Without a named exemplar the tier degenerates into vague resemblance, so the hunk is `novel`. Record the exemplar path with the hunk. Exemplar judging is downstream; classification only names the exemplar the hunk claims to follow.

## Classifier decision rules

Apply these rules to fresh classification and build-time self-classification alike:

1. Classify **per hunk, never per file**. One file can contain a mechanical rename and a novel decision in adjacent hunks.
2. Start at `novel`. Promote to `mechanical` only for a named, behavior-preserving transformation; promote to `pattern` only for conformance to a named exemplar.
3. Read surrounding code when needed to verify a rename, move, or exemplar claim. A hunk not fully understood remains `novel`.
4. Emit a one-line `claim` containing the assertion the tier rests on — for example, "renames `foo` to `bar` across 4 call sites, no behavior change"; "new repository adapter conforming to `exemplars/python/repo_pattern.py`"; or "adds a retry branch with a new backoff default". For `pattern`, also emit the `exemplar` path.
5. Never invent a fourth tier or use "unsure". Uncertainty resolves to `novel`.
6. Never rubber-stamp a cheap tier to look decisive. A wrong `mechanical` or `pattern` hides a decision; an over-cautious `novel` only increases human attention.

Build-time authors additionally record `source: "authored"` and `intent` per [`build-time.md`](./build-time.md). Fresh classification records `source: "classified"` and has no author intent.

## Fresh-classification procedure

The caller supplies the in-scope targets, each worktree path and base ref, the exact `git diff` command, and the **canonical hunk-id list** enumerated by [`process.md`](./process.md). For an isolated fresh classifier:

1. Run the supplied diff command in each worktree and read the full diff, not only the `--stat`.
2. Classify **each canonical id supplied by the caller**. Do not invent ids, renumber them, or derive ids from the first changed line. If a listed id has no matching hunk, report that rather than guessing.
3. Read surrounding code and any candidate exemplar needed to apply the decision rules.
4. Return the tier, one-line claim, and `pattern` exemplar for every supplied id.

The hunk id is `<repo>/<file>@@<line>`, where `<line>` is the post-image start line `c` from the hunk's `@@ -a,b +c,d @@` header. The caller reconciles independent votes by these exact ids, so the report must omit none and add none.

## Fresh-classifier output

Report one record for every hunk id on the supplied list:

```text
<repo>/<file>@@<line>  <tier>  exemplar=<path|->
  claim: <one line>
```

Then report a one-line tally with the hunk count per tier and the ids the classifier found itself on the line about. Hesitation is signal to the caller. If a listed id has no matching hunk, name it and explain why; never silently drop it or substitute a different id.
