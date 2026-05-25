# Pre-push review

Run an LLM-guided review over the un-pushed range before pushing completed work. Spawns `code-reviewer`, `harness-reviewer`, and (conditionally) `context-reviewer` in parallel as one-shot subagents, then synthesizes the findings into a single summary for the caller.

`/wf-pre-push` mirrors `/wf-cold-review` and `/wf-harness-review` in shape (cold, one-shot, no team) but differs in two ways:

- **Scope is fixed to the un-pushed range** (`<base>..HEAD`, where `<base>` is `origin/master` or its equivalent). The point is to gate the push, so the range is whatever the push would actually deliver — not branch-vs-base of an arbitrary diverged history, and never uncommitted work (you don't push uncommitted work).
- **Multiple reviewers in parallel**, fanned out from one entry point. `/wf-cold-review` and `/wf-harness-review` are single-axis; `/wf-pre-push` covers the full review surface in one round-trip.

## Mode

Determined from `$ARGUMENTS`:

| Argument | Mode |
|----------|------|
| _(none, default)_ | **Advisory** — surface findings, prompt the caller to address them or proceed |
| `blocking` | **Blocking** — present findings and stop; caller must address them (or explicitly bypass) before pushing |

## Steps

### 1. Determine mode

- `$ARGUMENTS` empty → advisory (default)
- `$ARGUMENTS` is `blocking` → blocking
- Anything else → tell the user the valid forms and stop

### 2. Resolve the un-pushed range

Detect the repository's main branch ref. Try in order, use the first that exists; call the result `<base>`:

```bash
git rev-parse --verify origin/master 2>/dev/null \
  || git rev-parse --verify origin/main 2>/dev/null \
  || git rev-parse --verify master 2>/dev/null \
  || git rev-parse --verify main
```

Confirm there is something to review:

```bash
git diff --quiet <base>...HEAD
```

Exit 0 means the branch has no commits beyond `<base>` — report "nothing to review; branch is at base" and stop. Do not spawn reviewers on an empty range.

### 3. Classify the diff

Decide which reviewers to spawn based on what files the range touches:

```bash
git diff --name-only <base>...HEAD
```

- **Always spawn** `code-reviewer` — any change wants a structural read.
- **Always spawn** `harness-reviewer` — any change might affect the application↔harness seam.
- **Conditionally spawn** `context-reviewer` if the range touches agent-facing markdown. The canonical list of paths that trigger this gate (`.claude/`, `agents/`, `skills/**/SKILL.md`, any `CLAUDE.md`, any `ai/**/*.md`) lives in [`../commit/SKILL.md`](../commit/SKILL.md) under step 3 — apply the same classifier here. Product/backlog content (future vision, roadmaps, open backlog items) is excluded per the same convention.

Record which reviewers will be spawned. Tell the caller in one short line (e.g., "Spawning code-reviewer + harness-reviewer + context-reviewer over 7 files…") before issuing the spawns.

### 4. Spawn the reviewers in parallel

**Critical**: spawn all selected reviewers in a **single message** — multiple `Agent` tool calls in the same assistant turn. They are independent and benefit from concurrent execution. Sequential spawns waste wall time and give the caller a worse experience.

Each reviewer is one-shot, role-pure, and receives a **self-contained** prompt. None of them sees this session's history. All spawns are foreground — you need the findings to synthesize them.

Use the canonical preamble at the top of every spawn prompt, then attach the per-reviewer body documented below:

> This is a one-shot standalone review spawned by `/wf-pre-push`. Read the diff and the relevant context, report categorized findings, and stop. There is no team coordinating you — do not call `SendMessage`, `TaskCreate`, or `TaskUpdate`. When your report is done, stop.

Each prompt is inlined to keep step 4 self-contained — no cross-file step-number references, no competing preambles. If the sibling skills' prompt shapes evolve, update the inlined bodies here to stay aligned.

#### code-reviewer (`subagent_type: code-reviewer`)

Inline body:

> **Scope**: branch-vs-base.
> **Base**: `<base>` (substitute the ref resolved in step 2).
> **Repository path**: the current working directory.
>
> Read the diff yourself:
>
> ```
> git diff <base>...HEAD --stat
> git diff <base>...HEAD
> ```
>
> Read the changed files and surrounding code for context (existing patterns, conventions). Eagerly load project documentation relevant to code review — coding standards, patterns, architecture, in-flight initiatives. Review against documented standards if present; fall back to your own judgment if not.
>
> Be specific: file, line, principle violated, suggested direction. No rewrites.
>
> Output format — categorized findings:
> - `## must-fix` — structural issues, principle violations, dangerous coupling, broken abstractions
> - `## consider` — non-blocking suggestions
> - `## notes` — brief acknowledgments of things the code gets right (optional, keep short)
>
> If the code is clean, one sentence is the whole report.

#### harness-reviewer (`subagent_type: harness-reviewer`)

Inline body:

> **Scope**: branch-vs-base.
> **Base**: `<base>`.
> **Repository path**: the current working directory.
>
> Read the diff yourself:
>
> ```
> git diff <base>...HEAD --stat
> git diff <base>...HEAD
> git log --oneline <base>..HEAD
> ```
>
> Follow the *Mining mistake evidence* section of your agent body for the full procedure (encoded-cwd derivation, mtime + filename-overlap filters, failure signals, graceful fallback). Caller-supplied context:
>
> - **CWDs to enumerate** for transcripts: the workspace root, the worktree path under review, and the project source checkout. Pass each candidate through the encoded-cwd transform (`/` → `-`); skip those without a directory in `~/.claude/projects/`.
> - **Time window** for both git history and transcripts: the diff's age (since the base commit).
>
> Documentation to load eagerly: workspace `CLAUDE.md` and nested `CLAUDE.md` files, `ai/` directories (workspace and per-project/per-extension), `agents/README.md` and adjacent agent definitions, relevant `SKILL.md` files, `CONTRIBUTING.md` / `ARCHITECTURE.md`.
>
> Walk both checklists from your agent body — harness-change concerns (verification tooling currency, agent markdown currency, recent-mistake evidence, feedforward/feedback opportunities, new conventions) and application-architecture concerns with agentic ramifications (observability, configurability/pluggability, code architecture, typing/inline comments). Skip an axis silently if there are no findings — do not pad. Be specific: file, line, agent/skill, axis, concrete direction. No rewrites.
>
> Output format — categorized findings plus an evidence sources footer:
> - `## must-fix` — concrete harness/application gaps that will produce repeated agent mistakes or block verification
> - `## consider` — non-blocking agent-productivity suggestions
> - `## notes` — brief acknowledgments + any out-of-scope routing
> - `## Evidence sources` — one line for git history (what was searched, what surfaced) and one line for transcripts (paths searched, or "not present, git-history-only")
>
> If the diff has no agent-seam concerns, one or two sentences is the entire report.

#### context-reviewer (`subagent_type: context-reviewer`, only if classified in step 3)

Inline body:

> **Scope**: branch-vs-base.
> **Base**: `<base>`.
> **Repository path**: the current working directory.
>
> Read the diff yourself:
>
> ```
> git diff <base>...HEAD --stat
> git diff <base>...HEAD
> ```
>
> Load workspace `CLAUDE.md` and nested `CLAUDE.md` files, any harness conventions for agent-facing markdown the workspace exposes, and any `ai/` docs that govern the touched files.
>
> Check the diff against documented conventions — naming and prefixes (`ws-` vs `wf-`, agent names, skill names), path notation (`workspace:`, `<extension>:`), voice and imperative style, freshness of cross-references (broken links, stale section anchors), and consistency with existing patterns in the same family. Be specific: file, line, convention violated, suggested direction. No rewrites.
>
> Output format — same categorized shape used by code-reviewer and harness-reviewer:
> - `## must-fix`
> - `## consider`
> - `## notes`
>
> If the agent-facing markdown is clean, one sentence is the whole report.

### 5. Synthesize findings

Once every spawned reviewer has reported back, produce **one consolidated summary** for the caller. Do **not** paste all three reports verbatim — synthesize.

Output shape:

```
## Pre-push review: <range>

Reviewers: code-reviewer, harness-reviewer[, context-reviewer]
Files: <N> changed, <M> commits

## must-fix
- (code-reviewer) <finding>
- (harness-reviewer) <finding>

## consider
- (code-reviewer) <finding>
- (context-reviewer) <finding>

## clean
- <reviewer that reported clean — one line each>
```

Rules for the summary:

- Cap at roughly 25 lines. If the findings exceed that, list the headlines and offer to relay the full report from a specific reviewer on request.
- Attribute every finding to its reviewer in parentheses — the caller needs to know which axis raised what.
- Sort within each section by reviewer in this order: code-reviewer, harness-reviewer, context-reviewer (matches the spawn order so the caller can scan predictably).
- If a reviewer found nothing, list it under `## Clean` rather than omitting it — absence of a section is ambiguous, presence in `## Clean` is signal.

### 6. Decide

**Advisory mode** (default): ask the caller once via `AskUserQuestion` with three options:

- **Acknowledge findings; caller pushes manually** — `/wf-pre-push` does not invoke push. This option just confirms the caller has read the findings and intends to push regardless. Push remains the caller's responsibility (raw `git push` or `/ws-push`).
- **Address findings first** — stop; return control so the findings can be fixed before re-running.
- **Show full reports** — relay each reviewer's raw report (sectioned by reviewer name), then re-prompt with the same three options.

**Blocking mode**: present the summary and stop. Do not prompt. The caller must invoke `/wf-pre-push` again after addressing findings, or push without it if they want to bypass. Blocking mode exists for callers (or routines) that want a hard gate without an interactive prompt.

In **neither** mode does `/wf-pre-push` invoke `git push`, `/ws-push`, or any other delivery action. The push step is decoupled by design — see "Why no automatic push" below.

## Why one entry point with three reviewers

The three review axes — code structure, application↔harness seam, agent-facing markdown — are complementary. A clean code review can still ship stale agent docs; a clean context review can still ship a broken abstraction. Running all three before push catches the full surface in one round-trip instead of three sequential invocations, and the parallel fan-out keeps wall time bounded by the slowest reviewer rather than the sum.

## Why no team

Like `/wf-cold-review` and `/wf-harness-review`, `/wf-pre-push` is deliberately team-less. Each reviewer is a role-pure one-shot. No shared `TaskList`, no peers, no follow-on. This keeps `/wf-pre-push` composable: a user can invoke it directly, a `/wf-blizzard` snowflake can invoke it as a contained pre-push step without nesting teams, and the reviewers never try to coordinate work they aren't responsible for.

## Why no automatic push

Coupling `/wf-pre-push` to `/ws-push` would invert the dependency direction. `/ws-push` lives in winter core (workspace `.claude/skills/`); `/wf-pre-push` lives in `winter-workflow` (an extension). Workflow can depend on core; core cannot depend on extensions. Keeping the two skills decoupled preserves that arrow — invoke `/wf-pre-push` for review, then `/ws-push` (or raw `git push`) to deliver. Callers who want a one-shot "review then push" flow can chain them themselves.

## Why "cold"

Each spawned reviewer reads only the diff, the code, and the docs — never this session's design discussion. A reviewer that sat in on the design absorbs the author's framing; a cold reviewer reads what's actually on disk. That gap is where the most valuable findings live, and `/wf-pre-push` preserves it for all three axes simultaneously.
