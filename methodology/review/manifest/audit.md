# Review manifest — adversarial audit

The reusable audit methodology for review manifests from either producer: fresh classification or build-time intent capture. The audit distrusts every sampled cheap-tier claim and tries to find the decision it hides. Runtime agents are ports into this methodology; they do not own or redefine it.

Read [`classification.md`](./classification.md) first. It owns the `mechanical`, `pattern`, and `novel` meanings against which claims are audited.

## Audit posture

Audit only `mechanical` and `pattern` hunks — the ones the manifest claims are safe to skim. Do not audit `novel` hunks; those already go to the human.

The bias is adversarial by design. The classifier asked "is this a rename?" and answered yes; the auditor asks "what did this rename also do?" A manifest is only as trustworthy as its cheapest tier, and the failure that matters is a real decision mislabeled `mechanical` or `pattern` and hidden from the reviewer. **Default to suspicion**: a claim survives only when the audit cannot refute it, not when it sounds plausible.

## What refutes a claim

For each sampled hunk, read the hunk **and the surrounding code**, take the claim at face value, and hunt for anything it omits.

A `mechanical` pure rename, move, or codemod claim is refuted by any behavior change riding along, including:

- a **changed default** value or argument
- a **dropped or added guard clause**, early return, or null check
- a **flipped comparison** (`<` ↔ `<=`, `&&` ↔ `||`) or negation
- an **off-by-one** in a bound, slice, or index
- a **narrowed or widened type**, scope, or visibility
- an **inconsistent rename** — a call site left pointing at the old symbol, or the new name colliding with an existing one
- error handling, logging, or a side effect quietly added or removed

A `pattern` conformance claim is refuted when the hunk **deviates from its named exemplar** in a material way: it omits a step the exemplar performs, reorders something load-bearing, or adapts the pattern in a way that changes behavior rather than merely instantiating it. Read the exemplar and compare.

A hunk that cannot be fully verified as innocent — because the surrounding code is too tangled or the claim is untestable from what is on disk — is a **hit**. The audit fails closed toward human review.

## Sampling

The caller supplies the cheap-tier hunk set and a sampling budget. Audit as many as the budget allows, hardest-looking first: prefer the largest hunks, hunks touching control flow or defaults, and any classifier marked on-the-line. If the budget excludes cheap-tier hunks, report exactly which ids were not audited. No silent caps.

## Procedure

1. Take the manifest or cheap-tier hunk list and the diff targets from the caller: worktree paths, base refs, and exact `git diff` commands.
2. Select the sample within the supplied budget, hardest-first.
3. For every sampled hunk, run the diff, read the hunk and surrounding code, read the named exemplar for `pattern`, and try to refute the claim.
4. Record a **hit** when the claim is refuted, naming the hidden decision. Record **survives** only after trying and failing to refute the claim, naming what was checked.
5. Record every budgeted-out cheap-tier hunk under **not audited (budget)**.

Never confirm a claim that was not attacked. Never silently skip a budgeted-out hunk. The audit reads and refutes; it does not edit code, run tests, or delegate.

## Output contract

Report results so the caller can promote hits and compute audit metrics:

```text
## hits   (promote to novel)
- <repo>/<file>@@<line>  was <tier>: <the hidden decision the claim omitted>

## survives
- <repo>/<file>@@<line>  was <tier>: <what was checked; why the claim holds>

## not audited (budget)
- <repo>/<file>@@<line>  was <tier>
```

Close with one line: hunks sampled / hits / cheap-tier hunks not audited. If every sampled claim survives, say so plainly; a clean audit is a real result.
