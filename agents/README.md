# Agents

This directory holds the role-pure subagents provided by `winter-workflow`. Each agent is a single role with a focused responsibility:

| File | Role |
|------|------|
| `architect.md` | High-level design, interfaces, dependencies |
| `backend-verifier.md` | API/CLI/database verification |
| `code-reviewer.md` | Architectural code review |
| `context-reviewer.md` | Reviews agent-facing markdown against documented conventions |
| `developer.md` | Code implementation, unit tests, refactoring |
| `documentation-reviewer.md` | Reviews external-facing public documentation for accuracy and currency |
| `explorer.md` | Investigates undocumented systems, writes AI-centric docs |
| `frontend-verifier.md` | Chrome DevTools browser verification |
| `harness-reviewer.md` | Application↔harness seam review against a diff |
| `runner.md` | Service lifecycle and log monitoring |
| `test-mediator.md` | Test strategy, scenario design, verifier dispatch |

Shared default docs (SOLID + Clean Architecture, default test strategy, etc.) consumed by `architect.md` and `test-mediator.md` live under `docs/`.

## Convention: role-pure agents, caller-injected coordination

Agent bodies describe **what the role does and how it works** — coding standards, exploration approach, verification reporting, escalation paths. They do **not** describe how the role participates in a particular team workflow. That coordination context is the caller's responsibility.

Concretely:

- Agent bodies reference "your caller" rather than a named coordinator.
- Agents do not include `TaskList`/`TaskUpdate` instructions by default. Where coordination tools appear in the `tools:` frontmatter, they're listed because some caller (today, `/wf-blizzard`) genuinely needs them.
- Skills that compose multiple agents are expected to inject a short **coordination preamble** at the top of each spawn prompt explaining how the agent should participate (claim tasks, report back, when to stop).

The `/wf-blizzard` skill documents its preamble in [`../skills/blizzard/SKILL.md`](../skills/blizzard/SKILL.md) under *Team-coordination preamble*. New skills that compose these agents should follow the same pattern with whatever coordination shape they need (or skip it entirely for one-shot work, like `/wf-cold-review` does with `code-reviewer`).

## Convention: tool grant vs. preamble

Each agent's `tools:` frontmatter is the **permissive** set — every tool the agent is allowed to use across all callers. The spawning skill's preamble is the **authoritative contract** for any given run, and may forbid a subset of those tools when the invocation mode demands it. When the two disagree, the preamble wins.

This split exists because the same agent definition is reused across very different coordination shapes. The `developer` agent ships with `SendMessage`, `TaskUpdate`, and `TaskList` in its tool list because `/wf-blizzard` genuinely needs them — the lead claims tasks from a shared list and teammates report back via `SendMessage`. The same agent is also spawned one-shot by `/wf-thaw` with a preamble that explicitly forbids those same tools, because no shared task list exists in that mode.

Worked example — `/wf-thaw`'s preamble narrows the grant for one-shot runs:

> You are operating as a one-shot agent spawned by the `/wf-thaw` skill. No shared task list exists. Report results to the skill via your final response only — do not call `SendMessage`, `TaskCreate`, or `TaskUpdate`. When your task is done, stop.

The `developer` (or `explorer`, or a verifier) agent reads this and ignores its task tools for the duration of the call. The tools stay in the grant so `/wf-blizzard` can use them; the preamble is what scopes any one run.

If you add a new skill that composes these agents, decide which tools its mode allows and document the restrictions in your preamble. The agent definitions themselves stay stable.

## Worked examples (non-blizzard callers)

Non-blizzard skills compose these role-pure agents without spinning up a team. Each one shows how a different coordination shape stays compatible with the convention above.

| Skill | Agent(s) composed | Coordination shape |
|-------|-------------------|--------------------|
| [`/wf-cold-review`](../skills/cold-review/SKILL.md) | `code-reviewer` | One-shot, single agent, no preamble — the reviewer reads the diff and reports |
| [`/wf-thaw`](../skills/thaw/SKILL.md) | `explorer` → `developer` → `backend-verifier` \| `frontend-verifier` | Sequential one-shots, capped iteration loop; each spawn gets a verbatim "you are operating as a one-shot agent, no shared task list" preamble |
| [`/wf-harness-review`](../skills/harness-review/SKILL.md) | `harness-reviewer` | One-shot, single agent, no preamble — the reviewer reads the diff plus harness/transcripts and reports |
| [`/wf-harness-score`](../skills/harness-score/SKILL.md) | `explorer` | One-shot evidence gathering; main agent applies the rubric and renders the report. Preamble adds a "no documentation writing, no context-reviewer request" clause on top of the standard one-shot wording, since `explorer`'s default body otherwise authors `ai/` docs |

`/wf-harness-review` is the same composition shape as `/wf-cold-review` but reviews a different concern axis (application↔harness seam, not architectural code quality). It is the standard worked example of "add a new role-pure reviewer and expose it as a one-shot skill" without touching `/wf-blizzard` or the other composed skills.

