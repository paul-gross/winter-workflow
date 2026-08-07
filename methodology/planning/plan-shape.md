# Plan shape

The form conventions for an implementation plan authored under the [planning process](./process.md). The plan-review gate applies this file as the plan's governing conventions through the [`plan` axis](../review/axes/plan.md)'s planning-spec conformance gate; a planning framework's own declared conventions replace it for plans that framework owns.

**A plan is a record of decisions, not an implementation transcript.** Its size scales with decision density — how many choices the builder must not get wrong — never with implementation size, and never with how many review rounds it has survived. The builder owns the mechanism; the build verifies it. Prose mechanism cannot be compiled or executed, so every mechanism passage a plan carries can be judged only by a reviewer reading it — which generates findings, which generate prose, which generates findings.

## Altitude

Pick the plan's altitude **first**, from what is being built, and declare it in the plan's opening line with the expected shape of the change that selected it. Altitude enables and disables the standards below: a section the altitude disables is not rigor, it is detail below altitude — removable on sight. Two standards are never disabled — **acceptance criteria** and **verification bindings** exist at every altitude and only shrink with the change; what altitude scales is decomposition and structural detail.

| Altitude | The work | The plan |
|----------|----------|----------|
| **one-liner** | One change in one place — a fix, a tweak, a single-file adjustment | A few sentences: the change, its acceptance criterion, and its verification binding. Phases, structural outcome, and decision records are disabled |
| **single-phase** | One coherent change in one module or repository, buildable and verifiable as a single increment | Intent, structural outcome, verification bindings, acceptance criteria; a decision entry only where a choice could be got wrong. Phase decomposition is disabled — the plan is one implicit phase |
| **phased** | A feature spanning modules or surfaces, or needing ordered, independently verifiable increments | The full owns-list below, phases included |
| **epic** | Multiple features or work items delivered over time | The decomposition only: the items, their sequence, the cross-cutting decisions and seams they share, and per-item acceptance criteria at the item level. Item-level structural detail is disabled — each item gets its own lower-altitude plan |

The gate judges the selection as well as the content: work that outgrows the declared altitude re-bands upward (a "one-liner" hiding a multi-module feature is a finding), and detail below the declared altitude is a finding directing deletion (a single-file fix carrying phases and a structural-outcome section is the same defect in the other direction). When review rounds keep adding material that the declared altitude disables, the altitude selection — not the material — is what to revisit.

## What a plan owns

The full set, enabled per altitude:

- **Intent and scope boundary** — what the change is, in a few sentences, and what is explicitly out.
- **Structural outcome** — the new or changed interfaces, modules, and seams, and where each lives: what exists after the change that does not exist now.
- **Decisions with their governing rule** — each architectural choice the builder must not get wrong, citing the architecture-guidance rule it answers to.
- **Verification bindings** — each planned change mapped to a declared verifiability-matrix method id, or the scheduled work to build the missing method first. Enabled at every altitude, down to the one-liner.
- **Acceptance criteria** — how done is judged, stated against the verification bindings. Enabled at every altitude: phases carry them when phases exist; the plan states them directly at lower altitudes.
- **Phases** — ordered, independently verifiable increments, each with acceptance criteria, covering every surface the change owes (code, agent-facing context, public docs).
- **Tested assumptions** — load-bearing claims about the target that were checked against it, with the evidence. Measured evidence that falsifies or confirms a premise prevents findings; keep it at any altitude where the claim is load-bearing.

## What a plan must not contain

At any altitude:

- **Mechanism prose** — function bodies, algorithms, or control flow narrated in English. Name the seam and the responsibility; let the builder write the mechanism where the compiler and tests can judge it.
- **Restated facts** — content the target codebase, its harness, or another document already owns. Point to the owner instead; a restatement is a second copy that can drift and a second surface that can be reviewed.
- **More than one worked example** per genuinely novel pattern, and none for a pattern the codebase already exhibits.
- **Defensive prose** — text addressed to a hypothetical reviewer rather than the builder: justifications, reassurances, and anticipated-objection clauses accreted across review rounds.
- **Test enumerations** — lists of individual test cases beyond the phase acceptance criteria; case selection belongs to the builder and the verify finale.

## The removability rule

Every passage must change what the builder does, at the plan's declared altitude. A passage whose deletion would alter nothing about the resulting build, and any passage the declared altitude disables, is removable — the gate reviews removable text as an unmet obligation of this spec, directing deletion rather than revision.
