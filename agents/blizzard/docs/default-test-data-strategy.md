# Default Test Data Strategy

This document is used by the blizzard test-mediator agent during the **Test Data Strategy Bootstrap Workflow**. When a project has no documented test data strategy, the test-mediator proposes these defaults.

The user may accept these as-is, modify them, or specify an entirely different approach.

---

## Core Philosophy

Test data should be created through the same interfaces the application uses, not by directly manipulating databases or bypassing business logic. This ensures test data is valid, consistent, and exercises the same code paths that production data flows through.

## CLI Test Data Toolkit

The project should maintain a CLI tool (or a module within an existing CLI tool) with multiple components that serve testing and verification agents. The goal is to enable agents to quickly create scenarios and interface with the backend system without having to reverse-engineer APIs, data models, or setup procedures.

### Component 1: Backend Command Interface

A thin, simple interface layer over the project's backend APIs.

- **Purpose**: Provide a straightforward way to call any backend operation from the command line — create entities, trigger actions, query state — without needing to know endpoint URLs, authentication details, or payload formats.
- **Design**: Each command maps to a single backend operation. Inputs are simple CLI arguments or flags. Outputs are the raw API response (JSON). No business logic in this layer — it's a pass-through.
- **Why this matters for agents**: Verification agents (backend-verifier, frontend-verifier) and the test-mediator itself can issue commands without crafting raw HTTP requests. This removes a class of errors (wrong URL, wrong auth header, wrong payload shape) and lets agents focus on what they're actually testing.
- **In practice**: A command like `cli user create --name "Test User" --email "test@example.com"` should call the appropriate API endpoint, handle authentication, and return the created entity. A command like `cli universe status` should return the current state.

### Component 2: Fixture Scaffolding

Higher-level commands that compose backend commands to create complex test scenarios using domain-level abstractions.

- **Purpose**: Set up multi-entity, multi-step scenarios in a single command. Instead of manually creating a user, then a session, then an entity, then placing it — one fixture command does it all.
- **Design**: Fixtures accept domain-level inputs that describe the desired scenario in abstract terms (e.g., "a player with 3 ships in sector X" or "two players in a trade negotiation"). Internally, they orchestrate multiple backend commands in the correct order, handling dependencies and relationships.
- **Why this matters for agents**: Complex test scenarios require entities to be created in a specific order with specific relationships. Fixtures encode this knowledge once, so every agent (and every test run) gets it right without re-deriving the setup sequence.
- **In practice**: A fixture like `cli fixture create-combat-scenario --attackers 2 --defenders 1 --sector "Alpha Centauri"` should create all the required entities, place them correctly, and return the IDs of everything it created so the test can reference them.

### Component 3: State Inspection

Commands that query and report on the current state of test data.

- **Purpose**: Allow verification agents to check what exists, verify preconditions, and confirm postconditions without writing raw database queries or API calls.
- **Design**: Read-only commands that return structured data about the current state of entities, relationships, and system status.
- **In practice**: Commands like `cli inspect user --id 123` or `cli inspect scenario --name "combat-test"` that return the full state of an entity or scenario in a format agents can parse.

## Test Data Lifecycle

- **Create before test** — Each test scenario creates its own data using fixtures or backend commands. Never depend on pre-existing state.
- **Document what was created** — Fixtures should return or log the IDs and types of everything they created, so cleanup and verification can reference them.
- **Cleanup awareness** — Understand the project's cleanup mechanism (transaction rollback, database reset, ephemeral environments) and design fixtures accordingly. If no cleanup exists, fixtures should support a teardown mode.
