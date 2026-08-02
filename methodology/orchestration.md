# Orchestrated execution — blizzard fleet node-steps

How to use this extension when an **orchestrator** — not you — drives the feature process. In a blizzard fleet, the work graph owns the spine the build skills normally drive (plan → plan-review → build → verify → review → pre-push → deliver); you execute **one node-step** of it. You are in this mode when your session opens as a fleet worker (`# Blizzard fleet worker`), your prompt names a chunk's node-step, and the `blizzard runner` CLI is on your path.

Two rules follow:

- **The node prompt is the charter.** It defines your step's scope, the assets it `produces:`, and how you end. This extension supplies the *method* inside that charter — never a competing process spine. Do not run a whole-feature build process (`glacier`, `flurry`, `iceberg`) to execute a node-step: the graph already is that process. A build process is only in play when the node's own requirements align with one's shape (see the `build` row below).
- **Methodology output feeds node assets.** Where a process below produces a report or findings, submit that content as the node's declared asset (`blizzard runner artifact create`), in the shape the node prompt asks for.

## Node-step → methodology map

Generic node names map to this extension's processes and canonical roles. Match on the node's *name and requirements*, not on graph identity — a custom graph reusing these names gets the same mapping. The highest-leverage rows are `verify` and `review`: those node-steps must run through this extension's machinery, not improvised inline checks.

| Node-step | Use from this extension |
|-----------|------------------------|
| `plan` | Author the plan the way [glacier's planning step](./build/glacier/process.md) does: target the application's **verifiability matrix** and **architecture guidance**, and spawn an isolated `arctic-explorer` for codebase research rather than reading it all into your own context. |
| `plan-review` | Run the **plan-review gate** over the plan through the [`plan` review axis](./review/axes/plan.md), which owns what the gate checks. |
| `build` | [Philosophy](./philosophy.md) and [completion](./completion.md) govern how you build — doc-first, tested-and-docs-updated. If the node's requirements align with a build process's shape — e.g. a small localized fix matching `snowball` — choose it from [the build index](./build/index.md); otherwise build directly, spawning isolated `ice-carver` slices for independent parallel work. |
| `verify` | Close through the **verify finale**: spawn the canonical `verify-finale` role to verify through a method the application's verifiability matrix declares, building and recording a missing method rather than improvising an LLM pass. Spawn `frontend-verifier` / `backend-verifier` for runtime checks. A green build or type-check is not verification. |
| `review` | Run the [faceted review](./review/faceted/process.md) as the review engine — a cold facet lead, one fork per facet, one aggregated deduped report; its cold lead matches the node's cold-eyes charter. Name facets from the [axes registry](./review/axes/index.md) to cover the node's required axes (correctness, architecture, design quality, …), adding `context` when agent-facing markdown changed and `documentation` when public docs changed. [Reporting](./review/reporting.md) severities structure the findings asset. |
| `pre-push` | [Commit conventions](./delivery/commit/conventions.md) govern the rebased commits; where the node asks for review judgment on the integrated result, the [multi-axis delivery review](./delivery/review/process.md) is the reusable core. |
| `resolve` | Mechanical repair under the node prompt — commit conventions apply; no process spine. |
| `retrospective` | Orchestrator-owned; no winter-workflow process maps. |

The `deliver` node runs on the hub with no agent session, so no row maps.
