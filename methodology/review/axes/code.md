# Code review axis

Review source-code changes for correctness, architectural quality, and adherence to the target's documented design principles. Produce high-signal, low-noise findings about problems that matter rather than comments on every changed file.

## Inputs

Consume the semantic review inputs prepared by the [review process](../process.md): scope, in-scope targets, review material, cross-repo framing when applicable, and any remote-feedback destination.

## Discover the criteria

Do not assume the target's principles or treat familiar filenames as authoritative by convention.

1. Start at the workspace and target agent-context entrypoints, then follow their routes to the declared owners of architecture, design, and style facts relevant to the changed area.
2. Follow target-owned indexes and explicit links to any governing architecture document, contribution convention, or in-flight initiative. Read a candidate such as `CONTRIBUTING.md` or `ARCHITECTURE.md` only as the target routes or declares it, not merely because the filename exists.
3. Treat `methodology/` as the owner of reusable operations, not generic target architecture or style facts. Read a methodology leaf only when a declared target rule says that operation governs the change; never mine methodology broadly for design criteria.
4. If the entrypoints do not route to an owner for a relevant fact, report the missing or ambiguous ownership rather than choosing a convenient document as canonical.

Review against the declared principles and cite their owner in each applicable finding. If no design principles are documented, use general software-design judgment and note the missing documented standard so the target can bootstrap one.

## Evidence method

1. Read all review material and establish the change's intent from the code and supplied scope.
2. Read surrounding code to understand existing patterns, boundaries, and conventions.
3. Evaluate the change against the discovered criteria and the checklist below.
4. Report only concrete issues supported by a file and location. Do not invent findings to fill the checklist.

## Checklist

- **Correctness and usefulness**: identify incorrect behavior, dead or useless code, dependencies, and method calls.
- **Principle adherence**: flag violations of documented architecture or design principles.
- **Separation of concerns**: detect business logic or responsibilities leaking across layers.
- **Naming and abstraction level**: assess whether names communicate intent and abstractions sit at the right level; ignore trivial preferences.
- **Coupling and boundaries**: identify tight coupling, missing boundaries, and concepts that should be encapsulated together.
- **Complexity**: flag unnecessary abstractions, premature generalization, and over-engineering.
- **Performance**: identify credible risks such as excessive rerenders, N+1 queries, or missing indexes.
- **Tests**: identify behavior gaps, useless assertions or tests, and application refactors that would simplify the tests.
- **Good decisions**: briefly acknowledge a particularly strong design decision when useful.

Do not report formatting, style, or trivial naming nitpicks. Do not run tests; this axis reviews the code and its tests but does not verify execution.

## Severity

- **must-fix**: correctness failures or structural issues likely to cause real problems, including principle violations, dangerous coupling, broken abstractions, and missing boundaries.
- **consider**: non-blocking improvements such as clearer naming, a better-fitting pattern, or a minor simplification.
- **notes**: brief acknowledgments and concise routing of an out-of-scope concern to another axis.

## Output

Follow the shared [reporting contract](../reporting.md). For every finding, identify the file and location, the principle or concern violated, the evidence, and a concrete direction without writing the replacement.

For a local target, return the report to the caller. For a remote PR or MR, honor its normalized `feedback` value. With `report`, return the findings to the caller without posting them. With `default` or `inline`, use the forge CLI (`gh`, `glab`, `tea`, or equivalent) to leave each finding as a self-contained inline comment on the remote review; each comment must include its finding id, severity, violated principle or concern, proposed direction, and reasoning. Return a concise posting summary only when every attempted post succeeds. If any post fails, return the failure and the affected unposted findings to the caller, and never imply that feedback was posted successfully.
