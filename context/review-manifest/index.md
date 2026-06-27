# Review manifest — tiered diff review

Human review cost scales with diff size, but the need for human judgment scales with **decision density** — a 1,000-line mechanical rename and a 200-line novel abstraction demand the same reviewer attention today, so reviewers stop reading. The review skills ([`cold-review`](../../skills/cold-review/SKILL.md), [`pre-push`](../../skills/pre-push/pre-push-review.md)) surface findings over the whole change-set but do nothing to **shrink the surface a human must trust** — every diff line is presented identically.

A **review manifest** partitions every hunk of a change-set into three verification tiers and renders a *review order* that lands full attention only on the hunks holding real decisions:

| Tier | What it claims | Where attention goes |
|------|----------------|----------------------|
| `mechanical` | rename / move / codemod, no behavior change | a one-line list, skimmed |
| `pattern` | conforms to a named exemplar | collapsed behind the claim |
| `novel` | a new decision | the human, in full |

It is **advisory** — a reading guide for the person reviewing the change, not a gate and not a substitute for the review itself. And it only ever moves attention **toward** the human: every uncertainty (unclassified hunk, contested classification, audit hit) fails closed to `novel`.

Agents *build* the manifest; a **human** is the intended reader of the rendered review document: it tells them what to read in full (`novel`), what to skim (`pattern`), and what to trust (`mechanical`).

## Two producers — classify after, or capture intent while building

The per-hunk tiers and claims can come from either of two producers. The JSON facts shape and the human-facing markdown are identical; only *who fills in the tiers* differs:

- **Cold classification (after the fact)** — a fresh-context [`diff-classifier`](../../agents/diff-classifier.md) k-vote reconstructs the tiers from the finished diff, having never seen the task. Use it to review an existing change-set, a PR, someone else's work, or your own when no manifest was kept while building. This is the [`pipeline.md`](./pipeline.md) flow; its strength is independence — the classifier can't be told "it's just a rename."
- **Build-time intent capture (while writing)** — the agent *building* the change records each hunk's tier, claim, and **intent** as it writes (a `glacier` phase, a `blizzard` developer), so the manifest carries the author's actual reasons rather than a cold guess. Higher fidelity, and no second classification pass. This is the [`build-time.md`](./build-time.md) flow.

The two are **mutually exclusive per hunk** (a hunk is either cold-classified or author-recorded) but share everything downstream: the same JSON facts, the same two invariants, the same markdown render, and — crucially — the **same adversarial audit**. An author's cheap-tier claim ("just a rename") is exactly what the [`manifest-auditor`](../../agents/manifest-auditor.md) exists to distrust, so build-time intent is *recorded by the author but still verified by a skeptic* before it reaches the human. Capturing intent does not relax the fail-closed guarantee.

## Where this fits

| Skill / doc | Scope | Question |
|-------------|-------|----------|
| [`review.md`](../review.md) (engine) | a change-set | *Is this change sound?* (findings, per axis) |
| `review-manifest` (this) | a change-set | *Which hunks actually need me?* (a human's review order) |
| [`cold-review`](../../skills/cold-review/SKILL.md) | a change-set | a cold code review the manifest can also focus |
| [`pre-push`](../../skills/pre-push/pre-push-review.md) | the un-pushed change-set | a multi-axis gate the manifest can also pre-order |

The **primary consumer is a human about to review a large change** — run `review-manifest`, read the review order, and review the `novel` hunks at full attention while skimming the rest. The same review order can *also* focus an agent review: generate it before the `cold-review` or `pre-push` skill to order their attention too. Either way, skip it on a small diff that fits in a glance — and remember the manifest never replaces the review, it only sequences it.

## The two hard invariants

- **Total coverage** — every hunk of the diff is assigned exactly one tier; an unclassified hunk is `novel` by definition. Checked mechanically against the diff.
- **Freshness binding** — the manifest records the SHA of the diff it describes; a stale manifest (recorded SHA ≠ current) is mechanically rejected, never silently reused.

## Routing

| File | Read when… |
|------|------------|
| [`./format.md`](./format.md) | You need the on-disk shape — JSON schema, the markdown document, tier values, invariants, hunk identity, `diff_sha` recipe, metrics |
| [`./pipeline.md`](./pipeline.md) | You are generating a manifest **by cold classification** of a finished diff — the classify → audit → render control flow |
| [`./build-time.md`](./build-time.md) | You are **building** a change and accumulating the manifest as you write — capturing intent per hunk, then closing it with the audit + render |
| [`diff-classifier`](../../agents/diff-classifier.md) | You need the tier *semantics* — what makes a hunk mechanical / pattern / novel |
| [`manifest-auditor`](../../agents/manifest-auditor.md) | You need the adversarial audit — how cheap-tier claims are refuted |

## Scope of this cut

This cut covers both producers (cold classification and build-time intent capture), the adversarial audit, and the render. Two verifications named in the tier table are deliberate follow-ups, not built here:

- **Replay proofs for `mechanical`** — regenerate the change from the claim and byte-compare. Follow-up once the observed tier distribution justifies it.
- **Exemplar judging for `pattern`** — an LLM judge with the named exemplar in context. Follow-up, blocked on curated exemplars; until then the `pattern` tier records a named exemplar but is verified only by the adversarial audit, like `mechanical`.

Gating merges/pushes on manifest state, and cross-change trend dashboards for the metrics, are also out of scope — advisory first.
