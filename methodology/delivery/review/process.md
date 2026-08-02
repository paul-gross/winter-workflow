# Multi-axis delivery review

Run a fresh, one-shot review across every applicable delivery axis for one local change-set, then synthesize the reports into one result. This process owns scope discovery, conditional axis selection, concurrent execution, synthesis, and advisory-versus-blocking policy. Callers bind its semantic inputs; specialized delivery processes do not copy its logic.

Use the semantic operations in [`../../runtime-ports.md`](../../runtime-ports.md). If fresh isolated roles or required concurrency are unavailable, return the runtime contract's `unsupported-capability` result.

## Inputs

| Input | Values |
|-------|--------|
| `scope` | `unpushed` or `uncommitted` |
| `mode` | `advisory` (default) or `blocking` |
| `pinned_scope` | for `unpushed`: `exclude`, `include`, or `only`; default owned by [`../../review/change-set.md`](../../review/change-set.md) |
| `review_bases` | optional per-worktree verified refs, with a documented reason, for upstream-less or unresolved-upstream review |

Reject any other value. `unpushed` reviews committed work relative to each worktree's configured upstream and applies `pinned_scope`; `uncommitted` reviews tracked changes from `HEAD` plus untracked, non-ignored files. The selected scope is used consistently for discovery and every axis.

## Output

Return one synthesized review result containing the selected scope, pinned scope when applicable, targets and their base kinds, delivery blockers, reviewers run and skipped, findings with original ids and severities, any gaps the reviewers returned, clean axes, and a `blocking_findings` set. Delivery blockers, confirmed cross-repository contradictions, and `must-fix` findings are blocking; `consider` findings and gaps remain advisory.

## Steps

### 1. Discover the change-set

Follow [`../../review/change-set.md`](../../review/change-set.md) in the selected scope. Pass `pinned_scope` and any documented `review_bases` for `unpushed`. It returns reviewable target entries and delivery blockers; do not rederive its predicates or base selection.

- For `unpushed`, each ordinary target's review material is `<configured-upstream>...HEAD`. A target using an explicit review base is labeled as such and remains blocked when it has no configured upstream.
- For `uncommitted`, each target's review material is its tracked diff from `HEAD` plus untracked, non-ignored files as whole-file additions.
- With zero reviewable targets and no blockers, return `nothing to review` with the selected scope and stop without starting reviewers.
- Preserve every blocker. Do not send a target with no review base to an axis reviewer; report it as unreviewed. Review other targets normally.
- Outside a feature environment, or with one target, use single-repository framing.
- With two or more targets, every reviewer receives the union as one change-set.

### 2. Classify applicable axes

Inspect the union of changed paths and probe each target's surfaces cheaply. Select an axis when any target meets its trigger:

- **Code**: select when the change-set changes code. A docs-only change-set skips it.
- **Harness**: select when any target has an agentic-harness surface, including agent definitions, skills, verifier scaffolds, harness conventions, agent-context entrypoints, or a `context/` or `methodology/` tree.
- **Context**: select when any target has agent-facing markdown and the change-set touches it. Apply [`../../review/agent-context-surface.md`](../../review/agent-context-surface.md).
- **Documentation**: select when any target has external-facing public documentation and the change-set touches code or docs that documentation covers. Public documentation includes docs sites, adopter guides, and user-facing README material; it excludes agent-facing context and methodology.

Record why each axis was selected or skipped and return a short dispatch line to the caller before starting reviews. A surface in one target can select an axis for the entire cross-repository change-set.

### 3. Run selected axes concurrently

Prepare one execution of [`../../review/process.md`](../../review/process.md) per selected axis with:

- the selected `scope` and already-discovered target set;
- the selected `pinned_scope`, review-base labels, and delivery blockers for `unpushed`;
- `execution_mode: fresh`;
- `axis: code`, `harness`, `context`, or `documentation` as selected.

Run all selected executions concurrently. Each uses a judgment-class model and the canonical role mapped by the shared review process. Every isolated reviewer spans all targets, returns one report, performs no follow-on work, and stops. Do not rediscover scope independently per axis.

### 4. Synthesize

After every selected reviewer returns, produce one consolidated result rather than pasting raw reports.

For a change-set spanning two or more repositories, scan the reports and changed material for contradictions between repositories. Consolidate a confirmed contradiction into one `cross-repo` finding naming all affected repositories and source finding ids. Treat it as blocking. Skip this pass for a single repository.

Use this shape:

```text
## Delivery review: <scope> — <target summary>

Reviewers: <roles run>
Not run: <roles skipped and why>
Files: <N> changed across <R> repositories

## delivery-blockers
- <repo>: <missing or unresolved upstream; review-base status>

## cross-repo
- (<role> <id>[ + <role> <id>]) <contradiction naming the repositories>

## must-fix
- (<role> <id>) <repo>: <finding>

## consider
- (<role> <id>) <repo>: <finding>

## gaps
- (<role> <id>) <repo>: <gap, naming the must-fix id(s) it explains as <role> <id>>

## clean
- <role>: no findings
```

Omit empty sections, including `delivery-blockers` and `gaps` when none exist. Preserve every original finding id. Prefix findings with their repository when the change-set spans repositories. Sort by axis in this order: code, harness, context, documentation. Distinguish skipped axes from axes that ran clean. Keep the synthesis to roughly 25 lines; offer a named raw report when more detail exists.

### 5. Apply mode

In `advisory` mode, ask the human caller once to choose:

1. Acknowledge the findings and continue delivery manually.
2. Address findings first and stop.
3. Show full reviewer reports, then ask the same question again.

This process performs no push, completion claim, or other delivery action.

In `blocking` mode, return the synthesis and stop without asking. The caller decides how to resolve or explicitly bypass findings. A completion-gating caller must resolve `blocking_findings` and rerun this process before claiming completion; advisory findings do not block that claim.

## Why fresh and concurrent

Fresh reviewers see the change on disk without the author's design-history bias. The axes are independent, so concurrent execution bounds wall time by the slowest applicable review while each reviewer still holds the complete cross-repository change-set.
