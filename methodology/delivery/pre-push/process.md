# Pre-push review

Review the selected committed delivery change-set without pushing it. This process is the pre-push binding for the reusable [multi-axis delivery review](../review/process.md).

## Inputs

- `mode: advisory|blocking`. Default an omitted mode to `advisory`.
- `pinned_scope: exclude|include|only`. Default an omitted value to `include` to preserve the workflow's historical coverage. This is explicitly equivalent to reviewing the project-worktree scope of `winter ws push --include-pinned`; use `exclude` to match bare default push or `only` to match a pinned-only push.
- `review_bases`: optional per-worktree verified refs with documented reasons for targets whose configured upstream cannot be diffed.

Reject any other value.

## Steps

1. Optionally generate a [review manifest](../../review/manifest/process.md) first with `scope: unpushed`, the selected `pinned_scope`, and any `review_bases` when the change-set is large or mechanical-heavy. It is advisory and does not replace review or clear a delivery blocker.
2. Execute [`../review/process.md`](../review/process.md) with `scope: unpushed`, the selected `pinned_scope`, any `review_bases`, and the supplied `mode`.
3. Return its synthesized result and decision outcome unchanged. If nothing is ahead of an upstream in the selected pinned scope and there are no blockers, report `nothing to review; nothing is ahead of upstream`.
4. Do not push. Delivery remains the human caller's separate decision.

`unpushed` is intentional: a pre-push gate reviews only committed work relative to each worktree's delivery upstream because uncommitted work cannot be pushed. It remains distinct from `branch-vs-base`, which compares a feature branch with the repository's integration base. Processes that gate completion before commit must bind `uncommitted` directly to the reusable delivery review instead.
