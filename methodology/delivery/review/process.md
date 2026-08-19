# Multi-axis delivery review

The multi-axis delivery review runs one fresh, one-shot review across every applicable delivery axis for a single local
change-set, then synthesizes the axis reports into one result. It performs no push, no completion claim, and no other
delivery action.

This process owns scope-discovery orchestration, conditional axis selection, concurrent execution, synthesis, and the
advisory-versus-blocking policy; callers bind its semantic inputs, and specialized delivery processes must not copy its
logic. The meanings of the `unpushed` and `uncommitted` scopes and their per-target review material are owned elsewhere
— discovery by [change-set discovery](../../review/change-set.md), per-scope review material by the scope-semantics
table in the [review process](../../review/process.md) — and this process does not redefine them. The rationale for
fresh execution — a reviewer context free of the author's framing and design-history bias — is owned by the review
process's execution-mode section.

Runtime coordination uses the semantic operations owned by [runtime ports](../../runtime-ports.md); when fresh isolated
roles or the required concurrency are unavailable, the process returns that runtime contract's `unsupported-capability`
result.

## Inputs

| Input          | Values                                                                                                                                                        |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `scope`        | Exactly `unpushed` or `uncommitted`; any other value is rejected.                                                                                             |
| `mode`         | `advisory` (the default) or `blocking`; any other value is rejected.                                                                                          |
| `pinned_scope` | `exclude`, `include`, or `only`; applies only to `unpushed`. The default for an omitted value is owned by [change-set discovery](../../review/change-set.md). |
| `review_bases` | Optional. Per-worktree verified refs, each with a documented reason, for reviewing a target whose upstream is missing or unresolved.                          |

## Discovery

Change-set discovery executes the procedure owned by [change-set discovery](../../review/change-set.md) in the selected
scope, passing `pinned_scope` and any documented `review_bases` for `unpushed`; its predicates and base selection must
never be re-derived here. Discovery returns reviewable target entries plus delivery blockers. The selected scope is used
consistently for discovery and for every axis run, and scope is never rediscovered independently per axis.

- With zero reviewable targets and no blockers, return `nothing to review` together with the selected scope and stop
  before starting any reviewer.
- Every delivery blocker from discovery is preserved into the final result.
- A target with no review base is never sent to an axis reviewer; it is reported as unreviewed while other targets are
  reviewed normally.
- A target reviewed against an explicit review base is labeled as such and remains a delivery blocker while it has no
  configured upstream.
- Outside a feature environment, or with exactly one target, the review uses single-repository framing. With two or more
  targets, every reviewer receives the union of targets as one change-set.

## Axis selection

Axis selection inspects the union of changed paths and cheaply probes each target's surfaces, selecting an axis whenever
any single target meets that axis's trigger. A surface present in one target selects its axis for the entire
cross-repository change-set.

| Axis            | Selected when…                                                                                                                                                                                     |
| --------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `code`          | …the change-set changes code; a docs-only change-set skips it.                                                                                                                                     |
| `harness`       | …any target has an agentic-harness surface: agent definitions, skills, verifier scaffolds, harness conventions, agent-context entrypoints, or a `context/` or `methodology/` tree.                 |
| `context`       | …any target has agent-facing markdown that the change-set touches; whether a path counts as agent-facing markdown is classified by [agent-context surface](../../review/agent-context-surface.md). |
| `documentation` | …any target has external-facing public documentation and the change-set touches code or docs that documentation covers.                                                                            |

For axis selection, public documentation means docs sites, adopter guides, and user-facing README material; it excludes
agent-facing context and methodology.

Record why each axis was selected or skipped and return a short dispatch line to the caller before any review starts.

## Execution

For each selected axis, prepare one execution of the [review process](../../review/process.md) carrying the selected
scope with the already-discovered target set, the selected `pinned_scope` with review-base labels and delivery blockers
for `unpushed`, `execution_mode: fresh`, and the selected axis (`code`, `harness`, `context`, or `documentation`). Each
axis execution uses a judgment-class model and the canonical role the shared review process maps for that axis.

All selected axis executions run concurrently. The axes are independent, so concurrent execution bounds wall time by the
slowest applicable review while each reviewer still holds the complete cross-repository change-set. Each isolated
reviewer spans all targets, returns exactly one report, performs no follow-on work, and stops.

## Cross-repository consistency

For a change-set spanning two or more repositories, synthesis scans the reports and the changed material for
contradictions between repositories; this pass is skipped for a single repository. A confirmed cross-repository
contradiction is consolidated into one `cross-repo` finding naming all affected repositories and the source finding ids.

## Synthesis

Synthesis produces one consolidated result rather than pasting raw reviewer reports. Keep the synthesis to roughly 25
lines and offer a named raw report when more detail exists.

The synthesis opens with:

- the title line `## Delivery review: <scope> — <target summary>`;
- a `Reviewers:` line listing roles run;
- a `Not run:` line listing skipped roles with why;
- a `Files: <N> changed across <R> repositories` line.

The sections, in order:

1. `## delivery-blockers`
2. `## cross-repo`
3. `## must-fix`
4. `## consider`
5. `## gaps`
6. `## clean`

Empty sections are omitted, including `delivery-blockers` and `gaps`. The synthesis distinguishes axes that were skipped
from axes that ran clean.

Line forms:

- A delivery-blockers line names the repo plus its missing or unresolved upstream and review-base status.
- A cross-repo line cites the source findings as `(<role> <id>[ + <role> <id>])` before the contradiction naming the
  repositories.
- A must-fix or consider line reads `(<role> <id>) <repo>: <finding>`.
- A gaps line additionally names the must-fix id(s) it explains in the same `<role> <id>` form.
- A clean line reads `<role>: no findings`.

Synthesis sorts findings by axis in the order code, harness, context, documentation. Every original finding id is
preserved through synthesis, and findings are prefixed with their repository whenever the change-set spans repositories.

The synthesized result contains the selected scope, the pinned scope when applicable, the targets with their review-base
kinds, delivery blockers, reviewers run and skipped, findings with their original ids and severities, any gaps the
reviewers returned, clean axes, and a `blocking_findings` set.

## Advisory versus blocking

Delivery blockers, confirmed cross-repository contradictions, and `must-fix` findings are blocking; `consider` findings
and gaps remain advisory.

- In `advisory` mode, ask the human caller once to choose among exactly three options: acknowledge the findings and
  continue delivery manually; address findings first and stop; or show the full reviewer reports and then ask the same
  question again.
- In `blocking` mode, return the synthesis and stop without asking; the caller decides how to resolve or explicitly
  bypass findings.

A completion-gating caller must resolve the `blocking_findings` set and rerun this process before claiming completion;
advisory findings do not block that claim.
