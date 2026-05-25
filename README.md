# winter-workflow

A [winter](https://codeberg.org/pgross/winter) extension that adds an opinionated agentic workflow to a winter workspace.

## Features

- **Blizzard team workflow** (`/wf-blizzard`) — turn the session into a lead agent that decomposes work and delegates to specialized teammates (architect, developer, code-reviewer, runner, test-mediator, backend/frontend verifiers, explorer). The lead agent orchestrates; teammates do the work.
- **Thaw** (`/wf-thaw`) — focused investigate-change-verify loop for small, localized changes to existing code (bug fix, tweak, adjustment, regression repair). Composes explorer → developer → verifier, each spawned standalone (no team coordination), with a hard iteration cap; bails to `/wf-blizzard` when the work is bigger than a thaw.
- **Cold review** (`/wf-cold-review`) — independent code review by a fresh-context `code-reviewer` subagent with zero prior conversation history.
- **Harness review** (`/wf-harness-review`) — independent review of whether the agentic harness (verifier tooling, agent context, conventions) is keeping pace with application change, and whether the application is shaped for agent productivity. Cold, one-shot `harness-reviewer` subagent; complements `/wf-cold-review`.
- **Harness score** (`/wf-harness-score`) — codebase-scoped maturity score against the harness-model 5-stage × 10-dimension matrix. Spawns `explorer` to gather evidence; the main agent applies the rubric and emits an HTML report (plus JSON sidecar) under `~/.claude/winter/harness-scores/`. Codebase-scoped counterpart to `/wf-cold-review` and `/wf-harness-review` (which are diff-scoped).
- **Pre-push review** (`/wf-pre-push`) — fans out `code-reviewer`, `harness-reviewer`, and (conditionally) `context-reviewer` in parallel over the un-pushed range (`origin/master..HEAD`), then synthesizes a single advisory summary. Deliberately decoupled from `/ws-push` — invoke before pushing to surface findings, then push (or not) yourself.
- **Context Reviewer** (`context-reviewer` subagent) — reviews agent-facing markdown (agents, skills, CLAUDE.md, `ai/` docs) against the workspace's documented conventions for clarity, single-source-of-truth, and non-duplication. Review-only; paired with `harness-reviewer`.
- **Conventional commits** (`/wf-commit`) — stages everything, infers the right type/scope from the diff and conversation, and writes a conventional-commit message.
- **Project-convention defaults** — when a project has no documented principles or test strategy, the blizzard team has built-in defaults (SOLID + Clean Architecture, test pyramid, CLI-driven test data) it can offer to adopt.

## Installation

Add to the workspace's `.winter/config.toml`:

```toml
[[standalone_repository]]
name = "winter-workflow"
url = "git@codeberg.org:pgross/winter-workflow.git"
```

Then run `winter ws init` (or `/ws-setup`). After install:

- `/wf-blizzard` starts a blizzard
- `/wf-thaw` runs an investigate-change-verify loop for a small, localized code change
- `/wf-cold-review` runs a fresh-context code review
- `/wf-harness-review` runs a fresh-context harness review
- `/wf-harness-score` scores the codebase against the harness-model maturity matrix
- `/wf-pre-push` fans out all three review axes in parallel over the un-pushed range
- `/wf-commit` commits the worktree
- `wf-context-reviewer` is spawnable as a subagent
- The role-pure subagents (`architect`, `developer`, `explorer`, `runner`, `test-mediator`, `backend-verifier`, `frontend-verifier`, `code-reviewer`, `harness-reviewer`) live at the top of `agents/`, symlinked into `.claude/agents/` as `wf-<name>.md`. They can be spawned standalone from any caller (the `/wf-thaw` skill composes `explorer` → `developer` → verifier this way) or as members of a blizzard team via `/wf-blizzard`. `harness-reviewer` is one exception — it's role-pure and symlinked like its peers, but it's currently invoked one-shot via `/wf-harness-review` rather than as a blizzard teammate. See [`agents/README.md`](./agents/README.md) for the role-pure / caller-injects-coordination convention.
