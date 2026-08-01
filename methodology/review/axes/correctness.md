# Correctness review axis

Review source-code changes for one question: does the change do what it claims, without breaking anything it touches? This axis owns defect-hunting depth — broken behavior, broken neighbors, and false claims. Structural conformance and quality-attribute trade-offs belong to sibling axes; route them, don't judge them here.

## Inputs

Consume the semantic review inputs prepared by the [review process](../process.md): scope, in-scope targets, review material, cross-repo framing when applicable, and any remote-feedback destination.

## Stance

The change is unproven until you have attacked it. Plausible-looking code is where defects live: a clean-reading change has survived only its author's framing, and you are its first hostile reader. An empty report is a strong claim — that you ran every attack line below to a conclusion and the change held — and you must earn it before making it.

## Discover the claims

Correctness is judged against what the change claims, so establish the claims first:

1. The stated intent — commit messages across the reviewed range, linked plan or work item, and the scope's framing.
2. The in-code assertions — names, docstrings, comments, type signatures, and the behaviors the tests pin.
3. The target's declared behavioral invariants, discovered through the workspace and target agent-context entrypoints — domain rules, protocol contracts, and any declared verification methods for the changed area.

## The hunt

Pursue each attack line to a conclusion; do not read the diff once and report whatever surfaced. The diff shows what the author touched, not what the change affects — trace data flow through the changed paths rather than assuming the surrounding code still holds.

- **Broken behavior** — trace concrete inputs through every changed path and hunt for the input, state, or sequence that produces a wrong result: boundary values, empty and error cases, repeated or concurrent invocation, interrupted or partial execution, and the path the author visibly never exercised.
- **Broken neighbors** — the change's blast radius: callers, implementors, configuration, serialized state, and cross-repo dependents it obligates but does not touch. Read them; never infer their safety from the diff.
- **False claims** — check every discovered claim against what the code does. A name, comment, docstring, type, or commit message that asserts behavior the code does not deliver is a finding; so is a test whose name promises a check its assertions don't make.

## Substantiation

Re-derive every candidate finding before reporting it: confirm from the code that the failure actually occurs, and drop what you cannot substantiate.

You may run a targeted probe — a snippet, a REPL call, a one-off script — to confirm or refute a specific suspected defect. Do not run the target's test suite as certification: execution-based verification belongs to the verification processes, and a green run is not a review.

A suspicion on a load-bearing path that you genuinely cannot resolve is still reportable: state it as an open question with the evidence you have and what would settle it, explicitly labeled unconfirmed.

## Severity

- **must-fix**: confirmed incorrect behavior, a broken caller or dependent, or a false claim on a load-bearing surface.
- **consider**: fragile-but-currently-working behavior, a missing guard on a plausible path, a claim worth tightening.
- **notes**: concise routing of a structural or quality-attribute concern to its owning axis.

## Output

Follow the shared [reporting contract](../reporting.md), including its remote-feedback semantics with a default of `inline`. For every finding, identify the file and location, the claim or behavior violated, the evidence, and a concrete direction without writing the replacement.
