# Default Architectural Principles

This document is used by the `winter-architect` agent during the **Principles Bootstrap Workflow**. When a project has no documented architectural principles, the winter-architect proposes these as defaults. Each principle is spelled out for agent consumption — not just named, but explained with what it means in practice and how agents should apply it.

The user may accept these as-is, modify them, or specify entirely different principles.

---

## SOLID Principles

- **Single Responsibility (SRP)** — A class or module should have one reason to change. In practice: if you're adding a feature and an existing class needs changes for two unrelated reasons, split it.

- **Open/Closed (OCP)** — Software entities should be open for extension, closed for modification. In practice: add new behavior by creating new classes that implement existing interfaces, not by editing existing implementations.

- **Liskov Substitution (LSP)** — Subtypes must be substitutable for their base types without altering correctness. In practice: if a function accepts an interface, every implementation of that interface must honor the same contract — no surprising side effects or missing behavior.

- **Interface Segregation (ISP)** — No client should be forced to depend on methods it does not use. In practice: prefer small, focused interfaces over large ones. If an interface has methods that some consumers ignore, split it.

- **Dependency Inversion (DIP)** — Depend on abstractions, not concretions. In practice: every dependency should flow through an interface or abstract class. Constructors receive interfaces; DI containers wire the concrete implementations.

## Clean Architecture — The Dependency Rule

- **Dependency Rule** — Source code dependencies must point inward only. Outer layers (UI, infrastructure, frameworks) depend on inner layers (domain, use cases), never the reverse. In practice: domain models never import from HTTP controllers, database modules, or framework packages. This is the overarching rule that all the component principles below serve to enforce.

## Clean Architecture — Component Cohesion Principles

- **Reuse/Release Equivalence Principle (REP)** — The granule of reuse is the granule of release. Classes and modules that are reused together must be released together and share the same version lifecycle. In practice: if two classes are always imported as a pair, they belong in the same component/package. If a class can be used independently, it belongs in its own.

- **Common Closure Principle (CCP)** — Gather into components those classes that change for the same reasons and at the same times. Separate into different components those classes that change at different times and for different reasons. In practice: if a business rule change requires editing files in three different modules, those files should probably be in one module. This is SRP applied at the component level.

- **Common Reuse Principle (CRP)** — Don't force users of a component to depend on things they don't need. Classes in a component should be inseparable — if you use one, you use them all. In practice: if a consumer imports your component but only uses half of it, the component is too big. Split it so consumers only take on dependencies they actually need. This is ISP applied at the component level.

## Clean Architecture — Component Coupling Principles

- **Acyclic Dependencies Principle (ADP)** — Allow no cycles in the component dependency graph. The dependency structure must be a directed acyclic graph (DAG). In practice: if component A depends on B and B depends on A (directly or transitively), break the cycle by extracting a shared interface into a third component that both depend on, or use dependency inversion to flip one of the arrows.

- **Stable Dependencies Principle (SDP)** — Depend in the direction of stability. A component that is designed to be easy to change should not be depended on by a component that is hard to change. In practice: volatile, frequently-changing modules should depend on stable ones, never the reverse. Measure stability by the ratio of incoming to outgoing dependencies — high fan-in means high stability and high responsibility to remain unchanging.

- **Stable Abstractions Principle (SAP)** — A component should be as abstract as it is stable. Stable components (many dependents) should consist mostly of interfaces and abstract classes so they can be extended without modification. Unstable components (few dependents) should be concrete. In practice: if a component has high fan-in, it should define abstractions. If it's a leaf with no dependents, concrete implementations are fine. The combination of SDP and SAP means dependencies flow toward abstraction.
