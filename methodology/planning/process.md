# Planning process

Author or revise an implementation plan artifact. This process is caller-neutral and owns only the **authoring**: a
build process executes it before its own plan-review gate; an orchestrated plan node executes it under its graph's
charter, including on a re-entry after a failed gate; any session may run it standalone to produce a plan ready for
review. Judging the plan belongs to the [`plan` review axis](../review/axes/plan.md) through the shared
[review process](../review/process.md); the review loop, its convergence rules, and approval belong to the caller. The
caller resolves runtime concerns — roles, models, human interaction — through
[`../runtime-ports.md`](../runtime-ports.md).

A plan targets the two artifacts the application's harness declares — its **verifiability matrix** (how the
application's changes are asserted correct) and its **architecture guidance** (how its code must be shaped) — and its
own form is governed by [`./plan-shape.md`](./plan-shape.md). A planning framework that declares its own plan builder or
plan conventions wins for whichever it declares — discover them from the runtime context rather than assuming an agent,
command, or file layout; the pieces named here fill whatever the framework leaves undeclared.

## Semantic inputs

| Input             | Meaning                                                                                                                                                                       |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `findings`        | Optional: a plan-review report with must-fix findings. Present selects the revision step; absent selects authoring                                                            |
| `feature_or_plan` | Authoring only: a feature description, a plan file or directory, a refined work item, or an inline plan. Omitted on a revision round — the plan at `plan_root` is the subject |
| `plan_root`       | The caller-resolved location where the plan artifact lives (a work-item directory, a `<workflows-dir>` session directory, a graph asset)                                      |
| `work_target`     | The absolute path(s) of the repository or repositories the plan is judged against                                                                                             |

## Author

**Given** `feature_or_plan` includes a plan — a refined work item with its own directory, or one stated inline — adopt
it as the candidate. An inline plan has no reviewable artifact yet: with a planning framework whose conventions win,
hand it to that framework's plan builder to produce the artifact those conventions expect; otherwise write it verbatim
to `plan_root` and treat that file as the candidate.

**Otherwise** author one. Pick the plan's **altitude** first, from what is being built, per
[`./plan-shape.md`](./plan-shape.md) §Altitude — it selects which plan standards apply, from a one-liner to a phased
epic decomposition. With a planning framework, run its **plan builder** in an isolated context. With no framework, spawn
the canonical `winter-architect` role in a one-shot isolated context, carrying the
[isolated-role default](../runtime-ports.md#spawn-an-isolated-role), the feature, and `work_target`. Ask it to read the
relevant code and return an implementation approach — not code — conforming to [`./plan-shape.md`](./plan-shape.md) at
the selected altitude. The approach names each change's verification method and architectural fit as far as the
application's harness declares them, and surfaces a missing matrix or architecture guidance as a gap rather than
inventing around it. Write the returned plan to `plan_root`. If the builder needs the codebase explored, spawn an
isolated `arctic-explorer` with the research question and hand it the distilled finding rather than reading the code
into the coordinating context.

## Revise

When `findings` is supplied, it is a plan-review report against the plan at `plan_root`. Route it to the plan builder
that owns the plan — the framework's builder, or a fresh `winter-architect` spawn carrying the findings, the plan's
path, and `work_target` — to resolve each finding in the plan text. The one exception is a finding only a product
decision can resolve: return it to the caller unresolved rather than answering it in prose. One rule shapes the
revision:

**Deletion first.** Resolve a finding by removing or pointing before defending with new prose: cut the claim, the
mechanism passage, the restated fact the finding attacks, or any detail that exceeds the plan's declared **altitude**
([`./plan-shape.md`](./plan-shape.md) §Altitude), or replace it with a pointer to the owner. Text may be added only
where a finding names misdirected building — something the builder would do wrong without it — and the revision states
in one line, per addition, which finding required new text. A revision that grows the plan without that justification is
itself an unmet obligation for the next gate round; when findings keep demanding material the declared altitude
disables, revisit the altitude selection rather than accreting the material.
