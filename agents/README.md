# Agents

This directory holds the role-pure subagents provided by `winter-workflow`. Each agent is a single role with a focused responsibility:

| File | Role |
|------|------|
| `winter-architect.md` | High-level design, interfaces, dependencies |
| `backend-verifier.md` | API/CLI/database verification |
| `cold-reviewer.md` | Architectural code review |
| `context-reviewer.md` | Reviews agent-facing markdown against documented conventions |
| `ice-carver.md` | Code implementation, unit tests, refactoring |
| `diff-classifier.md` | Fresh, k-voted per-hunk tier classifier for a review manifest |
| `documentation-reviewer.md` | Reviews external-facing public documentation for accuracy and currency |
| `arctic-explorer.md` | Investigates undocumented systems, writes AI-centric docs |
| `frontend-verifier.md` | Chrome DevTools browser verification |
| `harness-reviewer.md` | Application↔harness seam review against a diff |
| `manifest-auditor.md` | Adversarially refutes a review manifest's cheap-tier claims |
| `verify-finale.md` | Verification finale — verify via the matrix, build a missing method, fix and re-verify |

Shared default docs live under `docs/`: the principles defaults (SOLID + Clean Architecture) consumed by `winter-architect.md`, plus test-strategy defaults kept for a future bootstrap workflow (not currently wired to any agent).

## Canonical agent format

Each file in `agents/*.md` is a **canonical agent** — a single source of truth that
`winter ws init` transforms into harness-native copies for Claude Code, Codex, and OpenCode.
Never edit a harness copy; edit the canonical file and re-run init.

The format is owned by the harness conventions, not this README:

- **Frontmatter contract** (`name`, `description`, `model` tier, `tools`) — all four are `winter lint`-required.
- **Per-harness projection** — the `claude:`/`codex:`/`opencode:` override blocks, the model-tier→id table, lossy projection (e.g. `tools` has no Codex/OpenCode equivalent and is dropped with an actionable warning), and identity across harnesses.

**In this extension:** every agent declares its intended cross-harness access in its override
blocks — a `codex: {sandbox_mode: ...}` and an `opencode: {permission: ...}` matched to the
agent's `tools` — so no agent renders with silently-unrestricted access and no unexpected
lossy-drop warning survives at init.

## Convention: role-pure agents, caller-injected coordination

Agent bodies describe **what the role does and how it works** — coding standards, exploration approach, verification reporting, escalation paths. They do **not** describe how the role participates in a particular team workflow. That coordination context is the caller's responsibility.

Concretely:

- Agent bodies reference "your caller" rather than a named coordinator.
- Agents do not include `TaskList`/`TaskUpdate` instructions by default. Where coordination tools appear in the `tools:` frontmatter, they're listed because some caller (today, `iceberg`) genuinely needs them.
- Skills that compose multiple agents are expected to inject a short **coordination preamble** at the top of each spawn prompt explaining how the agent should participate (claim tasks, report back, when to stop).

The `iceberg` skill documents its preamble in [`../skills/iceberg/SKILL.md`](../skills/iceberg/SKILL.md) under *Coordination preamble (inject verbatim)*. New skills that compose these agents should follow the same pattern with whatever coordination shape they need (or skip it entirely for one-shot work, like `cold-review` does with `cold-reviewer`).

## Convention: tool grant vs. preamble

Each agent's `tools:` frontmatter is the **permissive** set — every tool the agent is allowed to use across all callers. The spawning skill's preamble is the **authoritative contract** for any given run, and may forbid a subset of those tools when the invocation mode demands it. When the two disagree, the preamble wins.

> **The key is `tools`, not `allowed-tools`.** Claude Code reads `tools` for *agents* (`allowed-tools` is the *skills/commands* key) and silently ignores `allowed-tools` here — so an agent that declares `allowed-tools` gets the wide default grant, not the restricted set the author intended. Every agent must also declare a non-empty `description` and a `model` of `haiku`, `sonnet`, or `opus`. `winter lint` enforces all three keys and flags the `allowed-tools` mistake.

This split exists because the same agent definition is reused across very different coordination shapes. A **resident** teammate — an `iceberg` target-pinned `ice-carver` — genuinely uses `SendMessage`, `TaskUpdate`, and `TaskList`: the foreman manages a shared task list and the resident teammate reports back via `SendMessage` for as long as it stays up. The one-shot build skills run the same `ice-carver` differently: `snowball`, `glacier`, and `flurry` spawn it with a preamble that forbids those tools — a one-shot ice-carver owns a single slice and reports in its final response. The grant stays in the definition for the resident mode; the preamble scopes it out for one-shot spawns.

