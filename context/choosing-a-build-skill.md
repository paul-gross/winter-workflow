# Choosing a build skill

This extension installs the skills described in the [README](../README.md) Features section and the role-pure subagents rostered in [`agents/README.md`](../agents/README.md), spawnable standalone or as blizzard teammates — see that README for the roster and the role-pure / caller-injects-coordination convention. Skill and agent names in this extension's docs are canonical; the install symlinks add a workspace-configurable prefix (commonly `wf-`), so e.g. `glacier` is typically invoked as `/wf-glacier`.

Route by the shape of the work before invoking a build skill — the [README](../README.md) feature entries describe what each one does:

| Skill | When to use |
|-------|-------------|
| [`thaw`](../skills/thaw/SKILL.md) | Small, localized change to existing code — bug fix, tweak, adjustment, regression repair, confined to one worktree |
| [`flurry`](../skills/flurry/SKILL.md) | A batch of several small, mostly-independent features — a defined set of distinct small asks to deliver together, fanned out across multiple feature environments in parallel (a fresh one-shot developer per ask, one commit each, a pre-push review per env) |
| [`glacier`](../skills/glacier/SKILL.md) | Planned or phased work — a mid-sized feature with a plan and/or acceptance criteria, workable as-is, or a discrete phase of a larger plan |
| [`delegate`](../skills/delegate/SKILL.md) | Ad hoc work — unplanned, unphased instructions fed in conversationally, especially several in flight across different work targets — default to delegation via the standing foreman |
| [`blizzard`](../skills/blizzard/SKILL.md) | One large feature needing a coordinated team — net-new feature or multi-module work in a single feature environment, where design, verification, and review should run as a live team |

`flurry` vs. `delegate` — both spread work across multiple environments, but `flurry` is a **closed batch** (a known set of asks, run to completion, then it ends with a per-env review) driven by one lead with no team, while `delegate` is an **open-ended conversational stream** handled by a standing foreman running a live team. `flurry` vs. `glacier` — `glacier` is one feature on one linear track; `flurry` is many small features across many parallel tracks.

Across these skills, reach for **Sonnet `developer` subagents** often: `developer` is the workhorse implementation role, and Sonnet is the right default tier for routine implementation — reserve more capable tiers for orchestration and judgment.
