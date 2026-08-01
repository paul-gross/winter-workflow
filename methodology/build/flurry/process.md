# Flurry

## Inputs

- **Feature batch** — a defined set of small feature asks, including each ask's target repository and stated dependencies when known.
- **Environment pool** — optional human-caller-supplied feature environments to use.
- **Workspace state** — environment status, worktree paths, upstream state, and project-specific setup context.
- **Human-caller channel** — available for decomposition clarification, schedule confirmation, environment creation approval, and escalations.

## Outputs

- Exactly one verified commit per successfully completed non-no-op task, subject to the preserved soft attempt cap.
- One aggregated batch review phase, with fixes folded into their originating commits where possible.
- The step 6 per-environment digest; nothing is pushed.

The executor is the **flurry lead**. The human caller supplies a batch of small, mostly-independent feature requests — a flurry of asks, each its own small feature. The executor parses them, works out which can run at once and which must run in order, spreads the parallel work across multiple feature environments, and dispatches a **fresh one-shot isolated role per task**. Each successfully completed non-no-op task lands **exactly one commit**. When the batch is done, the executor closes it with **one batch review phase** — one concurrent pre-push process execution per environment, aggregated into a single findings list — and folds each finding back into the commit that produced it. Use the semantic operations in [`../../runtime-ports.md`](../../runtime-ports.md).

Like `glacier`, flurry is **one lead agent that delegates** — no team, no shared task list — but where glacier drives one feature on a single linear track, flurry runs **many small features across many tracks in parallel**. Reach for flurry when you have several distinct small asks to deliver together; [`winter-workflow:/methodology/build/index.md`](winter-workflow:/methodology/build/index.md) owns how it routes against `snowball`, `glacier`, and `iceberg`.

The per-task runtime verification (step 4) and the aggregated per-environment pre-push review phase (step 5) are how flurry meets the shared **Definition of done for feature work** ([`winter-workflow:/methodology/completion.md`](winter-workflow:/methodology/completion.md)) — tested-and-docs-updated — for every successfully completed feature in the batch.

## The model: tasks → tracks → environments

Three concepts drive the whole process:

- **Task** — one small feature, one ask. It touches one or more repos within a single environment and produces **exactly one commit**. Every task gets its **own fresh isolated role** — never reuse a context across tasks.
- **Track** — a chain of tasks that must run **sequentially**, because a later task depends on an earlier one (shared files, a built-on-top-of change, an ordering requirement). All tasks in a track run on the **same environment**, one after another, so each later task sees the earlier ones' commits. Independent asks each form their own one-task track.
- **Environment** — a Greek-letter feature env (`alpha/`, `beta/`, …). Each track is pinned to **one** environment; distinct tracks run on **distinct** environments **in parallel**. An environment hosts at most one *running* task at a time — concurrency comes from running many environments at once, not many tasks in one.

So: **sequential work shares an environment; parallel work gets its own.** The number of environments you need is the number of tracks you want running concurrently.

## Isolated-role restrictions

Every isolated role invocation carries these semantic restrictions before its role-specific task:

- Run as a one-shot isolated role for this Flurry operation, with no resident peers or shared assignment queue.
- Return the requested result once through the isolated-result channel; perform no follow-on coordination.
- Stop when the result is complete.

The steps below refer to these as **the isolated-role restrictions**.

## Prime directives

- **Orchestrate, don't implement** — the lead does not modify project files. Every code touch and every commit goes to an isolated implementation role. The lead may inspect only what it needs to parse asks, resolve environment paths, inspect version-control state, and map findings to commits.
- **One task, one fresh isolated role, one commit** — never reuse an isolated context across tasks, and hold each task's ice-carver to exactly one commit. This is what makes the fold (step 5) clean.
- **Parallel by default, serialize only on dependency** — independent tracks run concurrently on separate environments. Only force tasks onto the same track (same env, in order) when a real dependency demands it.
- **Confirm the schedule and the env plan before dispatching** — especially before creating new environments (per workspace `CLAUDE.md`).
- **Provision before implementation or runtime exercise** — every allocated environment must pass the idempotent readiness operation before any task is dispatched. A failed environment stops its track.
- **Digest, don't dump** — summarize each isolated role's report; never echo raw output.

## Steps

### 1. Parse the asks into tasks

