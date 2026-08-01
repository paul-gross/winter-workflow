# Test review axis

Review the change's tests against the target's declared testing requirements: do the tests accompanying the change actually hold it to its claims, at the levels the target requires? Behavioral defects in the application code belong to the correctness axis and code-shape concerns to the architecture axis — route them, don't judge them here.

## Inputs

Consume the semantic review inputs prepared by the [review process](../process.md): scope, in-scope targets, review material, cross-repo framing when applicable, and any remote-feedback destination.

## Discover the testing requirements

1. Route from the workspace and target agent-context entrypoints to the target's declared testing conventions and capabilities — test layout and level requirements, coverage expectations, declared verification methods, and any project testing harnesses the tests are expected to use.
2. Where the target declares nothing for a concern, review against the basic testing pyramid — many fast unit tests at the base, fewer integration tests above them, few end-to-end tests at the top — and note the missing declared standard so the target can bootstrap one.

Cite the owning declaration (or the pyramid default) in each applicable finding.

## The review

- **Unpinned behavior** — changed or new behavior no test pins: the regression the target could reintroduce tomorrow without a test failing.
- **Assertions that cannot fail** — tautological assertions, over-mocked tests that verify the mock, tests that pass regardless of the behavior under test.
- **Implementation-pinned tests** — tests coupled to implementation detail rather than behavior, which break on a safe refactor and stay green on a regression.
- **Wrong level** — checks living at the wrong level for the declared requirements or the pyramid default: an end-to-end test asserting what a unit test owns, a unit test stubbing so much of the world it silently became an integration test.
- **Test debt the change creates** — useless or dead tests left behind, and application refactors that would materially simplify the tests.

Substantiate every finding from the tests and the code under test; drop what you cannot substantiate. Execution is bounded to targeted probes that confirm or refute a specific suspected weakness — such as running one test against a hand-broken behavior to show it stays green. Do not run the target's test suite as certification: execution-based verification belongs to the verification processes, and a green run is not a review.

## Severity

- **must-fix**: changed behavior with no pinning test where the declared requirements demand one, an assertion that cannot fail on a load-bearing path, or a violation of a declared testing requirement.
- **consider**: a check at a better level, a worthwhile additional edge, a meaningful test simplification.
- **notes**: concise routing of a correctness or code-shape concern to its owning axis, and missing-declaration gaps not tied to a specific weakness.

## Output

Follow the shared [reporting contract](../reporting.md), including its remote-feedback semantics with a default of `report`. For every finding, identify the file and location, the requirement violated (or the gap), the evidence, and a concrete direction without writing the replacement.
