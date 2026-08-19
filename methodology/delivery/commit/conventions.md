# Commit Message Conventions (Workspace Default)

This is the fallback convention used when no project-specific `CONTRIBUTING.md` or
`workspace:/context/project/contributing.md` exists. Projects can provide their own conventions — this file covers the
basics.

## Format

```text
<type>(<scope>): <description>

<optional body>
```

**The first line (type, scope, description) must be all lowercase.**

## Types

| Type       | When to Use                                |
| ---------- | ------------------------------------------ |
| `feat`     | New feature or capability                  |
| `fix`      | Bug fix                                    |
| `docs`     | Documentation changes                      |
| `chore`    | Maintenance, dependency updates            |
| `refactor` | Code restructuring without behavior change |
| `test`     | Test additions or updates                  |
| `perf`     | Performance improvements                   |
| `style`    | Code style / formatting changes            |
| `ai`       | AI agent workflow improvements             |

### Product-backlog types

These types apply only when the workspace ships product-backlog content under `winter-product:/backlog/` and
`winter-product:/work/` (or an equivalent backlog layout). Skip them if the workspace doesn't manage a product backlog.

| Type              | When to Use                                                                                                                                               |
| ----------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `product(<name>)` | Any change to a `.idea.md` or `.work.md` item — creating, refining, promoting to work, or adding a technical approach. Scope is the kebab-case item name. |
| `todo(<name>)`    | Any change to a `.todo.md` item — creating, editing, or promoting. Scope is the kebab-case TODO name.                                                     |
| `feat`            | Archiving a completed work item or TODO (the archive move ships completed functionality, not backlog content).                                            |

### Initial repo setup

A brand-new repo starts with **two** `initial(<repo-name>)` commits, in this order:

1. `initial(<repo-name>): initial commit` — **empty**: no files (`git commit --allow-empty`). It exists purely as a
   stable anchor for rebasing — with it in place, every real commit (including the next one) can be rewritten with
   `git rebase -i` without hitting the root-commit special case.
2. `initial(<repo-name>): initial implementation` — the first real content. During the first pass on a new repo, keep
   **amending this commit** (`git commit --amend`) as the initial implementation takes shape, rather than stacking
   micro-commits; normal commit history starts after it.

These two are the only commits that use the `initial` type; everything after them follows the standard types above.

## Body

For non-trivial changes, include a body that explains:

- What was changed and why
- Any important decisions or trade-offs
