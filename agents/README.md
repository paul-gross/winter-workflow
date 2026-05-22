# Agents

This directory holds the role-pure subagents provided by `winter-workflow`. Each agent is a single role with a focused responsibility:

| File | Role |
|------|------|
| `agentic-development-manager.md` | Reviews and authors agent-facing markdown |
| `architect.md` | High-level design, interfaces, dependencies |
| `backend-verifier.md` | API/CLI/database verification |
| `code-reviewer.md` | Architectural code review |
| `developer.md` | Code implementation, unit tests, refactoring |
| `explorer.md` | Investigates undocumented systems, writes AI-centric docs |
| `frontend-verifier.md` | Chrome DevTools browser verification |
| `runner.md` | Service lifecycle and log monitoring |
| `test-mediator.md` | Test strategy, scenario design, verifier dispatch |

Shared default docs (SOLID + Clean Architecture, default test strategy, etc.) consumed by `architect.md` and `test-mediator.md` live under `docs/`.

## Convention: role-pure agents, caller-injected coordination

Agent bodies describe **what the role does and how it works** — coding standards, exploration approach, verification reporting, escalation paths. They do **not** describe how the role participates in a particular team workflow. That coordination context is the caller's responsibility.

Concretely:

- Agent bodies reference "your caller" rather than a named coordinator.
- Agents do not include `TaskList`/`TaskUpdate` instructions by default. Where coordination tools appear in the `tools:` frontmatter, they're listed because some caller (today, `/blizzard`) genuinely needs them.
- Skills that compose multiple agents are expected to inject a short **coordination preamble** at the top of each spawn prompt explaining how the agent should participate (claim tasks, report back, when to stop).

The `/blizzard` skill documents its preamble in [`../skills/blizzard/SKILL.md`](../skills/blizzard/SKILL.md) under *Team-coordination preamble*. New skills that compose these agents should follow the same pattern with whatever coordination shape they need (or skip it entirely for one-shot work, like `/cold-review` does with `code-reviewer`).

## Reusing these agents outside `/blizzard`

The agents are general-purpose. `/cold-review` already reuses `code-reviewer` in a one-shot, no-team configuration. Other skills can compose the rest the same way.

### Design sketch: `/thaw` (debug-and-fix)

A worked sketch of a non-blizzard skill that reuses the extracted agents. The full skill is tracked separately as [winter-workflow#2](https://codeberg.org/pgross/winter-workflow/issues/2); this sketch shows the composition.

**Goal.** A focused "this doesn't work — figure out why and fix it" skill for small, isolated bugs. Distinct from `/blizzard`, which targets large feature arcs.

**Composition.**

- `explorer` (optional, sonnet) — when the bug is in an unfamiliar area, kick off a brief investigation first to identify the suspect code path.
- `developer` (sonnet) — applies the fix.
- `backend-verifier` and/or `frontend-verifier` (sonnet) — confirms the fix and watches for regressions on adjacent surface area.
- `code-reviewer` (opus, optional) — only if the fix introduces non-trivial structural change.

**Why no `runner` or `test-mediator`?** The bug-fix loop is small enough that the skill itself can manage service health (start once, restart only on demand) and define the verification scenarios inline in the spawn prompt. Skipping those two agents trims latency and token cost for the common case.

**Spawn-prompt context.** Each agent gets a small preamble appropriate to a non-team composition — there is no `TeamCreate`, no shared `TaskList`. The skill spawns agents serially, waits for each report, and routes work itself:

```
You are operating as a one-shot agent spawned by the /thaw skill.
No shared task list exists. Report results to the skill via your final response only —
do not call SendMessage, TaskCreate, or TaskUpdate. When your task is done, stop.
```

**Loop shape.** `(explorer? → developer → verifier)`, repeat the inner pair until the verifier reports green, then optionally `code-reviewer` for structural concerns. **The skill itself tracks attempt count** and exits after 3 failed develop-verify cycles on the same root cause, surfacing the trace to the user.

**What this validates.** Every extracted agent except `code-reviewer` (already proved by `/cold-review`) is reachable from a non-blizzard caller, and the role-pure agent bodies remain coherent without the team scaffolding the snowflake provides. Coordination is something callers compose, not something baked into roles.
