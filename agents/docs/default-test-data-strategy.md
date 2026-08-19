# Default Test Data Strategy

The default test data strategy to propose when a target project has none documented. Everything below this paragraph
transcribes into the target project's test-data document as the project's own content; the title and this paragraph do
not.

## Core Philosophy

Create test data through the same interfaces the application uses — never by manipulating the database directly or
bypassing business logic. Data created this way is valid, consistent, and exercises the code paths production data flows
through.

## CLI Test Data Toolkit

The project maintains a CLI tool (or a module within an existing one) that lets testing and verification agents create
scenarios and interface with the backend without reverse-engineering APIs, data models, or setup procedures. Three
components:

- **Backend command interface** — A thin pass-through layer: each command maps to one backend operation, takes simple
  arguments or flags, handles endpoint and authentication details, and returns the raw API response as JSON. Agents call
  `cli user create --name "Test User" --email "test@example.com"` instead of crafting HTTP requests, which eliminates
  wrong-URL, wrong-auth, and wrong-payload errors.
- **Fixture scaffolding** — Higher-level commands that compose backend commands into complete multi-entity scenarios
  from domain-level inputs (e.g. `cli fixture create-combat-scenario --attackers 2 --defenders 1`). Fixtures encode the
  required creation order and relationships once, so every agent and test run gets them right, and return the IDs of
  everything created.
- **State inspection** — Read-only commands (e.g. `cli inspect user --id 123`) that return structured state for an
  entity or scenario, so agents check preconditions and postconditions without raw database queries or API calls.

## Test Data Lifecycle

- **Create before test** — Each scenario creates its own data via fixtures or backend commands; never depend on
  pre-existing state.
- **Document what was created** — Fixtures return or log the IDs and types of everything they created, so verification
  and cleanup can reference them.
- **Cleanup awareness** — Design fixtures around the project's cleanup mechanism (transaction rollback, database reset,
  ephemeral environments); when none exists, fixtures support a teardown mode.
