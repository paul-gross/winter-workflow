---
description: Use when the user says "review the harness" or asks about agent context, verifier tooling, agent docs, or recent agent mistakes — checks whether the agentic harness keeps pace with application change and whether the application is shaped for agent productivity. Cold, one-shot harness-reviewer subagent. Different axis from /wf-cold-review (which reviews the code, not the harness).
model: opus
argument-hint: "[uncommitted]"
allowed-tools: Bash, Read, Agent
---

# Harness Review

Run a **cold** harness review — an independent `harness-reviewer` subagent evaluates the changes with **zero prior conversation context**. "Cold" means fresh eyes: the reviewer hasn't seen your design discussion, your prior attempts, or your justifications. It reads the diff, the harness, and the documentation on its own terms.

`/wf-harness-review` mirrors `/wf-cold-review` in shape (cold, one-shot, no team) but reviews a *different concern axis*. Where `/wf-cold-review` asks "is the code architecturally sound?", `/wf-harness-review` asks "does the harness keep pace with the change, and is the application shaped so agents can develop it productively?". Run both for full coverage; run this one when you specifically care about the application↔harness seam.

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

Use `Agent` to spawn `harness-reviewer` with a **self-contained** prompt. The reviewer has no memory of this session — every fact it needs must be in the prompt.

The prompt must contain:

1. **Framing**: "This is a one-shot standalone harness review. Read the diff, the harness, and the documentation; report categorized findings; and stop. There is no team coordinating you — do not attempt task coordination, messaging, or follow-on work."
2. **Scope**: which mode (branch-vs-base vs. uncommitted), the base ref if applicable, and the repository path (CWD).
3. **The diff commands to run** so the reviewer reads the diff itself:
   - Branch-vs-base: `git diff <base>...HEAD --stat` for the file overview, then `git diff <base>...HEAD` for the full diff, then `git log --oneline <base>..HEAD` for commit shapes (reverts/fixups are signal).
   - Uncommitted: `git diff HEAD --stat` then `git diff HEAD`.
4. **Where to look for evidence** — follow the *Mining mistake evidence* section of your agent body for the full procedure (encoded-cwd derivation, mtime + filename-overlap filters, failure signals, graceful fallback). The caller-supplied context you need on top of that:
   - **CWDs to enumerate** for transcripts: the workspace root, the worktree path under review, and the project source checkout. Pass each candidate through the encoded-cwd transform (`/` → `-`); skip those without a directory in `~/.claude/projects/`.
   - **Time window** for both git history and transcripts: roughly the diff's age — for branch-vs-base, since the base commit; for uncommitted, the last ~30 days.
   - **Documentation** to load eagerly: workspace `CLAUDE.md` and nested `CLAUDE.md` files, `ai/` directories (workspace and per-project/per-extension), `agents/README.md` and adjacent agent definitions, relevant `SKILL.md` files, `CONTRIBUTING.md`/`ARCHITECTURE.md`.
5. **Review instructions**: walk both checklists from `agents/harness-reviewer.md` explicitly — harness-change concerns (verification tooling currency, agent markdown currency, recent-mistake evidence, feedforward/feedback opportunities, new conventions) and application-architecture concerns with agentic ramifications (observability, configurability/pluggability, code architecture, typing/inline comments). Skip an axis silently if there are no findings — do not pad. Be specific: file, line, agent/skill, axis, concrete direction. No rewrites.
6. **Output format**: categorized findings, plus an evidence sources footer.
   - `## must-fix` — concrete harness/application gaps that will produce repeated agent mistakes or block verification.
   - `## consider` — non-blocking agent-productivity suggestions.
   - `## notes` — brief acknowledgments of what the change gets right + any out-of-scope routing (e.g., "structural concern; defer to `code-reviewer`").
   - `## Evidence sources` — one line for git history (what was searched, what surfaced) and one line for transcripts (paths searched, or "not present, git-history-only").
   - If the diff has no agent-seam concerns, one or two sentences saying so is the entire report.

Spawn in the foreground — you need the findings to relay them.

### 5. Relay findings

Present the reviewer's report to the user as-is, with a one-line preamble noting the scope reviewed (e.g., "Cold harness review of 7 files changed on `<branch>` vs. `<base>` in `<repo-path>`"). Do not editorialize or argue with findings — the user decides what to act on.

## Why "cold"

A reviewer that sat in on the design discussion absorbs the author's framing. A cold reviewer reads only what's in the code, the harness, and the docs. That gap is where the most valuable findings live — and for the application↔harness seam specifically, the "outsider re-reading the agent context" perspective is exactly the one that catches stale references and missing feedforward.

## Why no team

`/wf-harness-review` is deliberately one-shot, mirroring `/wf-cold-review`. The reviewer is a role-pure agent (see [`../../agents/README.md`](../../agents/README.md)) and the skill injects no coordination context — there is no shared `TaskList`, no peers, no follow-on. This keeps it composable: a user can invoke it directly, a blizzard snowflake can invoke it as a contained sub-step, and the reviewer never tries to coordinate work it isn't responsible for.
