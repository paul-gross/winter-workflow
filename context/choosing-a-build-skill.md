# Choosing a build skill

Skill and agent names in this extension's docs are canonical; the install symlinks add a workspace-configurable prefix (commonly `wf-`), so e.g. `glacier` is typically invoked as `/wf-glacier`.

Route by the shape of the work before invoking a build skill:

| Skill | When to use |
|-------|-------------|
| [`snowball`](../skills/snowball/SKILL.md) | Small, localized change to existing code — bug fix, tweak, adjustment, regression repair, confined to one worktree |
| [`flurry`](../skills/flurry/SKILL.md) | A batch of several small, mostly-independent features — a defined set of distinct small asks to deliver together, fanned out across multiple feature environments in parallel (a fresh one-shot ice-carver per ask, one commit each, one batch pre-push review at the end) |
| [`glacier`](../skills/glacier/SKILL.md) | One feature built to a plan — mid-sized or large, net-new or multi-module, with a plan and/or acceptance criteria, workable as-is, or a discrete phase of a larger plan; phases run strictly in order, with a phase's independent slices parallelized inside it |
| [`iceberg`](../skills/iceberg/SKILL.md) | Ad hoc work — unplanned, unphased instructions fed in conversationally, especially several in flight across different work targets — default to delegation via the standing foreman |

`flurry` vs. `iceberg` — both spread work across multiple environments, but `flurry` is a **closed batch** (a known set of asks, run to completion, then it ends with a per-env review) driven by one lead with no team, while `iceberg` is an **open-ended conversational stream** handled by a standing foreman running a live team. `flurry` vs. `glacier` — `glacier` is one feature on one linear track; `flurry` is many small features across many parallel tracks. `snowball` vs. `glacier` — `snowball` is one packed throw at one spot; when the work turns out to need design, phasing, or more roles, it bails to `glacier`.

Across these skills, aim for **Sonnet/Terra-class `ice-carver` subagents**: `ice-carver` is the workhorse implementation role, and that class is the right default tier for routine implementation — reserve more capable tiers for orchestration and judgment.
