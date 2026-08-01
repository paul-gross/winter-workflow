# Agent-facing markdown — trigger paths

The canonical classifier for "does this change touch agent-facing markdown?". Multi-axis delivery review applies this list — point here rather than copying it.

A changed path is agent-facing markdown when it matches any of:

- `.claude/` (any path)
- `agents/` or `agents/**/*.md`
- `skills/` or `skills/**/SKILL.md`
- Any `CLAUDE.md` (root or nested)
- Any `context/**/*.md`
- Any `methodology/**/*.md`

**Exclusion:** product/backlog content is not agent-facing configuration, even when it lives under a matching path — backlog plans, approaches, and product-centered initiatives describing future vision or roadmaps are reviewed by the user and downstream implementation agents, not the `context` axis.
