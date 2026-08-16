# Review manifest — tiered diff review

A review manifest is an advisory reading guide for a human reviewing a change-set. It orders attention by decision density; it gates nothing and does not replace the review.

| File | Read when… |
|------|------------|
| [`./format.md`](./format.md) | You are writing or reading a manifest file and need the on-disk contract it is held to |
| [`./classification.md`](./classification.md) | You need the tier semantics and classifier decision rules shared by every producer, auditor, renderer, and human reader |
| [`./audit.md`](./audit.md) | You are adversarially auditing a manifest's cheap-tier claims, or consuming an audit's results |
| [`./process.md`](./process.md) | You are generating a manifest by fresh classification of a finished diff — the classify → audit → render control flow |
| [`./build-time.md`](./build-time.md) | You are building a change and capturing each hunk's tier, claim, and intent as you write |
