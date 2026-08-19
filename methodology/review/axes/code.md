# Code review axis

This axis reviews source-code changes with one goal: find what is not good enough to ship — incorrect behavior,
structural weakness, violations of the target's documented design principles, and tests that fail to hold the change to
its claims. It consumes the semantic review inputs prepared by the review process at [../process.md](../process.md).

Treat the change as unproven until you have attacked it: the job is finding where it is wrong, weak, or below the
target's declared bar — never summarizing, appreciating, or certifying it. Plausible-looking code is where defects live
— a clean-reading change has survived only its author's framing, the reviewer is its first hostile reader, and "it reads
fine" is a starting condition rather than a verdict. An empty report is a strong claim — that every attack line was run
against the change and held — and must be earned before it is made.

Spend no attention on praise, and none on formatting, style, or trivial naming preferences; none of these is a finding.

## Criteria discovery

Discover criteria by starting at the workspace and target agent-context entrypoints and following their routes to the
declared owners of the architecture, design, and style facts relevant to the changed area. Review against the discovered
declared principles and cite their owner in each applicable finding.

- Follow target-owned indexes and explicit links to any governing architecture document, contribution convention, or
  in-flight initiative, and read a candidate such as `CONTRIBUTING.md` or `ARCHITECTURE.md` only as the target routes or
  declares it.
- Never assume the target's principles and never treat a familiar filename as authoritative by convention.
- Treat `methodology/` as the owner of reusable operations rather than generic target architecture or style facts: read
  a methodology leaf only when a declared target rule says that operation governs the change, and never mine methodology
  broadly for design criteria.
- When the entrypoints do not route to an owner for a relevant fact, report the missing or ambiguous ownership rather
  than electing a convenient document as canonical.
- When no design principles are documented, use general software-design judgment and note the missing documented
  standard so the target can bootstrap one.

## The hunt

Begin by establishing the change's intent from the review material and scope, stating what the change claims to do,
because several attack lines test the code against its claims. Then enumerate the attack lines against this specific
change and pursue each to a conclusion — never read the diff once and report whatever surfaced, because the defects
worth finding are the ones a single pass misses.

Investigate beyond the diff: the diff shows what the author touched, not what the change affects, so read the callers,
implementors, and neighbors of every changed surface and trace data flow through the changed paths rather than assuming
the surrounding code still holds.

## Attack lines

- **Broken behavior** — trace concrete inputs through every changed path hunting for the input, state, or sequence that
  produces a wrong result: boundary values, empty and error cases, repeated or concurrent invocation, and the path the
  author visibly never exercised.
- **Broken neighbors** — the change's blast radius: callers, implementors, configuration, and cross-repo dependents it
  obligates but does not touch. Read them rather than inferring their safety from the diff.
- **False claims** — names, comments, docstrings, types, and commit messages assert behavior, so check every assertion
  against what the code does; a lying name or a stale comment is a finding.
- **Wrong shape** — coupling across boundaries, responsibilities leaking between layers, abstractions at the wrong
  level, structure the change needed but lacks, and structure it carries but never needed.
- **Principle violations** — judge the change against the discovered criteria and cite the owner; a decision the change
  had to make with no documented criterion to govern it is itself a finding.
- **Weak tests** — ask whether the suite would catch the defects hunted on the other attack lines: assertions that
  cannot fail, tests pinned to implementation rather than behavior, and changed behavior no test pins are findings, as
  are application refactors that would materially simplify the tests.
- **Credible performance harm** — N+1 queries, missing indexes, unbounded growth, excessive rerenders — reported only
  with a concrete mechanism, never on vibes.

## Execution bounds

- A targeted probe — a snippet, a REPL call, a one-off script — is permitted to confirm or refute a specific suspected
  defect.
- Never run the target's test suite as certification: execution-based verification belongs to the verification
  processes, and a green run is not a review.

## Findings

- Re-derive every candidate finding before reporting it: confirm from the code that the failure or weakness actually
  occurs, and drop what you cannot substantiate.
- A suspicion on a load-bearing path that genuinely cannot be resolved is still reportable: state it as an open
  question, explicitly labeled unconfirmed, with the evidence held and what would settle it.
- What a finding reports as violated is the discovered principle or concern.

## Severity

- **must-fix** — incorrect behavior, broken callers or dependents, and structural issues likely to cause real problems,
  including principle violations, dangerous coupling, broken abstractions, and missing boundaries.
- **consider** — real non-blocking improvements: a better-fitting pattern, a meaningful simplification, or a test that
  should pin behavior it currently misses.
- **notes** — concise routing of an out-of-scope concern to another axis.

## Output

Output follows the shared reporting contract at [../reporting.md](../reporting.md). For a local target return the report
to the caller; for a remote PR or MR follow the reporting contract's remote-feedback semantics — this axis's default
feedback is `inline`.
