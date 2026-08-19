# Iceberg — process

The iceberg executor is the visible tip of a standing delegation team whose mass works below the waterline: the human
caller supplies a conversational stream of instructions, and the executor fans the work out to resident workers, keeps
them in their working trees, and reports results back in aggregate. It coordinates many work targets simultaneously —
feature environments, standalone repositories, and the workspace branch — never just one.

The executor is a pure orchestrator: it does no work itself, uses resident coordination one hundred percent of the time,
and never reads or edits application code to fix something directly — every code touch goes to a worker. It inspects
only what it needs to resolve target paths and sanity-check assignments, and routes all implementation to an ice-carver.
Iceberg is light rather than ceremonial: no mandated activity logs and no retrospective; assignments are tracked in the
executor's own context and reported as digests.

Iceberg requires the resident-worker port declared in [`../../runtime-ports.md`](../../runtime-ports.md); when the
active harness cannot create, communicate with, re-task, stop, and tear down resident workers while remaining receptive
to the human caller, return `unsupported-capability` before dispatching rather than emulating iceberg with isolated
runs.

## Inputs

- **Opening instruction stream** — one or more conversational instructions, each with an optional work-target hint.
- **Ongoing instruction stream** — subsequent human-caller instructions accepted while work is in flight, treated as
  first-class input rather than an interruption.
- **Workspace state** — the available targets, their absolute paths, and current assignment overlap.
- **Human-caller channel** (required) — used for ambiguous targets, the tmux choice, dispatch decisions, progress
  digests, and teardown.

## Outputs

- Work delegated to target-pinned resident workers, with independent assignments parallelized and conflicting
  assignments queued.
- Per-worker progress digests and final digests to the human caller.
- A cleanly deleted resident coordination context at teardown, with no required activity log or retrospective.

## Work targets

Each instruction names or implies a work target: a feature-environment worktree (such as `alpha/<repo>/`), a standalone
repository, or the workspace branch itself. Target paths resolve as: feature environment to
`<workspace>/<env>/<repo>/...`, standalone repository to `<workspace>/<repo>/...`, and workspace branch to
`<workspace>/...`.

The human caller may name the target, imply it from an earlier instruction in the same stream, or leave it ambiguous;
when it is ambiguous and matters, ask through the human-caller port rather than guessing. A feature environment's index
is resolved with `winter ws index <name> --json` — index allocation is owned by
`workspace:/context/winter-cli/usage/ws/init.md` — and an environment's existence is confirmed with
`winter ws list --json` before pinning a teammate to it. Before dispatching, resolve each instruction to a target and an
absolute path.

## Workers

Every resident worker is pinned to exactly one work target. A teammate works only inside its target's path and never
changes directory out of it; for feature-environment work specifically, the repo's source checkout under `projects/` is
off-limits and never a fallback, while standalone repos and the workspace branch are worked on directly.

- Reuse the extension's canonical role-pure agents rather than redefining roles; the session adapter resolves each
  canonical role to its projected harness identity. Match the teammate's role to the work: ice-carver for code,
  verifiers for confirmation, arctic-explorer for investigation, cold-reviewer for review.
- Workers are named `<target>-<role>` with the target first (such as `beta-dev`, `alpha-fe`, `winter-cli-dev`) so the
  working tree is the first thing read at a glance, using a short role tag such as `dev`, `fe`, `be`, `review`,
  `explore`, or `arch`. The name is only a display label; the worker itself is selected by canonical role (ice-carver,
  frontend-verifier, and so on), which the session adapter resolves to the active harness's projected identity.
- One target can host multiple teammates when its work is independent, using numbered or area-distinct names such as
  `beta-dev-2` or `beta-dev-api` and `beta-dev-ui`.
- Workers are always started from the workspace root so they inherit workspace instructions and the installed agent and
  operation definitions. Start each worker as a resident concurrent operation so dispatch never blocks the conversation,
  and supply the role's declared model intent explicitly so the adapter can resolve the appropriate harness model tier.
- A teammate can run the full local dev-verify cycle inside its own target, including bringing a feature environment's
  services up with `winter service up <env>` — the run phase per `workspace:/context/environment-lifecycle.md`.

## Assignments

A resident invocation names semantically: the canonical role, the coordination context, the display name, the model
intent, the target path, the task, the files/area, and the expected result shape through the resident communication
channel. Every worker assignment carries, in order:

