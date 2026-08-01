# ❄️ winter-workflow

A [winter](https://github.com/paul-gross/winter) extension that adds an opinionated agentic workflow to a winter workspace.

📚 **Documentation:** <https://paul-gross.github.io/winter-docs/>

## ✨ Features

### Build

- **Iceberg foreman** (`iceberg`) — turn the session into a standing delegation foreman across *many* work targets at once (feature environments, standalone repos, or the workspace branch): the user feeds instructions conversationally, the foreman fans each out to a target-pinned teammate, parallelizes independent work (always across targets, and within a target when files don't overlap), queues conflicts, and reports results back as a per-agent digest. Always a team; the foreman never edits code.
- **Glacier** (`glacier`) — drive a single feature — mid-sized or large, net-new or multi-module — to completion on one linear track of sequential subagent spawns, no team. Adopts or creates a plan gated on the verifiability + architecture plan-review (with user approval), breaks it into ordered phases, and builds-and-verifies each phase one at a time (a phase's independent slices parallelized inside it) — an `ice-carver` implements it and the tool-building `verify-finale` closes it through the application's verifiability matrix; finishes with a `pre-push` review and a retrospective.
- **Snowball** (`snowball`) — focused investigate-change-verify loop for small, localized changes to existing code (bug fix, tweak, adjustment, regression repair). Composes arctic-explorer → ice-carver → verifier, each spawned standalone (no team coordination), with a hard iteration cap; bails to `glacier` when the work is bigger than a snowball.
- **Flurry** (`flurry`) — fan a *batch* of small, mostly-independent feature asks out across *multiple* feature environments in parallel, no team. The flurry lead schedules the asks (parallel vs. sequential), pins each parallel track to its own environment, and dispatches a fresh one-shot `ice-carver` per task that implements, verifies at runtime, and lands exactly one commit; finishes with one batch `pre-push` review when every track is complete, folding each finding back into the commit that produced it.

### Review

The four single-axis review skills below and `pre-push` share one **review engine** — [`context/review.md`](context/review.md) — the single source for the scope vocabulary, how the change-set is discovered across a feature env, the reviewer prompt scaffold, the explicit-and-overridable model, and inline-vs-subagent execution. Beyond the default branch-vs-base and `uncommitted` diffs it adds explicit `<ref|range>` and `<paths>` scopes, and the skills are thin pointers at it — so the harness can run an ad-hoc micro-review by following the engine directly, no skill load required.

#### Skills

- **Cold review** (`cold-review`) — independent code review by a fresh-context `cold-reviewer` subagent with zero prior conversation history. Like the other review skills, it reviews the whole **change-set**: in a feature env, it discovers every in-scope repo and hands one reviewer the union of their diffs, so a change spanning multiple repos is reviewed as one. A standalone repo, or an env where only one repo changed, is reviewed exactly as a single repo.
- **Context review** (`context-review`) — independent review of agent-facing markdown (agents, skills, `CLAUDE.md`, `context/` docs) against the workspace's documented conventions for clarity, single-source-of-truth, and non-duplication. Fresh, one-shot `context-reviewer` subagent; complements `cold-review` and `harness-review`.
- **Documentation review** (`documentation-review`) — independent review of external-facing public documentation (user/adopter guides, a rendered docs site, the user-facing README) against the code it documents. Fresh, one-shot `documentation-reviewer` subagent; complements `cold-review`, `harness-review`, and `context-review`.
- **Harness review** (`harness-review`) — independent review of whether the agentic harness (verifier tooling, agent context, conventions) is keeping pace with application change, and whether the application is shaped for agent productivity. Fresh, one-shot `harness-reviewer` subagent; complements `cold-review`.
- **Pre-push review** (`pre-push`) — fans out `cold-reviewer` plus, conditionally on the in-scope repos' surfaces, `harness-reviewer`, `context-reviewer`, and `documentation-reviewer` in parallel over the un-pushed range (`origin/master..HEAD`), then synthesizes a single advisory summary. Reviews the whole **change-set** — every repo in the feature env ahead of its upstream — together, with a cross-repo consistency pass that catches a change in one repo contradicting another. Deliberately decoupled from `/ws-push` — invoke before pushing to surface findings, then push (or not) yourself.

#### Agents

- **Context Reviewer** (`context-reviewer` subagent) — reviews agent-facing markdown (agents, skills, CLAUDE.md, `context/` docs) against the workspace's documented conventions for clarity, single-source-of-truth, and non-duplication. Review-only; paired with `harness-reviewer`.
- **Documentation Reviewer** (`documentation-reviewer` subagent) — reviews external-facing public documentation (user/adopter guides, a rendered docs site, the user-facing README) for accuracy against the code it documents, completeness for a human audience, and single-source-of-truth against canonical sources. Review-only; explicitly distinct from `context-reviewer` (agent-facing markdown) and `harness-reviewer` (the harness seam).

### Evaluations

- **Harness score** (`harness-score`) — codebase-scoped maturity score against the harness-model 5-stage × 10-dimension matrix. Spawns `arctic-explorer` to gather evidence; the main agent applies the rubric and emits an HTML report (plus JSON sidecar) into the winter space's scores directory (`.winter/scores/` in the workspace by default). Codebase-scoped counterpart to `cold-review` and `harness-review` (which are diff-scoped).

### Support

- **Review manifest** (`review-manifest`) — a **reading guide for a human reviewing a large diff**. It partitions every hunk of a change-set into verification tiers (`mechanical` / `pattern` / `novel`) and renders a **review order** so you spend full attention only on the hunks holding real decisions: `novel` first and in full, `pattern` collapsed behind their claims, `mechanical` as a one-line list. Agents *build* it — a fresh-context `diff-classifier` k-fan-out tiers each hunk (any disagreement fails closed to `novel`); a `manifest-auditor` adversarially refutes the cheap-tier claims and promotes any hit to `novel` — but **you read it**. Two hard invariants — total coverage (every hunk gets exactly one tier) and a diff-SHA freshness binding (a stale manifest is rejected). Advisory; gates nothing. Generate it on a large or rename-heavy diff — on its own to guide your own review, or before `cold-review` / `pre-push` to also focus an agent review. See [`context/review-manifest/index.md`](context/review-manifest/index.md).
- **Diff Classifier & Manifest Auditor** (`diff-classifier`, `manifest-auditor` subagents) — the role-pure pair behind the review manifest. `diff-classifier` is a fresh, k-voted per-hunk tier classifier (closed `mechanical`/`pattern`/`novel` vocabulary); `manifest-auditor` is the skeptic that samples the cheap tiers and tries to refute each claim. Both fail closed toward human review.

### Utility

- **Conventional commits** (`commit`) — stages everything, infers the right type/scope from the diff and conversation, and writes a conventional-commit message.
- **Project-convention defaults** — when a project has no documented principles, the `winter-architect` agent has built-in defaults (SOLID + Clean Architecture) it can offer to adopt.

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
