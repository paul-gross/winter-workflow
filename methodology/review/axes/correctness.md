# Correctness review axis

This axis reviews source-code changes for one question: does the change do what it claims, without breaking anything it
touches? It owns defect-hunting depth — broken behavior, broken neighbors, and false claims. Structural conformance and
quality-attribute trade-offs belong to sibling axes — route them there rather than judging them here. The axis consumes
the semantic review inputs prepared by the review process at [../process.md](../process.md).

Treat the change as unproven until you have attacked it: plausible-looking code is where defects live, a clean-reading
change has survived only its author's framing, and the reviewer is its first hostile reader. An empty report is a strong
claim — that every attack line was run to a conclusion and the change held — and must be earned before it is made.

## Establish the claims

Correctness is judged against what the change claims, so establish the claims before hunting. The claims sources:

- **Stated intent** — commit messages across the reviewed range, the linked plan or work item, and the scope's framing.
- **In-code assertions** — names, docstrings, comments, type signatures, and the behaviors the tests pin.
- **Declared behavioral invariants** — discovered through the workspace and target agent-context entrypoints: domain
  rules, protocol contracts, and any declared verification methods for the changed area.

## Attack lines

Pursue each attack line to a conclusion; never read the diff once and report whatever surfaced. The diff shows what the
author touched, not what the change affects: trace data flow through the changed paths rather than assuming the
surrounding code still holds.

- **Broken behavior** — trace concrete inputs through every changed path hunting for the input, state, or sequence that
  produces a wrong result: boundary values, empty and error cases, repeated or concurrent invocation, interrupted or
  partial execution, and the path the author visibly never exercised.
- **Broken neighbors** — the change's blast radius: callers, implementors, configuration, serialized state, and
  cross-repo dependents it obligates but does not touch. Read them, and never infer their safety from the diff.
- **False claims** — check every discovered claim against what the code does: a name, comment, docstring, type, or
  commit message asserting behavior the code does not deliver is a finding, as is a test whose name promises a check its
  assertions do not make.

## Execution bounds

- A targeted probe — a snippet, a REPL call, a one-off script — is permitted to confirm or refute a specific suspected
  defect.
- Never run the target's test suite as certification: execution-based verification belongs to the verification
  processes, and a green run is not a review.

## Findings

- Re-derive every candidate finding before reporting it: confirm from the code that the failure actually occurs, and
  drop what you cannot substantiate.
- A suspicion on a load-bearing path that genuinely cannot be resolved is still reportable: state it as an open
  question, explicitly labeled unconfirmed, with the evidence held and what would settle it.
- What a finding reports as violated is the claim or behavior.

## Severity

- **must-fix** — confirmed incorrect behavior, a broken caller or dependent, or a false claim on a load-bearing surface.
- **consider** — fragile-but-currently-working behavior, a missing guard on a plausible path, or a claim worth
  tightening.
- **notes** — concise routing of a structural or quality-attribute concern to its owning axis.

## Output

Output follows the shared reporting contract at [../reporting.md](../reporting.md), including its remote-feedback
semantics; this axis's default remote feedback is `inline`.