1. **The resident-worker restrictions** — participate as a resident worker coordinated by the current caller; stay
   pinned to the supplied absolute work target, never leaving it or touching another, and for a feature-environment
   target never falling back to a source checkout under `projects/`; after each assignment, consult the resident
   coordination context for queued work relevant to this target and claim it before becoming idle; send concise
   progress, completion, and final status through the resident communication channel without raw file dumps; and on a
   completion notice, finish the current assignment, return final status, and stop.
2. **The target pin** — the target name plus its absolute path plus the hard rule never to leave it.
3. **The task** — what to do and why.
4. **The constraints plus reporting** — what not to touch, and the result shape to send through the resident
   communication channel.

Preserve the resident-worker restrictions as declared, adding only role-specific task content.

## Dispatch policy

The dispatch decision is made per incoming instruction and stated to the human caller in one line; announce
queue-versus-parallelize decisions tersely, saying which and why in one line rather than narrating at length. Work runs
parallel by default and is serialized only when it would collide:

- Instructions targeting different targets always run in parallel — separate working trees never interfere, so spawn a
  teammate per target.
- An instruction for a target with in-flight work runs in parallel there when it touches a different area — no
  overlapping files or directories and no shared build artifact — by spawning a second teammate, with the decision
  announced.
- An instruction that would touch the same files or region as in-flight work on its target — or that otherwise cannot
  safely run concurrently, such as the same migration or the same build artifact — is queued behind the running task,
  with the decision announced.
- When in doubt about overlap, queue: a false serialize costs latency, while a false parallel costs a merge conflict in
  a shared working tree.

A queued instruction is realized either by holding it and dispatching when the blocking teammate reports done, or by
placing it in the resident coordination context's shared assignment queue for the same worker to claim after its current
assignment. When a single instruction is really a whole plan-driven feature build — design, implement, verify, review on
one target — hand that target's teammate the work as a unit.

## The ledger

The executor tracks target-to-teammate assignment in its own context — there is no on-disk log — as a ledger table with
columns for target, teammate, task, files or area, and status, updated as work moves. The files/area column must stay
accurate because it drives the queue-versus-parallel decision.

## Preflight and panes

Preflight first performs the required resident-capability check from the runtime-port contract, then asks the session
adapter whether it provides live resident-worker panes.

- When the session adapter supplies tmux-backed resident-worker panes and the session runs inside tmux, each worker is
  watchable live in its own pane; the target-first worker naming exists so a glance at the panes shows who is working
  where.
- When the optional pane view is tmux-backed, check whether tmux is active by testing the `TMUX` environment variable
  (for example `[ -n "$TMUX" ]`). When the pane view is supported but tmux is not active, tell the human caller once up
  front that rerunning inside tmux provides a live pane per worker but resident coordination can proceed without that
  optional view; let them choose to restart or continue, and do not block on it.
- On a harness without tmux-backed panes, use that harness's declared resident-worker observability and do not promise
  panes it does not provide. When the adapter provides no live-pane view, state that once without implying tmux will
  create one; this is not an unsupported-capability result, because panes are observational rather than required
  coordination.

The team's worker panes are distinct from the winter-service-tmux session, which orchestrates a feature environment's
application services (`./up`, `./down`, `./status`, session `<prefix>-<env>`): that session is the services of one
environment, the team panes are the agents across all targets, and a teammate may drive its environment's service
session to run the app — do not conflate the two.

## Execution loop

Execution starts by creating the resident coordination context, parsing the opening instruction stream, resolving its
work targets, and dispatching. In order:

1. Run the preflight and note whether live panes are available.
2. Create a resident coordination context through the runtime port with a short display name such as `iceberg` or
   `coordination`.
3. Parse the opening instruction stream, resolving each instruction to a work target.
4. Dispatch per the dispatch policy, starting resident workers concurrently so the conversation stays live.
5. Loop — receiving worker reports and ongoing instructions, updating the ledger, dispatching or re-tasking, and
   reporting digests — with no fixed end, until the human caller says to stop, then tear down.

The executor stays receptive: it accepts new human-caller input immediately and never blocks the conversation waiting on
a running teammate.

## Reporting

Worker reports arriving through the resident communication channel are aggregated into a per-worker digest — one concise
line per worker, never raw output; the executor never echoes a teammate's raw output, it summarizes. Surface a digest
when a batch completes or when the human caller asks where things stand; do not post a line per arriving message unless
the human caller wants live play-by-play.

## Teardown

Teardown happens when the human caller signals they are done, or all work is complete with no more coming: send each
active worker a completion notice so it finishes its current assignment and stops; stop any worker that must halt
mid-assignment through the resident coordination port; give a final per-agent digest of everything that landed; and
delete the resident coordination context. Teardown stays light — no retrospective and no activity-log roundup.
