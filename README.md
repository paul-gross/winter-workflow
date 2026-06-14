# ❄️ winter-workflow

A [winter](https://github.com/paul-gross/winter) extension that adds an opinionated agentic workflow to a winter workspace.

📚 **Documentation:** <https://paul-gross.github.io/winter-docs/>

## ✨ Features

### Build

- **Blizzard team workflow** (`/wf-blizzard`) — turn the session into a lead agent that decomposes work and delegates to specialized teammates (architect, developer, code-reviewer, runner, test-mediator, backend/frontend verifiers, explorer). The lead agent orchestrates; teammates do the work. Single feature environment, dev→verify→review chain.
- **Delegate foreman** (`/wf-delegate`) — turn the session into a standing delegation foreman across *many* work targets at once (feature environments, standalone repos, or the workspace branch): the user feeds instructions conversationally, the foreman fans each out to a target-pinned teammate, parallelizes independent work (always across targets, and within a target when files don't overlap), queues conflicts, and reports results back as a per-agent digest. Always a team; the foreman never edits code.
- **Glacier** (`/wf-glacier`) — drive a single feature to completion on one linear track of sequential subagent spawns, no team. Adopts or creates a plan (with user approval), breaks it into ordered phases, and builds-and-verifies each phase one at a time with a `developer` that implements and verifies at runtime; finishes with a `/wf-pre-push` review and a retrospective.
- **Thaw** (`/wf-thaw`) — focused investigate-change-verify loop for small, localized changes to existing code (bug fix, tweak, adjustment, regression repair). Composes explorer → developer → verifier, each spawned standalone (no team coordination), with a hard iteration cap; bails to `/wf-blizzard` when the work is bigger than a thaw.

### Review

The four single-axis review skills below and `/wf-pre-push` share one **review engine** — [`ai/review.md`](ai/review.md) — the single source for the scope vocabulary, how the change-set is discovered across a feature env, the reviewer prompt scaffold, the explicit-and-overridable model, and inline-vs-subagent execution. Beyond the default branch-vs-base and `uncommitted` diffs it adds explicit `<ref|range>` and `<paths>` scopes, and the skills are thin pointers at it — so the harness can run an ad-hoc micro-review by following the engine directly, no skill load required.

- **Cold review** (`/wf-cold-review`) — independent code review by a fresh-context `code-reviewer` subagent with zero prior conversation history. Like the other `/wf-*` review skills, it reviews the whole **change-set**: in a feature env, it discovers every in-scope repo and hands one reviewer the union of their diffs, so a change spanning multiple repos is reviewed as one. A standalone repo, or an env where only one repo changed, is reviewed exactly as a single repo.
- **Context review** (`/wf-context-review`) — independent review of agent-facing markdown (agents, skills, `CLAUDE.md`, `ai/` docs) against the workspace's documented conventions for clarity, single-source-of-truth, and non-duplication. Cold, one-shot `context-reviewer` subagent; complements `/wf-cold-review` and `/wf-harness-review`.
- **Context Reviewer** (`context-reviewer` subagent) — reviews agent-facing markdown (agents, skills, CLAUDE.md, `ai/` docs) against the workspace's documented conventions for clarity, single-source-of-truth, and non-duplication. Review-only; paired with `harness-reviewer`.
- **Documentation review** (`/wf-documentation-review`) — independent review of external-facing public documentation (user/adopter guides, a rendered docs site, the user-facing README) against the code it documents. Cold, one-shot `documentation-reviewer` subagent; complements `/wf-cold-review`, `/wf-harness-review`, and `/wf-context-review`.
- **Documentation Reviewer** (`documentation-reviewer` subagent) — reviews external-facing public documentation (user/adopter guides, a rendered docs site, the user-facing README) for accuracy against the code it documents, completeness for a human audience, and single-source-of-truth against canonical sources. Review-only; explicitly distinct from `context-reviewer` (agent-facing markdown) and `harness-reviewer` (the harness seam).
- **Harness review** (`/wf-harness-review`) — independent review of whether the agentic harness (verifier tooling, agent context, conventions) is keeping pace with application change, and whether the application is shaped for agent productivity. Cold, one-shot `harness-reviewer` subagent; complements `/wf-cold-review`.
- **Harness score** (`/wf-harness-score`) — codebase-scoped maturity score against the harness-model 5-stage × 10-dimension matrix. Spawns `explorer` to gather evidence; the main agent applies the rubric and emits an HTML report (plus JSON sidecar) under `~/.claude/winter/harness-scores/`. Codebase-scoped counterpart to `/wf-cold-review` and `/wf-harness-review` (which are diff-scoped).
- **Pre-push review** (`/wf-pre-push`) — fans out `code-reviewer` plus, conditionally on the in-scope repos' surfaces, `harness-reviewer`, `context-reviewer`, and `documentation-reviewer` in parallel over the un-pushed range (`origin/master..HEAD`), then synthesizes a single advisory summary. Reviews the whole **change-set** — every repo in the feature env ahead of its upstream — together, with a cross-repo consistency pass that catches a change in one repo contradicting another. Deliberately decoupled from `/ws-push` — invoke before pushing to surface findings, then push (or not) yourself.
- **Review manifest** (`/wf-review-manifest`) — a **reading guide for a human reviewing a large diff**. It partitions every hunk of a change-set into verification tiers (`mechanical` / `pattern` / `novel`) and renders a **review order** so you spend full attention only on the hunks holding real decisions: `novel` first and in full, `pattern` collapsed behind their claims, `mechanical` as a one-line list. Agents *build* it — a fresh-context `diff-classifier` k-fan-out tiers each hunk (any disagreement fails closed to `novel`); a `manifest-auditor` adversarially refutes the cheap-tier claims and promotes any hit to `novel` — but **you read it**. Two hard invariants — total coverage (every hunk gets exactly one tier) and a diff-SHA freshness binding (a stale manifest is rejected). Advisory; gates nothing. Generate it on a large or rename-heavy diff — on its own to guide your own review, or before `/wf-cold-review` / `/wf-pre-push` to also focus an agent review. See [`ai/review-manifest/index.md`](ai/review-manifest/index.md).
- **Diff Classifier & Manifest Auditor** (`diff-classifier`, `manifest-auditor` subagents) — the role-pure pair behind the review manifest. `diff-classifier` is a cold, k-voted per-hunk tier classifier (closed `mechanical`/`pattern`/`novel` vocabulary); `manifest-auditor` is the skeptic that samples the cheap tiers and tries to refute each claim. Both fail closed toward human review.

### Utility

- **Conventional commits** (`/wf-commit`) — stages everything, infers the right type/scope from the diff and conversation, and writes a conventional-commit message.
- **Project-convention defaults** — when a project has no documented principles or test strategy, the blizzard team has built-in defaults (SOLID + Clean Architecture, test pyramid, CLI-driven test data) it can offer to adopt.

## 🚀 Installation

Add to the workspace's `.winter/config.toml`:

```toml
[[standalone_repository]]
name = "winter-workflow"
url = "git@github.com:paul-gross/winter-workflow.git"
```

Then run `winter ws init` (or `/ws-setup`). The `wf-` prefix is the default — it is workspace-configurable, so your install may differ.

See [`index.md`](./index.md) for the skills, agents, and commands this extension makes available once installed.

## License

MIT.
