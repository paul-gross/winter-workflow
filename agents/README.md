# Agents

This directory holds the role-pure subagents provided by `winter-workflow`. Each agent is a single role with a focused responsibility:

| File | Role |
|------|------|
| `architect.md` | High-level design, interfaces, dependencies |
| `backend-verifier.md` | API/CLI/database verification |
| `code-reviewer.md` | Architectural code review |
| `context-reviewer.md` | Reviews agent-facing markdown against documented conventions |
| `developer.md` | Code implementation, unit tests, refactoring |
| `diff-classifier.md` | Cold, k-voted per-hunk tier classifier for a review manifest |
| `documentation-reviewer.md` | Reviews external-facing public documentation for accuracy and currency |
| `explorer.md` | Investigates undocumented systems, writes AI-centric docs |
| `frontend-verifier.md` | Chrome DevTools browser verification |
| `harness-reviewer.md` | Application↔harness seam review against a diff |
| `manifest-auditor.md` | Adversarially refutes a review manifest's cheap-tier claims |
| `runner.md` | Service lifecycle and log monitoring |
| `test-mediator.md` | Test strategy, scenario design, verifier dispatch |

Shared default docs (SOLID + Clean Architecture, default test strategy, etc.) consumed by `architect.md` and `test-mediator.md` live under `docs/`.

## Convention: role-pure agents, caller-injected coordination

Agent bodies describe **what the role does and how it works** — coding standards, exploration approach, verification reporting, escalation paths. They do **not** describe how the role participates in a particular team workflow. That coordination context is the caller's responsibility.

Concretely:

- Agent bodies reference "your caller" rather than a named coordinator.
- Agents do not include `TaskList`/`TaskUpdate` instructions by default. Where coordination tools appear in the `tools:` frontmatter, they're listed because some caller (today, `blizzard`) genuinely needs them.
- Skills that compose multiple agents are expected to inject a short **coordination preamble** at the top of each spawn prompt explaining how the agent should participate (claim tasks, report back, when to stop).

The `blizzard` skill documents its preamble in [`../skills/blizzard/SKILL.md`](../skills/blizzard/SKILL.md) under *Team-coordination preamble*. New skills that compose these agents should follow the same pattern with whatever coordination shape they need (or skip it entirely for one-shot work, like `cold-review` does with `code-reviewer`).

## Convention: tool grant vs. preamble

Each agent's `tools:` frontmatter is the **permissive** set — every tool the agent is allowed to use across all callers. The spawning skill's preamble is the **authoritative contract** for any given run, and may forbid a subset of those tools when the invocation mode demands it. When the two disagree, the preamble wins.

> **The key is `tools`, not `allowed-tools`.** Claude Code reads `tools` for *agents* (`allowed-tools` is the *skills/commands* key) and silently ignores `allowed-tools` here — so an agent that declares `allowed-tools` gets the wide default grant, not the restricted set the author intended. Every agent must also declare a non-empty `description` and a `model` of `haiku`, `sonnet`, or `opus`. `winter lint` enforces all three keys and flags the `allowed-tools` mistake.

This split exists because the same agent definition is reused across very different coordination shapes. The `developer` agent ships with `SendMessage`, `TaskUpdate`, and `TaskList` in its tool list because `blizzard` genuinely needs them — the lead claims tasks from a shared list and teammates report back via `SendMessage`. The same agent is also spawned one-shot by `thaw` with a preamble that explicitly forbids those same tools, because no shared task list exists in that mode.

Worked example — `thaw`'s preamble narrows the grant for one-shot runs:

> You are operating as a one-shot agent spawned by the `thaw` skill. No shared task list exists. Report results to the skill via your final response only — do not call `SendMessage`, `TaskCreate`, or `TaskUpdate`. When your task is done, stop.

The `developer` (or `explorer`, or a verifier) agent reads this and ignores its task tools for the duration of the call. The tools stay in the grant so `blizzard` can use them; the preamble is what scopes any one run.

If you add a new skill that composes these agents, decide which tools its mode allows and document the restrictions in your preamble. The agent definitions themselves stay stable.

## Worked examples (non-blizzard callers)

Non-blizzard skills compose these role-pure agents without spinning up a team. Each one shows how a different coordination shape stays compatible with the convention above.

| Skill | Agent(s) composed | Coordination shape |
|-------|-------------------|--------------------|
| [`cold-review`](../skills/cold-review/SKILL.md) | `code-reviewer` | One-shot, single agent, no preamble — the reviewer reads the diff and reports |
| [`glacier`](../skills/glacier/SKILL.md) | `architect` *(optional)* → `developer` (one per phase) | Sequential one-shots across ordered phases; each spawn gets a verbatim "you are operating as a one-shot agent, no shared task list" preamble; the per-phase `developer` both implements and verifies, and the skill gates phase advancement on an adequate runtime check |
| [`harness-review`](../skills/harness-review/SKILL.md) | `harness-reviewer` | One-shot, single agent, no preamble — the reviewer reads the diff plus harness/transcripts and reports |
| [`review-manifest`](../skills/review-manifest/SKILL.md) | `diff-classifier` (k-fan-out) → `manifest-auditor` | One-shot, no team; **k = 3** classifiers spawned in parallel over the same diff (reconciled per hunk, any split fails closed to `novel`), then one auditor refutes the cheap tiers. Each spawn gets the verbatim one-shot/no-team preamble; the classifiers additionally never receive the task prompt (coldness is the point) |
| [`harness-score`](../skills/harness-score/SKILL.md) | `explorer` | One-shot evidence gathering; main agent applies the rubric and renders the report. Preamble adds a "no documentation writing, no context-reviewer request" clause on top of the standard one-shot wording, since `explorer`'s default body otherwise authors `ai/` docs |
| [`thaw`](../skills/thaw/SKILL.md) | `explorer` → `developer` → `backend-verifier` \| `frontend-verifier` | Sequential one-shots, capped iteration loop; each spawn gets a verbatim "you are operating as a one-shot agent, no shared task list" preamble |
| [`flurry`](../skills/flurry/SKILL.md) | `developer` (one fresh per task) → `developer` (one per env *with findings*, to fold them) | Parallel one-shots, no team; tracks run concurrently across environments (background spawns), tasks within a track sequentially. Each spawn gets the verbatim one-shot/no-team preamble, but unlike `glacier`/`thaw` the per-task `developer` also lands exactly one commit. Composes `pre-push` (per env) for review |

`harness-review` is the same composition shape as `cold-review` but reviews a different concern axis (application↔harness seam, not architectural code quality). It is the standard worked example of "add a new role-pure reviewer and expose it as a one-shot skill" without touching `blizzard` or the other composed skills.

The four single-axis review skills (`cold-review`, `context-review`, `harness-review`, `documentation-review`) and `pre-push` no longer carry their own spawn instructions — they route through the shared engine [`../ai/review.md`](../ai/review.md), which builds every reviewer prompt (the one-shot/no-team preamble, scope, diff commands, per-axis body, output shape) and chooses the model. The role-pure / caller-injects-coordination convention is unchanged: the engine is the caller, and it injects exactly the one-shot, no-team preamble these reviewers expect.

