# Architecture review axis

Review source-code changes for conformance to the target's established rules about how its code must be shaped — layers, boundaries, abstractions, structure, and declared design principles. This axis judges shape against declaration; behavioral defects belong to the correctness axis and quality-attribute trade-offs to the qualities axis — route them, don't judge them here.

## Inputs

Consume the semantic review inputs prepared by the [review process](../process.md): scope, in-scope targets, review material, cross-repo framing when applicable, and any remote-feedback destination.

## Discover the principles

Do not assume the target's principles or treat familiar filenames as authoritative by convention.

1. Start at the workspace and target agent-context entrypoints, then follow their routes to the declared owners of architecture, design, and structural facts relevant to the changed area — governing architecture documents, exemplars, contribution conventions, and in-flight initiatives.
2. Read a candidate such as `ARCHITECTURE.md` or an exemplar file only as the target routes or declares it, not merely because the filename exists.
3. If the entrypoints do not route to an owner for a structural fact the change depends on, report the missing or ambiguous ownership rather than choosing a convenient document as canonical.

Cite the owning declaration in every applicable finding. A structural decision the change had to make with no declared principle to govern it is itself a finding — the gap that lets the target grow its guidance. Where nothing is declared, judge with general software-design judgment and say that you are.

## The review

Evaluate the change against the discovered principles:

- **Principle adherence** — flag violations of declared architecture, design, and structural rules, citing the owner.
- **Layer separation** — business logic or responsibilities leaking across declared layers or module boundaries.
- **Coupling and boundaries** — tight coupling across seams, missing boundaries, and concepts that the declared design says belong encapsulated together.
- **Abstraction level** — abstractions at the wrong altitude, and names that misrepresent the abstraction they label; ignore trivial naming preference.
- **Pattern conformance** — divergence from the target's established patterns and exemplars without a declared reason.
- **Complexity in both directions** — unnecessary abstraction, premature generalization, and over-engineering; equally, structure the declared design requires that the change lacks.

Substantiate every finding from the code and the declaration it violates; drop what you cannot substantiate. Formatting, style, and trivial naming preferences are not findings.

## Severity

- **must-fix**: a violation of a declared principle, dangerous coupling, a broken abstraction, or a missing boundary likely to cause real problems.
- **consider**: a better-fitting pattern, a cleaner boundary, a meaningful simplification.
- **notes**: concise routing of a behavioral or quality-attribute concern to its owning axis, and undeclared-ownership gaps not tied to a specific violation.

## Output

Follow the shared [reporting contract](../reporting.md), including its remote-feedback semantics with a default of `report`. For every finding, identify the file and location, the declaration violated (or the gap), the evidence, and a concrete direction without writing the replacement.
