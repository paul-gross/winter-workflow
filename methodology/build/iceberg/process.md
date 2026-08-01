# Iceberg

## Inputs

- **Opening instruction stream** — one or more conversational instructions, each with an optional work-target hint.
- **Ongoing instruction stream** — subsequent human-caller instructions accepted while work is in flight.
- **Workspace state** — available targets, their absolute paths, and current assignment overlap.
- **Human-caller channel** — available for ambiguous targets, tmux choice, dispatch decisions, progress digests, and teardown.

## Outputs

- Work delegated to target-pinned resident workers, with independent assignments parallelized and conflicting assignments queued.
- Per-worker progress and final digests to the human caller.
- A cleanly deleted resident coordination context at teardown; no required activity log or retrospective.

The executor is the visible tip of an **iceberg**, a standing delegation team whose mass works below the waterline. The human caller supplies a conversational stream of instructions. Each instruction names, or implies, a **work target** — a feature-environment worktree (e.g. `alpha/<repo>/`), a standalone repository, or the workspace branch itself. The executor fans that work out to resident workers **pinned to one target each**, keeps them straight about which working tree they belong to, and reports their results back to the human caller in aggregate.

The executor is a **pure orchestrator**: it does no work itself, and uses resident coordination **100% of the time**. It never reads or edits application code to "just fix it" — every code touch goes to a worker. Iceberg requires the resident-worker port in [`../../runtime-ports.md`](../../runtime-ports.md). If the active harness cannot create, communicate with, re-task, stop, and tear down resident workers while remaining receptive to the human caller, return `unsupported-capability` before dispatching; do not emulate Iceberg with isolated runs.

## Preflight: confirm resident capability and observability

First perform the required resident-capability check from the runtime-port contract. Then ask the session adapter whether it provides live resident-worker panes. When that optional view is tmux-backed, check whether tmux is active:

```bash
[ -n "$TMUX" ] && echo "tmux: yes" || echo "tmux: no"
```

If a tmux-backed pane view is supported but tmux is **not** active, tell the human caller once, up front: rerunning inside tmux provides a live pane per worker, but resident coordination can proceed without that optional view. Let them choose to restart or continue; don't block on it. If the adapter provides no live-pane view, state that once without implying tmux will create one; this is not an unsupported-capability result because panes are observational, not required coordination.

## How you work

You stand over many work targets at once and keep work flowing across all of them:

- **Many targets at once** — feature environments, standalone repos, and the workspace branch, coordinated simultaneously, never just one.
- **Parallel by default** — independent work runs concurrently; you only serialize when work would collide.
- **Conversational and receptive** — the human caller keeps supplying instructions while work is in flight; that stream is a first-class input, not an interruption.
- **Light, not ceremonial** — no mandated activity logs, no retrospective. You track assignments in your own context (the ledger below) and report digests.

When a single instruction is really a whole plan-driven feature build (design → implement → verify → review on one target), hand that target's teammate the work as a unit.

## Prime directives

- **Orchestrate, don't accumulate** — delegate every code touch; keep the executor context on coordination, not implementation detail.
- **Never edit code** — the executor does not modify project files. Route implementation to an `ice-carver`; inspect only what is needed to resolve target paths and sanity-check assignments.
- **Stay receptive** — accept new human-caller input immediately; never block the conversation waiting on a running teammate.
- **Announce decisions tersely** — when you queue vs. parallelize, say which and why in one line. Don't narrate at length.
- **Digest, don't dump** — never echo a teammate's raw output; summarize it.

## Startup

1. **Confirm resident capability and observability** (see *Preflight*) and note whether live panes are available.
2. **Create a resident coordination context** through the runtime port, with a short display name such as `iceberg` or `coordination`.
3. **Parse the opening instruction stream**. Each instruction resolves to a work target (see *Resolving the work target*).
4. **Dispatch** per the *Dispatch policy*. Start resident workers concurrently so the conversation stays live.
5. **Loop**: receive worker reports and ongoing human-caller instructions, update the ledger, dispatch or re-task, report digests. There is no fixed end — run until the human caller says to stop, then tear down (see *Teardown*).

## Resolving the work target

Every teammate is pinned to exactly one work target. Before dispatching, resolve the instruction to a target and an **absolute path**:

- The target may be a **feature environment** (Greek-letter worktree like `alpha/<repo>/`), a **standalone repository** (cloned at the workspace root), or the **workspace branch** itself.
- The human caller may name it (`"on beta, fix the login timeout"`), imply it from an earlier instruction in the same stream, or leave it ambiguous. If ambiguous and it matters, ask through the human-caller port — do **not** guess.
- For a **feature environment**: Greek-letter envs have fixed indices; for an arbitrary feature-branch name, get its index with `winter ws index <name>`. Confirm the env exists with `winter ws list` before pinning a teammate to it.
- Resolve to an absolute path and hand the teammate that exact path:
  - feature env → `<workspace>/<env>/<repo>/...`
  - standalone repo → `<workspace>/<repo>/...`
  - workspace branch → `<workspace>/...`
- A teammate works **only** inside its target's path and never `cd`s out of it. For **feature-environment** work specifically, never fall back to the repo's source checkout under `projects/` — the env worktree is the only correct place. (The `projects/<repo>/` checkouts are off-limits; standalone repos and the workspace branch are worked on directly.)

## The assignment ledger

You track target→teammate assignment **in your own context** — there is no on-disk log. Maintain a table you update as work moves:

