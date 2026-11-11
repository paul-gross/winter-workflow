# Rapid iteration — process

Keep the conversation responsive while implementation workers turn evolving requests into small, visible increments.
This is an explicitly selected local development mode, not a delivery pipeline. The coordinator owns scheduling and the
durable queue; workers own implementation. Work on one or more targets without requiring a resident team.

## Inputs and results

- **Request stream** — opening requests and subsequent corrections, priorities, cancellations, and additions.
- **Targets** — absolute authorized worktree paths and their governing instructions.
- **Ledger path** — an optional caller-selected session file, writable only by the coordinator.
- **Preview binding** — the local preview URL, HMR/service owner, and any separately owned runtime or service files.
- **External ownership** — files and shared resources reserved by other workers or sessions.

Return concise progress digests with the ledger location, active and queued request ids, changed paths, visible value,
preview evidence or blocker, and deferred hardening. An increment is **preview-ready**, not tested, reviewed, or
production-ready. Keep those distinctions in the ledger and final handoff.

## Mode boundary

Activate only when the caller explicitly chooses rapid iteration or asks for this ongoing deferred-hardening mode. Keep
it active across conversational turns and compaction until the caller explicitly pauses, stops, or switches out. A new
feature request, an empty queue, or a worker finishing does not switch modes.

During this mode:

- Do not add, update, or run tests, test harnesses, lint, format sweeps, review gates, or broad verification.
- Do not invoke glacier, snowball, flurry, verify-finale, or completion workflows that restore those gates.
- Do not perform unrelated cleanup, speculative refactors, documentation sweeps, or retrospectives.
- Make only the focused implementation and minimal local runtime/UI checks needed to expose the requested value.
- Repair blocking runtime/build failures only as far as needed to restore that feedback loop. A one-shot targeted build
  is for diagnosing a blocked preview, not a substitute gate on every increment.
- Record deferred tests, lint, reviews, documentation, and other hardening without doing them. This includes deferred
  changes to any existing tests affected by an implementation edit.
- Do not commit, push, release, deploy, or access production. Delivery requires leaving this mode and separate caller
  authorization; a stop request is not delivery authorization.

This process replaces the ordinary [completion bar](../../completion.md) for the active mode only. Architecture,
security, ownership, source-checkout restrictions, and the provision-before-run baseline still apply. If a higher-priority
requirement cannot be reconciled with the mode, report the conflict rather than silently running hardening or weakening
the requirement.

## Start

1. Read the [philosophy](../../philosophy.md), target entrypoints, and only the target guidance needed for the first
   increment. Confirm the actual repository and worktree with git before assigning edits. Never substitute a project
   source checkout; standalone extensions may be authored directly in their configured standalone checkout.
2. Bind target paths, preview URL, provisioned state, and current service owners. Reuse the authorized HMR session. Do
   not re-provision, restart, or reconfigure a service another worker owns; queue a request to its owner instead. If a
   required environment is unprovisioned, arrange the documented provisioning with its owner before running it.
3. Resolve projected agent identities and **judgment** model intent (Opus/Sol class) through the
   [runtime adapter contract](../../runtime-ports.md). Use that intent for implementation workers by default in this
   process, explicitly overriding ice-carver's routine workhorse default. Do not silently downgrade. If that tier is
   unavailable, ask whether to use an available tier or pause, and record any approved substitution.
4. Confirm the adapter supports nonblocking worker dispatch and completion notifications while the conversation remains
   available. Use resident workers if supported, or isolated background assignments returning one result each. The latter
   is an intentional execution form here, not an emulation of iceberg's resident protocol. Do not poll or block awaiting
   a worker. If no responsive dispatch mechanism exists, return `unsupported-capability` using the runtime contract;
   offer to pause rather than silently implementing inline.
5. Open the caller-selected ledger. Without one, resolve the `workflows` artifact directory through
   [artifact storage](../../artifact-storage.md) and create a session directory using its naming convention, with
   `queue.md` inside. Announce its resolved location. Preserve an existing ledger and reconcile it before dispatch.
6. Persist `mode: active`, target and preview bindings, coordinator identity, external ownership, and the initial
   requests. Tell the caller the mode is active and hardening is deferred, then dispatch the first safe increments.

