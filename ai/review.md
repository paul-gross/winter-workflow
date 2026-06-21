# Review engine — one cold review, every axis and scope

This is the single source for **how a change-set review runs** in this workspace: the axes, the scope vocabulary, how the change-set is discovered, whether the review runs inline or as a subagent, which model it uses, and the exact prompt scaffold every reviewer receives. The review skills are thin pointers at this doc; `pre-push` composes it across axes. Nothing here is duplicated in the skills — read this, parameterized by **axis** and **scope**, and run the review.

The unit of review is the **change-set**, which may span several repos in one feature env. A reviewer holds the whole set at once so a change in one repo that contradicts something left stale in another is caught by the reviewer that sees both. Run from a standalone repo, or in an env where only one repo changed, the change-set is that single repo.

## Reordering attention before a review — the manifest

This engine produces *findings*; it does not shrink the surface a human must read. A [**review manifest**](./review-manifest/index.md) does — it partitions every hunk of the same change-set into verification tiers (`mechanical` / `pattern` / `novel`) and renders a review order that a **human reviewer** reads so full attention lands on the `novel` hunks. It is an **optional preprocessing step**, not a review axis, and its reader is a human first: run [`review-manifest`](../skills/review-manifest/SKILL.md) on a large or mechanical-heavy diff to get a review order — read it to focus your own review, and optionally generate it before a cold review to pre-order that too. On a small diff that fits in a glance, skip it. Advisory; gates nothing.

## Invoking this doc

Three entry points resolve here. They differ only in which axis (and, for `pre-push`, which axes) they run — the mechanics below are identical:

- **A review skill** — `cold-review` (code), `context-review` (context), `harness-review` (harness), `documentation-review` (documentation). Each binds one axis and passes `$ARGUMENTS` through as the scope. Cold subagent by default; runs inline when `$ARGUMENTS` leads with the `inline` selector.
- **The harness directly, no skill** — point any agent at this doc with an axis and a scope for an ad-hoc review (e.g. "review the **code** axis of `HEAD~1` per `winter-workflow:/ai/review.md`"), inline or as a subagent (see *Execution mode*).
- **`pre-push`** — composes several axes in parallel over the un-pushed change-set; see [`../skills/pre-push/pre-push-review.md`](../skills/pre-push/pre-push-review.md), which references this doc for the scaffold and per-axis bodies rather than restating them.

## Axes

Each axis is a concern with a dedicated role-pure reviewer agent. The **agent definition is the deep source** for what that axis looks for — this doc never restates it; the per-axis bodies below only add the caller-supplied context the agent can't gather on its own.

| Axis | Reviewer agent | Concern |
|------|----------------|---------|
| `code` | [`code-reviewer`](../agents/code-reviewer.md) | architectural quality, design-principle adherence |
| `context` | [`context-reviewer`](../agents/context-reviewer.md) | agent-facing markdown vs documented conventions |
| `harness` | [`harness-reviewer`](../agents/harness-reviewer.md) | the application↔harness seam |
| `documentation` | [`documentation-reviewer`](../agents/documentation-reviewer.md) | external-facing public documentation |

## Scope vocabulary

A caller selects scope from `$ARGUMENTS` (or states it directly). The default is branch-vs-base. The two **implicit** scopes ("whatever changed") fan out across the feature env; the two **explicit** scopes (a range, a path set) the caller names, and they operate on the current repo only.

`$ARGUMENTS` may also lead with the **execution selector** `inline` (see *Execution mode*) — e.g. `inline main` runs the review in-context over `main...HEAD`. Strip a leading `inline` token first; everything after it is the scope.

| Scope | Selector | Discovery | What the reviewer reads |
|-------|----------|-----------|-------------------------|
| **branch-vs-base** (default) | _(none)_ | env-wide — `./changeset-scope.md`, repos with `ahead > 0` | per repo: `git diff <base>...HEAD` |
| **uncommitted** | `uncommitted` | env-wide — `./changeset-scope.md`, repos with `dirty > 0` | per repo: `git diff HEAD` |
| **range** | a git ref or range (`main`, `HEAD~3`, `a..b`, `v1..HEAD`) | current repo only | a range with `..`/`...` → use as-is; a single ref → `<ref>...HEAD` (everything since that ref — so `main` → `main...HEAD`, `HEAD~3` → the last 3 commits) |
| **paths** | one or more existing files/dirs (incl. `<env>:<repo>` / `<extension>:` notation) | current repo only | the **current state** of the named files — no diff |
| **unpushed** | _(`pre-push` only)_ | env-wide — `./changeset-scope.md`, unpushed predicate | per repo: `git diff <base>...HEAD` |