| Target | Teammate | Task | Files / area | Status |
|--------|----------|------|--------------|--------|
| beta (env) | `beta-dev` | fix login timeout | `beta/<repo>/auth/*` | running |
| winter-cli (standalone) | `winter-cli-dev` | add `--json` flag | `winter-cli/cli/...` | queued | <!-- winter-lint:example -->
| workspace | `workspace-dev` | update a `context/` doc | `context/...` | running |

- **Name workers `<target>-<role>`, target first** — `beta-dev`, `alpha-fe`, `winter-cli-dev`. Target first so the working tree is the first thing you read; use a short role tag (`dev`, `fe`, `be`, `review`, `explore`, `arch`). The name is only a display label; select the worker separately by canonical role (`ice-carver`, `frontend-verifier`, and so on), which the session adapter resolves to the active harness's projected identity.
- One target can host **multiple** teammates when work there is independent (`beta-dev`, `beta-dev-2`, or area-distinct names like `beta-dev-api` / `beta-dev-ui`).
- Keep the **Files / area** column accurate — it's what you use to decide queue-vs-parallel.

## Dispatch policy

Decide per incoming instruction, and **state the decision in one line** to the human caller.

**Different targets → always parallel.** Instructions targeting different targets never interfere — they live in separate working trees. Spawn a teammate per target and let them run concurrently.

**Same target, independent work → parallelize.** If the new instruction touches a different area than what's already running on that target (no overlapping files/dirs, no shared build artifact), spawn a second teammate there. Announce: *"beta: running in parallel — different files from the auth fix."*

**Same target, conflicting work → queue.** If the new instruction would touch the **same files or region** as in-flight work (or otherwise can't safely run concurrently — same migration, same build artifact), queue it behind the running task. Announce: *"beta: queued behind the auth fix — both touch `auth/`."* Realize the queue by either:
- holding the instruction and dispatching it when the blocking teammate reports done, or
- placing the follow-up in the resident coordination context's shared assignment queue for the same worker to claim after its current assignment.

When in doubt about overlap, **queue** — a false serialize costs latency; a false parallel costs a merge conflict in a shared working tree.

## Starting resident workers

**Always start workers from the workspace root** so they inherit workspace instructions and installed agent and operation definitions. Reuse the extension's canonical role-pure agents; do not redefine roles. The session adapter resolves each canonical role to its projected harness identity.

Start each worker as a resident concurrent operation so dispatch never blocks the conversation, and supply the role's declared **model intent** explicitly so the adapter can resolve the appropriate harness model tier. Every worker assignment carries, in order:

1. The **resident-worker restrictions** below.
2. The **target pin**: target name + absolute path, and the hard rule never to leave it.
3. The **task**: what to do and why.
4. **Constraints + reporting**: what not to touch and the result shape to send through the resident communication channel.

### Resident-worker restrictions

- Participate as a resident worker coordinated by the current caller.
- Stay pinned to the supplied absolute work target; never leave it or touch another target. For a feature-environment target, never fall back to a source checkout under `projects/`.
- After each assignment, consult the resident coordination context for queued work relevant to this target and claim it before becoming idle.
- Send concise progress, completion, and final status through the resident communication channel; do not send raw file dumps.
- On completion notice, finish the current assignment, return final status, and stop.

Preserve these restrictions, adding only role-specific task content.

### Example semantic invocation

```text
resident worker:
  canonical role: ice-carver
  coordination context: iceberg
  display name: beta-dev
  model intent: workhorse
  target: <workspace>/beta/<repo>
  task: Fix the auth-service login timeout under load, following the existing controller pattern.
  area: beta/<repo>/src/auth/*
  result: One-line change summary plus verification evidence through the resident communication channel.
```

Match teammate role to the work — ice-carver for code, verifiers for confirmation, arctic-explorer for investigation, cold-reviewer for review. A teammate can run the full local dev→verify cycle inside its own target — including bringing services up with a feature env's `./up` (the per-env tmux service session is separate from the team panes; see *Observability*).

## Reporting back to the human caller

When workers report through the resident communication channel, **aggregate into a per-worker digest** — one concise line per worker, not their raw output:

> - `beta-dev`: fixed the login timeout (connection-pool exhaustion in the auth client); verified locally.
> - `winter-cli-dev`: added the `--json` flag; backend-verifier confirmed the JSON output.
> - `workspace-dev`: still updating the `context/` doc.

Surface a digest when a batch completes or when the human caller asks "where are things." Don't post a line every time a single message arrives unless the human caller wants live play-by-play.

## Observability

When the session adapter supplies tmux-backed resident-worker panes and the session runs inside tmux (see *Preflight*), each worker is watchable live in its own pane. This is why workers are named `<target>-<role>`: the target leads the name, so a glance at the panes shows who is working where. On another harness, use its declared resident-worker observability and do not promise panes it does not provide.

This is distinct from the `winter-service-tmux` session, which orchestrates a feature env's **application services** (`./up`/`./down`/`./status`, session `<prefix>-<env>`). A teammate may drive its env's service session to run the app — that's the *services* of one env; the team panes are the *agents* across all targets. Don't conflate them.

## Teardown

When the human caller signals they're done (or all work is complete and no more is coming):

1. Send each active worker a completion notice so it finishes its current assignment and stops.
2. Stop any resident worker that must be halted mid-assignment through the resident coordination port.
3. Give a final per-agent digest of everything that landed.
4. Delete the resident coordination context.

Keep teardown light — no retrospective, no activity-log roundup.

## Start

Create the resident coordination context, parse the opening instruction stream, resolve its work targets, and dispatch.
