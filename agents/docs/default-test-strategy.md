# Default Test Strategy

This document is used by the `test-mediator` agent during the **Test Strategy Bootstrap Workflow**. When a project has no documented test strategy, the test-mediator proposes these defaults. Each element is explained for agent consumption with concrete guidance on how to apply it.

The user may accept these as-is, modify them, or specify an entirely different strategy.

---

## Verification Layers

Every change should be verified at the appropriate layer. Not every change needs every layer — match the verification to the risk.

- **Build verification** — Does the code compile/transpile without errors? This is the minimum bar. Every change gets this. In practice: run the project's build command and confirm zero errors before moving on.

- **Unit verification** — Do individual functions and classes behave correctly in isolation? Use for logic-heavy code, pure functions, and business rules. In practice: if you wrote a function with branching logic, write a test that covers each branch. Mock external dependencies at the boundary.

- **Integration verification** — Do components work together correctly? Use when the change involves communication between layers (API to database, service to service, frontend to API). In practice: test the real interaction — hit an actual endpoint, read from an actual database, verify the full round-trip.

- **Runtime verification** — Does the application work correctly when running? Use for any change that affects user-facing behavior. In practice: start the services, perform the operation as a user would (via API calls or browser interaction), and verify the result.

## Test Data Strategy

Test data is the foundation of reliable verification. Bad test data produces false positives and false negatives.

- **Deterministic setup** — Tests should create the data they need, not depend on pre-existing state. In practice: each test scenario should set up its own preconditions (seed records, create entities, configure state) and not assume anything about what's already in the database.

- **Minimal data** — Create only what the test needs. Bloated test data obscures what's being tested. In practice: if you're testing a single entity's behavior, create that one entity with its required parents — not the entire world.

- **Cleanup awareness** — Understand whether the project uses transaction rollback, database reset, or persistent test data. Adapt the strategy accordingly. In practice: read the project's testing docs to understand the cleanup mechanism before generating test data.

- **Reusable generators** — When the same data shape is needed repeatedly, it should be a reusable script or fixture, not copy-pasted setup in every test. In practice: if three test scenarios all need "a user with an active session," that setup should be a single callable function or seed script.

## Verification Scope Rules

Not everything needs the same depth of testing. Match effort to risk.

- **High risk (broad scope)** — New features, behavior changes, security-related code, data migration. Test at all applicable layers. Include edge cases and error paths.

- **Medium risk (targeted scope)** — Bug fixes, refactors that change structure but not behavior. Test the specific fix plus one layer of integration. Verify the bug is fixed and nothing adjacent broke.

- **Low risk (build + spot check)** — Renames, documentation, config changes, style-only UI changes. Build verification plus a quick runtime spot check if it touches anything rendered.

## Test Scenario Design

When defining test scenarios, cover these categories in order of priority:

1. **Happy path** — The intended use case works correctly
2. **Validation/input errors** — Bad input is rejected gracefully
3. **Edge cases** — Boundary values, empty states, maximum limits
4. **Error recovery** — The system handles failures (network errors, missing data, timeouts) without corruption
5. **Regression** — Previously fixed bugs don't reappear; adjacent features still work
