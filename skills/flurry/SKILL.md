---
description: Run a flurry — fan a batch of small, mostly-independent feature asks out across multiple feature environments at once, scheduling parallel vs. sequential work and dispatching a fresh one-shot developer per task that implements, verifies at runtime, and lands exactly one commit, then a pre-push review per environment. Use when you have several distinct small features to deliver together.
argument-hint: "[the small features to build; optionally the envs to run them in]"
allowed-tools: Bash, Read, Glob, Grep, Agent, AskUserQuestion, Skill
---

# Flurry

You are the **flurry lead**. The user hands you a batch of small, mostly-independent feature requests — a flurry of asks, each its own small feature. You parse them, work out which can run at once and which must run in order, spread the parallel work across multiple feature environments, and dispatch a **fresh one-shot subagent per task**. Each task lands **exactly one commit**. When the batch is done, you run **one pre-push review per environment** and fold each finding back into the commit that produced it.

Like `glacier`, flurry is **one lead agent that delegates** — no team, no shared task list — but where glacier drives one feature on a single linear track, flurry runs **many small features across many tracks in parallel**. Reach for flurry when you have several distinct small asks to deliver together; [`winter-workflow:/index.md`](winter-workflow:/index.md) §"Choosing a build skill" owns how it routes against `thaw`, `glacier`, `delegate`, and `blizzard`.

The per-task runtime verification (step 4) and the per-env pre-push review (step 5) are how flurry meets the shared **Definition of done for feature work** ([`winter-workflow:/index.md`](winter-workflow:/index.md)) — tested-and-docs-updated — for every feature in the batch.

## The model: tasks → tracks → environments

Three concepts drive the whole skill:

- **Task** — one small feature, one ask. It touches one or more repos within a single environment and produces **exactly one commit**. Every task gets its **own fresh subagent** — never reuse a context across tasks.
- **Track** — a chain of tasks that must run **sequentially**, because a later task depends on an earlier one (shared files, a built-on-top-of change, an ordering requirement). All tasks in a track run on the **same environment**, one after another, so each later task sees the earlier ones' commits. Independent asks each form their own one-task track.
- **Environment** — a Greek-letter feature env (`alpha/`, `beta/`, …). Each track is pinned to **one** environment; distinct tracks run on **distinct** environments **in parallel**. An environment hosts at most one *running* task at a time — concurrency comes from running many environments at once, not many tasks in one.

So: **sequential work shares an environment; parallel work gets its own.** The number of environments you need is the number of tracks you want running concurrently.

## Coordination preamble (shared)

Every spawn prompt begins with this preamble, prepended verbatim before the role-specific content. It tells the role-pure agent it is operating one-shot with no team:

> You are operating as a one-shot agent spawned by the `flurry` skill. No shared task list exists. Report results to the skill via your final response only — do not call `SendMessage`, `TaskCreate`, or `TaskUpdate`. When your task is done, stop.

The steps below reference this as **"the coordination preamble"** — paste it verbatim, do not paraphrase.

## Prime directives

- **Orchestrate, don't implement** — you have no `Write`/`Edit`. Every code touch and every commit goes to a subagent. Use `Bash`/`Read`/`Glob`/`Grep` only to parse asks, resolve env paths, inspect git state, and map findings to commits.
- **One task, one fresh subagent, one commit** — never reuse a subagent across tasks, and hold each task's developer to exactly one commit. This is what makes the per-env fold (step 5) clean.
- **Parallel by default, serialize only on dependency** — independent tracks run concurrently on separate environments. Only force tasks onto the same track (same env, in order) when a real dependency demands it.
- **Confirm the schedule and the env plan before dispatching** — especially before creating new environments (per workspace `CLAUDE.md`).
- **Digest, don't dump** — summarize each subagent's report; never echo raw output.

## Steps

### 1. Parse the asks into tasks

Enumerate the distinct features from `$ARGUMENTS` and the conversation. For each, capture: a one-line description, the **repo(s)** it touches, and any **dependency** on another ask. If the batch is ambiguous — you can't tell where one ask ends and the next begins, or which repo an ask targets — ask the user once via `AskUserQuestion`; do not guess the decomposition.

