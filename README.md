# ❄️ winter-workflow

A [winter](https://github.com/paul-gross/winter) extension that adds an opinionated agentic workflow to a winter
workspace.

📚 **Documentation:** <https://paul-gross.github.io/winter-docs/>

## ✨ Features

### Build

- **Rapid iteration** (`rapid-iteration`) — keep an interactive local build moving with a responsive coordinator,
  durable request queue, and fast preview feedback. Choose it explicitly when hardening should wait; see the
  [process](methodology/build/rapid-iteration/process.md) for its mode and ownership contract.
- **Iceberg foreman** (`iceberg`) — turn the session into a standing delegation foreman across *many* work targets at
  once (feature environments, standalone repos, or the workspace branch): the user feeds instructions conversationally,
  the foreman fans each out to a target-pinned teammate, parallelizes independent work (always across targets, and
  within a target when files don't overlap), queues conflicts, and reports results back as a per-agent digest. Always a
  team; the foreman never edits code. Requires resident-worker coordination and stops rather than substituting isolated
  runs when the active harness lacks it.
- **Ice age** (`ice-age`) — the monumental build: drive a whole *program* — many epics, hundreds of changes — from a
  rough backlog to an integrated, verified result, one segment at a time, asking you questions as they arise without
  idling. For each segment a handful of roles survey the reference implementation, correct the backlog, and cut slices
  just before building; each slice is built by an `ice-carver`, closed by `verification-engineer`, reviewed, and landed
  through a serialized integration gate; a checkpoint proves the segment and measures what it cost before the next
  begins. A concurrency cap bounds the roles in flight, a ledger on disk lets any later session resume, and a register
  lists everything decided without you. Nothing is pushed.
- **Glacier** (`glacier`) — drive a single feature — mid-sized or large, net-new or multi-module — to completion on one
  linear track of sequential subagent spawns, no team. Adopts or creates a plan put through the plan-review gate (with
  user approval), breaks it into ordered phases, and builds-and-verifies each phase one at a time (a phase's independent
  slices parallelized inside it) — an `ice-carver` implements it and the tool-building `verification-engineer` closes it
  through the application's verifiability matrix; finishes with a blocking multi-axis completion review over uncommitted
  work and a retrospective.
- **Snowball** (`snowball`) — focused investigate-change-verify loop for small, localized changes to existing code (bug
  fix, tweak, adjustment, regression repair). Composes arctic-explorer → ice-carver → verifier, each spawned standalone
  (no team coordination), with a hard iteration cap; bails to `glacier` when the work is bigger than a snowball.
- **Flurry** (`flurry`) — fan a *batch* of small, mostly-independent feature asks out across *multiple* feature
  environments in parallel, no team. The flurry lead schedules the asks (parallel vs. sequential), pins each parallel
  track to its own environment, and dispatches a fresh one-shot `ice-carver` per task that implements, verifies at
  runtime, and lands exactly one commit; finishes with one concurrent `pre-release` invocation per environment,
  aggregates the findings into one batch review phase, and folds each finding back into the commit that produced it.

### Review

The four single-axis review skills below and `pre-release` share one **review engine** —
[`methodology/review/process.md`](methodology/review/process.md) — the single source for the scope vocabulary, how the
change-set is discovered across a feature env, the reviewer prompt scaffold, judgment-class model selection, and
inline-vs-subagent execution. The process selects judgment model intent and only deliberately downgrades a trivial
scope, disclosing that downgrade to the caller; this is not a public model-input override unless a skill actually
exposes one. Beyond the default branch-vs-base and `uncommitted` diffs it adds explicit `<ref|range>` and `<paths>`
scopes, and the skills are thin pointers at it — so the harness can run an ad-hoc micro-review by following the engine
directly, no skill load required.

Cold, context, and documentation review also accept a remote PR or MR locator supported by an available, authenticated
forge CLI; a caller using the engine directly may hand the `plan` axis a remote scope as well. The skills bind axis
defaults: remote code findings post inline, while context and documentation findings return as reports. A caller using
the review engine's normalized semantic inputs directly may explicitly override `scope.feedback` to `report` or
`inline`; the skills do not expose that override until their argument syntax adds it. Retrieval and posting failures are
surfaced to the caller and never silently replaced with a local-branch review or reported as successful feedback.

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
- **Plan review** (`plan-review`) — independent review of an implementation plan before building, against the
  application's verifiability matrix and architecture guidance and the plan's own planning specs. Fresh, one-shot
  `plan-reviewer` subagent; runs standalone against a plan directory or a plan stated in the conversation (a
  conversation-stated plan is first persisted into the winter space's workflows directory so the review has an
  artifact), and is `glacier`'s default plan-review gate.
- **Faceted review** (`faceted-review`) — one cold **facet lead** gathers the change-set context once (diffs across all
  in-scope repos, commit messages, the adjacent agent-context needed to understand the change), then seeds one reviewer
  per review **facet** with it and aggregates the facet reports into a single deduped, re-ranked review. The lead is
  normally a spawned `faceted-reviewer`, which seeds each facet reviewer with a written orientation briefing; where the
  lead's own seat supports forking, it forks its gathered context per facet instead so each facet inherits it whole.
  Facets are open-ended: the registered review axes are facets, and any caller-named concern is too — an unregistered
  facet is reviewed by discovering the target's declared conventions for it, with the missing methodology reported as a
  finding. Methodology at [`methodology/review/faceted/process.md`](methodology/review/faceted/process.md).
- **Pre-release review** (`pre-release`) — fans out `cold-reviewer` plus, conditionally on the in-scope repos' surfaces,
  `context-reviewer` and `documentation-reviewer` in parallel over each worktree's configured-upstream merge diff
  (`<upstream>...HEAD`), then synthesizes a single advisory summary. Reviews the whole **change-set** together, filtered
  by the explicit pinned scope: a resolvable upstream is included only when `tracking_ahead > 0`; `ahead > 0` only
  detects a delivery blocker when the upstream is missing or unresolved, so a fully pushed feature branch is not
  included. A verified explicit review base can make a blocked target reviewable but does not clear its delivery
  blocker. The cross-repo consistency pass catches a change in one repo contradicting another. Deliberately decoupled
  from `/ws-push` — invoke before releasing to surface findings, then push (or not) yourself.

#### Agents

- **Context Reviewer** (`context-reviewer` subagent) — reviews agent-facing markdown (agents, skills, CLAUDE.md,
  `context/` or `methodology/` docs) against the workspace's documented conventions for clarity, single-source-of-truth,
  and non-duplication. Review-only.
- **Documentation Reviewer** (`documentation-reviewer` subagent) — reviews external-facing public documentation
  (user/adopter guides, a rendered docs site, the user-facing README) for accuracy against the code it documents,
  completeness for a human audience, and single-source-of-truth against canonical sources. Review-only; explicitly
  distinct from `context-reviewer` (agent-facing markdown).
- **Plan Reviewer** (`plan-reviewer` subagent) — reviews an implementation plan against the application's verifiability
  matrix and architecture guidance, plus the plan's own planning specs, running the plainly read-only checks those specs
  declare. The gate for `glacier`'s planning step; its planning-spec conformance gate discovers the plan conventions a
  workspace planning framework declares.

### Evaluations

- **Harness score** (`harness-score`) — codebase-scoped maturity score against the harness-model 5-stage × 10-dimension
  matrix. Spawns `arctic-explorer` to gather evidence; the main agent applies the rubric and emits an HTML report (plus
  JSON sidecar) into the winter space's scores directory (`.winter/scores/` in the workspace by default).
  Codebase-scoped counterpart to `cold-review` (which is diff-scoped).

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
- **Optimize context** (`optimize-context`) — audits a target's standing agent-context cost: per-skill and per-subagent
  invocation counts mined from every session transcript on this machine (machine-global — every local project, not just
  the target), joined against an inventory of the target's always-loaded surfaces — memory files, the extension hub,
  agent definitions, skill descriptions (target-scoped) — to find what's never invoked, dated by when it was added so a
  recently added skill reads as too new to judge rather than dead. Proposes `skillOverrides` entries for unused skills
  and writes only the operator-approved subset into a `settings.json`'s `skillOverrides` key, defaulting to
  `user-invocable-only`; hands every markdown-restructuring finding to `distill` or the context review axis rather than
  rewriting anything itself. The measurement half — mining invocation counts and inventorying surfaces — runs through
  [`scripts/context-usage.py`](scripts/context-usage.py), a deterministic, stdlib-only script; its `measure` subcommand
  is read-only, and its `apply` subcommand performs the one write described above. Methodology at
  [`methodology/optimize-context/process.md`](methodology/optimize-context/process.md).

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

See the ✨ Features section above for the skills, agents, and commands this extension makes available once installed;
[`index.md`](./index.md) routes to the reusable methodology behind each.

## License

Source-available under the Functional Source License 1.1 (FSL-1.1-ALv2). Each release converts to Apache License 2.0 two
years after it ships. See LICENSE.
