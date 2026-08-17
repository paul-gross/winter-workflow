# Default Automated Testing Strategy

The default automated testing strategy to propose when a target project has none documented. Everything below this paragraph transcribes into the target project's testing-strategy document as the project's own content; the title and this paragraph do not.

## The Test Pyramid

Many fast, isolated tests at the bottom; fewer, broader tests at the top. Each layer catches a different class of bug.

### Unit Tests

Many — the base of the pyramid. Test individual functions and classes in isolation: business logic, calculations, state transitions, validation rules, pure transformations. Write them when code contains branching logic, non-trivial computation, or business rules that could regress — simple getters, pass-through wrappers, and trivial constructors don't warrant them. Mock external dependencies at the boundary, test behavior rather than implementation, and cover one behavior or path per test.

### Component / Integration Tests

Moderate volume — the middle. Test interactions that cross internal boundaries but stay within the codebase: a service calling a repository, a controller calling a service, a module's public API. Write them when the interesting behavior emerges from the interaction rather than from any single unit, or when a contract between components could break independently of either side's unit tests. Use real implementations of internal components where practical; mock external systems (databases, third-party APIs, message queues) at the outermost boundary — e.g. a service with a real repository backed by an in-memory or test database, asserting on both the return value and the stored state.

### End-to-End Tests

Few — the top. Full user journeys through the running application, exercising the real stack (frontend, API, backend, database). Reserve them for critical flows where a failure would be immediately visible and damaging — login, core CRUD, the primary user journey — not for edge cases or error paths, which the lower layers cover. Run the actual services; use browser automation (Playwright) for UI flows or HTTP clients for API-only flows, asserting on observable outcomes.

#### E2E in Ephemeral Agent Environments

E2E suites are fragile where agents work: feature worktrees vary in port configuration and service availability, services must be running, databases need seeding, and timing issues are common. Accordingly:

- **E2E is not a hard requirement.** A project with a working local suite keeps supporting it and extends it for features that warrant coverage; a project without one shouldn't force it — the lower pyramid layers plus runtime verification give adequate coverage.
- **When agents are testing, prefer runtime verification.** Start the services and exercise the change against the running application — driving the UI in a browser, or calling the API or CLI and checking resulting state — effectively manual E2E, often more practical in ephemeral environments than maintaining a persistent suite.
- **Where E2E exists, keep it green.** Fix tests a change breaks; stabilize or remove flaky ones — a flaky test is worse than none, because it erodes trust in the suite.

## Which Layer to Prioritize

When time or scope is limited:

1. **Unit tests for new business logic** — cheap to write, fast to run, highest signal
2. **Integration tests for new component boundaries** — catch wiring bugs unit tests miss
3. **Runtime verification against the running application** — covers the E2E gap without a formal suite's maintenance burden
4. **E2E tests for critical paths** — only when the project supports them and the path is high-value
