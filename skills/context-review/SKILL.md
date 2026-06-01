---
description: Use when the user says "review the agent docs/context" or asks whether agents, skills, commands, CLAUDE.md, or ai/ docs follow the workspace's documented conventions — checks agent-facing markdown for clarity, single-source-of-truth, and non-duplication. Cold, one-shot context-reviewer subagent. Different axis from /wf-cold-review (code) and /wf-harness-review (the harness seam); explicitly NOT external-facing public documentation (that's documentation-reviewer).
argument-hint: "[uncommitted]"
allowed-tools: Bash, Read, Agent
---

# Context Review

Run a **cold** context review — an independent `context-reviewer` subagent evaluates the changes with **zero prior conversation context**. "Cold" means fresh eyes: the reviewer hasn't seen your design discussion, your prior attempts, or your justifications. It reads the diff and the documented conventions on its own terms.

`/wf-context-review` mirrors `/wf-cold-review` and `/wf-harness-review` in shape (cold, one-shot, no team) but reviews a *different concern axis*: agent-facing markdown — agents, skills, commands, `CLAUDE.md` files, and `ai/` docs — against the workspace's documented conventions for clarity, single-source-of-truth, and non-duplication. It does **not** review code (`code-reviewer`), the application↔harness seam (`harness-reviewer`), or external-facing public documentation (`documentation-reviewer`).

The unit of review is the **change-set**, which may span several repos in one feature env. The skill discovers every in-scope repo and spawns **one** reviewer over the union of their diffs — never one reviewer per repo. This is the axis where cross-repo drift bites hardest: a convention renamed in one repo and left stale in another's mirror is one reviewer's finding only when that reviewer holds both. Run from a standalone repo, or in an env where only one repo changed, it reviews that single repo exactly as before.

## Scope

Determined from `$ARGUMENTS`:

| Argument | Scope |
|----------|-------|
| _(none, default)_ | **Branch vs. base** — all commits on each in-scope repo's branch since it diverged from that repo's main branch |
| `uncommitted` | **Uncommitted changes** — staged + unstaged dirty local changes only |

## Steps

### 1. Determine scope

- `$ARGUMENTS` empty → branch-vs-base mode (default)
- `$ARGUMENTS` is `uncommitted` → uncommitted mode
- Anything else → tell the user the valid forms and stop

### 2. Discover the change-set

A logical change may span several repos in one feature env. Follow `winter-workflow:/ai/changeset-scope.md` to detect the env and list the **in-scope repos** for this mode — branch-vs-base selects repos with `ahead > 0`; uncommitted selects repos with `dirty_count > 0`. The result is a set of `(repo, worktree-path, base-ref)` entries.

- **Zero repos in scope** → report "no changes to review" and stop.
- **Not in a feature env, or exactly one repo in scope** → single-repo mode: the change-set is the current repo (resolve its base ref with the ladder in the shared doc for branch-vs-base). Spawn one reviewer over that repo.
- **Two or more repos in scope** → the change-set spans the env: spawn **one** reviewer over the union of their diffs.

### 3. Spawn the reviewer

Use `Agent` to spawn `context-reviewer` with a **self-contained** prompt. Spawn **one** reviewer over the whole change-set — never one per repo. The reviewer has no memory of this session — every fact it needs must be in the prompt.

The prompt must contain:

1. **Framing**: "This is a one-shot standalone context review. Read the diff and the documented conventions; report categorized findings; and stop. There is no team coordinating you — do not attempt task coordination, messaging, or follow-on work."
2. **Scope**: which mode (branch-vs-base vs. uncommitted), and the in-scope repos — for each, its absolute worktree path and base ref (single-repo mode lists one). State explicitly: "Review these as one change-set."
3. **The diff commands to run** so the reviewer reads the diff itself — run them in **each** in-scope repo's worktree (`cd` to its path first):
   - Branch-vs-base: `git diff <base>...HEAD --stat` for the file overview, then `git diff <base>...HEAD` for the full diff.
   - Uncommitted: `git diff HEAD --stat` then `git diff HEAD`.
4. **Review instructions**: load workspace `CLAUDE.md` and nested `CLAUDE.md` files, plus whatever agent-facing-markdown conventions the workspace exposes (discover them — its `CLAUDE.md` and `ai/` docs point the way) and any `ai/` docs that govern the touched files. Check the changes against documented conventions — naming and prefixes (`ws-` vs `wf-`, agent/skill names), path notation (`workspace:`, `<extension>:`), voice and imperative style, frontmatter correctness, freshness of cross-references (broken links, stale anchors), and single-source-of-truth / non-duplication against existing peers. When the change-set spans two or more repos: because you hold all of them at once, flag any **cross-repo contradiction** — a command, convention, or symbol changed in one repo and left stale in another's reference or mirror — as a single finding. Be specific: file, line, convention violated, suggested direction. No rewrites.
5. **Output format**: categorized findings.
   - `## must-fix` — conflicting information, broken references, frontmatter errors, duplication that will drift.
   - `## consider` — non-blocking clarity/consistency suggestions.
   - `## notes` — brief acknowledgments + any out-of-scope routing.
   - If the agent-facing markdown is clean, one sentence is the whole report.

Spawn in the foreground — you need the findings to relay them.

### 4. Relay findings

Present the reviewer's report to the user as-is, with a one-line preamble noting the scope reviewed — single-repo (e.g., "Cold context review of 4 agent-facing files changed on `<branch>` vs. `<base>` in `<repo-path>`") or change-set (e.g., "Cold context review of 6 agent-facing files across 2 repos in env `alpha`"). Do not editorialize or argue with findings — the user decides what to act on.

## Why "cold"

A reviewer that sat in on the design discussion absorbs the author's framing and reads the doc as the author meant it. A cold reviewer reads only what's on the page against the documented conventions — which is exactly the perspective that catches an unclear instruction, a duplicated rule, or a stale cross-reference.

## Why no team

`/wf-context-review` is deliberately one-shot, mirroring `/wf-cold-review` and `/wf-harness-review`. The reviewer is a role-pure agent (see [`../../agents/README.md`](../../agents/README.md)) and the skill injects no coordination context — there is no shared `TaskList`, no peers, no follow-on. This keeps it composable: a user can invoke it directly, a blizzard snowflake can invoke it as a contained sub-step, and the reviewer never tries to coordinate work it isn't responsible for.
