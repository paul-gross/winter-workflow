# Ice age — process

The ice-age executor is the program lead: it drives a **program** — a body of work too large for one plan, spanning many
epics and hundreds of changes — from a rough backlog to an integrated, verified result, one **segment** at a time, with
the human caller answering questions as they arise rather than approving each step. For each segment it refines just
that part of the backlog into slices, builds the slices across a small pool of feature environments, lands each through
one serialized integration gate, and closes with a checkpoint that proves the whole still holds.
[`../index.md`](../index.md) owns how ice age routes against the smaller build processes.

Ice age is deliberately narrow. Refinement is never done for the whole program up front: a segment is refined only when
it is next, by a handful of roles, so the backlog is corrected by what the previous segments taught. No more roles run
at once than the charter's concurrency cap allows.

The lead orchestrates and never implements. It never edits a tracked file by hand; every edit goes to an isolated role.
It does run the mechanical version-control steps this process names — committing what a role wrote, rebasing, running a
gate, fast-forwarding — and its own files are the program directory and the retrospective.

The lead reads results, not work. Every isolated role returns at most ten lines — verdict, commit, counts — plus the
path of its full report under `<program-dir>/reports/<slice-or-area>/<stage>-<attempt>.md`. A role without write access
returns its report as its result, and the lead saves it there unread beyond the verdict. A role that needs an earlier
report receives its path, not its text.

Ice age meets the shared definition of done owned by [`../../completion.md`](../../completion.md) per slice — the tested
half through the verify finale — and per segment, where the checkpoint carries the docs-updated half.

## Inputs

- **Program** — the goal and its backlog: a planning-repository project, a set of epics, or a bare description.
- **Reference implementation** (optional) — an existing system the program replaces or must match, with its tests and
  documentation.
- **Target hints** (optional) — the code repositories the program changes, the planning repository, and the branch each
  starts from.
