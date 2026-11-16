# Pre-push review

Review the selected committed delivery change-set without pushing it. This process is the pre-push binding for the
reusable [multi-axis delivery review](../review/process.md).

## Inputs

- `mode: advisory|blocking`. Default an omitted mode to `advisory`.
- `pinned_scope: exclude|include|only`. An omitted value takes the default owned by
  [`../../review/change-set.md`](../../review/change-set.md).
- `review_bases`: optional per-worktree verified refs with documented reasons for targets whose configured upstream
  cannot be diffed.

Reject any other value.

## Steps

1. Execute [`../review/process.md`](../review/process.md) with `scope: unpushed`, the selected `pinned_scope`, any
   `review_bases`, and the supplied `mode`.
2. Return its synthesized result and decision outcome unchanged. If nothing is ahead of an upstream in the selected
   pinned scope and there are no blockers, report `nothing to review; nothing is ahead of upstream`.
3. Do not push. Delivery remains the human caller's separate decision.

`unpushed` is intentional: a pre-push gate reviews only committed work relative to each worktree's delivery upstream
because uncommitted work cannot be pushed. It remains distinct from `branch-vs-base`, which compares a feature branch
with the repository's integration base. Processes that gate completion before commit must bind `uncommitted` directly to
the reusable delivery review instead.
