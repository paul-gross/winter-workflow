# Code review axis

Review source-code changes with one goal: find what is not good enough to ship — incorrect behavior, structural weakness, violations of the target's documented design principles, and tests that fail to hold the change to its claims. The review's value is measured by the real problems it surfaces.

## Inputs

Consume the semantic review inputs prepared by the [review process](../process.md): scope, in-scope targets, review material, cross-repo framing when applicable, and any remote-feedback destination.

## Stance

The change is unproven until you have attacked it. Your job is to find the ways it is wrong, weak, or below the target's declared bar — not to summarize it, appreciate it, or certify it.

Plausible-looking code is where defects live: a clean-reading change has survived only its author's framing, and you are its first hostile reader. Treat "it reads fine" as the starting condition, not a verdict.

An empty report is a strong claim — that you ran every attack line below against the change and it held. Earn it before you make it.

Spend no attention on praise, and none on formatting, style, or trivial naming preferences; neither is a finding.

## Discover the criteria

Do not assume the target's principles or treat familiar filenames as authoritative by convention.

1. Start at the workspace and target agent-context entrypoints, then follow their routes to the declared owners of architecture, design, and style facts relevant to the changed area.
2. Follow target-owned indexes and explicit links to any governing architecture document, contribution convention, or in-flight initiative. Read a candidate such as `CONTRIBUTING.md` or `ARCHITECTURE.md` only as the target routes or declares it, not merely because the filename exists.
3. Treat `methodology/` as the owner of reusable operations, not generic target architecture or style facts. Read a methodology leaf only when a declared target rule says that operation governs the change; never mine methodology broadly for design criteria.
4. If the entrypoints do not route to an owner for a relevant fact, report the missing or ambiguous ownership rather than choosing a convenient document as canonical.

Review against the declared principles and cite their owner in each applicable finding. If no design principles are documented, use general software-design judgment and note the missing documented standard so the target can bootstrap one.

## The hunt

1. Establish the change's intent from the review material and scope. State what the change claims to do — several attack lines test the code against its claims.
2. Enumerate the attack lines below against this specific change, then pursue each one to a conclusion. Do not read the diff once and report whatever happened to surface — the defects worth finding are the ones a single pass misses.
3. Investigate beyond the diff. The diff shows what the author touched, not what the change affects: read the callers, implementors, and neighbors of every changed surface, and trace data flow through the changed paths rather than assuming the surrounding code still holds.

### Attack lines

- **Broken behavior** — trace concrete inputs through every changed path and hunt for the input, state, or sequence that produces a wrong result: boundary values, empty and error cases, repeated or concurrent invocation, the path the author visibly never exercised.
- **Broken neighbors** — the change's blast radius: callers, implementors, configuration, and cross-repo dependents it obligates but does not touch. Read them; do not infer their safety from the diff.
- **False claims** — names, comments, docstrings, types, and commit messages assert behavior; check every assertion against what the code does. A lying name or a stale comment is a finding.
- **Principle violations** — judge the change against the discovered criteria and cite the owner. A decision the change had to make with no documented criterion to govern it is itself a finding.
- **Wrong shape** — coupling across boundaries, responsibilities leaking between layers, abstractions at the wrong level; structure the change needed but lacks, and structure it carries but never needed.
- **Weak tests** — ask whether the suite would catch the defects you hunted for above. Assertions that cannot fail, tests pinned to implementation rather than behavior, and changed behavior no test pins are findings, as are application refactors that would materially simplify the tests.
- **Credible performance harm** — N+1 queries, missing indexes, unbounded growth, excessive rerenders. Report only with a concrete mechanism, never on vibes.

### Substantiation

Re-derive every candidate finding before reporting it: confirm from the code that the failure or weakness actually occurs, and drop what you cannot substantiate.

You may run a targeted probe — a snippet, a REPL call, a one-off script — to confirm or refute a specific suspected defect. Do not run the target's test suite as certification: execution-based verification belongs to the verification processes, and a green run is not a review.

A suspicion on a load-bearing path that you genuinely cannot resolve is still reportable: state it as an open question with the evidence you have and what would settle it, explicitly labeled unconfirmed.

## Severity

- **must-fix**: incorrect behavior, broken callers or dependents, and structural issues likely to cause real problems — including principle violations, dangerous coupling, broken abstractions, and missing boundaries.
- **consider**: real, non-blocking improvements — a better-fitting pattern, a meaningful simplification, a test that should pin behavior it currently misses.
- **notes**: concise routing of an out-of-scope concern to another axis.

## Output

Follow the shared [reporting contract](../reporting.md). For every finding, identify the file and location, the principle or concern violated, the evidence, and a concrete direction without writing the replacement.

For a local target, return the report to the caller. For a remote PR or MR, follow the reporting contract's remote-feedback semantics; this axis's default feedback is `inline`.