Resolve `$ARGUMENTS` in this order: strip a leading `inline` selector if present (record it for *Execution mode*); then of what remains — empty → branch-vs-base; `uncommitted` → uncommitted; resolves to an existing path → paths; otherwise a git ref/range that `git rev-parse` verifies → range; anything else → tell the caller the valid forms and stop. A filler word between the selector and the ref (`inline against main`, `vs main`) is noise — read past it to the ref.

**paths** generalizes what `context-review` used to call "audit": any axis can review a path set in its current state. The reviewer filters the set to the files its axis owns (e.g. `context` keeps agent-facing markdown per `./agent-facing-paths.md`; `documentation` keeps public docs) and reviews their current state with no diff.

### Discovering the change-set

For the **env-wide** scopes (branch-vs-base, uncommitted, unpushed), follow [`./changeset-scope.md`](./changeset-scope.md) — it detects the feature env, lists the in-scope repos via `winter ws status <env> --json`, resolves each repo's base ref, and collapses to single-repo when the set has 0 or 1 repo. The result is a set of `(repo, worktree-path, base-ref)` entries.

- **Zero repos in scope** → report "no changes to review" and stop; spawn nothing.
- **One repo (or not in a feature env)** → single-repo mode; review that one repo, no cross-repo framing.
- **Two or more repos** → the change-set spans the env; hand the union to **one** reviewer — never one reviewer per repo.

The **explicit** scopes (range, paths) skip discovery: the change-set is the named range or path set in the current repo.

## Execution mode

- **Subagent (default, cold).** Spawn the axis's reviewer agent with the self-contained prompt below. The reviewer has **zero prior conversation context** — fresh eyes that never saw the design discussion, the prior attempts, or the author's justifications. This is the point of a review; it is where the most valuable findings live. This is the default for every entry point, and the **only** mode `pre-push` uses (a push gate must be cold).
- **Inline (opt-in, warm).** The invoking agent performs the review itself, in the current context, following the same scaffold and per-axis body plus the agent definition's checklists. **Inline forfeits coldness** — the reviewer has seen this session's history and absorbs its framing, which is exactly the bias a cold review exists to avoid. Use it for a quick read on a small change where being already in context is acceptable: the harness micro/ad-hoc path, or a review skill invoked with the leading `inline` selector (e.g. `cold-review inline main`). When in doubt, spawn a subagent.

The scaffold below is written as the subagent prompt. Inline runs it as self-instructions — same steps, no spawn.

## Model

Reviews run on **`opus`** by default — review is judgment-heavy and quality-first. Pass it **explicitly** so the choice is deliberate, not inherited from the agent's frontmatter: `Agent(subagent_type: <reviewer>, model: "opus", …)`. Override to a cheaper tier only for a deliberately trivial scope (a tiny range, a one-file paths review); state the downgrade when you do.

## Spawn-prompt scaffold

Build the reviewer prompt from these axis-independent parts, then append the **per-axis body** for the selected axis. Keep it self-contained — the reviewer reads only what the prompt carries.

1. **Preamble (one-shot, no team).** Open with, verbatim:

   > This is a one-shot standalone review. Read the inputs, report categorized findings, and stop. There is no team coordinating you — do not call `SendMessage`, `TaskCreate`, or `TaskUpdate`, and do not attempt follow-on work. When your report is done, stop.

2. **Scope.** Name the scope (branch-vs-base / uncommitted / range / paths / unpushed) and list the in-scope target(s): for diff scopes, each repo's absolute worktree path and base ref (single-repo lists one); for paths, the absolute path set. For multi-repo diff scopes, add: "Review these as one change-set."

3. **What to read.** Give the reviewer the commands to gather its own inputs, run in **each** in-scope worktree (`cd` to its path first):
   - branch-vs-base / unpushed: `git diff <base>...HEAD --stat`, then `git diff <base>...HEAD`.
   - uncommitted: `git diff HEAD --stat`, then `git diff HEAD`; **also** read the untracked, non-ignored files (`git ls-files --others --exclude-standard`) — they are uncommitted work `git diff HEAD` omits. See [`./changeset-scope.md`](./changeset-scope.md) §uncommitted.
   - range: `git diff <range> --stat`, then `git diff <range>` (with `<range>` resolved per the scope table).
   - paths: enumerate and read the current state of the named files (no diff).

4. **Cross-repo rule** (multi-repo diff scopes only). "Because you hold every in-scope repo at once, flag any **cross-repo contradiction** within your axis — a change in one repo that leaves a broken caller, dead reference, contradicting assumption, or stale mirror in another — as a single finding."

