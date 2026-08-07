# Plan shape

The form conventions for an implementation plan authored under the [planning process](./process.md). The plan-review gate applies this file as the plan's governing conventions through the [`plan` axis](../review/axes/plan.md)'s planning-spec conformance gate; a planning framework's own declared conventions replace it for plans that framework owns.

**A plan is a record of decisions, not an implementation transcript.** Its size scales with decision density — how many choices the builder must not get wrong — never with implementation size, and never with how many review rounds it has survived. The builder owns the mechanism; the build verifies it. Prose mechanism cannot be compiled or executed, so every mechanism passage a plan carries can be judged only by a reviewer reading it — which generates findings, which generate prose, which generates findings.

## What a plan owns

- **Intent and scope boundary** — what the change is, in a few sentences, and what is explicitly out.
- **Structural outcome** — the new or changed interfaces, modules, and seams, and where each lives: what exists after the change that does not exist now.
- **Decisions with their governing rule** — each architectural choice the builder must not get wrong, citing the architecture-guidance rule it answers to.
- **Verification bindings** — each planned change mapped to a declared verifiability-matrix method id, or the scheduled work to build the missing method first.
- **Phases** — ordered, independently verifiable increments, each with acceptance criteria stated against the verification bindings, covering every surface the change owes (code, agent-facing context, public docs).
- **Tested assumptions** — load-bearing claims about the target that were checked against it, with the evidence. Measured evidence that falsifies or confirms a premise prevents findings; keep it.

## What a plan must not contain

- **Mechanism prose** — function bodies, algorithms, or control flow narrated in English. Name the seam and the responsibility; let the builder write the mechanism where the compiler and tests can judge it.
- **Restated facts** — content the target codebase, its harness, or another document already owns. Point to the owner instead; a restatement is a second copy that can drift and a second surface that can be reviewed.
- **More than one worked example** per genuinely novel pattern, and none for a pattern the codebase already exhibits.
- **Defensive prose** — text addressed to a hypothetical reviewer rather than the builder: justifications, reassurances, and anticipated-objection clauses accreted across review rounds.
- **Test enumerations** — lists of individual test cases beyond the phase acceptance criteria; case selection belongs to the builder and the verify finale.

## The removability rule

Every passage must change what the builder does. A passage whose deletion would alter nothing about the resulting build is removable, and removable text is a conformance violation — the gate reviews it as an unmet obligation of this spec, directing deletion rather than revision.
