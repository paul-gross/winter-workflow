# Choosing a build process

Route by the shape of the work before executing a build process:

| Process | When to use |
|---------|-------------|
| [`snowball`](./snowball/process.md) | Small, localized change to existing code — bug fix, tweak, adjustment, regression repair, confined to one worktree |
| [`flurry`](./flurry/process.md) | A batch of several small, mostly-independent features — a defined set of distinct small asks to deliver together, fanned out across multiple feature environments in parallel (a fresh one-shot ice-carver per ask, one commit each, then one concurrent pre-push process execution per environment) |
| [`glacier`](./glacier/process.md) | One feature built to a plan — mid-sized or large, net-new or multi-module, with a plan and/or acceptance criteria, workable as-is, or a discrete phase of a larger plan; phases run strictly in order, with a phase's independent slices parallelized inside it |
| [`iceberg`](./iceberg/process.md) | Ad hoc work — unplanned, unphased instructions fed in conversationally, especially several in flight across different work targets — default to delegation via a standing coordinator |

`flurry` vs. `iceberg` — both spread work across multiple environments, but `flurry` is a **closed batch** (a known set of asks, run to completion, then closed by one aggregated review phase built from concurrent per-environment `pre-push` invocations) driven by one lead with no team, while `iceberg` is an **open-ended conversational stream** handled by a standing coordinator running a live team. `flurry` vs. `glacier` — `glacier` is one feature on one linear track; `flurry` is many small features across many parallel tracks. `snowball` vs. `glacier` — `snowball` is one packed throw at one spot; when the work turns out to need design, phasing, or more roles, it bails to `glacier`.

Across these processes, use **workhorse model intent (Sonnet/Terra class) for isolated `ice-carver` roles**: `ice-carver` is the routine implementation role; reserve more capable tiers for orchestration and judgment.
