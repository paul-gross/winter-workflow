# Pre-push review

Run an LLM-guided review over the un-pushed change-set before pushing completed work. The change-set is every repo in the feature env with commits ahead of its upstream — `pre-push` reviews them **together**, not one repo at a time. It fans out up to four one-shot reviewers in parallel — `code-reviewer`, `harness-reviewer`, `context-reviewer`, and `documentation-reviewer`, **one per axis, each spanning every in-scope repo** — then synthesizes the findings into a single summary for the caller, including a cross-repo consistency pass. Which reviewers spawn depends on what surfaces the in-scope repos actually have: an env with no agentic harness anywhere gets no `harness-reviewer`, none with public docs gets no `documentation-reviewer`, and so on (see step 3).

`pre-push` mirrors `cold-review` and `harness-review` in shape (cold, one-shot, no team) but differs in three ways:

- **Scope is the un-pushed change-set across the env** — every repo with commits ahead of upstream, each reviewed over its own `<base>...HEAD` (where `<base>` is `origin/master` or its equivalent). The point is to gate the push, so the set is whatever `winter ws push` would actually deliver — not branch-vs-base of an arbitrary diverged history, and never uncommitted work (you don't push uncommitted work). Run from a standalone repo, or in an env where only one repo is ahead, it gates that single repo exactly as before.
- **Multiple reviewers in parallel**, fanned out from one entry point. `cold-review` and `harness-review` are single-axis; `pre-push` covers the full review surface in one round-trip — but only the axes the in-scope repos have.
- **A cross-repo consistency pass** in synthesis (step 5). Because each axis reviewer holds the whole change-set, `pre-push` surfaces a change in one repo that contradicts another — a removed command still referenced in a sibling's docs — as a single finding instead of letting it fall between two repo-scoped runs that never meet.

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

### 2. Discover the un-pushed change-set

Follow `winter-workflow:/ai/changeset-scope.md` in **unpushed** mode to detect the feature env and list the in-scope repos — every worktree `winter ws push` would push (non-pinned: `tracking_ahead > 0` or `ahead > 0`; pinned: `tracking_ahead > 0`), read from `winter ws status <env> --json` rather than re-derived with hand-rolled `git rev-list`. For each in-scope repo, resolve its base ref (`origin/<main>` via the ladder in the shared doc, run inside that worktree). The result is a set of `(repo, worktree-path, base-ref)` entries; each reviewer reviews each repo over `<base>...HEAD`.

- **Zero repos in scope** (nothing ahead of upstream) → report "nothing to review; nothing is ahead of upstream" and stop. Do not spawn reviewers.
- **Not in a feature env, or exactly one repo in scope** → single-repo mode: gate that one repo over its `<base>...HEAD`, no cross-repo pass.
- **Two or more repos in scope** → review them together; each axis reviewer spans all of them, and step 5 adds the cross-repo consistency pass.

### 3. Classify the change-set and its repos

A reviewer is only worth spawning when **some in-scope repo** actually contains the surface it reviews. Spawning a `documentation-reviewer` when no in-scope repo has public docs, or a `harness-reviewer` when none has an agentic harness, burns wall time to produce "nothing in my lane." So this step has two parts: **what the in-scope repos have** (probe each) and **what the change-set touches** (the union of the per-repo diffs).

First, see what the change-set touches — union the name-only diffs across the in-scope repos (run in each worktree):

```bash
git diff --name-only <base>...HEAD
```

Then decide each reviewer against the union — spawn it if **any** in-scope repo satisfies its trigger:

- **`code-reviewer` — spawn whenever the change-set changes code** in any repo. Any code change wants a structural read. (A docs-only change-set can skip it.)
- **`harness-reviewer` — spawn if any in-scope repo has an agentic-harness surface.** Evidence: agent definitions (`agents/*.md`, `.claude/agents/`), skills, verifier/test scaffolds, harness conventions, any `CLAUDE.md`, an `ai/` tree. If no in-scope repo has any of these, there is no application↔harness seam to review — skip it.
- **`context-reviewer` — spawn if any in-scope repo has agent-facing markdown AND the change-set touches it.** Apply the canonical classifier at `winter-workflow:/ai/agent-facing-paths.md` (it also defines the product/backlog exclusion). If no in-scope repo has agent-facing markdown, skip.
- **`documentation-reviewer` — spawn if any in-scope repo has external-facing public documentation AND the change-set touches code or docs that documentation covers.** Public documentation is what a human adopter/end-user reads: a `docs/` content tree with a site-generator config (`astro.config.*` + Starlight, `docusaurus.config.*`, `mkdocs.yml`, `book.toml`, VitePress), a separate docs-site repo, user/adopter guides, or the user-facing portion of a public `README.md`. It is **not** the agent-facing `ai/` tree or `CLAUDE.md` — those belong to `context-reviewer`. If no in-scope repo ships public documentation, skip the reviewer.

Probe each in-scope repo's surfaces with cheap checks before deciding — e.g. `ls docs/ ai/ agents/ .claude/ 2>/dev/null` in each worktree, look for a docs-generator config, check for `CLAUDE.md`. When in doubt about whether a surface exists, a quick `git ls-files` glob settles it. A surface in **any** in-scope repo qualifies its reviewer — a docs-only repo paired with a code-only repo in the same change-set spawns both `documentation-reviewer` and `code-reviewer`.

Record which reviewers will be spawned and why the others were skipped. Tell the caller in one short line (e.g., "Spawning code-reviewer + context-reviewer over 9 files across `alpha/winter` + `alpha/winter-docs`; no public-docs surface in scope…") before issuing the spawns.

### 4. Spawn the reviewers in parallel

**Critical**: spawn all selected reviewers in a **single message** — multiple `Agent` tool calls in the same assistant turn. They are independent and benefit from concurrent execution. Sequential spawns waste wall time and give the caller a worse experience.

Each reviewer's prompt is built from the **shared review engine**, `winter-workflow:/ai/review.md` — the same scaffold the single-axis review skills use, so `pre-push` and `cold-review` never drift. For every selected reviewer, follow the engine's **Spawn-prompt scaffold** and append its **per-axis body**, with these `pre-push`-specific bindings:

- **Scope** = `unpushed` (the engine scope of that name). The in-scope target set is the `(repo, worktree-path, base-ref)` entries from step 2; each reviewer reads each repo over `<base>...HEAD` and, for ≥2 repos, applies the engine's cross-repo rule.
- **Execution / model** = the engine default — a cold subagent, with the model passed explicitly per the engine's Model section. All spawns are foreground — you need the findings to synthesize them.
- **Reviewers** = those selected in step 3:
  - `subagent_type: code-reviewer` — axis `code`
  - `subagent_type: harness-reviewer` — axis `harness`
  - `subagent_type: context-reviewer` — axis `context` (only if classified in step 3)
  - `subagent_type: documentation-reviewer` — axis `documentation` (only if classified in step 3)

The engine carries the canonical one-shot/no-team preamble, the diff commands, the cross-repo rule, the per-axis bodies (including the harness axis's transcript-mining context and `## Evidence sources` footer), and the `## must-fix` / `## consider` / `## notes` output shape. Do not restate them here — if the scaffold evolves, it evolves once in the engine.

### 5. Synthesize findings

Once every spawned reviewer has reported back, produce **one consolidated summary** for the caller. Do **not** paste the reviewer reports verbatim — synthesize.

**Cross-repo consistency pass** (change-sets spanning two or more repos only). Before writing the summary, scan the reviewers' findings and the change-set for contradictions *between* repos — a command, flag, convention, or symbol changed in one repo and left stale in another's docs, mirror, or caller. Each axis reviewer holds the whole change-set and should already flag these within its lane; this pass consolidates them and catches any that span axes (e.g. `code-reviewer` saw the removal, `documentation-reviewer` saw the stale mention). Promote each confirmed cross-repo contradiction to a single `## cross-repo` finding that names both repos. Single-repo change-sets skip this pass entirely.

Output shape:

```
## Pre-push review: env `<env>` — <repo>@<commits>[, <repo>@<commits>]   (single repo: <base>...HEAD)

Reviewers: code-reviewer[, harness-reviewer][, context-reviewer][, documentation-reviewer]
Files: <N> changed across <R> repos, <M> commits

## cross-repo
- (code-reviewer + documentation-reviewer) <contradiction naming both repos>

## must-fix
- (code-reviewer) <repo>: <finding>
- (harness-reviewer) <repo>: <finding>

## consider
- (code-reviewer) <repo>: <finding>
- (context-reviewer) <repo>: <finding>

## clean
- <reviewer that reported clean — one line each>
```

Rules for the summary:

- Cap at roughly 25 lines. If the findings exceed that, list the headlines and offer to relay the full report from a specific reviewer on request.
- Attribute every finding to its reviewer in parentheses — the caller needs to know which axis raised what. When the change-set spans multiple repos, prefix each finding with its repo so the caller can locate it.
- Lead with `## cross-repo` when present — a contradiction between repos is the failure mode this skill exists to catch, so it goes first. Omit the section for single-repo change-sets and when none is found.
- Sort within each section by reviewer in this order: code-reviewer, harness-reviewer, context-reviewer, documentation-reviewer (matches the spawn order so the caller can scan predictably). Skip the ones that weren't spawned.
- If a reviewer found nothing, list it under `## clean` rather than omitting it — absence of a section is ambiguous, presence in `## clean` is signal. List reviewers that were **not spawned** (no matching surface in any in-scope repo) on one line under the `Reviewers:` header, not in `## clean` — "not run" and "ran clean" are different signals.

### 6. Decide

**Advisory mode** (default): ask the caller once via `AskUserQuestion` with three options:

- **Acknowledge findings; caller pushes manually** — `pre-push` does not invoke push. This option just confirms the caller has read the findings and intends to push regardless. Push remains the caller's responsibility (raw `git push` or `/ws-push`).
- **Address findings first** — stop; return control so the findings can be fixed before re-running.
- **Show full reports** — relay each reviewer's raw report (sectioned by reviewer name), then re-prompt with the same three options.

**Blocking mode**: present the summary and stop. Do not prompt. The caller must invoke `pre-push` again after addressing findings, or push without it if they want to bypass. Blocking mode exists for callers (or routines) that want a hard gate without an interactive prompt.

In **neither** mode does `pre-push` invoke `git push`, `/ws-push`, or any other delivery action. The push step is decoupled by design — see "Why no automatic push" below.

## Why one entry point, several reviewers

The review axes — code structure, application↔harness seam, agent-facing markdown, external-facing public documentation — are complementary. A clean code review can still ship stale agent docs; a clean context review can still ship a broken abstraction; a clean code-and-context review can still ship a public doc that now lies to adopters. Running the applicable axes before push catches the full surface in one round-trip instead of several sequential invocations, and the parallel fan-out keeps wall time bounded by the slowest reviewer rather than the sum.

The same logic extends across repos. A logical change in this workspace often spans several repos in one env — a command in one, its docs in another. Reviewing each repo in isolation lets a contradiction between them (removed in repo A, still referenced in repo B) fall between two runs that never meet. Spanning every axis reviewer across the whole change-set, plus the cross-repo consistency pass in step 5, closes that gap: one reviewer per axis holds the entire change at once.

The fan-out is conditional, not fixed: each reviewer is spawned only when some in-scope repo carries the surface it reviews (step 3). An env of libraries with no docs site and no agentic harness gets a code review and nothing else — the skill does not manufacture lanes the change-set doesn't have.

## Why no team

Like `cold-review` and `harness-review`, `pre-push` is deliberately team-less. Each reviewer is a role-pure one-shot. No shared `TaskList`, no peers, no follow-on. This keeps `pre-push` composable: a user can invoke it directly, a `blizzard` snowflake can invoke it as a contained pre-push step without nesting teams, and the reviewers never try to coordinate work they aren't responsible for.

## Why no automatic push

Coupling `pre-push` to `/ws-push` would invert the dependency direction. `/ws-push` lives in winter core (workspace `.claude/skills/`); `pre-push` lives in `winter-workflow` (an extension). Workflow can depend on core; core cannot depend on extensions. Keeping the two skills decoupled preserves that arrow — invoke `pre-push` for review, then `/ws-push` (or raw `git push`) to deliver. Callers who want a one-shot "review then push" flow can chain them themselves.

## Why "cold"

Each spawned reviewer reads only the diff, the code, and the docs — never this session's design discussion. A reviewer that sat in on the design absorbs the author's framing; a cold reviewer reads what's actually on disk. That gap is where the most valuable findings live, and `pre-push` preserves it across every axis it runs.
