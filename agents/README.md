# Agents

This directory holds the role-pure subagents provided by `winter-workflow`. Each agent is a single role with a focused responsibility:

| File | Role |
|------|------|
| `winter-architect.md` | High-level design, interfaces, dependencies |
| `backend-verifier.md` | API/CLI/database verification |
| `cold-reviewer.md` | Runtime adapter for the code-facing review axes |
| `faceted-reviewer.md` | Faceted review lead — gathers the change-set context, fans out per facet, aggregates |
| `context-reviewer.md` | Reviews agent-facing markdown against documented conventions |
| `ice-carver.md` | Code implementation, unit tests, refactoring |
| `diff-classifier.md` | Fresh, k-voted per-hunk tier classifier for a review manifest |
| `documentation-reviewer.md` | Reviews external-facing public documentation for accuracy and currency |
| `plan-reviewer.md` | Runtime adapter for the plan review axis — reviews an implementation plan before building |
| `arctic-explorer.md` | Investigates undocumented systems, writes AI-centric docs |
| `frontend-verifier.md` | Chrome DevTools browser verification |
| `harness-reviewer.md` | Application↔harness seam review against a diff |
| `manifest-auditor.md` | Adversarially refutes a review manifest's cheap-tier claims |
| `verify-finale.md` | Verification finale — verify via the matrix, build a missing method, fix and re-verify |

Shared default docs live under `docs/`: the principles defaults (SOLID + Clean Architecture) consumed by `winter-architect.md`, plus test-strategy defaults kept for a future bootstrap workflow (not currently wired to any agent).

The reviewer files are isolated-runtime adapters rather than methodology owners. Their canonical methods live under [`../methodology/review/axes/`](../methodology/review/axes/index.md); inline and fresh execution consume those same files.

## Canonical agent format

Each file in `agents/*.md` is a canonical agent transformed by `winter ws init`; edit it rather than a generated harness copy. The installed `winter-harness` conventions own the authoring/frontmatter and cross-harness projection contracts at their `agent-context/index.md` entrypoint, specifically its writing-agent and projection references.

**In this extension:** every agent declares its intended cross-harness access in its override
blocks — a `codex: {sandbox_mode: ...}` and an `opencode: {permission: ...}` matched to the
agent's `tools` — so no agent renders with silently-unrestricted access and no unexpected
lossy-drop warning survives at init.

## Convention: role-pure agents, caller-injected coordination

Agent bodies describe **what the role does and how it works** — coding standards, exploration approach, verification reporting, escalation paths. They do **not** describe how the role participates in a particular team workflow. That coordination context is the caller's responsibility.

Concretely:

- Agent bodies reference "your caller" rather than a named coordinator.
- Agents do not include `TaskList`/`TaskUpdate` instructions by default. Where coordination tools appear in the `tools:` frontmatter, they're listed because some caller (today, `iceberg`) genuinely needs them.
- Callers that compose multiple agents are expected to inject a short **coordination preamble** at the top of each spawn prompt explaining how the agent should participate (claim tasks, report back, when to stop).

## Convention: tool grant vs. preamble

Each agent's `tools:` frontmatter is the **permissive** set — every tool the agent is allowed to use across all callers. The spawning process's preamble is the **authoritative contract** for any given run, and may forbid a subset of those tools when the invocation mode demands it. When the two disagree, the preamble wins.

This split exists because the same definition serves resident teammates and one-shot agents. Resident modes genuinely need coordination tools; one-shot process preambles scope those tools out. The process that spawns an agent owns the exact preamble and composition.

If you add a new process that composes these agents, decide which tools its mode allows and document the restrictions in its preamble. The agent definitions themselves stay stable.

Exact compositions, preambles, and execution contracts live with their processes under [`../methodology/build/`](../methodology/build/index.md), [`../methodology/review/`](../methodology/review/index.md), and the other routed procedures in [`../methodology/`](../methodology/index.md). Agent bodies retain only stable role behavior and runtime boundaries.
