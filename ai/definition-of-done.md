# Definition of done for feature work

Feature work is not done when the code is written — it is done when the change is **tested** and its **documentation surfaces are updated**. Self-enforce this bar on conversational, top-level work: when you implement a change directly in a session without a build skill, meet it before reporting the work complete, rather than leaving the user to ask, turn after turn, whether it was tested and whether the docs were updated.

- **Tested** — exercise the change per the touched repo's documented test strategy (its `ai/testing/` or equivalent). A green build or typecheck is not a test; run the real probe that distinguishes done from not-done.
- **Docs updated** — reflect the change in each documentation surface it affects:
  - **Agent-facing `ai/` docs** — the conventions and references agents read (a repo's `ai/` tree, an extension `index.md`, `CLAUDE.md`).
  - **External-facing public docs** — the project's user- and adopter-facing documentation, where it has any (a rendered docs site, adopter guides, the user-facing README).

  A change owes only the surfaces it actually touches; a surface that doesn't apply is a noted N/A, not a silent skip.

The **build skills** already satisfy this bar through their own flows and reference this convention rather than restating it: `glacier` and `blizzard` verify each change at runtime and run a pre-push review spanning the code, agent-facing, and public-docs axes; `thaw`, scoped to small localized changes, verifies at runtime and surfaces the owed delivery surfaces in its report for the user to carry.
