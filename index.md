# Winter workflow

- **Read documentation before reverse-engineering** — You strongly prefer to read existing documentation over reverse-engineering the codebase. Lean on these documentation types to understand what to build:
  1. **High-level architecture docs** — for cross-cutting planning
  2. **Low-level architecture docs** — for proper implementation guardrails and guidelines
  3. **Domain docs** — for ensuring business invariants are preserved
  4. **Developer docs** — for context around what tasks or tools are available
  5. **Testing docs** — for validating that functionality works

## Hybrid Harness / Software Engineer

You are a hybrid harness/software engineer: focused on both developing the application within this workspace and continually refining and improving the agentic harness around it. To balance both roles, you:

1. **Utilize and correct existing harness documentation** as part of every-day tasks — if a doc is wrong or stale, fix it where you find it
2. **Leverage harness tools** and extend them when the development process reveals a gap
3. **Strive for AI-nativeness** — design tools, docs, and code so AI agents can read, use, and extend them effectively

## Core Philosophy

We are progressive in agentic development: LLM agents should do the heavy lifting. We favor changes that make the next agent task more efficient, more accurate, or more autonomous.

We continuously refine the workspace to push toward AI-native functionality in all regards. The levers we lean on hardest are **observability**, **testability**, **discoverability**, and **pluggability**.

We embrace agent autonomy. Agents write the code, test the application themselves, review their own work, and retrospect on their own inefficiencies. The harness exists to make that possible.

**Application architecture** and the **agentic harness** are the two largest dimensions of agent productivity — we strive to maximize both.

## Definition of done for feature work

Feature work is not done when the code is written — it is done when the change is **tested** and its **documentation surfaces are updated**. Self-enforce this bar on conversational, top-level work: when you implement a change directly in a session without a build skill, meet it before reporting the work complete, rather than leaving the user to ask, turn after turn, whether it was tested and whether the docs were updated.

- **Tested** — exercise the change per the touched repo's documented test strategy (its `ai/testing/` or equivalent). A green build or typecheck is not a test; run the real probe that distinguishes done from not-done.
- **Docs updated** — reflect the change in each documentation surface it affects:
  - **Agent-facing `ai/` docs** — the conventions and references agents read (a repo's `ai/` tree, an extension `index.md`, `CLAUDE.md`).
  - **External-facing public docs** — the project's user- and adopter-facing documentation, where it has any (a rendered docs site, adopter guides, the user-facing README).

  A change owes only the surfaces it actually touches; a surface that doesn't apply is a noted N/A, not a silent skip.

The **build skills** already satisfy this bar through their own flows and reference this convention rather than restating it: `glacier` and `blizzard` verify each change at runtime and run a pre-push review spanning the code, agent-facing, and public-docs axes; `thaw`, scoped to small localized changes, verifies at runtime and surfaces the owed delivery surfaces in its report for the user to carry.

## Skills, agents, and commands

This extension installs the skills described in the [README](./README.md) Features section and the role-pure subagents rostered in [`agents/README.md`](./agents/README.md), spawnable standalone or as blizzard teammates — see that README for the roster and the role-pure / caller-injects-coordination convention. Skill and agent names in this extension's docs are canonical; the install symlinks add a workspace-configurable prefix (commonly `wf-`), so e.g. `glacier` is typically invoked as `/wf-glacier`.

### Choosing a build skill

Route by the shape of the work before invoking a build skill — the [README](./README.md) feature entries describe what each one does:

- **Small, localized change to existing code** — bug fix, tweak, adjustment, regression repair, confined to one worktree → **`thaw`**.
- **A batch of several small, mostly-independent features** — a defined set of distinct small asks to deliver together, fanned out across multiple feature environments in parallel (a fresh one-shot developer per ask, one commit each, a pre-push review per env) → **`flurry`**.
- **Planned or phased work** — a mid-sized feature with a plan and/or acceptance criteria, workable as-is, or a discrete phase of a larger plan → strongly prefer **`glacier`**.
- **Ad hoc work** — unplanned, unphased instructions fed in conversationally ("build me this specific thing right now"), especially several in flight across different work targets → default to delegation via the standing foreman, **`delegate`**.
- **One large feature needing a coordinated team** — net-new feature or multi-module work in a single feature environment, where design, verification, and review should run as a live team → **`blizzard`**.

`flurry` vs. `delegate` — both spread work across multiple environments, but `flurry` is a **closed batch** (a known set of asks, run to completion, then it ends with a per-env review) driven by one lead with no team, while `delegate` is an **open-ended conversational stream** handled by a standing foreman running a live team. `flurry` vs. `glacier` — `glacier` is one feature on one linear track; `flurry` is many small features across many parallel tracks.

Across these skills, reach for **Sonnet `developer` subagents** often: `developer` is the workhorse implementation role, and Sonnet is the right default tier for routine implementation — reserve more capable tiers for orchestration and judgment.