Worked example — `snowball`'s preamble narrows the grant for one-shot runs:

> You are operating as a one-shot agent spawned by the `snowball` skill. No shared task list exists. Report results to the skill via your final response only — do not call `SendMessage`, `TaskCreate`, or `TaskUpdate`. When your task is done, stop.

The `ice-carver` (or `arctic-explorer`, or a verifier) agent reads this and ignores its task tools for the duration of the call. The tools stay in the grant so `iceberg` can use them; the preamble is what scopes any one run.

If you add a new skill that composes these agents, decide which tools its mode allows and document the restrictions in your preamble. The agent definitions themselves stay stable.

## Worked examples (one-shot callers)

These skills compose the role-pure agents without spinning up a team. Each one shows how a different coordination shape stays compatible with the convention above.

| Skill | Agent(s) composed | Coordination shape |
|-------|-------------------|--------------------|
| [`cold-review`](../skills/cold-review/SKILL.md) | `cold-reviewer` | One-shot, single agent, no preamble — the reviewer reads the diff and reports |
| [`glacier`](../skills/glacier/SKILL.md) | `winter-architect` *(optional)* → `ice-carver` (one per phase; a phase's independent slices may run in parallel) → `verify-finale` (one per phase) → `frontend-verifier` *(per phase, for a browser-driven method the Bash-only finale can't drive)* | Sequential one-shots across ordered phases; each spawn gets a verbatim "you are operating as a one-shot agent, no shared task list" preamble; per phase the `ice-carver` implements and the `verify-finale` closes it through the application's verifiability matrix, and the skill gates phase advancement on the finale (and any split-off `frontend-verifier`) passing |
| [`harness-review`](../skills/harness-review/SKILL.md) | `harness-reviewer` | One-shot, single agent, no preamble — the reviewer reads the diff plus harness/transcripts and reports |
| [`review-manifest`](../skills/review-manifest/SKILL.md) | `diff-classifier` (k-fan-out) → `manifest-auditor` | One-shot, no team; **k = 3** classifiers spawned in parallel over the same diff (reconciled per hunk, any split fails closed to `novel`), then one auditor refutes the cheap tiers. Each spawn gets the verbatim one-shot/no-team preamble; the classifiers additionally never receive the task prompt (freshness is the point) |
| [`harness-score`](../skills/harness-score/SKILL.md) | `arctic-explorer` | One-shot evidence gathering; main agent applies the rubric and renders the report. Preamble adds a "no documentation writing, no context-reviewer request" clause on top of the standard one-shot wording, since `arctic-explorer`'s default body otherwise authors `context/` docs |
| [`snowball`](../skills/snowball/SKILL.md) | `arctic-explorer` → `ice-carver` → `backend-verifier` \| `frontend-verifier` | Sequential one-shots, capped iteration loop; each spawn gets a verbatim "you are operating as a one-shot agent, no shared task list" preamble |
| [`flurry`](../skills/flurry/SKILL.md) | `ice-carver` (one fresh per task) → `ice-carver` (one per env *with findings*, to fold them) | Parallel one-shots, no team; tracks run concurrently across environments (background spawns), tasks within a track sequentially. Each spawn gets the verbatim one-shot/no-team preamble, but unlike `glacier`/`snowball` the per-task `ice-carver` also lands exactly one commit. Composes `pre-push` once over the finished batch for review |

`harness-review` is the same composition shape as `cold-review` but reviews a different concern axis (application↔harness seam, not architectural code quality). It is the standard worked example of "add a new role-pure reviewer and expose it as a one-shot skill" without touching the other composed skills.

The four single-axis review skills (`cold-review`, `context-review`, `harness-review`, `documentation-review`) and `pre-push` no longer carry their own spawn instructions — they route through the shared engine [`../context/review.md`](../context/review.md), which builds every reviewer prompt (the one-shot/no-team preamble, scope, diff commands, per-axis body, output shape) and chooses the model. The role-pure / caller-injects-coordination convention is unchanged: the engine is the caller, and it injects exactly the one-shot, no-team preamble these reviewers expect.

