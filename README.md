# winter-workflow

A [winter](https://github.com/paul-gross/winter) extension that adds an opinionated agentic workflow to a winter workspace.

## Features

- **Blizzard team workflow** (`/wf-blizzard`) — turn the session into a lead agent that decomposes work and delegates to specialized teammates (architect, developer, code-reviewer, runner, test-mediator, backend/frontend verifiers, explorer). The lead agent orchestrates; teammates do the work.
- **Thaw** (`/wf-thaw`) — focused investigate-change-verify loop for small, localized changes to existing code (bug fix, tweak, adjustment, regression repair). Composes explorer → developer → verifier, each spawned standalone (no team coordination), with a hard iteration cap; bails to `/wf-blizzard` when the work is bigger than a thaw.
- **Cold review** (`/wf-cold-review`) — independent code review by a fresh-context `code-reviewer` subagent with zero prior conversation history.
- **Harness review** (`/wf-harness-review`) — independent review of whether the agentic harness (verifier tooling, agent context, conventions) is keeping pace with application change, and whether the application is shaped for agent productivity. Cold, one-shot `harness-reviewer` subagent; complements `/wf-cold-review`.
- **Context review** (`/wf-context-review`) — independent review of agent-facing markdown (agents, skills, `CLAUDE.md`, `ai/` docs) against the workspace's documented conventions for clarity, single-source-of-truth, and non-duplication. Cold, one-shot `context-reviewer` subagent; complements `/wf-cold-review` and `/wf-harness-review`.
- **Documentation review** (`/wf-documentation-review`) — independent review of external-facing public documentation (user/adopter guides, a rendered docs site, the user-facing README) against the code it documents. Cold, one-shot `documentation-reviewer` subagent; complements `/wf-cold-review`, `/wf-harness-review`, and `/wf-context-review`.
- **Harness score** (`/wf-harness-score`) — codebase-scoped maturity score against the harness-model 5-stage × 10-dimension matrix. Spawns `explorer` to gather evidence; the main agent applies the rubric and emits an HTML report (plus JSON sidecar) under `~/.claude/winter/harness-scores/`. Codebase-scoped counterpart to `/wf-cold-review` and `/wf-harness-review` (which are diff-scoped).
- **Pre-push review** (`/wf-pre-push`) — fans out `code-reviewer` plus, conditionally on the project's surfaces, `harness-reviewer`, `context-reviewer`, and `documentation-reviewer` in parallel over the un-pushed range (`origin/master..HEAD`), then synthesizes a single advisory summary. Deliberately decoupled from `/ws-push` — invoke before pushing to surface findings, then push (or not) yourself.
- **Context Reviewer** (`context-reviewer` subagent) — reviews agent-facing markdown (agents, skills, CLAUDE.md, `ai/` docs) against the workspace's documented conventions for clarity, single-source-of-truth, and non-duplication. Review-only; paired with `harness-reviewer`.
- **Documentation Reviewer** (`documentation-reviewer` subagent) — reviews external-facing public documentation (user/adopter guides, a rendered docs site, the user-facing README) for accuracy against the code it documents, completeness for a human audience, and single-source-of-truth against canonical sources. Review-only; explicitly distinct from `context-reviewer` (agent-facing markdown) and `harness-reviewer` (the harness seam).
- **Conventional commits** (`/wf-commit`) — stages everything, infers the right type/scope from the diff and conversation, and writes a conventional-commit message.
- **Project-convention defaults** — when a project has no documented principles or test strategy, the blizzard team has built-in defaults (SOLID + Clean Architecture, test pyramid, CLI-driven test data) it can offer to adopt.

## Installation

Add to the workspace's `.winter/config.toml`:

```toml
[[standalone_repository]]
name = "winter-workflow"
url = "git@github.com:paul-gross/winter-workflow.git"
```

Then run `winter ws init` (or `/ws-setup`). The `wf-` prefix below is the default — it is workspace-configurable, so your install may differ.

**Skills** — invoke as `/wf-<name>`:

- [`/wf-blizzard`](./skills/blizzard/SKILL.md) — turn the session into a lead agent that decomposes work and delegates to a team of specialists.
- [`/wf-cold-review`](./skills/cold-review/SKILL.md) — fresh-context, one-shot code review of a diff.
- [`/wf-commit`](./skills/commit/SKILL.md) — stage everything and write a conventional-commit message inferred from the diff.
- [`/wf-context-review`](./skills/context-review/SKILL.md) — fresh-context, one-shot review of agent-facing markdown against the workspace's documented conventions.
- [`/wf-documentation-review`](./skills/documentation-review/SKILL.md) — fresh-context, one-shot review of external-facing public documentation against the code it documents.
- [`/wf-harness-review`](./skills/harness-review/SKILL.md) — fresh-context, one-shot review of whether the harness keeps pace with the code.
- [`/wf-harness-score`](./skills/harness-score/SKILL.md) — score the codebase against the harness-model maturity matrix and emit an HTML report.
- [`/wf-pre-push`](./skills/pre-push/SKILL.md) — fan out the applicable reviewers in parallel over the un-pushed range, then synthesize one advisory summary.
- [`/wf-thaw`](./skills/thaw/SKILL.md) — investigate-change-verify loop for a small, localized code change, with a hard iteration cap.

**Agents** — role-pure subagents, symlinked as `wf-<name>` and spawnable standalone or as blizzard teammates (see [`agents/README.md`](./agents/README.md) for the role-pure / caller-injects-coordination convention):

- [`architect`](./agents/architect.md) — high-level design, interfaces, dependencies.
- [`backend-verifier`](./agents/backend-verifier.md) — API/CLI/database verification.
- [`code-reviewer`](./agents/code-reviewer.md) — architectural code review.
- [`context-reviewer`](./agents/context-reviewer.md) — reviews agent-facing markdown against documented conventions.
- [`developer`](./agents/developer.md) — code implementation, unit tests, refactoring.
- [`documentation-reviewer`](./agents/documentation-reviewer.md) — reviews external-facing public documentation for accuracy and currency.
- [`explorer`](./agents/explorer.md) — investigates undocumented systems, writes AI-centric docs.
- [`frontend-verifier`](./agents/frontend-verifier.md) — Chrome DevTools browser verification.
- [`harness-reviewer`](./agents/harness-reviewer.md) — application↔harness seam review against a diff.
- [`runner`](./agents/runner.md) — service lifecycle and log monitoring.
- [`test-mediator`](./agents/test-mediator.md) — test strategy, scenario design, verifier dispatch.
