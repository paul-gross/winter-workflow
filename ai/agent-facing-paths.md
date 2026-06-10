# Agent-facing markdown — trigger paths

The canonical classifier for "does this change touch agent-facing markdown?". The commit skill's context-review gate and the pre-push reviewer classification both apply this list — point here rather than copying it.

A changed path is agent-facing markdown when it matches any of:

- `.claude/` (any path)
- `agents/` or `agents/**/*.md`
- `skills/` or `skills/**/SKILL.md`
- Any `CLAUDE.md` (root or nested)
- Any `ai/**/*.md`

**Exclusion:** product/backlog content is not agent-facing configuration, even when it lives under a matching path — backlog plans, approaches, and product-centered initiatives describing future vision or roadmaps are reviewed by the user and downstream implementation agents, not the `context-reviewer`. See `winter-workflow:/index.md` ("Context review for agent-facing configuration").
