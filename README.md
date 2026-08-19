# ❄️ winter-workflow

A [winter](https://github.com/paul-gross/winter) extension that adds an opinionated agentic workflow to a winter
workspace.

📚 **Documentation:** <https://paul-gross.github.io/winter-docs/>

## ✨ Features

### Build

- **Iceberg foreman** (`iceberg`) — turn the session into a standing delegation foreman across *many* work targets at
  once (feature environments, standalone repos, or the workspace branch): the user feeds instructions conversationally,
  the foreman fans each out to a target-pinned teammate, parallelizes independent work (always across targets, and
  within a target when files don't overlap), queues conflicts, and reports results back as a per-agent digest. Always a
  team; the foreman never edits code. Requires resident-worker coordination and returns `unsupported-capability` rather
  than substituting isolated runs when the active runtime lacks it.
- **Glacier** (`glacier`) — drive a single feature — mid-sized or large, net-new or multi-module — to completion on one
  linear track of sequential subagent spawns, no team. Adopts or creates a plan put through the plan-review gate (with
  user approval), breaks it into ordered phases, and builds-and-verifies each phase one at a time (a phase's independent
  slices parallelized inside it) — an `ice-carver` implements it and the tool-building `verify-finale` closes it through
  the application's verifiability matrix; finishes with a blocking multi-axis completion review over uncommitted work
  and a retrospective.
- **Snowball** (`snowball`) — focused investigate-change-verify loop for small, localized changes to existing code (bug
  fix, tweak, adjustment, regression repair). Composes arctic-explorer → ice-carver → verifier, each spawned standalone
  (no team coordination), with a hard iteration cap; bails to `glacier` when the work is bigger than a snowball.
- **Flurry** (`flurry`) — fan a *batch* of small, mostly-independent feature asks out across *multiple* feature
  environments in parallel, no team. The flurry lead schedules the asks (parallel vs. sequential), pins each parallel
  track to its own environment, and dispatches a fresh one-shot `ice-carver` per task that implements, verifies at
  runtime, and lands exactly one commit; finishes with one concurrent `pre-push` invocation per environment, aggregates
  the findings into one batch review phase, and folds each finding back into the commit that produced it.

### Review

The five single-axis review skills below and `pre-push` share one **review engine** —
[`methodology/review/process.md`](methodology/review/process.md) — the single source for the scope vocabulary, how the
change-set is discovered across a feature env, the reviewer prompt scaffold, judgment-class model selection, and
inline-vs-subagent execution. The process selects judgment model intent and only deliberately downgrades a trivial
scope, disclosing that downgrade to the caller; this is not a public model-input override unless an adapter actually
exposes one. Beyond the default branch-vs-base and `uncommitted` diffs it adds explicit `<ref|range>` and `<paths>`
scopes, and the skills are thin pointers at it — so the harness can run an ad-hoc micro-review by following the engine
directly, no skill load required.

Cold, context, harness, and documentation review also accept a remote PR or MR locator supported by an available,
authenticated forge CLI; a caller using the engine directly may hand the `plan` axis a remote scope as well. The skills
bind axis defaults: remote code findings post inline, while context, harness, and documentation findings return as
reports. A caller using the review engine's normalized semantic inputs directly may explicitly override `scope.feedback`
to `report` or `inline`; the skills do not expose that override until their adapter syntax adds it. Retrieval and
posting failures are surfaced to the caller and never silently replaced with a local-branch review or reported as
successful feedback.

Direct reviewer-agent calls must use the engine's normalized axis, scope, and execution mode plus its shared prompt
scaffold, resolved targets, and review material. An arbitrary standalone prompt does not satisfy the review contract;
the skills perform this preparation for normal interactive use.

#### Skills

- **Cold review** (`cold-review`) — independent code review by a fresh-context `cold-reviewer` subagent with zero prior
  conversation history. Like the other review skills, it reviews the whole **change-set**: in a feature env, it
  discovers every in-scope repo and hands one reviewer the union of their diffs, so a change spanning multiple repos is
  reviewed as one. A standalone repo, or an env where only one repo changed, is reviewed exactly as a single repo.
- **Context review** (`context-review`) — independent review of agent-facing markdown (agents, skills, `CLAUDE.md`,
  `context/` or `methodology/` docs) against the workspace's documented conventions for clarity, single-source-of-truth,
  and non-duplication. Fresh, one-shot `context-reviewer` subagent.
- **Documentation review** (`documentation-review`) — independent review of external-facing public documentation
  (user/adopter guides, a rendered docs site, the user-facing README) against the code it documents. Fresh, one-shot
  `documentation-reviewer` subagent.
- **Harness review** (`harness-review`) — independent review of whether the agentic harness (verifier tooling, agent
  context, conventions) is keeping pace with application change, and whether the application is shaped for agent
  productivity. Fresh, one-shot `harness-reviewer` subagent.
- **Plan review** (`plan-review`) — independent review of an implementation plan before building, against the
  application's verifiability matrix and architecture guidance and the plan's own planning specs. Fresh, one-shot
  `plan-reviewer` subagent; runs standalone against a plan directory or a plan stated in the conversation (a
  conversation-stated plan is first persisted into the winter space's workflows directory so the review has an
  artifact), and is `glacier`'s default plan-review gate.
- **Faceted review** (`faceted-review`) — one cold **facet lead** gathers the change-set context once (diffs across all
  in-scope repos, commit messages, the adjacent agent-context needed to understand the change), then forks that context
  once per review **facet** and aggregates the facet reports into a single deduped, re-ranked review. Facets are
  open-ended: the registered review axes are facets, and any caller-named concern is too — an unregistered facet is
  reviewed by discovering the target's declared conventions for it, with the missing methodology reported as a finding.
  Methodology at [`methodology/review/faceted/process.md`](methodology/review/faceted/process.md).
- **Pre-push review** (`pre-push`) — fans out `cold-reviewer` plus, conditionally on the in-scope repos' surfaces,
  `harness-reviewer`, `context-reviewer`, and `documentation-reviewer` in parallel over each worktree's
  configured-upstream merge diff (`<upstream>...HEAD`), then synthesizes a single advisory summary. Reviews the whole
  **change-set** together, filtered by the explicit pinned scope: a resolvable upstream is included only when
  `tracking_ahead > 0`; `ahead > 0` only detects a delivery blocker when the upstream is missing or unresolved, so a
  fully pushed feature branch is not included. A verified explicit review base can make a blocked target reviewable but
  does not clear its delivery blocker. The cross-repo consistency pass catches a change in one repo contradicting
  another. Deliberately decoupled from `/ws-push` — invoke before pushing to surface findings, then push (or not)
  yourself.

#### Agents

- **Context Reviewer** (`context-reviewer` subagent) — reviews agent-facing markdown (agents, skills, CLAUDE.md,
  `context/` or `methodology/` docs) against the workspace's documented conventions for clarity, single-source-of-truth,
  and non-duplication. Review-only; paired with `harness-reviewer`.
- **Documentation Reviewer** (`documentation-reviewer` subagent) — reviews external-facing public documentation
  (user/adopter guides, a rendered docs site, the user-facing README) for accuracy against the code it documents,
  completeness for a human audience, and single-source-of-truth against canonical sources. Review-only; explicitly
  distinct from `context-reviewer` (agent-facing markdown) and `harness-reviewer` (the harness seam).
- **Plan Reviewer** (`plan-reviewer` subagent) — reviews an implementation plan against the application's verifiability
  matrix and architecture guidance, plus the plan's own planning specs, running the plainly read-only checks those specs
  declare. The gate for `glacier`'s planning step; its planning-spec conformance gate discovers the plan conventions a
  workspace planning framework declares.

### Evaluations

- **Harness score** (`harness-score`) — codebase-scoped maturity score against the harness-model 5-stage × 10-dimension
  matrix. Spawns `arctic-explorer` to gather evidence; the main agent applies the rubric and emits an HTML report (plus
  JSON sidecar) into the winter space's scores directory (`.winter/scores/` in the workspace by default).
  Codebase-scoped counterpart to `cold-review` and `harness-review` (which are diff-scoped).

### Tend

- **Distill** (`distill`) — rewrite existing markdown, agent-facing or human-facing, into its smallest current form, one
  file at a time: an extraction pass reduces each file to atomic fact lines (with deletions verified and auditable), the
  lines are mechanically scrambled, and a composition pass writes each replacement from the scrambled facts alone to a
  human-voice, agent-density bar, reporting measured before/after reductions. Preserves meaning, never changes what a
  rule requires — substance doubts and cross-file restructuring are escalated, not silently applied. Closes with a
  fresh-context `context-reviewer` pass over the result. Methodology at
  [`methodology/distill/process.md`](methodology/distill/process.md).
- **Distiller** (`distiller` subagent) — the cold role behind `distill`, spawned separately for each pass. The
  composition spawn never sees the original files, only scrambled fact lines: a writer that can see the source's
  structure and sentences trims them instead of rewriting, and one that knows what the content used to say frames the
  rewrite as a change ("previously X, now Y") instead of stating the current state. The coordinating session binds
  scope, spawns the passes, scrambles and installs between them, and routes review findings back through fresh spawns;
  it never authors content itself.

### Support

- **Review manifest** (`review-manifest`) — a **reading guide for a human reviewing a large diff**. It partitions every
  hunk of a change-set into verification tiers (`mechanical` / `pattern` / `novel`) and renders a **review order** so
  you spend full attention only on the hunks holding real decisions: `novel` first and in full, `pattern` collapsed
  behind their claims, `mechanical` as a one-line list. Agents *build* it — a fresh-context `diff-classifier` k-fan-out
  tiers each hunk (any disagreement fails closed to `novel`); a `manifest-auditor` adversarially refutes the cheap-tier
  claims and promotes any hit to `novel` — but **you read it**. Two hard invariants — total coverage (every hunk gets
  exactly one tier) and a diff-SHA freshness binding (a stale manifest is rejected). Advisory; gates nothing. Generate
  it on a large or rename-heavy diff — on its own to guide your own review, or before `cold-review` / `pre-push` to also
  focus an agent review. See [`methodology/review/manifest/index.md`](methodology/review/manifest/index.md).
- **Diff Classifier & Manifest Auditor** (`diff-classifier`, `manifest-auditor` subagents) — the role-pure pair behind
  the review manifest. `diff-classifier` is a fresh, k-voted per-hunk tier classifier (closed
  `mechanical`/`pattern`/`novel` vocabulary); `manifest-auditor` is the skeptic that samples the cheap tiers and tries
  to refute each claim. Both fail closed toward human review.

### Utility

- **Conventional commits** (`commit`) — stages everything, infers the right type/scope from the diff and conversation,
  and writes a conventional-commit message.
- **Project-convention defaults** — when a project has no documented principles, the `winter-architect` agent has
  built-in defaults (SOLID + Clean Architecture) it can offer to adopt.

## 🚀 Installation

Add to the workspace's `.winter/config.toml`:

```toml
[[standalone_repository]]
name = "winter-workflow"
url = "git@github.com:paul-gross/winter-workflow.git"
```

Then run `winter ws init` (or `/ws-setup`). The `wf-` prefix is the default — it is workspace-configurable, so your
install may differ.

See [`index.md`](./index.md) for the skills, agents, and commands this extension makes available once installed.

## License

MIT.
