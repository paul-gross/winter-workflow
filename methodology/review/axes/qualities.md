# Qualities review axis

This axis reviews source-code changes against the software qualities the target has chosen to prioritize — the architectural 'ilities and the trade-offs between them. Every application trades software qualities off differently, so the axis judges the change against the target's declared position, never a universal standard: a one-nine service is not held to five-nines standards, and hardening it as if it were is a finding of over-engineering, not a virtue. Behavioral defects belong to the correctness axis and code-shape conformance to the architecture axis — route them there rather than judging them here. The axis consumes the semantic review inputs prepared by the review process at [../process.md](../process.md).

## Trait discovery

The review criteria are the target's own declared quality commitments, so establish them before reviewing. Enumerate every quality commitment the target declares, in the target's own vocabulary, by routing from the workspace and target agent-context entrypoints to wherever such commitments live — architecture guidance, operational and deployment documentation, infrastructure and capacity configuration, SLO or availability declarations, threat models, compliance obligations, and promises made in adopter-facing docs.

- Record each discovered trait with its magnitude, because the magnitude is the criterion.
- Expect the target to declare qualities this axis document never names — observability, auditability, data durability, cost, portability, offline operation, or anything else — and carry them into the review with equal weight.
- When the change forces a trade-off on a trait the target has never declared a position on, report the missing declaration as a gap, then judge conservatively from the evident current posture — existing infrastructure, operational tooling, and documented behavior — and say that you did.

## The review

The trait inventory from discovery is the checklist: iterate it, not the common-trait examples. For each discovered trait, determine whether the change upholds it, degrades it, or silently ignores it at its declared magnitude. Flag a change that silently shifts a declared trade-off even when no single trait is violated outright — such as introducing a stateful component into a tier the target declares horizontally scalable.

Common-trait question forms:

- **Performance** — declared budgets and credible mechanisms of regression, never on vibes.
- **Scalability and capacity** — does the change hold at the declared scale target: growth of state, fan-out, contention, per-request cost?
- **Availability and reliability** — failure modes, retries, timeouts, and degradation paths measured against the declared SLA.
- **Security** — the change against the declared posture and threat model, and its handling of data the target declares sensitive.
- **Deployability** — migration safety, rollout ordering, and compatibility windows measured against the declared deployment model, such as zero-downtime.
- **Extensibility and maintainability** — declared pluggability seams, public contracts, and evolution commitments the change forecloses or honors.

A review whose findings touch only the common example traits has reviewed the template rather than the target — return to the discovered inventory.

## Findings

- Substantiate every finding with the declared trait, its magnitude, and the concrete mechanism by which the change affects it, and drop what you cannot substantiate.
- What a finding reports as violated is the declared trait at its magnitude — or the missing-declaration gap — with the mechanism.

## Severity

- **must-fix** — a change that degrades a declared trait at its declared magnitude or forecloses a declared commitment.
- **consider** — tension with a declared trait that current usage tolerates, a cheap strengthening of a declared trait, or over-engineering toward a trait nobody declared.
- **notes** — concise routing of a correctness or code-shape concern to its owning axis, and missing-declaration gaps not tied to a specific degradation.

## Output

Output follows the shared reporting contract at [../reporting.md](../reporting.md), including its remote-feedback semantics; this axis's default remote feedback is `report`.

Append a `## Trait inventory` section after the normal report, included even when no findings exist: name the discovered trait inventory and where each trait is declared, so the caller can see what the review was measured against.
