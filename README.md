# winter-workflow

A [winter](https://codeberg.org/pgross/winter) extension that adds an opinionated agentic workflow to a winter workspace.

## Features

- **Blizzard team workflow** (`/wf-blizzard`) — turn the session into a lead agent that decomposes work and delegates to specialized teammates (architect, developer, code-reviewer, runner, test-mediator, backend/frontend verifiers, explorer). The lead agent orchestrates; teammates do the work.
- **Thaw** (`/wf-thaw`) — focused investigate-change-verify loop for small, localized changes to existing code (bug fix, tweak, adjustment, regression repair). Composes explorer → developer → verifier, each spawned standalone (no team coordination), with a hard iteration cap; bails to `/wf-blizzard` when the work is bigger than a thaw.
- **Cold review** (`/wf-cold-review`) — independent code review by a fresh-context `code-reviewer` subagent with zero prior conversation history.
- **Harness review** (`/wf-harness-review`) — independent review of whether the agentic harness (verifier tooling, agent context, conventions) is keeping pace with application change, and whether the application is shaped for agent productivity. Cold, one-shot `harness-reviewer` subagent; complements `/wf-cold-review`.
- **Agentic Development Manager** (`agentic-development-manager` subagent) — reviews and authors agent-facing markdown (agents, skills, CLAUDE.md, `ai/` docs) for clarity, single-source-of-truth, and non-duplication.
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
- `/wf-commit` commits the worktree
- `wf-agentic-development-manager` is spawnable as a subagent
- The blizzard team agents (`architect`, `developer`, `explorer`, `runner`, `test-mediator`, `backend-verifier`, `frontend-verifier`, `code-reviewer`) are role-pure subagents that live at the top of `agents/`, symlinked into `.claude/agents/` as `wf-<name>.md`. They can be spawned standalone from any caller (the `/wf-thaw` skill composes `explorer` → `developer` → verifier this way), or as members of a blizzard team via `/wf-blizzard`. See [`agents/README.md`](./agents/README.md) for the role-pure / caller-injects-coordination convention.
