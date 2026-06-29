# Definition of done for feature work

Feature work is not done when the code is written — it is done when the change is **tested** and its **documentation surfaces are updated**. Self-enforce this bar on conversational, top-level work: when you implement a change directly in a session without a build skill, meet it before reporting the work complete, rather than leaving the user to ask, turn after turn, whether it was tested and whether the docs were updated.

- **Tested** — exercise the change using a verification method declared in the application's **verifiability matrix**: the catalog its own harness maintains of how that application's changes are asserted correct, each entry a runnable command or a named conceptual interaction. A green build or typecheck is not a test; run the real probe that distinguishes done from not-done.

  When no declared method covers the change: build one — add or extend a durable verification method and add its row to the matrix — rather than running an ad-hoc LLM verification pass.

  When the application has no matrix yet: fall back to its documented test strategy (`context/testing/` or equivalent) and treat the absence as a prompt to bootstrap the matrix.
- **Docs updated** — reflect the change in each documentation surface it affects:
  - **Agent-facing `context/` docs** — the conventions and references agents read (a repo's `context/` tree, an extension `index.md`, `CLAUDE.md`).
  - **External-facing public docs** — the project's user- and adopter-facing documentation, where it has any (a rendered docs site, adopter guides, the user-facing README).

  A change owes only the surfaces it actually touches; a surface that doesn't apply is a noted N/A, not a silent skip.

The **build skills** satisfy the *tested* bar through their own runtime-probe flows and reference this convention rather than restating it: `glacier` and `blizzard` verify each change at runtime and run a pre-push review spanning the code, agent-facing, and public-docs axes; `thaw`, scoped to small localized changes, verifies at runtime and surfaces the owed delivery surfaces in its report for the user to carry. `blizzard`'s verify finale now consults the application's verifiability matrix first — verifying through a declared method and building one (with its matrix row) when none exists, rather than an ad-hoc LLM pass; aligning `glacier` and `thaw` to read the matrix the same way is follow-up work.
