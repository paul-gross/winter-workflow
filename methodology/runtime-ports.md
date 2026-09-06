# Methodology runtime ports

Reusable methodology describes coordination through the semantic operations below. The executing session is the runtime
adapter: it maps each operation to capabilities available in its harness without exposing harness syntax to the
methodology.

## Adapter responsibilities

Before executing a process, the session adapter must:

1. Resolve a canonical role to the identity installed for the active harness. Follow the live agent installation and
   prefix facts at `workspace:/context/winter-cli/configuration/extensions.md#what-gets-symlinked` and inspect the
   active projected artifact rather than assuming one harness's invocation identity.
2. Resolve model intent through the active harness's model-tier projection at
   `workspace:/context/winter-cli/configuration/agents.md`. A process names intent such as **workhorse** (Sonnet/Terra
   class) or **judgment** (Opus/Sol class), not a vendor model id.
3. Map the semantic operations below to native session capabilities and preserve their isolation, concurrency,
   lifecycle, and return semantics.
4. Check required capabilities before starting work that depends on them.

The adapter may add projected identity or native invocation details, but it must not change the selected canonical role,
weaken a restriction, serialize work declared concurrent, or invent a capability.

## Operations

### Spawn an isolated role

Run a canonical role in a fresh isolated context with:

- its canonical role name and model intent;
- a self-contained task, absolute targets, and supplied methodology references;
- semantic restrictions and a declared result shape;
- either **await result** or participation in a declared concurrent group.

An isolated role has no prior conversation context. Unless a process explicitly says otherwise, it has no resident peers
or shared assignment queue, returns its result once through the harness's isolated-result channel, performs no follow-on
coordination, and stops.

### Fork the current context

Create concurrent copies of the calling context that inherit everything it has read and established, each carrying one
bounded charter and a declared result shape.

- A fork inherits the parent's accumulated context and model intent; its charter adds only the fork's task,
  restrictions, and result shape.
- **Fork to deepen, spawn fresh to diversify or adjudicate.** A fork shares the parent's framing, so use forks to pursue
  work the parent has already framed correctly. Any step whose value depends on independence from that framing —
  verification of the parent's findings, adjudication between results, a control read of the same material — uses
  **Spawn an isolated role** instead.
- Forks run as a declared concurrent group, return one distilled result each through the harness's isolated-result
  channel, and stop; the parent awaits the group. A fork returns conclusions, not its investigation.
- When a context cannot fork and the process explicitly permits a fallback, substitute an orientation briefing: the
  parent writes one from its own context and spawns isolated roles carrying it. Without an explicit fallback permission,
  an unavailable fork capability is an unsupported capability.
- A briefing is lossy — the children inherit a summary the parent chose to write, not everything it read — so a result
  says which mechanism produced it whenever the difference is material. A run that **fell back**, where the process's
  placement expected a fork and the seat could not supply one, labels itself a degraded execution. A process that
  instead **declares** briefing its standing mechanism for a placement owns that declaration, and a run executing it is
  neither degraded nor labeled.
- Whether a given context can fork — and through which native mechanism — is a harness capability fact, not a
  methodology fact: resolve it from the live capability declaration at `workspace:/context/harness-runtime-ports.md`
  before any placement decision that depends on it, and treat a harness or nesting depth with no declared fork support
  as unable to fork.

### Ask the human caller

Present the declared question and choices through the session's human interaction channel. Stop until the answer is
available when the process requires a decision before continuing.

### Resolve a workflow artifact directory

Resolve one winter-workflow artifact kind named by [`artifact-storage.md`](./artifact-storage.md) through the active
Winter CLI contract. The adapter follows `workspace:/context/winter-cli/usage/space.md` for invocation and result
handling; methodology receives only the resolved directory or a failure. Preserve the fail-closed consumer policy in
`artifact-storage.md` and do not invent a fallback path.

### Run concurrently

Start all declared independent operations in one scheduling group and await the results required by the next step. The
adapter chooses native concurrency mechanics; the methodology owns which operations may overlap. Do not silently
serialize a group whose process requires concurrency.

### Create and coordinate resident workers

Create a resident coordination context, start workers by canonical role and model intent, assign or queue work, exchange
progress and control messages, observe completion, stop workers, and delete the coordination context. Resident workers
retain their assignment context and may accept follow-up work until teardown.

This port is materially different from spawning isolated roles. A process that requires ongoing conversational
receptiveness, resident workers, or a shared assignment queue cannot be emulated by unrelated one-shot runs.

### Return a result

Return the process's declared result to its caller through the current runtime's result channel. Preserve status, every
section of the declared result, ids, evidence, and stop/report behavior; do not claim an external action succeeded when
the adapter could not perform it.

## Unsupported capabilities

If a required port or semantic guarantee is unavailable, stop before pretending to execute it and return:

```text
status: unsupported-capability
process: <process name>
capability: <required semantic capability>
detail: <what the active harness cannot provide>
```

Only degrade behavior when the process explicitly permits a fallback.