## Durable queue

The coordinator is the ledger's only writer; workers report updates rather than editing it. Record each incoming
request before acknowledging or dispatching it. Keep stable ids and the caller's intent when an ask changes.

Each request entry carries:

- Request id, current revision, requested outcome, and priority/order.
- Absolute target and explicit owned file paths or narrowly bounded path sets, including planned new files.
- Dependencies, shared resources, and excluded paths, including external reservations.
- State: `queued`, `running`, `blocked`, `preview-ready`, `superseded`, or `cancelled`.
- Assigned worker/session identity, assignment revision, and its current ownership reservation.
- Latest result: changed paths, preview evidence or blocker, and deferred hardening.

Keep session-level deferred hardening alongside the requests so a completed or superseded ask cannot erase it. Persist
every dispatch, ownership change, result, cancellation, and mode transition. A caller-selected ledger is session state,
not permission to change repository configuration or ignore files.

On resume, read the ledger first. Reconcile recorded workers against live session state and repository changes; do not
assume `running` means a worker is alive or release an uncertain reservation. Mark uncertainty blocked and establish
ownership before redispatching. Resume the recorded mode without automatically performing the deferred work.

## Scheduling and evolving requests

The coordinator does not implement application changes. Delegate bounded increments to one or more canonical
**ice-carver** workers, started from the workspace root with absolute targets and self-contained assignments.

- Default to parallel dispatch when file ownership and shared resources are disjoint. One worker is sufficient when the
  next value is one slice; avoid spawning a team merely to fill roles.
- Reserve files before dispatch. Different functions in the same file still overlap. Serialize shared files, generated
  outputs, dependency manifests, migrations, build artifacts, service configuration, and runtime lifecycle operations.
- Treat unknown ownership as overlapping. Have a worker investigate within its reservation, then return a proposed file
  set; the coordinator grants any expansion before edits begin. Workers cannot claim extra paths themselves.
- For a correction, persist a new request revision. Redirect a running worker only when the adapter can reliably deliver
  the change; otherwise queue a follow-up behind its reservation. A cancelled or superseded worker retains its reservation
  until it has acknowledged stopping or returned. Do not discard its edits.
- Record stale-revision results as such; they cannot mark the caller's latest intent preview-ready. Schedule the missing
  delta after ownership is released.

After each dispatch group, return control to the conversation with a short active/queued summary. On incoming user
messages or worker completion notifications, update the ledger and dispatch newly unblocked work. Do not wait for all
workers to finish before acknowledging a new request. Surface an ownership conflict or runtime blocker promptly.

## Worker assignment contract

Supply each worker with the mode boundary above and:

- Request id and revision, outcome, absolute target, and relevant target guidance.
- Exact allowed files, excluded files, dependencies, and external reservations.
- The instruction to stop and request an ownership expansion before touching any additional path.
- The preview binding and permitted runtime actions; no service or config mutation outside its reservation.
- The instruction not to delegate further, edit the queue, perform hardening, or invoke another build workflow.
- The instruction to preserve existing user/other-worker changes and stop on unexpected overlap.
- A result shape: request/revision, status, changed paths, visible value, minimal preview evidence or blocker, deferred
  hardening, and whether the worker has stopped writing and released ownership.

The injected restrictions narrow the agent's permissive role contract. They apply even when its general instructions
mention tests, architecture review, or broader verification.

## Fast feedback and stopping

Have the implementing worker use the existing HMR path and report where the caller can see the increment. Prefer one
focused local UI interaction, screenshot, or API/CLI observation showing the requested behavior. Reuse evidence already
gathered; do not launch a second verifier or require a separate build when HMR already exposes the change. If the worker
cannot access the preview, report **implemented; preview unconfirmed** and ask the caller to look, without claiming
preview-ready. Runtime recovery that needs another owner's files is blocked work for that owner, not an ownership bypass.

On pause or stop, stop dispatching and coordinate running workers to a safe stop; preserve edits and reservations until
workers confirm they are no longer writing. Persist the mode transition, unfinished requests, worker state, and deferred
hardening, then hand back a concise summary. Do not stop shared services. An explicit switch out of rapid mode permits
discussing a hardening pass; it does not automatically execute that pass or authorize delivery.