Enumerate the distinct features from the supplied feature batch. For each, capture: a one-line description, the **repo(s)** it touches, and any **dependency** on another ask. If the batch is ambiguous — you can't tell where one ask ends and the next begins, or which repo an ask targets — ask the human caller once through the human-caller port; do not guess the decomposition.

If an environment pool was supplied (e.g. "run these across alpha, beta, gamma"), record that env list for step 3.

### 2. Build the schedule (dependency graph → tracks)

Group the tasks into **tracks**:

- Tasks with a dependency between them go in the **same track**, in dependency order.
- Independent tasks each start their **own track**.
- Two tasks that would touch the **same files** must not run concurrently — put them in the same track (serialize) even if neither strictly depends on the other. When unsure whether two tasks overlap, serialize them: a false serialize costs latency; a false parallel costs a collision in a shared worktree.

The number of tracks is your **parallelism width**. Present the schedule to the human caller as a short plan and **confirm it** before allocating environments:

```
Flurry schedule (4 tasks → 3 tracks):
  Track A  →  env α   :  add `--json` to `repo ls`            (1 commit)
  Track B  →  env β   :  fix login timeout  →  then: add retry  (2 commits, sequential)
  Track C  →  env γ   :  bump winter-docs deps               (1 commit)
```

### 3. Allocate the environment pool

You need one environment per concurrent track. Resolve the pool in this order:

- **Supplied envs** — if the environment pool names environments, use those, one per track. Warn the human caller (don't silently proceed) if a named env has a dirty worktree or commits already ahead of upstream — flurry's review and fold assume the env's change-set is **only** this batch's commits.
- **Otherwise, reuse idle Greek envs first** — read `winter ws status --json` (or `winter ws list`) and pick environments whose worktrees are **clean** (`dirty == 0`) and **not ahead** of upstream. Prefer the conventional order (alpha, beta, gamma, …). An idle env keeps flurry's change-set isolated.
- **Create the rest** — if there aren't enough idle envs, create fresh ones with `winter ws init <greek>` (next unused Greek letter; `winter ws index <name>` resolves a name's slot). **Confirm with the human caller before creating any env** (workspace `CLAUDE.md` rule). After `winter ws init`, complete any project-specific env setup per `workspace:/context/project/project-setup.md`.

If tracks outnumber the environments you can reasonably run, cap the pool and **queue** the extra tracks: when a track finishes and frees its env, dispatch the next queued track onto it. Tell the human caller the cap and the queue in one line.

Record the pool in the ledger (below) as track → env → absolute worktree path(s).

#### Provision every allocated environment

Before dispatching any implementation role or exercising any runtime in an allocated environment, run the idempotent readiness command for each selected, reused, or newly created environment:

```bash
winter provision <env>
```

Independent environments may provision concurrently. Record the result per environment. If provisioning fails, do not dispatch or runtime-exercise the assigned track in that environment; mark that track stopped, which is terminal for batch closure, and report the provisioning failure to the human caller while unaffected tracks continue. A queued track may reuse an environment that already provisioned successfully unless intervening work invalidated its readiness.

Provisioning does not start services. Retain the task-level service policy in step 4: flurry does not start services, and a probe that requires an unavailable service reports that condition rather than guessing.

### 4. Run the flurry

Dispatch tracks across the pool. **Distinct tracks run in parallel**; **tasks within a track run in order**.

#### 4a. Run one ice-carver per task

For each task, spawn the canonical `ice-carver` role in a one-shot isolated context with **workhorse model intent** (Sonnet/Terra class). Start the leading task of every parallel track as one concurrent group so dispatch does not wait on one track before starting another; consume each isolated result as it becomes available. Each invocation carries, in order:

1. **The isolated-role restrictions**.
2. **The env pin** — the env name and the **absolute worktree path(s)** for the repo(s) this task touches (`<workspace>/<env>/<repo>`). Hard rule: work only inside that env's worktrees, never `cd` out, and never fall back to a source checkout under `projects/`.
3. **The task** — what to build and why. For a non-leading task in a track, note that earlier tasks in this track have already committed on this branch and its work builds on them.
4. **Verify at runtime** — the definition-of-done bar. A green build or typecheck is **not** verification; run a real probe (execute the affected test, `curl` the endpoint, invoke the CLI, load the page) and report what was run and what was observed. Pass the base URL/port from `workspace:/context/project/project-setup.md` or the env's computed vars (`winter env <env>`) if the probe needs a running service; if services aren't up, the ice-carver should say so rather than guess — flurry does not start services.
5. **Land exactly one commit** — once implemented and verified, make **one** conventional commit (with scope, and a `Closes #N` footer if the ask maps to an issue) covering this task's work and nothing else. **Do not push.**
6. **Report** — files + line ranges changed, the **commit SHA**, the probe(s) run and what was observed, and a one-line verdict.

