# Default Automated Testing Strategy

This document is used by the blizzard test-mediator agent during the **Automated Testing Strategy Bootstrap Workflow**. When a project has no documented automated testing strategy, the test-mediator proposes these defaults.

The user may accept these as-is, modify them, or specify an entirely different approach.

---

## The Test Pyramid

The project's automated tests should follow the classic test pyramid: many fast, isolated tests at the bottom; fewer, broader tests at the top. Each layer serves a different purpose and catches a different class of bug.

### Unit Tests

**Volume**: Many. These form the base of the pyramid.

- **What to test**: Individual functions, methods, and classes in isolation. Business logic, calculations, state transitions, validation rules, pure transformations.
- **When to write them**: When the code contains branching logic, non-trivial computation, or business rules that could regress. Not every function needs a unit test — simple getters, pass-through wrappers, and trivial constructors don't warrant them.
- **How to write them**: Mock or stub external dependencies at the boundary. Test the unit's behavior, not its implementation. Each test should cover one behavior or path.
- **In practice**: If a developer writes a function that calculates resource costs based on multiple inputs, that function gets unit tests covering normal inputs, edge cases (zero, negative, max values), and error conditions.

### Component / Integration Tests

**Volume**: Moderate. The middle of the pyramid.

- **What to test**: Interactions between components within the codebase — a service calling a repository, a controller calling a service, a module's public API. Tests that cross internal boundaries but stay within the codebase.
- **When to write them**: When the interesting behavior emerges from the interaction between components, not from any single unit. When the contract between two components is important and could break independently of either component's unit tests.
- **How to write them**: Use real implementations of internal components (not mocks) where practical. Mock external systems (databases, third-party APIs, message queues) at the outermost boundary. Test the integrated behavior end-to-end within the component boundary.
- **In practice**: A test that creates a service with a real repository implementation backed by an in-memory or test database, calls the service method, and verifies both the return value and the database state.

### End-to-End Tests

**Volume**: Few. The top of the pyramid.

- **What to test**: Full user journeys through the running application. The complete path from user action to system response, exercising the real stack (frontend, API, backend, database).
- **When to write them**: For critical user flows — the paths where a failure would be immediately visible and damaging. Login, core CRUD operations, the primary user journey. Not for edge cases or error paths (those are covered lower in the pyramid).
- **How to write them**: Run the actual application services. Use browser automation (Playwright) for UI tests or HTTP clients for API-only flows. Assert on observable outcomes (page content, API responses, database state).

#### E2E in Ephemeral Agent Environments

End-to-end tests are the most valuable and the most difficult to maintain in local, ephemeral environments where agents are working. Acknowledge this reality:

- **E2E suites are fragile in agent workflows** — Services need to be running, ports need to be available, databases need to be seeded, and timing issues are common. Agents working in feature worktrees may have different port configurations or partial service availability.
- **This is not a hard requirement** — If the project already has a working E2E suite that runs locally, continue supporting it and add to it when writing new features that warrant E2E coverage. If the project doesn't have E2E tests, don't force them — the lower pyramid layers plus runtime verification by blizzard verifier agents provide adequate coverage.
- **Prefer runtime verification over formal E2E suites when agents are testing** — The blizzard's frontend-verifier and backend-verifier agents perform what is effectively manual E2E testing (start services, interact, verify). This is often more practical in ephemeral environments than maintaining a persistent E2E test suite.
- **If E2E exists, keep it green** — Don't let existing E2E tests rot. If a change breaks an E2E test, fix it. If an E2E test is flaky, either stabilize it or remove it — flaky tests are worse than no tests because they erode trust in the suite.

## Which Layer to Prioritize

When time or scope is limited, prioritize in this order:

1. **Unit tests for new business logic** — Cheap to write, fast to run, highest signal-to-noise ratio
2. **Integration tests for new component boundaries** — Catches wiring bugs that unit tests miss
3. **Runtime verification by blizzard agents** — Covers the E2E gap without the maintenance burden of a formal suite
4. **E2E tests for critical paths** — Only if the project supports them and the path is high-value
