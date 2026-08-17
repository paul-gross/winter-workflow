# Architecture review axis

This axis reviews source-code changes for conformance to the target's established rules about how its code must be shaped — layers, boundaries, abstractions, structure, and declared design principles. It judges shape against declaration only: route behavioral defects to the correctness axis and quality-attribute trade-offs to the qualities axis rather than judging them here. The axis consumes the semantic review inputs prepared by the review process at [../process.md](../process.md).

## Criteria discovery

Discover principles by starting at the workspace and target agent-context entrypoints and following their routes to the declared owners of the architecture, design, and structural facts relevant to the changed area — governing architecture documents, exemplars, contribution conventions, and in-flight initiatives.

- Never assume the target's principles and never treat a familiar filename as authoritative by convention: read a candidate file such as `ARCHITECTURE.md` or an exemplar only as the target routes to or declares it.
- When the entrypoints do not route to an owner for a structural fact the change depends on, report the missing or ambiguous ownership rather than electing a convenient document as canonical.
- Where nothing is declared, judge with general software-design judgment and state explicitly that you are doing so.

## Evaluation areas

- **Principle adherence** — flag violations of declared architecture, design, and structural rules, citing the owner.
- **Layer separation** — business logic or responsibilities leaking across declared layers or module boundaries.
- **Coupling and boundaries** — tight coupling across seams, missing boundaries, and concepts the declared design says belong encapsulated together.
- **Abstraction level** — abstractions at the wrong altitude and names that misrepresent the abstraction they label, while ignoring trivial naming preference.
- **Pattern conformance** — divergence from the target's established patterns and exemplars without a declared reason.
- **Complexity, in both directions** — unnecessary abstraction, premature generalization, and over-engineering, and equally structure the declared design requires that the change lacks.

A structural decision the change had to make with no declared principle to govern it is itself a finding — the gap that lets the target grow its guidance.

## Findings

- Substantiate every finding from the code and the declaration it violates, and drop any finding you cannot substantiate.
- What a finding reports as violated is the owning declaration — cite it in every finding it applies to — or the ownership gap.
- Formatting, style, and trivial naming preferences are never findings.

## Severity

- **must-fix** — a violation of a declared principle, dangerous coupling, a broken abstraction, or a missing boundary likely to cause real problems.
- **consider** — a better-fitting pattern, a cleaner boundary, or a meaningful simplification.
- **notes** — concise routing of a behavioral or quality-attribute concern to its owning axis, and undeclared-ownership gaps not tied to a specific violation.

## Output

Output follows the shared reporting contract at [../reporting.md](../reporting.md), including its remote-feedback semantics; this axis's default remote feedback is `report`.
