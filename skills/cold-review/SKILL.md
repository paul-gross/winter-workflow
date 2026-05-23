---
description: Use when the user says "review the diff/PR/branch" or asks about code correctness, architecture, or design quality — independent fresh-context code review by a code-reviewer subagent with no session history. Cold, one-shot. Different axis from /wf-harness-review (which reviews the harness, not the code).
argument-hint: "[uncommitted]"
allowed-tools: Bash, Read, Agent
---

# Cold Review

Run a **cold** code review — an independent `code-reviewer` subagent evaluates the changes with **zero prior conversation context**. "Cold" means fresh eyes: the reviewer hasn't seen your design discussion, your prior attempts, or your justifications. It reads the diff and the code on its own terms.

## Scope

Determined from `$ARGUMENTS`:

| Argument | Scope |
|----------|-------|
| _(none, default)_ | **Branch vs. base** — all commits on the current branch since it diverged from the repository's main branch |
| `uncommitted` | **Uncommitted changes** — staged + unstaged dirty local changes only |

## Steps

### 1. Determine scope

- `$ARGUMENTS` empty → branch-vs-base mode (default)
- `$ARGUMENTS` is `uncommitted` → uncommitted mode
- Anything else → tell the user the valid forms and stop

### 2. Resolve scope parameters

**Branch-vs-base mode (default):** detect the repository's main branch ref. Try in order, use the first that exists; call the result `<base>`.

```bash
git rev-parse --verify origin/master 2>/dev/null \
  || git rev-parse --verify origin/main 2>/dev/null \
  || git rev-parse --verify master 2>/dev/null \
  || git rev-parse --verify main
```

**Uncommitted mode:** nothing to resolve.

### 3. Confirm there's something to review

State check only — do not consume diff output here; the reviewer will pull the diff itself.

- Branch-vs-base: `git diff --quiet <base>...HEAD` — exit 0 means no commits on the branch; report "no changes to review" and stop.
- Uncommitted: `git diff --quiet HEAD` — exit 0 means clean working tree; report "no changes to review" and stop.

### 4. Spawn the reviewer

Use `Agent` to spawn the most capable code review agent available with a **self-contained** prompt. The reviewer has no memory of this session — every fact it needs must be in the prompt.

The prompt must contain:

1. **Framing**: "This is a one-shot standalone code review. Read the diff and the code, report findings, and stop. There is no team coordinating you — do not attempt task coordination, messaging, or follow-on work."
2. **Scope**: which mode (branch-vs-base vs. uncommitted), the base ref if applicable, and the repository path (CWD).
3. **The diff commands to run** so the reviewer reads the diff itself:
   - Branch-vs-base: `git diff <base>...HEAD --stat` for the file overview, then `git diff <base>...HEAD` for the full diff.
   - Uncommitted: `git diff HEAD --stat` then `git diff HEAD`.
4. **Review instructions**:
   - Read the changed files and surrounding code for context (existing patterns, conventions).
   - Eagerly load project documentation relevant to code review — coding standards, patterns, architecture, in-flight initiatives, and so on. Review against documented standards if present; fall back to your own judgment if not.
   - Be specific: file, line, principle violated, suggested direction. No rewrites.
5. **Output format**: categorized findings.
   - `## must-fix` — structural issues, principle violations, dangerous coupling, broken abstractions
   - `## consider` — non-blocking suggestions
   - `## notes` — brief acknowledgment of things the code gets right (optional, keep short)
   - If the code is clean, say so in one sentence.

Spawn in the foreground — you need the findings to relay them.

### 5. Relay findings

Present the reviewer's report to the user as-is, with a one-line preamble noting the scope reviewed (e.g., "Cold review of 7 files changed on `<branch>` vs. `<base>` in `<repo-path>`"). Do not editorialize or argue with findings — the user decides what to act on.

## Why "cold"

A reviewer that sat in on the design discussion absorbs the author's framing. A cold reviewer reads only what's in the code and the docs. That gap is where the most valuable findings live.