5. **Review instructions.** "Load the documentation relevant to your axis and review against it; fall back to your own judgment where it is silent. Be specific: file, line, the principle/convention at issue, and a concrete direction. No rewrites." Then append the per-axis body.

6. **Output format.** See [§Output format](#output-format) below.

### Output format

Categorized findings:
   - `## must-fix` — issues that should block.
   - `## consider` — non-blocking suggestions.
   - `## notes` — brief acknowledgments of what the change gets right + any out-of-scope routing to another axis. Keep short.
   - If the change is clean on this axis, one sentence is the whole report.

   The `harness` axis adds one section — see its body.

## Per-axis bodies

Append exactly one. Each points at the agent definition for the methodology and adds only what the caller must supply.

### code

> Follow your agent body (`code-reviewer`). Read the changed files and surrounding code for context (existing patterns, conventions); eagerly load coding standards, architecture docs, and any in-flight initiatives. No extra caller context is needed.

### context

> Follow your agent body (`context-reviewer`). Load workspace `CLAUDE.md` and nested `CLAUDE.md` files, the harness conventions for agent-facing markdown the workspace exposes, and any `ai/` docs governing the touched files. Check naming/prefixes, path notation, voice, frontmatter, cross-reference freshness, and single-source-of-truth.
> For **paths** scope, enumerate the agent-facing markdown under the path set per [`./agent-facing-paths.md`](./agent-facing-paths.md) (plus any extension `index.md` / `README.md` written for agents; exclude test fixtures and external-facing public docs) and review its current state.

### harness

> Follow your agent body (`harness-reviewer`) — walk both its checklists (harness-change concerns and application-architecture concerns with agentic ramifications) and its *Mining mistake evidence* procedure. Caller-supplied context:
>
> - **Transcript CWDs to enumerate**: the workspace root, **every in-scope worktree path**, and each one's project source checkout. Apply the encoded-cwd transform (`/` → `-`); skip candidates with no directory under `~/.claude/projects/`.
> - **Time window** (git history and transcripts): the diff's age — since the base commit for diff scopes; the last ~30 days for uncommitted.
> - For diff scopes also run `git log --oneline <base>..HEAD` (or `<range>`) — reverts and fixups are signal.
>
> Add a final `## Evidence sources` section to the output: one line for git history (what was searched, what surfaced) and one for transcripts (paths searched, or "not present, git-history-only").

### documentation

> Follow your agent body (`documentation-reviewer`). Review **external-facing public documentation only** — what a human adopter/end-user reads; not `CLAUDE.md`, `.claude/`, `agents/`, `skills/`, or `ai/` (that's `context`), and not code. Locate the project's public docs and discover its documentation conventions rather than assuming them; if a "docs reflect this change" invariant is documented, review against it and cite it by path. Read code only to judge whether a public doc still describes it accurately. No extra caller context is needed.

## Relay

When the review returns (subagent) or completes (inline), present the report **as-is** with a one-line preamble naming the scope reviewed — e.g. "Cold code review of 7 files on `<branch>` vs. `<base>` in `<repo>`", "Cold context review of 6 files across 2 repos in env `alpha`", "Code review of `HEAD~1` in `<repo>`", or "Context audit of 23 agent-facing files under `<path>`". Do not editorialize or argue with findings — the caller decides what to act on. (`pre-push` synthesizes across axes instead; see its doc.)

**If a [review manifest](./review-manifest/index.md) was generated for this change-set, reconcile it after the review settles.** Two things can invalidate it: (1) the diff changed — fixes were applied in response to findings, or the review prompted edits — so the manifest's `diff_sha` no longer matches and it is now **stale**; regenerate it (`review-manifest`) rather than leave a manifest that describes a diff that no longer exists. (2) A finding contradicts a hunk's tier — the review showed a hunk the manifest called `mechanical` or `pattern` actually carried a decision; **promote those hunks to `novel`** (the same direction the adversarial audit promotes), or regenerate. If neither happened — the review applied no edits and left every cheap-tier classification standing — the manifest still holds; leave it. Never silently keep a manifest the review has outdated; the freshness binding exists precisely so a stale one is caught rather than trusted.

## Why cold, why no team

A reviewer that sat in on the design absorbs the author's framing and reads the change as the author meant it. A cold reviewer reads only what is on disk — the diff, the code, the docs, the conventions — and that gap is where the most valuable findings live. So the default is a fresh-context subagent.

Each reviewer is also **role-pure and team-less** (see [`../agents/README.md`](../agents/README.md)): no shared `TaskList`, no peers, no follow-on. This keeps every review composable — a user invokes it directly, a `blizzard` snowflake invokes it as a contained sub-step, `pre-push` fans several out in parallel, and no reviewer ever tries to coordinate work it isn't responsible for.
