---
description: Use when the user says "review the diff/PR/branch" or asks about code correctness, architecture, or design quality — independent fresh-context code review by a code-reviewer subagent with no session history. Cold, one-shot. Different axis from the harness-review skill (which reviews the harness, not the code).
argument-hint: "[uncommitted]"
allowed-tools: Bash, Read, Agent
---

# Cold Review

Run a **cold** code review — an independent `code-reviewer` subagent evaluates the changes with **zero prior conversation context**. "Cold" means fresh eyes: the reviewer hasn't seen your design discussion, your prior attempts, or your justifications. It reads the diff and the code on its own terms.

The unit of review is the **change-set**, which may span several repos in one feature env. The skill discovers every in-scope repo and spawns **one** reviewer over the union of their diffs — never one reviewer per repo. Run from a standalone repo, or in an env where only one repo changed, it reviews that single repo exactly as before.

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

Use `Agent` to spawn the most capable code review agent available with a **self-contained** prompt. Spawn **one** reviewer over the whole change-set — never one per repo. The reviewer has no memory of this session — every fact it needs must be in the prompt.

The prompt must contain:

1. **Framing**: "This is a one-shot standalone code review. Read the diff and the code, report findings, and stop. There is no team coordinating you — do not attempt task coordination, messaging, or follow-on work."
2. **Scope**: which mode (branch-vs-base vs. uncommitted), and the in-scope repos — for each, its absolute worktree path and base ref (single-repo mode lists one). State explicitly: "Review these as one change-set."
3. **The diff commands to run** so the reviewer reads the diff itself — run them in **each** in-scope repo's worktree (`cd` to its path first):
   - Branch-vs-base: `git diff <base>...HEAD --stat` for the file overview, then `git diff <base>...HEAD` for the full diff.
   - Uncommitted: `git diff HEAD --stat` then `git diff HEAD`.
4. **Review instructions**:
   - Read the changed files and surrounding code for context (existing patterns, conventions).
   - Eagerly load project documentation relevant to code review — coding standards, patterns, architecture, in-flight initiatives, and so on. Review against documented standards if present; fall back to your own judgment if not.
   - When the change-set spans two or more repos: because you hold all of them at once, flag any **cross-repo contradiction** within your axis — a structural change in one repo that leaves a now-broken caller, dead reference, or contradicting assumption in another — as a single finding.
   - Be specific: file, line, principle violated, suggested direction. No rewrites.
5. **Output format**: categorized findings.
   - `## must-fix` — structural issues, principle violations, dangerous coupling, broken abstractions
   - `## consider` — non-blocking suggestions
   - `## notes` — brief acknowledgment of things the code gets right (optional, keep short)
   - If the code is clean, say so in one sentence.

Spawn in the foreground — you need the findings to relay them.

### 4. Relay findings

Present the reviewer's report to the user as-is, with a one-line preamble noting the scope reviewed — single-repo (e.g., "Cold review of 7 files changed on `<branch>` vs. `<base>` in `<repo-path>`") or change-set (e.g., "Cold review of 11 files across 3 repos in env `alpha`"). Do not editorialize or argue with findings — the user decides what to act on.

## Why "cold"

A reviewer that sat in on the design discussion absorbs the author's framing. A cold reviewer reads only what's in the code and the docs. That gap is where the most valuable findings live.
