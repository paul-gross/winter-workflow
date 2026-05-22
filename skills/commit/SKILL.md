---
description: Commit all changes in the current worktree with a conventional commit message summarizing the work
argument-hint: "[amend]"
allowed-tools: Bash, Read, Grep, Glob
---

Commit all changes in the current working tree. Follow these steps:

## 1. Stage Everything

Stage ALL changes - tracked, untracked, and deleted files. Do not cherry-pick. Commit everything in the worktree.

```bash
git add -A
```

## 2. Review What's Being Committed

```bash
git diff --cached --stat
git diff --cached
git log --oneline -5
```

### 2a. ADM review gate for agent-facing config

If the staged diff touches any of these (run `git diff --cached --name-only` to check):

- `.claude/` (any path)
- `agents/` or `agents/**/*.md`
- `skills/` or `skills/**/SKILL.md`
- Any `CLAUDE.md` (root or nested)
- Any `ai/**/*.md`

…then **before** writing the commit message, **ask the user once**: "This commit touches agent-facing config. Want me to run the `agentic-development-manager` review first?" If they say yes, spawn the ADM with the staged diff as input; relay findings; let them decide whether to fix-then-commit or commit-as-is. This gate is documented in `winter-workflow:/index.md` ("ADM review for agent-facing configuration"). Do not auto-spawn — the user is in the loop.

If the diff is product/backlog content (under `winter-product:/backlog/`, `winter-product:/work/`, or a project repo's `ai/` docs that describe future vision/roadmaps), the ADM convention explicitly does **not** apply — skip the prompt.

## 3. Load Commit Conventions

Check for project-specific commit conventions in this order (use the first one found):

1. `CONTRIBUTING.md` in the current worktree root
2. `./ai/project/contributing.md` (project-specific workspace config)
3. [commit-conventions.md](./commit-conventions.md) (workspace default fallback)

## 4. Write the Commit Message

Follow the conventions loaded in step 3. Write a commit message that:
- Summarizes what changed and WHY based on the conversation context and the actual diff
- Uses the format specified by the conventions
- Includes a body with more detail if the changes are non-trivial
- Ends with the co-author line

## 5. Commit

Use a HEREDOC to ensure proper formatting:

Use the format from the conventions loaded in step 3. Example:

```bash
git commit -m "$(cat <<'EOF'
<commit message adhering to project's commit standards>

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
EOF
)"
```

## 6. If Arguments Include "amend"

Instead of creating a new commit, amend the previous commit:

1. Stage all changes: `git add -A`
2. Read the existing commit message: `git log -1 --format=%B`
3. Either append additional context to the bottom of the existing message, or rewrite the message entirely if the scope of changes has shifted significantly
4. Amend: `git commit --amend -m "$(cat <<'EOF' ... EOF )"`

## 7. Verify

```bash
git status
git log --oneline -3
```

$ARGUMENTS