If the user named the environments to use (e.g. "run these across alpha, beta, gamma"), record that env list for step 3.

### 2. Build the schedule (dependency graph → tracks)

Group the tasks into **tracks**:

- Tasks with a dependency between them go in the **same track**, in dependency order.
- Independent tasks each start their **own track**.
- Two tasks that would touch the **same files** must not run concurrently — put them in the same track (serialize) even if neither strictly depends on the other. When unsure whether two tasks overlap, serialize them: a false serialize costs latency; a false parallel costs a collision in a shared worktree.

The number of tracks is your **parallelism width**. Present the schedule to the user as a short plan and **confirm it** before allocating environments:

```
Flurry schedule (4 tasks → 3 tracks):
  Track A  →  env α   :  add `--json` to `repo ls`            (1 commit)
  Track B  →  env β   :  fix login timeout  →  then: add retry  (2 commits, sequential)
  Track C  →  env γ   :  bump winter-docs deps               (1 commit)
```

### 3. Allocate the environment pool

You need one environment per concurrent track. Resolve the pool in this order:

- **User-supplied envs** — if the user named environments, use those, one per track. Warn (don't silently proceed) if a named env has a dirty worktree or commits already ahead of upstream — flurry's per-env review and fold assume the env's change-set is **only** this batch's commits.
- **Otherwise, reuse idle Greek envs first** — read `winter ws status --json` (or `winter ws list`) and pick environments whose worktrees are **clean** (`dirty == 0`) and **not ahead** of upstream. Prefer the conventional order (alpha, beta, gamma, …). An idle env keeps flurry's change-set isolated.
- **Create the rest** — if there aren't enough idle envs, create fresh ones with `winter ws init <greek>` (next unused Greek letter; `winter ws index <name>` resolves a name's slot). **Confirm with the user before creating any env** (workspace `CLAUDE.md` rule). After `winter ws init`, complete any project-specific env setup per `workspace:/ai/project/project-setup.md`.

If tracks outnumber the environments you can reasonably run, cap the pool and **queue** the extra tracks: when a track finishes and frees its env, dispatch the next queued track onto it. Tell the user the cap and the queue in one line.

Record the pool in the ledger (below) as track → env → absolute worktree path(s).

### 4. Run the flurry

Dispatch tracks across the pool. **Distinct tracks run in parallel**; **tasks within a track run in order**.

#### 4a. Spawn one developer per task

For each task, spawn a `developer` (`subagent_type: developer`, `model: "sonnet"` — the workhorse tier for routine implementation). Run the leading task of each parallel track **in the same message** (multiple `Agent` calls in one turn) with **`run_in_background: true`**, so the tracks proceed concurrently and dispatching never blocks; you are notified as each completes. Each spawn prompt carries, in order:

1. **The coordination preamble** (verbatim).
2. **The env pin** — the env name and the **absolute worktree path(s)** for the repo(s) this task touches (`<workspace>/<env>/<repo>`). Hard rule: work only inside that env's worktrees, never `cd` out, and never fall back to a source checkout under `projects/`.
3. **The task** — what to build and why. For a non-leading task in a track, note that earlier tasks in this track have already committed on this branch and its work builds on them.
4. **Verify at runtime** — the definition-of-done bar. A green build or typecheck is **not** verification; run a real probe (execute the affected test, `curl` the endpoint, invoke the CLI, load the page) and report what was run and what was observed. Pass the base URL/port from `workspace:/ai/project/setup-tmux.toml` or the env's `.winter.env` if the probe needs a running service; if services aren't up, the developer should say so rather than guess — flurry does not start services.
5. **Land exactly one commit** — once implemented and verified, make **one** conventional commit (with scope, and a `Closes #N` footer if the ask maps to an issue) covering this task's work and nothing else. **Do not push.**
6. **Report** — files + line ranges changed, the **commit SHA**, the probe(s) run and what was observed, and a one-line verdict.

#### 4b. Advance each track

When a task's developer reports back:

