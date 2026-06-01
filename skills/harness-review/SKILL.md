---
description: Use when the user says "review the harness" or asks about agent context, verifier tooling, agent docs, or recent agent mistakes — checks whether the agentic harness keeps pace with application change and whether the application is shaped for agent productivity. Cold, one-shot harness-reviewer subagent. Different axis from /wf-cold-review (which reviews the code, not the harness).
argument-hint: "[uncommitted]"
allowed-tools: Bash, Read, Agent
---

# Harness Review

Run a **cold** harness review — an independent `harness-reviewer` subagent evaluates the changes with **zero prior conversation context**. "Cold" means fresh eyes: the reviewer hasn't seen your design discussion, your prior attempts, or your justifications. It reads the diff, the harness, and the documentation on its own terms.

`/wf-harness-review` mirrors `/wf-cold-review` in shape (cold, one-shot, no team) but reviews a *different concern axis*. Where `/wf-cold-review` asks "is the code architecturally sound?", `/wf-harness-review` asks "does the harness keep pace with the change, and is the application shaped so agents can develop it productively?". Run both for full coverage; run this one when you specifically care about the application↔harness seam.

The unit of review is the **change-set**, which may span several repos in one feature env — for example, a CLI command in one repo and the agent docs that describe it in another. The skill discovers every in-scope repo and spawns **one** reviewer over the union of their diffs — never one reviewer per repo. Run from a standalone repo, or in an env where only one repo changed, it reviews that single repo exactly as before.

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

Use `Agent` to spawn `harness-reviewer` with a **self-contained** prompt. Spawn **one** reviewer over the whole change-set — never one per repo. The reviewer has no memory of this session — every fact it needs must be in the prompt.

The prompt must contain:

1. **Framing**: "This is a one-shot standalone harness review. Read the diff, the harness, and the documentation; report categorized findings; and stop. There is no team coordinating you — do not attempt task coordination, messaging, or follow-on work."
2. **Scope**: which mode (branch-vs-base vs. uncommitted), and the in-scope repos — for each, its absolute worktree path and base ref (single-repo mode lists one). State explicitly: "Review these as one change-set."
3. **The diff commands to run** so the reviewer reads the diff itself — run them in **each** in-scope repo's worktree (`cd` to its path first):
   - Branch-vs-base: `git diff <base>...HEAD --stat` for the file overview, then `git diff <base>...HEAD` for the full diff, then `git log --oneline <base>..HEAD` for commit shapes (reverts/fixups are signal).
   - Uncommitted: `git diff HEAD --stat` then `git diff HEAD`.
4. **Where to look for evidence** — follow the *Mining mistake evidence* section of your agent body for the full procedure (encoded-cwd derivation, mtime + filename-overlap filters, failure signals, graceful fallback). The caller-supplied context you need on top of that:
   - **CWDs to enumerate** for transcripts: the workspace root, **every in-scope worktree path**, and each one's project source checkout. Pass each candidate through the encoded-cwd transform (`/` → `-`); skip those without a directory in `~/.claude/projects/`.
   - **Time window** for both git history and transcripts: roughly the diff's age — for branch-vs-base, since the base commit; for uncommitted, the last ~30 days.
   - **Documentation** to load eagerly: workspace `CLAUDE.md` and nested `CLAUDE.md` files, `ai/` directories (workspace and per-project/per-extension), `agents/README.md` and adjacent agent definitions, relevant `SKILL.md` files, `CONTRIBUTING.md`/`ARCHITECTURE.md`.
5. **Review instructions**: walk both checklists from `agents/harness-reviewer.md` explicitly — harness-change concerns (verification tooling currency, agent markdown currency, recent-mistake evidence, feedforward/feedback opportunities, new conventions) and application-architecture concerns with agentic ramifications (observability, configurability/pluggability, code architecture, typing/inline comments). When the change-set spans two or more repos: because you hold all of them at once, flag any **cross-repo contradiction** within your axis — a harness change in one repo (a renamed command, a removed convention) that leaves agent docs, verifier scaffolds, or `CLAUDE.md` in another repo stale — as a single finding. Skip an axis silently if there are no findings — do not pad. Be specific: file, line, agent/skill, axis, concrete direction. No rewrites.
6. **Output format**: categorized findings, plus an evidence sources footer.
   - `## must-fix` — concrete harness/application gaps that will produce repeated agent mistakes or block verification.
   - `## consider` — non-blocking agent-productivity suggestions.
   - `## notes` — brief acknowledgments of what the change gets right + any out-of-scope routing (e.g., "structural concern; defer to `code-reviewer`").
   - `## Evidence sources` — one line for git history (what was searched, what surfaced) and one line for transcripts (paths searched, or "not present, git-history-only").
   - If the diff has no agent-seam concerns, one or two sentences saying so is the entire report.

Spawn in the foreground — you need the findings to relay them.

### 4. Relay findings

Present the reviewer's report to the user as-is, with a one-line preamble noting the scope reviewed — single-repo (e.g., "Cold harness review of 7 files changed on `<branch>` vs. `<base>` in `<repo-path>`") or change-set (e.g., "Cold harness review of 12 files across 3 repos in env `alpha`"). Do not editorialize or argue with findings — the user decides what to act on.

## Why "cold"

A reviewer that sat in on the design discussion absorbs the author's framing. A cold reviewer reads only what's in the code, the harness, and the docs. That gap is where the most valuable findings live — and for the application↔harness seam specifically, the "outsider re-reading the agent context" perspective is exactly the one that catches stale references and missing feedforward.

## Why no team

`/wf-harness-review` is deliberately one-shot, mirroring `/wf-cold-review`. The reviewer is a role-pure agent (see [`../../agents/README.md`](../../agents/README.md)) and the skill injects no coordination context — there is no shared `TaskList`, no peers, no follow-on. This keeps it composable: a user can invoke it directly, a blizzard snowflake can invoke it as a contained sub-step, and the reviewer never tries to coordinate work it isn't responsible for.