- **Settled decisions** (optional) — answers the human caller gave before the run to the backlog's open decisions.
- **Environment pool** (optional) — feature environments the run may use.
- **Model policy** (optional) — a model intent per role, or one intent bound to every role.
- **Human-caller channel** (required) — used for the charter approval, the questions of [Asking](#asking), a halt, and
  the final report.

## The program directory

Resolve `<workflows-dir>` per [`../../artifact-storage.md`](../../artifact-storage.md) and keep the run's state in
`<program-dir>`, which is `<workflows-dir>/<yyyy-mm-dd>-<name>/` with `<name>` a short kebab-case slug for the program.
An existing program directory named by the caller means resume: go to [Resuming](#resuming) rather than step 1.

| File           | Holds                                                                                                   |
| -------------- | ------------------------------------------------------------------------------------------------------- |
| `charter.md`   | The charter from step 1; approved only once it carries an `Approved: <date>` line                       |
| `plan.md`      | The whole program at a glance — see below                                                               |
| `ledger.md`    | One row per slice: id, segment, depends-on, files, environment, state, attempts, queue position, commit |
| `register.md`  | Everything decided without the human, for review afterwards — see below                                 |
| `questions.md` | One row per question for the human caller: id, what it blocks, the options, state, and the answer       |
| `journal.md`   | Append-only, one line per event: dispatch, result, integration, park, checkpoint, halt, resume          |
| `reports/`     | Every isolated role's full report                                                                       |
| `checkpoints/` | One report per checkpoint, numbered in order and named for its segment                                  |

A slice's state is one of `ready`, `building`, `built`, `verified`, `reviewed`, `queued`, `integrated`, `held`, or
`parked`. Write a ledger row before dispatching the work it describes and again when the result arrives.

`plan.md` is the holistic plan, short enough to read in one pass: the segments in order, each with its state —
`pending`, `refining`, `building`, `checkpoint`, `done` — and its slices counted by state; what is in flight and in
which environment; the questions outstanding; and the next three moves the lead intends. Bring it current at every
segment transition, every checkpoint, and before every batch of questions. It summarizes the other files and never holds
a fact they lack.

The register has four sections, each entry one line with the id it concerns:

- **Decisions made** — every open decision settled under the charter's policy, with the rule that settled it.
- **Deviations** — every place the result deliberately differs from the reference implementation or from the backlog as
  it stood.
- **Parked** — every slice or epic set aside, with its blocker and, for a slice, the ref holding its work.
- **Gaps** — every surface no slice's acceptance checks cover, and every checkpoint finding left open at close.

The lead is ready to have its context summarized, or to hand over to a fresh session, whenever the human caller asks. On
that request: record every result already received, bring `plan.md` current, and say the run is ready. After every
checkpoint, and whenever earlier context has been summarized, re-read the charter and this process and execute
[Resuming](#resuming) before the next dispatch.

## 1. Charter

The charter settles what the run cannot start without and carries every standing rule a later session must obey, since
later sessions read the charter and nothing else from the first. Draft it, present it, and stop until the human caller
approves it; write the `Approved: <date>` line only after they answer. It states:

- **The program** — the goal in two or three sentences, the terminal condition that ends the run, what is out of scope,
  and what must never be touched.
- **Targets** — each target repository, the planning repository, and the **integration line**: one local branch per
  target repository that every slice lands on. Name the **integration environment** whose worktrees hold the integration
  line checked out. No slice is built there; backlog refinement happens there.
- **Segments** — the program cut into an ordered list, each small enough to finish and show — one epic, or a few that
  only make sense together — and ending in something a person can exercise. The default is the backlog's epics in its
  own priority order, preceded by the foundation. The order after the next segment is a forecast the human caller
  re-steers at each checkpoint.
- **The pool** — the environments slices are built in, and the **concurrency cap**: the most roles in flight at once, of
  every kind (default eight). Creating an environment is asked, never assumed.
- **The decision policy** — which open decisions the lead settles without asking, as an ordered rule list. The default:
  a settled decision or binding constraint settles it; otherwise the reference implementation's observable behavior is
  the answer. A decision neither rule settles is asked.
- **The gates** — three commands, each naming what it runs: a **bootstrap gate** (build plus whatever tests exist) used
  until the foundation's gate slice integrates; a **slice gate** of bounded runtime, run on every integration; and a
  **full gate**, run at checkpoints.
- **The model policy** — the model intent for each role. The default is workhorse intent (Sonnet/Terra class) for
  `ice-carver` and judgment intent for every other role; a policy binding one intent to every role, such as **frontier**
  (Fable/Astra class) for the whole run, overrides each role's default at every spawn.
- **Budgets** — the attempt cap per slice (default three), the revise cap per refinement gate (default two), the context
  budgets for a role and for the lead, and the halt conditions of [Halting](#halting).

A change to the charter mid-run is an amendment: ask it as a question, and record the answer in the charter.

## Asking

The human caller is available throughout and expects to be asked. Ask when:

- an open decision is not settled by the charter's decision policy;
- a deviation from the reference implementation is proposed that the backlog does not already call for;
- a slice reaches the attempt cap, or a segment's refinement reaches the revise cap;
- a checkpoint finding is a matter of intent rather than a defect, and at the end of every checkpoint;
- the charter needs amending.

Asking never idles the run:

1. Record the question in `questions.md` and mark the slice it blocks `held`. Everything depending on a held slice
   waits; nothing else does.
2. Dispatch every piece of work that does not depend on the answer.
3. Then ask, batching the questions that have accumulated. Each states what it blocks, the options, and the one the lead
   recommends with its reason, so it can be answered in a tap.
4. On the answer, record it in `questions.md`, have a decision written into the backlog's own decision format by the
   segment's author, naming the human caller as decider, and release what was held.

A question is never answered by the lead on the human's behalf, and a held slice is never built around.

## 2. Shared contracts

Before any segment, one `winter-architect` writes, into the backlog, the contracts more than one segment stands on: the
command or interface surface, the configuration model, result and error types, output formats, extension seams. Where a
reference implementation can enumerate its own surface — a command tree, a schema, a declared format — the author has an
`arctic-explorer` extract it mechanically rather than describing it from reading.

Gate the contracts as step 3 gates a segment, then commit them. This is the only refinement done ahead of its segment.

## 3. Refine the segment

Refine only the segment that is next, in the planning repository's worktree of the integration environment. The
workspace's planning framework owns what each artifact holds; ice age owns the order and the roles. When the workspace
has no planning framework, the same layers live under `<program-dir>/backlog/`, shaped per
[`../../planning/plan-shape.md`](../../planning/plan-shape.md), and the commit is skipped.

1. **Survey.** Spawn one `arctic-explorer` for the segment's area of the reference implementation — two when the area
   divides cleanly — carrying the rule to write nothing in the reference. It reports the observable capabilities in that
   area: entrypoints, inputs, outputs, exit behavior, refusals, side effects, each with the source location and the test
   that pins it. Skip this when the program has no reference implementation and no existing code.
2. **Author.** Spawn one `winter-architect` with the survey report, the shared contracts, the settled decisions, and the
   previous checkpoint report. In one pass over the segment's epics it:
   - corrects their intent against the survey and the charter — what is missing, wrong, or out of scope;
   - applies the decision policy to their open decisions, recording each one settled and returning each one that must be
     asked;
   - writes a spec only where the segment's behavior differs from the reference or the reference leaves it unclear — a
     behavior the reference already pins is specified by citing it;
   - cuts the slices: each one mergeable change with acceptance checks a test can verify, its dependencies, and the
     files it expects to touch.

   It returns one line per slice — id, depends-on, files — from which the lead writes the ledger rows.
3. **Gate.** Execute [`../../review/process.md`](../../review/process.md) with the plan axis and `execution_mode: fresh`
   over the files the author wrote, naming the workspace's planning framework as the plan's owning framework. On
   blocking findings, send the report to a fresh author for one revision, bounded by the revise cap; at the cap, ask.
4. **Commit.** The lead runs the planning repository's own checks and commits the segment's refinement, unpushed.

A slice becomes `ready` when everything it depends on is `integrated`.

## 4. Lay the foundation

The foundation is the first segment and runs alone, in one environment, strictly in order. It is every slice the rest of
the program stands on:

- the project skeleton, arranged so that later slices add files rather than edit shared ones — one file per command, per
  scenario, per registration — because parallel slices that all edit one file collide at integration;
- the test harness, and the slice gate and full gate, with the gate slice first;
- the contributor context and verifiability matrix that builders read;
- when a reference implementation exists, a differential method that runs the reference and the new system against the
  same input and compares what a user can observe, proven on one read-only and one state-changing behavior before any
  other segment relies on it.

Until the gate slice integrates, [Integrate](#integrate) runs the bootstrap gate in place of the slice gate. A
foundation slice cannot be parked: at the attempt cap its question offers only retry and re-cut. Start no other segment
until the foundation is integrated and the full gate runs green on the integration line.

## 5. Build the segment

Whenever a pool environment is free and the concurrency cap allows, assign it the first `ready` slice of the segment in
ledger order whose files do not overlap a slice in flight — when unsure whether two overlap, do not run them together.
An environment holds one slice from assignment until that slice is `integrated`, `held`, or `parked`.

Before an environment's first slice, provision it per the workspace's environment lifecycle. Before every slice, bring
the environment's branch to the integration line's tip by fast-forward. An environment that cannot fast-forward holds
work the run does not own: withdraw it from the pool and record it rather than resetting anything.

**The slice's commit** is the single commit on the environment's branch above the integration line's tip, in each target
repository the slice changes. Its message follows
[`../../delivery/commit/conventions.md`](../../delivery/commit/conventions.md) and ends with a `Slice: <id>` trailer.
Every later role in the loop — a retry, the verify finale, a review fix — amends that commit rather than adding one, and
nothing is pushed.

### Build

Spawn the canonical `ice-carver` role in a one-shot isolated context. Its prompt carries the instruction to report once
and stop; the environment pin, with the rule to work only inside that environment's worktrees; the slice file and the
spec sections and contracts it cites, by path; for a later attempt, the path of the previous failing report; the commit
rule above; and the reporting requirement — files changed, the commit, and which acceptance checks it believes it met.

A builder that finds the slice wrong — a contract that cannot be implemented as written, a missing dependency — reports
that instead of improvising. Have the segment's author correct the backlog, commit it, and retry the slice against the
corrected text.

### Verify

Spawn the canonical `verify-finale` role in a one-shot isolated context, carrying the instruction to report once and
stop, the environment pin, the slice's acceptance checks, and the builder's report path. It verifies each acceptance
check through a method the application's verifiability matrix declares — the differential method wherever the slice
ports reference behavior — building and recording a missing method rather than improvising one.

A slice is `verified` only when every acceptance check ran and passed. A check that could not run is a failed attempt,
never a gap.

### Review

For each target repository the slice changes, execute [`../../review/process.md`](../../review/process.md) on the code
axis with `execution_mode: fresh` and `scope: {range: <integration tip>..<environment branch>}`. On blocking findings,
spawn a fresh `ice-carver` to resolve them, re-run the affected verification, and re-run the review. Consider findings
stay in the report. The other axes are the checkpoint's.

A review that returns no reviewed target is a failed attempt, never a pass.

### Integrate

Integration is serialized across the whole program: one slice at a time, in the order slices became `reviewed`. Record
that order in the ledger's queue position when marking a slice `queued`.

For the slice at the head of the queue, the lead rebases the environment's branch onto the integration line and runs the
slice gate in that environment, sending the gate's output to the slice's report and reading only whether it passed. On
green, it fast-forwards the integration line to the environment's branch from the integration environment's worktree and
marks the slice `integrated` with its commit.

A rebase that stops on a conflict is handed to an isolated `ice-carver` pinned to that environment to settle and
re-verify; one it cannot settle is aborted. An unsettled conflict or a red gate is a failed attempt. A slice is never
integrated on a gate run that predates its rebase.

### Context budget

A large context re-read on every small turn is the run's most avoidable cost, so the charter sets two budgets: one for
each isolated role and one for the lead, whose turns are many and small.

**Roles.** Where the harness exposes a running role's context use, the lead reads it for every role in flight on each
turn it already takes — it never takes a turn only to poll. A role past its budget is turned over, not left to grow: ask
it, where the harness can address a running role, to commit or leave its work in place, write a handoff to its report —
what is done, what remains, what it learned — and stop; otherwise stop it. Then spawn a fresh role of the same kind
carrying the handoff path. A turnover is not an attempt. A second turnover on the same slice means the slice is too
large: have the segment's author re-cut it.

**The lead.** The lead keeps its own context small by construction — results of ten lines, reports by path, state on
disk — and handles the results that have arrived together in one turn rather than one turn each. On reaching its budget
it stops dispatching, records every result received, brings `plan.md` current, and asks the human caller to summarize
its context or start a fresh session on the program directory. Roles already in flight keep running meanwhile.

Where the harness exposes no context use, say so in the journal once and rely on slice size alone.

### On failure

Each failed build, verification, review round, or integration is one attempt. At the attempt cap, save the slice's
commit as the ref `held/<slice-id>`, reset the environment's branch to the integration line's tip so the environment is
free, mark the slice `held`, and ask: retry with the human caller's guidance, starting from the saved ref; have the
slice re-cut; or park it. That reset is the only one the run performs, and only on a commit the run made.

Parking is the human caller's answer, never the lead's default. A parked slice is recorded in the register with its ref
and attempt history, and every slice that depends on it is marked `parked` with that dependency as the reason.

## 6. Checkpoint

A segment's checkpoint is due when every one of its slices is `integrated` or `parked`. Run the following on the
integration environment and write the result to `checkpoints/`:

1. **The full gate.**
2. **Acceptance.** Spawn a `backend-verifier` — and a `frontend-verifier` where the segment has a browser surface — to
   exercise the segment's stated outcome from its requirements' acceptance bullets against the running system. It is
   given the requirements, not the slices or their tests.
3. **Drift and docs.** Execute [`../../review/process.md`](../../review/process.md) with
   `scope: {range: <previous checkpoint>..<integration tip>}` on the architecture axis, against the shared contracts and
   the backlog's engineering constraints, and on the context and documentation axes.
4. **What the segment taught.** Record in the checkpoint report what the build proved wrong in the contracts or in the
   plan for later segments, and the measured cost of the segment: slices, attempts, roles spawned, and elapsed time. The
   next segment's author receives this report.

Each blocking finding becomes a **repair slice**, written by the segment's author from the finding and run through step
5 before the next segment starts. Consider findings are listed in the report and go no further. The lead never changes
the integration line outside a slice.

Then evaluate the halt conditions, record the checkpoint in the journal, and bring `plan.md` current.

**Show the human caller.** A finished segment is a milestone for the human to try and to steer from. Present, in a few
lines: what now works and the exact commands to try it; what was parked or left open; what the segment cost; and the
segment proposed next, with any change to the remaining order the segment suggests. Ask whether to continue, adjust, or
stop. While waiting, start nothing of the next segment but its survey; take the next segment from step 3 once they
answer.

## 7. Close

When the terminal condition holds or the last segment's checkpoint has run, re-run that checkpoint after its repair
slices, at most twice; findings still open go under Gaps, and the final report's verdict is `incomplete`.

Return the final report: the verdict; per target repository, the integration line and its commit range; the slices
integrated and parked, by segment; the register in full; and each checkpoint's verdict and measured cost. State plainly
that nothing was pushed — delivery is the human caller's decision — and that the register is the list of what to review
first.

Write a retrospective titled "Ice age retrospective — \<program\>" to `<retrospectives-dir>/<yyyy-mm-dd>-<name>.md`,
resolved per [`../../artifact-storage.md`](../../artifact-storage.md), with the sections **What Went Well**, **What
Didn't Go Well**, **Harness / Context Improvements**, and **What We Skipped**.

## Halting

Asking is the default response to trouble; halting is for trouble that leaves nothing to dispatch. Halt, record why in
the journal, and report to the human caller when:

- the full gate is red on the integration line and one repair slice has not restored it;
- every slice of the segment that is not `integrated` or `parked` waits on an unanswered question;
- the parked share of the program's slices so far passes the charter's threshold (default one third);
- a segment's measured cost shows the remaining program cannot fit the budget the charter gives it;
- environments or a required runtime capability fail across the pool.

## Resuming

A session handed an existing program directory rebuilds its position before dispatching anything:

1. Read the charter. Without an `Approved:` line the run was never approved: return to step 1.
2. Read `plan.md` for the position and intent the last session recorded.
3. Read the ledger, `questions.md`, and the tail of the journal. Ask again every question still unanswered. A segment
   left `refining` restarts its refinement from the author, on whatever the last one wrote.
4. Reconcile the ledger with version control, which wins. Find slices by their `Slice:` trailer: one on the integration
   line is `integrated`; one on its environment's branch re-enters the loop at the stage after its last recorded state;
   a slice marked `building` with no trailer commit returns to `ready`, keeping its attempt count and its environment.
5. Run the slice gate on the integration line before building on it.
6. Record the resume in the journal, correct `plan.md` where reconciliation changed it, and continue from the first
   incomplete step.

An environment left with uncommitted work by an interrupted role is inspected, not reset: that work is handed to the
slice's next attempt as its starting point.