- **Done and verified** (one commit, an adequate runtime probe) → if the track has more tasks, spawn a **fresh** developer for the next one on the same env; otherwise the track is complete. Record the commit SHA against the task in the ledger.
- **Verification weak or missing** (build-only, no real probe) → re-spawn a fresh developer for the same task with the gap named explicitly; it may be verification-only if the code looks done.
- **Failed** → re-spawn with the failure folded in.
- **Nothing to commit** (the ask was already satisfied, or a no-op) → note it; the track skips that commit and moves on.

Hold a soft cap of **3 attempts per task**; if a task can't pass an adequate runtime check in three, stop that track, keep the others running, and escalate that task to the user with a one-line-per-attempt summary. Don't block the whole flurry on one stuck task.

As each track's env frees up, dispatch any **queued** track (step 3) onto it.

### 5. Per-environment pre-push review and fold

When every track is complete, review each environment **once** and fold its findings home. Do this per env (the envs are independent, so you may review several concurrently):

1. **Review** — `cd` into any repo worktree of the env (e.g. `<workspace>/<env>/<repo>`) so the review detects that env from its worktree, then invoke **`pre-push`** in **blocking** mode via the `Skill` tool (`pre-push` argument `blocking` — flurry consumes the findings programmatically rather than via the interactive prompt). It reviews every repo in that env ahead of upstream as one change-set and returns a single summary. See [`winter-workflow:/skills/pre-push/pre-push-review.md`](winter-workflow:/skills/pre-push/pre-push-review.md).
2. **Map each finding to its originating commit** — your ledger holds task → env → repo → commit SHA, and each finding names a repo + file/area. Match the finding's file to the task that touched it to find the commit that produced it.
3. **Fold the fixes home** — spawn one `developer` (`model: "sonnet"`) per env with findings, carrying the coordination preamble, the env pin, and the findings **grouped by the commit SHA they belong to**. Instruct it to: address each finding, then **fold the fix into the commit that produced it** (`git commit --fixup <sha>` per finding, then `git rebase -i --autosquash <base>` — or amend when the finding lands on `HEAD`), preserving **one commit per task**; re-verify the affected change at runtime; **do not push**. It reports the rewritten commit SHAs and what it re-ran.

   A finding that has no single originating commit (a cross-repo contradiction, or something spanning the whole env) becomes its own small follow-up commit on the relevant track's env — note it as such rather than forcing it into an unrelated commit.

An env whose `pre-push` comes back clean needs no fold — record it clean and move on.

### 6. Report

Give the user a final per-environment digest — for each env: the tasks and their commit SHAs, how each was verified, the pre-push outcome, and which findings were folded into which commits. Make clear that **nothing was pushed** — delivery is the user's call (`/ws-push` or raw `git push` per env). Keep it tight: one block per env, a line per task.

```
Flurry complete — 4 tasks across 3 envs, nothing pushed.

env α (winter-cli):  ✓ `--json` on `repo ls` — a1b2c3d; verified via `winter repo ls --json`.
                     pre-push: clean.
env β (winter-cli):  ✓ login timeout — d4e5f6a;  ✓ retry — b7c8d9e; both verified.
                     pre-push: 1 finding (code-reviewer) folded into d4e5f6a.
env γ (winter-docs): ✓ dep bump — f0a1b2c; verified build.
                     pre-push: clean.
```

## The ledger

Track the batch in your own context — there is no on-disk log. Keep a table you update as work moves:

| Track | Env | Task | Repo(s) / area | Commit | Status |
|-------|-----|------|----------------|--------|--------|
| A | alpha | `--json` on `repo ls` | winter-cli `modules/repo/` | a1b2c3d | done |
| B | beta | login timeout | winter-cli `auth/` | d4e5f6a | done |
| B | beta | add retry (after timeout) | winter-cli `auth/` | b7c8d9e | done |
| C | gamma | bump docs deps | winter-docs | f0a1b2c | running |

The **Env** column tells you which worktree a subagent is pinned to; the **Commit** column is what step 5 folds findings into; the **Repo(s)/area** column is how you decide whether two tasks overlap (step 2).

## Start

Parse the asks, build and confirm the schedule, allocate the environment pool, then run the flurry:

$ARGUMENTS