#### 4b. Advance each track

When a task's ice-carver reports back:

- **Done and verified** (one commit, an adequate runtime probe) → if the track has more tasks, spawn a **fresh** ice-carver for the next one on the same env; otherwise the track is complete. Record the commit SHA against the task in the ledger.
- **Verification weak or missing** (build-only, no real probe) → re-spawn a fresh ice-carver for the same task with the gap named explicitly; it may be verification-only if the code looks done.
- **Failed** → re-spawn with the failure folded in.
- **Nothing to commit** (the ask was already satisfied, or a no-op) → note it; the track skips that commit and moves on.

Hold a soft cap of **3 attempts per task**; if a task can't pass an adequate runtime check in three, mark that track failed and stop it. Failed and stopped tracks are terminal for batch closure: keep the others running and escalate that task to the human caller with a one-line-per-attempt summary, but do not require the track to become successful before closing the batch.

As each track's env frees up, dispatch any **queued** track (step 3) onto it.

### 5. Batch review and fold

When **every** track has reached a terminal state — completed, failed, or stopped — close the batch with **one review phase**. This is a single pass over everything the flurry successfully built, not a review ceremony per environment; a failed or stopped track does not prevent closure and does not need to be retried to success.

1. **Review** — for each env holding successful batch commits, including commits produced before its track later failed or stopped, use any repo worktree of that env (e.g. `<workspace>/<env>/<repo>`) as the working directory so the review detects the env, and execute [`winter-workflow:/methodology/delivery/pre-push/process.md`](winter-workflow:/methodology/delivery/pre-push/process.md) in **blocking** mode. Flurry consumes the findings programmatically rather than through the advisory prompt. Each execution reviews every repo in that env ahead of upstream as one change-set; the envs are independent, so run them concurrently. Pool every finding into **one batch-wide list** — the fold and the report treat the batch as a unit.
2. **Map each finding to its originating commit** — your ledger holds task → env → repo → commit SHA, and each finding names a repo + file/area. Match the finding's file to the task that touched it to find the commit that produced it.
3. **Fold the fixes home** — for each env with findings, spawn one isolated `ice-carver` with workhorse model intent, carrying the isolated-role restrictions, the env pin, and the findings **grouped by the commit SHA they belong to**. Run independent env invocations concurrently. Instruct each role to: address every finding, then **fold the fix into the commit that produced it** (`git commit --fixup <sha>` per finding, then `git rebase -i --autosquash <base>` — or amend when the finding lands on `HEAD`), preserving **one commit per task**; re-verify the affected change at runtime; **do not push**. It returns the rewritten commit SHAs and what it re-ran.

   A finding that has no single originating commit (a cross-repo contradiction, or something spanning the whole env) becomes its own small follow-up commit on the relevant track's env — note it as such rather than forcing it into an unrelated commit.

An env with no findings needs no fold; a fully clean batch skips the fold entirely.

### 6. Report

Give the human caller a final per-environment digest — for each env: the tasks and their commit SHAs, how each successful task was verified, the pre-push outcome for successful commits, and which findings were folded into which commits. Include every failed or stopped track with its terminal reason, attempt summary, successful commits (if any), and tasks not completed; do not present it as successful or require it to be repaired before reporting. Make clear that **nothing was pushed** — delivery is the human caller's decision (`winter ws push <env>` or raw `git push` per env). Keep it tight: one block per env, a line per task.

```
Flurry complete — 4 tasks across 3 envs, nothing pushed.

env α (winter-cli):  ✓ `--json` on `repo ls` — a1b2c3d; verified via `winter repo ls --json`.
                     pre-push: clean.
env β (winter-cli):  ✓ login timeout — d4e5f6a;  ✓ retry — b7c8d9e; both verified.
                     pre-push: 1 finding (cold-reviewer) folded into d4e5f6a.
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

The **Env** column tells you which worktree an isolated role is pinned to; the **Commit** column is what step 5 folds findings into; the **Repo(s)/area** column is how you decide whether two tasks overlap (step 2).

## Start

Parse the supplied feature batch, build and confirm the schedule, allocate the environment pool, then run the flurry.
