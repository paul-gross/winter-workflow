# winter-workflow

A [winter](https://codeberg.org/pgross/winter) extension that adds an opinionated agentic workflow to a winter workspace.

## Features

- **Blizzard team workflow** (`/wf-blizzard`) — turn the session into a lead agent that decomposes work and delegates to specialized teammates (architect, developer, code-reviewer, runner, test-mediator, backend/frontend verifiers, explorer). The lead agent orchestrates; teammates do the work.
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
- `/wf-commit` commits the worktree
- `wf-agentic-development-manager` is spawnable as a subagent
- The blizzard team agents (`architect`, `developer`, etc.) are spawnable inside a blizzard session by their basename — they live under `.claude/agents/wf-blizzard/` but Claude Code discovers them by filename
