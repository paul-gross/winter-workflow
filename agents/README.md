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

The `/blizzard` skill documents its preamble in [`../skills/blizzard/SKILL.md`](../skills/blizzard/SKILL.md) under *Team-coordination preamble*. New skills that compose these agents should follow the same pattern with whatever coordination shape they need (or skip it entirely for one-shot work, like `/wf-cold-review` does with `code-reviewer`).

## Worked examples (non-blizzard callers)

Non-blizzard skills compose these role-pure agents without spinning up a team. Each one shows how a different coordination shape stays compatible with the convention above.

| Skill | Agent(s) composed | Coordination shape |
|-------|-------------------|--------------------|
| [`/wf-cold-review`](../skills/cold-review/SKILL.md) | `code-reviewer` | One-shot, single agent, no preamble — the reviewer reads the diff and reports |
| [`/wf-thaw`](../skills/thaw/SKILL.md) | `explorer` → `developer` → `backend-verifier` \| `frontend-verifier` | Sequential one-shots, capped iteration loop; each spawn gets a verbatim "you are operating as a one-shot agent, no shared task list" preamble |
| [`/wf-harness-review`](../skills/harness-review/SKILL.md) | `harness-reviewer` | One-shot, single agent, no preamble — the reviewer reads the diff plus harness/transcripts and reports |

`/wf-harness-review` is the same composition shape as `/wf-cold-review` but reviews a different concern axis (application↔harness seam, not architectural code quality). It is the standard worked example of "add a new role-pure reviewer and expose it as a one-shot skill" without touching `/wf-blizzard` or the other composed skills.

