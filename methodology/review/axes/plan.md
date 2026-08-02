# Plan review axis

Review an implementation plan before any building, with one goal: catch the plan that would produce unverifiable work or the wrong shape while it is still cheap to change. The plan is judged against the two artifacts the target application's harness declares — its **verifiability matrix** (how the application's changes are asserted correct) and its **architecture guidance** (how its code must be shaped) — and against the planning specs that govern the plan's own form.

## Inputs

Consume the semantic review inputs prepared by the [review process](../process.md): scope, in-scope targets, review material, cross-repo framing when applicable, and any remote-feedback destination. The natural scope is paths naming a refined work item's plan directory or a plan file; filter the supplied set to the plan documents and their planning companions, and review their current state, not a diff. If the supplied scope contains no plan document, return one sentence saying so and stop.

This axis additionally requires the **work-target absolute path(s)** — the application repository or repositories the plan is judged against — supplied by the process's execution scaffold. The plan artifact commonly lives outside those repositories (a work-item directory or a workspace artifact directory), so never substitute the plan file's own location for the work target.

## Discover the criteria

Do not assume the target's layout or treat familiar filenames as authoritative by convention.

1. Start at the workspace and the supplied work target's agent-context entrypoints and follow their routes to the application's **verifiability matrix** and **architecture guidance** where its own harness declares them. Do not assume a directory layout, filename convention, or index path.
2. When a planning framework owns the plan — it lives in the framework's work-item layout, or the caller names the framework — follow that framework's declared conventions for what a plan must contain: required sections, phase structure, artifact locations.
3. If the entrypoints do not route to a matrix or guidance, that absence is itself reviewable: report the gap, and judge whether the plan acknowledges it and schedules bootstrapping the missing artifact rather than silently assuming verification or architectural criteria exist.

## The gates

Run every gate over the plan; each unmet obligation is a finding.

- **Verifiability gate** — every planned change maps to a verification method the matrix declares, or the plan schedules the work to build the missing method (and record its matrix row) before anything depends on that change being correct. A planned change with neither is a finding; so is a mapping to a declared method that does not actually exercise the changed surface.
- **Architecture gate** — the structure the plan commits to conforms to the architecture guidance: layers, boundaries, abstractions, and declared design principles. Cite the guidance a proposed decision violates. A structural decision the plan must make that no guidance governs is a gap finding.
- **Planning-spec conformance** — the plan conforms to the specs that govern its own form: the owning planning framework's declared plan conventions when one applies, and the plan's internal consistency either way — planned work that covers the stated scope, no contradiction between the stated goal and the planned changes, and no step that depends on an artifact no earlier step produces.

Substantiate every finding from the plan text and the declaration it violates, and drop what you cannot substantiate. You may read the target codebase to test a load-bearing plan assumption — a file the plan says exists, a seam it claims is free — but do not redesign the feature: review the plan the author wrote, not the plan you would have written.

## Severity

- **must-fix**: a planned change with no declared verification method and no scheduled build of one; a plan that violates the architecture guidance; a load-bearing plan assumption the target contradicts; a contradiction or omission that would misdirect building.
- **consider**: a sharper phase or scope split, a better-fitting verification method the matrix already declares, plan structure the owning specs recommend but do not require.
- **notes**: concise routing of an out-of-scope concern to another axis, and undeclared-ownership gaps — a missing matrix or guidance — not tied to a specific planned change.

## Output

Follow the shared [reporting contract](../reporting.md). This axis's default remote feedback is `report`. For a remote target, use the appropriate forge CLI to fetch the material; return findings to the caller unless the semantic inputs explicitly request remote inline comments. For every finding, identify the plan location, the gate and declaration violated (or the gap), the evidence, and a concrete direction without rewriting the plan.

The report is the gate verdict a caller consumes: no must-fix findings means the plan passes the gate.
