---
description: Use when the user says "review the docs" or asks whether external-facing public documentation is accurate, current, or complete for a change — checks the user/adopter-facing docs (a rendered docs site, guides, the user-facing README) against the code they describe. Cold, one-shot documentation-reviewer subagent. Different axis from /wf-cold-review (code) and /wf-harness-review (the harness); explicitly NOT agent-facing markdown (that's context-reviewer).
argument-hint: "[uncommitted]"
allowed-tools: Bash, Read, Agent
---

# Documentation Review

Run a **cold** documentation review — an independent `documentation-reviewer` subagent evaluates the changes with **zero prior conversation context**. "Cold" means fresh eyes: the reviewer hasn't seen your design discussion, your prior attempts, or your justifications. It reads the diff, the public documentation, and the project's documentation conventions on its own terms.

`/wf-documentation-review` mirrors `/wf-cold-review` and `/wf-harness-review` in shape (cold, one-shot, no team) but reviews a *different concern axis*: external-facing **public** documentation — the docs a human adopter or end-user reads. It does **not** review agent-facing markdown (`CLAUDE.md`, `.claude/`, `agents/`, `skills/`, `ai/` — that's `context-reviewer`), harness markdown (`harness-reviewer`), or code (`code-reviewer`). Run it when a change may have left a user-facing doc stale, wrong, or missing.

The unit of review is the **change-set**, which may span several repos in one feature env — for example, a CLI command changed in one repo and its user-facing reference page in a separate docs repo. The skill discovers every in-scope repo and spawns **one** reviewer over the union of their diffs — never one reviewer per repo. Run from a standalone repo, or in an env where only one repo changed, it reviews that single repo exactly as before.

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

Use `Agent` to spawn `documentation-reviewer` with a **self-contained** prompt. Spawn **one** reviewer over the whole change-set — never one per repo. The reviewer has no memory of this session — every fact it needs must be in the prompt.

The prompt must contain:

1. **Framing**: "This is a one-shot standalone documentation review. Read the diff and the public documentation; report categorized findings; and stop. There is no team coordinating you — do not attempt task coordination, messaging, or follow-on work."
2. **Scope**: which mode (branch-vs-base vs. uncommitted), and the in-scope repos — for each, its absolute worktree path and base ref (single-repo mode lists one). State explicitly: "Review these as one change-set."
3. **The diff commands to run** so the reviewer reads the diff itself — run them in **each** in-scope repo's worktree (`cd` to its path first):
   - Branch-vs-base: `git diff <base>...HEAD --stat` for the file overview, then `git diff <base>...HEAD` for the full diff.
   - Uncommitted: `git diff HEAD --stat` then `git diff HEAD`.
4. **Review instructions**: locate the project's external-facing public documentation and discover its documentation conventions (do not assume them); if a "docs reflect this change" invariant is documented, review against it and cite it by path. Walk every concern axis from `agents/documentation-reviewer.md` — accuracy/currency, completeness for the audience, single-source-of-truth, clarity/navigation, and convention conformance & placement (does the doc follow the project's documentation conventions — e.g. README structure and the consumable-extension vs. example/reference distinction — and sit on the right surface). When the change-set spans two or more repos: because you hold all of them at once, flag any **cross-repo contradiction** — a public doc in one repo that now describes behavior a sibling repo's code change removed or renamed — as a single finding. Read code only to judge whether a public doc still describes it accurately. Stay out of agent-facing markdown, harness markdown, and code review — route those to the responsible reviewer in a `notes` line. Skip an axis silently if there are no findings. Be specific: page/section, the code symbol or canonical source it concerns, concrete direction. No rewrites.
5. **Output format**: categorized findings.
   - `## must-fix` — a public doc now wrong against the diff, a user-facing capability the diff adds with no public-doc coverage, or a doc that has diverged from a canonical source it copied.
   - `## consider` — non-blocking clarity/completeness/cross-link suggestions.
   - `## notes` — brief acknowledgments + any out-of-scope routing.
   - If the diff changes nothing a public doc covers, one sentence is the whole report. If the project ships no public documentation, the reviewer says so and stops.

Spawn in the foreground — you need the findings to relay them.

### 4. Relay findings

Present the reviewer's report to the user as-is, with a one-line preamble noting the scope reviewed — single-repo (e.g., "Cold documentation review of 7 files changed on `<branch>` vs. `<base>` in `<repo-path>`") or change-set (e.g., "Cold documentation review of 9 files across 2 repos in env `alpha`"). Do not editorialize or argue with findings — the user decides what to act on.

## Why "cold"

A reviewer that sat in on the design discussion absorbs the author's framing and tends to assume the docs already say what the author meant. A cold reviewer reads only what's on the page against what's in the code — which is exactly the perspective that catches a doc still describing a removed flag or a feature that shipped with no user-facing page.

## Why no team

`/wf-documentation-review` is deliberately one-shot, mirroring `/wf-cold-review` and `/wf-harness-review`. The reviewer is a role-pure agent (see [`../../agents/README.md`](../../agents/README.md)) and the skill injects no coordination context — there is no shared `TaskList`, no peers, no follow-on. This keeps it composable: a user can invoke it directly, a blizzard snowflake can invoke it as a contained sub-step, and the reviewer never tries to coordinate work it isn't responsible for.
