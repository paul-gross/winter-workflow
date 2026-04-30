# Commit Message Conventions (Workspace Default)

This is the fallback convention used when no project-specific `CONTRIBUTING.md` or `workspace:/ai/project/contributing.md` exists. Projects can provide their own conventions — this file covers the basics.

## Format

```
<type>(<scope>): <description>

<optional body>

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```

**The first line (type, scope, description) must be all lowercase.**

## Types

| Type | When to Use |
|------|-------------|
| `feat` | New feature or capability |
| `fix` | Bug fix |
| `docs` | Documentation changes |
| `chore` | Maintenance, dependency updates |
| `refactor` | Code restructuring without behavior change |
| `test` | Test additions or updates |
| `perf` | Performance improvements |
| `style` | Code style / formatting changes |
| `ai` | AI agent workflow improvements |

### Product branch types

| Type | When to Use |
|------|-------------|
| `plan` | New plan or plan updates |
| `feat` | Archiving a completed plan |
| `todo` | Creating a TODO |

## Body

For non-trivial changes, include a body that explains:
- What was changed and why
- Any important decisions or trade-offs

## Co-Authorship

Always end with a co-author line:

```
Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```
