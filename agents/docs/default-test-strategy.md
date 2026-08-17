# Default Test Strategy

The default test strategy to propose when a target project has none documented. Everything below this paragraph transcribes into the target project's test-strategy document as the project's own content; the title and this paragraph do not.

## Verification Layers

Match verification to risk — not every change needs every layer.

- **Build verification** — The code compiles/transpiles with zero errors. The minimum bar; every change gets this.
- **Unit verification** — Individual functions and classes behave correctly in isolation. For logic-heavy code, pure functions, and business rules: cover each branch, mocking external dependencies at the boundary.
- **Integration verification** — Components work together. For changes crossing layers (API to database, service to service, frontend to API): test the real interaction and verify the full round-trip.
- **Runtime verification** — The running application behaves correctly. For any user-facing change: start the services, perform the operation as a user would, and verify the result.

## Test Data Strategy

- **Deterministic setup** — Each test creates its own preconditions (seed records, entities, configured state) and assumes nothing about pre-existing data.
- **Minimal data** — Create only what the test needs: the entity under test with its required parents, not the entire world.
- **Cleanup awareness** — Learn whether the project uses transaction rollback, database reset, or persistent test data before generating data, and adapt to it.
- **Reusable generators** — A data shape needed repeatedly becomes one callable fixture or seed script, not copy-pasted setup.

## Verification Scope Rules

- **High risk** (new features, behavior changes, security-related code, data migration) — all applicable layers, including edge cases and error paths.
- **Medium risk** (bug fixes, refactors that change structure but not behavior) — the specific change plus one layer of integration; confirm the fix and that nothing adjacent broke.
- **Low risk** (renames, documentation, config changes, style-only UI) — build verification, plus a quick runtime spot check when anything rendered is touched.

## Test Scenario Design

Cover these categories in priority order:

1. **Happy path** — the intended use case works
2. **Validation errors** — bad input is rejected gracefully
3. **Edge cases** — boundary values, empty states, maximum limits
4. **Error recovery** — failures (network errors, missing data, timeouts) leave no corruption
5. **Regression** — previously fixed bugs stay fixed; adjacent features still work
