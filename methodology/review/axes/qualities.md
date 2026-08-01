# Quality attribute review axis

Review source-code changes against the software qualities the target has chosen to prioritize — the architectural 'ilities and the trade-offs between them. Every application trades these off differently: one serves twenty million concurrent users behind a five-nines SLA with zero-downtime deploys, another serves twenty users with none of that. This axis judges the change against the target's declared position, not against a universal standard. Behavioral defects belong to the correctness axis and code-shape conformance to the architecture axis — route them, don't judge them here.

## Inputs

Consume the semantic review inputs prepared by the [review process](../process.md): scope, in-scope targets, review material, cross-repo framing when applicable, and any remote-feedback destination.

## Discover the declared traits

The review criteria are the target's own declared quality commitments, so establish them first:

1. Enumerate every quality commitment the target declares, in the target's own vocabulary. Route from the workspace and target agent-context entrypoints to wherever such commitments live — architecture guidance, operational and deployment documentation, infrastructure and capacity configuration, SLO or availability declarations, threat models, compliance obligations, and promises made in adopter-facing docs. Expect the target to declare qualities this document never names — observability, auditability, data durability, cost, portability, offline operation, or anything else — and carry them into the review with equal weight.
2. Record each discovered trait with its magnitude. The magnitude is the criterion: a one-nine service is not held to five-nines standards, and hardening it as if it were is a finding of over-engineering, not a virtue.
3. If the change forces a trade-off on a trait the target has never declared a position on, report the missing declaration as a gap, then judge conservatively from the evident current posture — existing infrastructure, operational tooling, and documented behavior — and say that you did.

## The review

The trait inventory from discovery is the checklist — iterate it, not the examples below. For each discovered trait, determine whether the change upholds it, degrades it, or silently ignores it at its declared magnitude. The question form, shown for common traits:

- **Scalability and capacity** — does the change hold at the declared scale target: growth of state, fan-out, contention, per-request cost?
- **Availability and reliability** — failure modes, retries, timeouts, and degradation paths measured against the declared SLA.
- **Deployability** — migration safety, rollout ordering, and compatibility windows measured against the declared deployment model, such as zero-downtime.
- **Security** — the change against the declared posture and threat model, and its handling of data the target declares sensitive.
- **Performance** — declared budgets and credible mechanisms of regression; never on vibes.
- **Extensibility and maintainability** — declared pluggability seams, public contracts, and evolution commitments the change forecloses or honors.

A review whose findings touch only traits named above has reviewed this template, not the target — return to the discovered inventory.

Also flag a change that silently shifts a declared trade-off even when no single trait is violated outright — such as introducing a stateful component into a tier the target declares horizontally scalable. Substantiate every finding with the declared trait, its magnitude, and the concrete mechanism by which the change affects it; drop what you cannot substantiate.

Execution is bounded to targeted probes that confirm or refute a specific suspected degradation. Do not run the target's test suite as certification: execution-based verification belongs to the verification processes, and a green run is not a review.

## Severity

- **must-fix**: the change degrades a declared trait at its declared magnitude, or forecloses a declared commitment.
- **consider**: tension with a declared trait that current usage tolerates, a cheap strengthening of one, or over-engineering toward a trait nobody declared.
- **notes**: concise routing of a correctness or code-shape concern to its owning axis, and missing-declaration gaps not tied to a specific degradation.

## Output

Follow the shared [reporting contract](../reporting.md), including its remote-feedback semantics with a default of `report`. Open the report by naming the discovered trait inventory and where each trait is declared, so the caller can see what the review was measured against. For every finding, identify the file and location, the declared trait and magnitude affected (or the gap), the mechanism, and a concrete direction without writing the replacement.
