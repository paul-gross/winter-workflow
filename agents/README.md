# Agents

This directory holds the role-pure subagents provided by `winter-workflow`. Each agent is a single role with a focused responsibility:

| File | Role |
|------|------|
| `arctic-explorer.md` | Investigates undocumented systems, writes AI-centric docs |
| `backend-verifier.md` | API/CLI/database verification |
| `cold-reviewer.md` | Runtime adapter for the code-facing review axes |
| `context-reviewer.md` | Runtime adapter for the context review axis — agent-facing markdown against documented conventions |
| `diff-classifier.md` | Fresh, k-voted per-hunk tier classifier for a review manifest |
| `distiller.md` | Cold rewrite of existing markdown into its smallest current form, via the distill process |
| `documentation-reviewer.md` | Runtime adapter for the documentation review axis — public docs against the code |
| `faceted-reviewer.md` | Faceted review lead — gathers the change-set context, fans out per facet, aggregates |
| `frontend-verifier.md` | Chrome DevTools browser verification |
| `harness-reviewer.md` | Runtime adapter for the harness review axis — the application↔harness seam |
| `ice-carver.md` | Code implementation, unit tests, refactoring |
| `manifest-auditor.md` | Adversarially refutes a review manifest's cheap-tier claims |
| `plan-reviewer.md` | Runtime adapter for the plan review axis — reviews an implementation plan before building |
| `verify-finale.md` | Verification finale — verify via the matrix, build a missing method, fix and re-verify |
| `winter-architect.md` | High-level design, interfaces, dependencies |

The reviewer files are isolated-runtime adapters, not methodology owners: their canonical methods live under [`../methodology/review/axes/`](../methodology/review/axes/index.md), and inline and fresh execution consume those same files.

Shared default docs live under `docs/`: the principles defaults (SOLID + Clean Architecture) consumed by `winter-architect.md`, plus test-strategy defaults kept for a future bootstrap workflow (not currently wired to any agent).

## Canonical agent format

Each file in `agents/*.md` is a canonical agent that `winter ws init` transforms into per-harness copies — edit the canonical file, never a generated copy. The installed `winter-harness` conventions own the frontmatter contract and the cross-harness projection mechanics, at their `agent-context/index.md` entrypoint's writing-agent and projection references.

In this extension, every agent declares its intended cross-harness access in override blocks — a `codex: {sandbox_mode: ...}` and an `opencode: {permission: ...}` matched to its `tools` — so no agent renders with silently-unrestricted access and no lossy-drop warning survives at init.

## Convention: role-pure agents, caller-injected coordination

Agent bodies describe what the role does and how it works — coding standards, exploration approach, verification reporting, escalation paths — never how the role participates in a particular team workflow:

- Bodies reference "your caller", never a named coordinator.
- Bodies carry no `TaskList`/`TaskUpdate` instructions; where coordination tools appear in `tools:` frontmatter, they're listed because some caller (today, `iceberg`) genuinely needs them.
- A caller that composes multiple agents injects a short **coordination preamble** at the top of each spawn prompt explaining how the agent should participate (claim tasks, report back, when to stop).

## Convention: tool grant vs. preamble

Each agent's `tools:` frontmatter is the **permissive** set — every tool the agent is allowed to use across all callers. The spawning process's preamble is the **authoritative contract** for any given run and may forbid a subset of those tools; when the two disagree, the preamble wins. The split exists because the same definition serves resident teammates and one-shot agents: resident modes genuinely need coordination tools, and one-shot process preambles scope them out.

A new process that composes these agents decides which tools its mode allows and documents the restrictions in its preamble; the agent definitions stay stable. Exact compositions, preambles, and execution contracts live with their processes under the routed procedures in [`../methodology/`](../methodology/index.md). Agent bodies retain only stable role behavior and runtime boundaries.
