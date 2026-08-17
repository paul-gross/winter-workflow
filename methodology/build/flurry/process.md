# Flurry — process

The flurry executor is the flurry lead: it parses a human-supplied batch of small, mostly independent feature asks, works out which can run at once and which must run in order, spreads parallel work across multiple feature environments, and dispatches a fresh one-shot isolated role per task. Flurry is one lead agent that delegates — no team and no shared task list; [`../index.md`](../index.md) owns how flurry routes against snowball, glacier, and iceberg.

The lead orchestrates and never implements: it does not modify project files, every code touch and every commit goes to an isolated implementation role, and the lead inspects only what it needs to parse asks, resolve environment paths, inspect version-control state, and map findings to commits. It digests rather than dumps — it summarizes each isolated role's report and never echoes raw output. Flurry parallelizes by default and serializes only on a real dependency.

Flurry meets the shared definition of done for feature work owned by [`../../completion.md`](../../completion.md) — the tested-and-docs-updated bar — through per-task runtime verification and the aggregated per-environment pre-push review phase.

Flurry executes its coordination through the semantic operations in [`../../runtime-ports.md`](../../runtime-ports.md). Every isolated-role invocation carries, before its role-specific task, the one-shot default declared at [`../../runtime-ports.md#spawn-an-isolated-role`](../../runtime-ports.md#spawn-an-isolated-role), scoped to this flurry operation — the steps below call this "the isolated-role restrictions".

## Inputs

- **Feature batch** — a defined set of small feature asks, including each ask's target repository and stated dependencies when known.
- **Environment pool** (optional) — human-caller-supplied feature environments to use.
- **Workspace state** — environment status, worktree paths, upstream state, and project-specific setup context.
- **Human-caller channel** (required) — used for decomposition clarification, schedule confirmation, environment-creation approval, and escalations.

## Outputs

- Exactly one verified commit per successfully completed non-no-op task, subject to the soft attempt cap.
- One aggregated batch review phase, with fixes folded into their originating commits where possible.
- A final per-environment digest — and nothing pushed.

## Tasks, tracks, and the ledger

- A **task** is one small feature or ask: it touches one or more repos within a single environment, produces exactly one commit, and gets its own fresh isolated role — a context is never reused across tasks.
- A **track** is a chain of tasks that must run sequentially because a later task depends on an earlier one (shared files, a built-on-top change, an ordering requirement); all tasks in a track run on the same environment one after another so each later task sees the earlier commits, and each independent ask forms its own one-task track.
- Each track is pinned to exactly one Greek-letter feature environment; distinct tracks run on distinct environments in parallel, and an environment hosts at most one running task at a time — concurrency comes from many environments, never many tasks in one.
- Sequential work shares an environment and parallel work gets its own, so the number of environments needed equals the number of tracks running concurrently.

The lead tracks the batch in its own context — there is no on-disk log — as a ledger table with columns for track, environment, task, repo(s) or area, commit, and status, updated as work moves. The environment column says which worktree an isolated role is pinned to, the commit column is what the fold targets, and the repo/area column is how the lead judges whether two tasks overlap when scheduling.

Execution starts by parsing the supplied feature batch, building and confirming the schedule, allocating the environment pool, and then running the flurry.

## 1. Parse the batch

Enumerate the distinct features, capturing for each a one-line description, the repo(s) it touches, and any dependency on another ask. When the batch is ambiguous — where one ask ends and the next begins, or which repo an ask targets — ask the human caller once through the human-caller port rather than guessing the decomposition.

## 2. Build and confirm the schedule

Group tasks into tracks: dependent tasks share a track in dependency order, and independent tasks each start their own track. Two tasks that would touch the same files must not run concurrently — put them in the same track even when neither strictly depends on the other. When unsure whether two tasks overlap, serialize: a false serialize costs latency, while a false parallel costs a collision in a shared worktree.

The number of tracks is the parallelism width. Present the schedule to the human caller as a short plan — each track mapped to an environment with its ordered tasks and commit count — and confirm it before allocating environments. The lead confirms the schedule and the environment plan before dispatching, and especially before creating any new environment, which workspace rules require confirming.

## 3. Allocate environments

Environment allocation needs one environment per concurrent track, resolved in order: supplied pool first, then reused idle environments, then newly created ones.

- **Supplied pool** — when a pool was supplied, record that environment list for allocation and use its environments one per track. Warn the human caller — never silently proceed — when a named environment has a dirty worktree or commits ahead of upstream, because flurry's review and fold assume the environment's change-set is only this batch's commits.
- **Reused idle environments** — read `winter ws status --json` (or `winter ws list --json`) and pick environments whose worktrees are clean (dirty equals zero) and not ahead of upstream, preferring the conventional order alpha, beta, gamma; an idle environment keeps flurry's change-set isolated.
- **Newly created environments** — run `winter ws init <greek>` on the next unused Greek letter (`winter ws index <name> --json` resolves a name's slot), confirm with the human caller before creating any environment, and after init complete any project-specific setup per `workspace:/context/project/project-setup.md`.

When tracks outnumber the environments that can reasonably run, cap the pool and queue the extra tracks: when a track finishes and frees its environment, dispatch the next queued track onto it, and tell the human caller the cap and the queue in one line. Record the allocated pool in the ledger as track to environment to absolute worktree path(s).

## 4. Provision

Before dispatching any implementation role or exercising any runtime in an allocated environment, run `winter provision <env>` for each selected, reused, or newly created environment; independent environments may provision concurrently; record the per-environment result. Every allocated environment must pass the idempotent readiness operation before any task is dispatched or any runtime exercised there; a failed environment stops its track.

When provisioning fails, do not dispatch or runtime-exercise that environment's track: mark the track stopped, which is terminal for batch closure, and report the provisioning failure to the human caller while unaffected tracks continue. A queued track may reuse an environment that already provisioned successfully unless intervening work invalidated its readiness.

Provisioning does not start services, and the task-level service policy stands: flurry does not start services, and a probe that requires an unavailable service reports that condition rather than guessing.

## 5. Dispatch tasks

Dispatch runs distinct tracks in parallel and a track's tasks in order. Each task spawns the canonical `ice-carver` role in a one-shot isolated context with workhorse model intent (Sonnet/Terra class); the leading task of every parallel track starts as one concurrent group so dispatch never waits on one track to start another, and each isolated result is consumed as it becomes available. As each track's environment frees, dispatch any queued track onto it.

Each task ice-carver's invocation carries, in order:

1. **The isolated-role restrictions.**
2. **The environment pin** — the environment name and the absolute worktree path(s) for the repo(s) the task touches (`<workspace>/<env>/<repo>`), with the hard rule to work only inside that environment's worktrees, never change directory out, and never fall back to a source checkout under `projects/`.
3. **The task** — what to build and why; a non-leading task in a track is told that earlier tasks in the track have already committed on this branch and its work builds on them.
4. **The runtime-verification requirement** — the definition-of-done bar: a green build or typecheck is not verification — run a real probe (execute the affected test, curl the endpoint, invoke the CLI, load the page) and report what was run and observed. The prompt passes the base URL and port from `workspace:/context/project/project-setup.md` or the environment's computed variables via `winter env <env>` when the probe needs a running service; when services are not up, the ice-carver says so rather than guessing, because flurry does not start services.
5. **The one-commit instruction** — once implemented and verified, make exactly one conventional commit with scope per [`../../delivery/commit/conventions.md`](../../delivery/commit/conventions.md) (and a `Closes #N` footer when the ask maps to an issue) covering this task's work and nothing else, and do not push.
6. **The reporting requirement** — files with line ranges changed, the commit SHA, the probe(s) run with what was observed, and a one-line verdict.

One task means one fresh isolated role and one commit; holding each task's ice-carver to exactly one commit is what makes the batch-review fold clean.

## 6. Run each track to terminal

- When a task reports done and verified — one commit and an adequate runtime probe — spawn a fresh ice-carver for the track's next task on the same environment, or mark the track complete, recording the commit SHA against the task in the ledger.
- When a task has nothing to commit (the ask was already satisfied, or a no-op), note it; the track skips that commit and moves on.
- When a task fails, re-spawn with the failure folded in.
- When a task's verification is weak or missing (build-only, no real probe), re-spawn a fresh ice-carver for the same task with the gap named explicitly; the run may be verification-only when the code looks done.
- Hold a soft cap of three attempts per task: a task that cannot pass an adequate runtime check in three attempts marks its track failed and stopped. Failed and stopped tracks are terminal for batch closure — keep the other tracks running, escalate the task to the human caller with a one-line-per-attempt summary, and do not require the track to succeed before closing the batch.

## 7. Batch review

Close the batch once every track is terminal — completed, failed, or stopped — with one review phase over everything the flurry successfully built, not a review ceremony per environment; a failed or stopped track neither prevents closure nor needs retry to success.

For each environment holding successful batch commits — including commits produced before the track later failed or stopped — use any repo worktree of that environment as the working directory so the review detects the environment, and execute [`../../delivery/pre-push/process.md`](../../delivery/pre-push/process.md) in blocking mode, consuming the findings programmatically rather than through the advisory prompt. Each pre-push execution reviews every repo in its environment ahead of upstream as one change-set; the environments are independent, so run their reviews concurrently and pool every finding into one batch-wide list, treating the batch as a unit for the fold and the report.

Map each finding to its originating commit: the ledger holds task to environment to repo to commit SHA, each finding names a repo plus file or area, and matching the finding's file to the task that touched it identifies the commit. A finding with no single originating commit — a cross-repo contradiction, or something spanning the whole environment — becomes its own small follow-up commit on the relevant track's environment, noted as such rather than forced into an unrelated commit. Gaps are not findings: keep them out of the pooled list and the fold, because an ice-carver cannot act on one, and carry them into the final digest instead.

## 8. Fold

For each environment with findings, spawn one isolated ice-carver with workhorse model intent, carrying the isolated-role restrictions, the environment pin, and the findings grouped by the commit SHA they belong to, running independent environment invocations concurrently. An environment with no findings needs no fold, and a fully clean batch skips the fold entirely.

The fold ice-carver addresses every finding and folds each fix into the commit that produced it — `git commit --fixup <sha>` per finding then `git rebase -i --autosquash <base>`, or amend when the finding lands on HEAD — preserving one commit per task. It re-verifies the affected change at runtime, does not push, and returns the rewritten commit SHAs and what it re-ran.

## 9. Final report

The final report is a per-environment digest: for each environment, the tasks and their commit SHAs, how each successful task was verified, the pre-push outcome for successful commits, which findings were folded into which commits, and any gaps the review returned. Keep it tight: one block per environment, one line per task.

Include every failed or stopped track with its terminal reason, attempt summary, successful commits if any, and tasks not completed, presented plainly rather than as a success and without requiring repair before reporting. State clearly that nothing was pushed — delivery is the human caller's decision, via `winter ws push <env>` or raw `git push` per environment.
