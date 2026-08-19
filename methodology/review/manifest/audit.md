# Review manifest — adversarial audit

The reusable audit methodology for review manifests from either producer — fresh classification or build-time intent
capture. Runtime agents are ports into this methodology; they do not own or redefine it. Read
[`classification.md`](./classification.md) first: it owns the tier meanings the claims are audited against.

## Audit posture

Audit only `mechanical` and `pattern` hunks — the tiers the manifest claims are safe to skim; never `novel`, which
already goes to the human. The posture is adversarial: the classifier asked "is this a rename?" and answered yes; the
auditor asks "what did this rename also do?" **Default to suspicion** — a claim survives only when the audit tries and
fails to refute it, never because it sounds plausible. The audit reads and refutes; it does not edit code, run tests, or
delegate.

## What refutes a claim

For each sampled hunk, read the hunk **and the surrounding code**, take the claim at face value, and hunt for anything
it omits.

A `mechanical` rename, move, or codemod claim is refuted by any behavior change riding along, including:

- a **changed default** value or argument
- a **dropped or added guard clause**, early return, or null check
- a **flipped comparison** (`<` ↔ `<=`, `&&` ↔ `||`) or negation
- an **off-by-one** in a bound, slice, or index
- a **narrowed or widened type**, scope, or visibility
- an **inconsistent rename** — a call site left pointing at the old symbol, or the new name colliding with an existing
  one
- error handling, logging, or a side effect quietly added or removed

A `pattern` claim is refuted when the hunk **deviates from its named exemplar** in a material way: it omits a step the
exemplar performs, reorders something load-bearing, or adapts the pattern in a way that changes behavior rather than
merely instantiating it. Read the exemplar and compare.

A hunk that cannot be fully verified as innocent — the surrounding code too tangled, the claim untestable from what is
on disk — is a **hit**. The audit fails closed toward human review.

## Procedure

1. Take from the caller the cheap-tier hunk list (or manifest), the diff targets — worktree paths, base refs, exact
   `git diff` commands — and a **sampling budget**.
2. Select the sample within the budget, hardest-looking first: the largest hunks, hunks touching control flow or
   defaults, and any the classifier marked on-the-line.
3. For every sampled hunk, run the diff, read the hunk and surrounding code — and the named exemplar for `pattern` — and
   try to refute the claim.
4. Record a **hit** when the claim is refuted, naming the hidden decision; record **survives** only after trying and
   failing to refute it, naming what was checked. Never confirm a claim that was not attacked.
5. Record every budgeted-out cheap-tier hunk under **not audited (budget)**, by exact id — no silent caps, no implied
   clearance.

## Output contract

Report so the caller can promote hits and compute the audit metrics:

```text
## hits   (promote to novel)
- <repo>/<file>@@<line>  was <tier>: <the hidden decision the claim omitted>

## survives
- <repo>/<file>@@<line>  was <tier>: <what was checked; why the claim holds>

## not audited (budget)
- <repo>/<file>@@<line>  was <tier>
```

Close with one line: hunks sampled / hits / cheap-tier hunks not audited. If every sampled claim survives, say so
plainly — a clean audit is a real result.
