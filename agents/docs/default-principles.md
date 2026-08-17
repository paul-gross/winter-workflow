# Default Architectural Principles

The default architectural principles to propose when a target project has none documented, each entry pairing a principle's definition with how to apply it. Everything below this paragraph transcribes into the target project's principles document as the project's own content; the title and this paragraph do not.

## SOLID Principles

- **Single Responsibility (SRP)** — A class or module has one reason to change. When an existing class needs edits for two unrelated reasons, split it.
- **Open/Closed (OCP)** — Open for extension, closed for modification: add behavior by writing new implementations of existing interfaces, not by editing existing ones.
- **Liskov Substitution (LSP)** — Subtypes are substitutable for their base types without altering correctness: every implementation of an interface honors the same contract, with no surprising side effects or missing behavior.
- **Interface Segregation (ISP)** — No client depends on methods it does not use. Prefer small, focused interfaces; when some consumers ignore part of an interface, split it.
- **Dependency Inversion (DIP)** — Depend on abstractions, not concretions: constructors receive interfaces, and the DI container wires the concrete implementations.

## Clean Architecture — The Dependency Rule

- **Dependency Rule** — Source code dependencies point inward only: outer layers (UI, infrastructure, frameworks) depend on inner layers (domain, use cases), never the reverse. Domain models never import from HTTP controllers, database modules, or framework packages. The component principles below all serve to enforce this rule.

## Clean Architecture — Component Cohesion

- **Reuse/Release Equivalence (REP)** — The granule of reuse is the granule of release. Classes always imported together belong in one component sharing a version lifecycle; a class usable independently belongs in its own.
- **Common Closure (CCP)** — Group classes that change for the same reasons at the same times; separate those that don't. When one business-rule change forces edits across three modules, those files probably belong in one. SRP at the component level.
- **Common Reuse (CRP)** — Classes in a component are inseparable: use one, use them all. A consumer importing a component but using half of it means the component is too big — split it so consumers take on only the dependencies they need. ISP at the component level.

## Clean Architecture — Component Coupling

- **Acyclic Dependencies (ADP)** — The component dependency graph is a DAG: no cycles, direct or transitive. Break a cycle by extracting a shared interface into a third component both depend on, or by inverting one of the arrows.
- **Stable Dependencies (SDP)** — Depend in the direction of stability: volatile, frequently-changing components depend on stable ones, never the reverse. Stability tracks the ratio of incoming to outgoing dependencies — high fan-in means high responsibility to remain unchanged.
- **Stable Abstractions (SAP)** — A component is as abstract as it is stable: high fan-in components consist mostly of interfaces and abstract classes so they extend without modification, while leaf components with no dependents stay concrete. Together with SDP, dependencies flow toward abstraction.
