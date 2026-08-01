# Review manifest — tiered diff review

A review manifest is an advisory reading guide for a human reviewing a change-set. It orders attention by decision density; it does not replace review or gate delivery.

## Routing

| File | Read when… |
|------|------------|
| [`./format.md`](./format.md) | You need the on-disk shape — JSON schema, the markdown document, tier values, invariants, hunk identity, `diff_sha` recipe, metrics |
| [`./classification.md`](./classification.md) | You need the tier semantics and classifier decision rules used by every producer, audit, render, and human reader |
| [`./audit.md`](./audit.md) | You need the reusable adversarial audit methodology and output contract |
| [`./process.md`](./process.md) | You are generating a manifest **by fresh classification** of a finished diff — the classify → audit → render control flow |
| [`./build-time.md`](./build-time.md) | You are **building** a change and accumulating the manifest as you write — capturing intent per hunk, then closing it with the audit + render |
