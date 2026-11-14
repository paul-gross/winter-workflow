# Ice age — process

The ice-age executor is the program lead: it drives a **program** — a body of work too large for one plan, spanning many
epics and hundreds of changes — from a rough backlog to an integrated, verified result, with the human caller answering
questions as they arise rather than approving each step. It refines the backlog itself, cuts it into slices, builds a
foundation, fans the slices out across feature environments, lands every slice through one serialized integration gate,
and stops at checkpoints to prove the whole still holds. [`../index.md`](../index.md) owns how ice age routes against
the smaller build processes.

The lead orchestrates and never implements. It never edits a tracked file in any repository; every edit and commit goes
to an isolated role. Its own writes are the program directory, the retrospective, environment lifecycle commands, and
the two ref moves [Integrate](#integrate) and [On failure](#on-failure) name.

The lead reads results, not work. Every isolated role writes its full report to
`<program-dir>/reports/<slice-or-area>/<stage>-<attempt>.md` and returns at most ten lines: verdict, commit, counts, and
the report path. A role that needs an earlier report receives its path, not its text.

Ice age meets the shared definition of done owned by [`../../completion.md`](../../completion.md) per slice — the tested
half through the verify finale, the docs-updated half through the slice review — and again per checkpoint for the
program as a whole.

Ice age executes its coordination through the semantic operations in [`../../runtime-ports.md`](../../runtime-ports.md).
Every isolated-role invocation carries, before its role-specific task, the one-shot default declared at
[`../../runtime-ports.md#spawn-an-isolated-role`](../../runtime-ports.md#spawn-an-isolated-role), scoped to this ice-age
operation — the steps below call this "the isolated-role restrictions".

## Inputs

- **Program** — the goal and its backlog: a planning-repository project, a set of epics, or a bare description.
- **Reference implementation** (optional) — an existing system the program replaces or must match, with its tests and
  documentation.
- **Target hints** (optional) — the code repositories the program changes, the planning repository, and the branch each
  starts from.
- **Environment pool** (optional) — feature environments the run may use.
- **Model policy** (optional) — a model intent per role, or one intent bound to every role.
- **Human-caller channel** (required) — used for the charter approval, the questions of [Asking](#asking), a halt, and
  the final report.

## The program directory

Resolve `<workflows-dir>` per [`../../artifact-storage.md`](../../artifact-storage.md) and keep the run's state in
`<program-dir>`, which is `<workflows-dir>/<yyyy-mm-dd>-<name>/` with `<name>` a short kebab-case slug for the program.
An existing program directory named by the caller means resume: go to [Resuming](#resuming) rather than step 1.

| File            | Holds                                                                                                    |
| --------------- | -------------------------------------------------------------------------------------------------------- |
| `charter.md`    | The charter from step 1; approved only once it carries an `Approved: <date>` line                        |
| `plan.md`       | The whole program at a glance — see below                                                                |
| `refinement.md` | One row per epic and refinement pass: state and revise count                                             |
| `ledger.md`     | One row per slice: id, epic, milestone, depends-on, environment, state, attempts, queue position, commit |
| `register.md`   | Everything decided without the human, for review afterwards — see below                                  |
| `questions.md`  | One row per question for the human caller: id, what it blocks, the options, state, and the answer        |
| `journal.md`    | Append-only, one line per event: dispatch, result, integration, park, checkpoint, halt, resume           |
| `survey/`       | The survey's inventories, one file per area                                                              |
| `reports/`      | Every isolated role's full report                                                                        |
| `checkpoints/`  | One report per checkpoint, numbered in order and named for its boundary                                  |

A slice's state is one of `planned`, `ready`, `building`, `built`, `verified`, `reviewed`, `queued`, `integrated`,
`held`, or `parked`. Write the `ledger.md` or `refinement.md` row before dispatching the work it describes and again
when the result arrives.

The register has four sections, each entry one line with the id it concerns:

- **Decisions made** — every open decision settled under the charter's policy, with the rule that settled it.
- **Deviations** — every place the result deliberately differs from the reference implementation or from the backlog as
  it stood.
- **Parked** — every slice or epic set aside, with its blocker and, for a slice, the ref holding its work.
- **Gaps** — every surface no slice's acceptance checks cover, and every checkpoint finding left open at close.

`plan.md` is the holistic plan, short enough to read in one pass: the process's steps with each one's state; each
milestone with its slices counted by state; what is in flight and in which environment; the questions outstanding; and
the next three moves the lead intends. Bring it current at every step transition, every checkpoint, and before every
batch of questions. It summarizes the other files and never holds a fact they lack.

The lead is ready to have its context summarized, or to hand over to a fresh session, whenever the human caller asks. On
that request: record every result already received, bring `plan.md` current, and say the run is ready. After every
checkpoint, and whenever earlier context has been summarized, re-read this process and execute [Resuming](#resuming)
before the next dispatch.

## 1. Charter

The charter settles only what the run cannot start without; everything else is asked when it arises, per
[Asking](#asking). Draft the charter, present it, and stop until the human caller approves it; write the
`Approved: <date>` line only after they answer. It states:

- **The program** — the goal in two or three sentences, the terminal condition that ends the run, and what is out of
  scope.
- **Targets** — each target repository, the planning repository, and the **integration line**: one local branch per
  target repository that every slice lands on. Reserve one **integration environment** whose worktrees hold the
  integration line checked out. No slice is built there; the planning repository's refinement happens there.
- **The pool** — the environments slices may be built in and the resulting parallel width. Resolve it as flurry does at
  [`../flurry/process.md`](../flurry/process.md#3-allocate-environments), with one difference: creating environments is
  approved here, once, for the whole run.
- **The decision policy** — which open decisions the lead settles without asking, as an ordered rule list. The default:
  a binding constraint settles it; otherwise the reference implementation's observable behavior is the answer. A
  decision neither rule settles is asked.
- **The gates** — three commands, each naming what it runs: a **bootstrap gate** (build plus whatever tests exist) used
  until the foundation's gate slice integrates; a **slice gate** of bounded runtime, run on every integration; and a
  **full gate**, run at checkpoints.
- **The model policy** — the model intent for each role. The default is workhorse intent for `ice-carver` and judgment
  intent for every other role; a policy binding one intent to every role, such as **frontier** (Fable/Astra class) for
  the whole run, overrides each role's default at every spawn.
- **Budgets** — the attempt cap per slice (default three), the revise cap per refinement gate (default two), the context
  budgets for a role and for the lead, and the halt conditions of [Halting](#halting).

A change to the charter mid-run is an amendment: ask it as a question, and record the answer in the charter.

## Asking

The human caller is available throughout and expects to be asked. Ask when:

- an open decision is not settled by the charter's decision policy;
- a deviation from the reference implementation is proposed that the backlog does not already call for;
- a slice reaches the attempt cap, or an epic reaches the revise cap;
- a checkpoint's acceptance or drift finding is a matter of intent rather than a defect;
- the charter needs amending.

Asking never idles the run:

1. Record the question in `questions.md` and mark what it blocks `held` — a slice in the ledger, an epic's pass in
   `refinement.md`. Everything depending on a held item waits; nothing else does.
2. Dispatch every piece of work that does not depend on the answer.
3. Then ask, batching the questions that have accumulated. Each states what it blocks, the options, and the one the lead
   recommends with its reason, so it can be answered in a tap.
4. On the answer, record it in `questions.md`, have it written where it belongs — a decision goes into the planning
   repository's decision format through step 3's roles, naming the human caller as decider — and release what was held.

A question is never answered by the lead on the human's behalf, and a held item is never built around.

## 2. Survey

Skip this step when the program has neither a reference implementation nor existing code to build on.

Divide the reference implementation into disjoint areas and spawn one `arctic-explorer` per area as a concurrent group.
Each carries the isolated-role restrictions and the rule to write nothing in the reference implementation; it writes its
inventory to `<program-dir>/survey/<area>.md` — observable capabilities by entrypoint, input, output, exit behavior,
refusal, and side effect, each row with an evidence anchor naming the source location and the test that pins it.

When the backlog already carries an inventory, the explorers are not given it. Afterwards spawn one `plan-reviewer` with
both and have it report what the backlog misses, misstates, or assigns to the wrong owner.

## 3. Refine the backlog

Refinement runs as the ordered passes below, in the planning repository's worktree of the integration environment. The
workspace's planning framework owns what each artifact holds and the rubric its gate applies; ice age owns the order and
the roles. When the workspace has no planning framework, the same layers live under `<program-dir>/backlog/`, shaped per
[`../../planning/plan-shape.md`](../../planning/plan-shape.md), and the per-pass commit is skipped.

Every pass has the same three roles:

- **Author** — `winter-architect`, carrying the isolated-role restrictions, the planning framework's rules for the
  artifact, and the survey paths. It writes files and commits nothing. In a concurrent pass each author writes only
  inside its own epic's folder and returns the changes it needs in shared files; one further author applies those
  serially.
- **Gate** — a fresh `plan-reviewer` that authored nothing in the pass, applying the planning framework's rubric for the
  artifact, or the framework's own gate when it declares one.
- **Committer** — once a pass's gates have settled, one `ice-carver` runs the planning repository's own checks and makes
  the pass's commit, unpushed.

1. **Intent.** Correct the epics and requirements against the survey and the charter: add what is missing, fix what is
   wrong, merge duplicates, move what is mis-owned, and mark out of scope what the charter excludes. Concurrent per
   epic.
2. **Decisions.** Apply the charter's decision policy to every open decision blocking an in-scope epic. A decision the
   policy settles is recorded as made in the planning repository's decision format; the author returns one register line
   per decision. Every other decision is asked, and the epics it blocks are `held` until it is answered.
3. **Shared contracts.** One author, serially, writes the contracts more than one epic stands on — the command or
   interface surface, the configuration model, result and error types, output formats, extension seams. This pass is
   never fanned out.
4. **Specs.** One spec per epic, concurrent, each citing the shared contracts rather than restating them.
5. **Slices.** Cut each epic into slices, concurrent: each slice one mergeable change with acceptance checks a test can
   verify, its dependencies declared, and the milestone it serves.
6. **Reconciliation.** One fresh `plan-reviewer` reads every slice and contract together and reports dependency cycles,
   requirements no slice delivers, contracts two specs disagree on, and files many slices will contend for. Route each
   finding back to the pass that owns it.

A gate that fails sends its report to a fresh author for one revision, bounded by the revise cap. An epic still failing
at the cap is `held` and asked about, with its blocking findings; the program continues without it meanwhile.

## 4. Build the graph

Have one isolated `plan-reviewer` read the committed slices and write the ledger's rows: each slice's dependencies taken
from the slices themselves and from the epic-to-epic dependencies the backlog declares, where depending on an epic means
depending on its last slice. Parked epics contribute no rows.

- **The foundation** is every slice the rest of the program stands on: the project skeleton and its composition seam,
  the test harness, the slice gate and full gate, the contributor context and verifiability matrix that builders read,
  and — when a reference implementation exists — a differential method that runs the reference and the new system
  against the same input and compares what a user can observe. The gate slice comes first.
- **Every other slice** becomes `ready` when everything it depends on is `integrated`.
- **A checkpoint** belongs to each milestone the backlog names, or to each quarter of the ledger when it names none.

## 5. Lay the foundation

Run the foundation in one environment, through the slice loop of step 6, strictly in order. Until the gate slice
integrates, [Integrate](#integrate) runs the bootstrap gate in place of the slice gate. Dispatch nothing else until the
foundation is integrated and the full gate runs green on the integration line.

A foundation slice cannot be parked: at the attempt cap its question offers only retry and re-cut.

## 6. Run the slices

Keep every pool environment busy: whenever one is free, assign it the first `ready` slice in ledger order whose files do
not overlap a slice in flight — when unsure whether two overlap, do not run them together. Dispatch all assignments made
at once as one concurrent group. An environment holds one slice from assignment until that slice is `integrated`,
`held`, or `parked`.

Before an environment's first slice, provision it per the workspace's environment lifecycle. Before every slice, bring
the environment's branch to the integration line's tip by fast-forward. An environment that cannot fast-forward holds
work the run does not own: withdraw it from the pool and record it rather than resetting anything.

**The slice's commit** is the single commit on the environment's branch above the integration line's tip, in each target
repository the slice changes. Its message follows
[`../../delivery/commit/conventions.md`](../../delivery/commit/conventions.md) and ends with a `Slice: <id>` trailer.
Every later role in the loop — a retry, the verify finale, a review fix — amends that commit rather than adding one, and
nothing is pushed.

### Build

Spawn the canonical `ice-carver` role in a one-shot isolated context. Its prompt carries the isolated-role restrictions;
the environment pin, with the rule to work only inside that environment's worktrees; the slice file and the spec
sections and contracts it cites, by path; for a later attempt, the path of the previous failing report; the commit rule
above; and the reporting requirement — files changed, the commit, and which acceptance checks it believes it met.

A builder that finds the slice wrong — a contract that cannot be implemented as written, a missing dependency — reports
that instead of improvising. Route the report to step 3's owning pass through its author, gate, and committer, then
retry the slice against the corrected text.

### Verify

Spawn the canonical `verify-finale` role in a one-shot isolated context, carrying the isolated-role restrictions, the
environment pin, the slice's acceptance checks, and the builder's report path. It verifies each acceptance check through
a method the application's verifiability matrix declares — the differential method wherever the slice ports reference
behavior — building and recording a missing method rather than improvising one.

A slice is `verified` only when every acceptance check ran and passed. A check that could not run is a failed attempt,
never a gap.

### Review

For each target repository the slice changes, execute [`../../review/process.md`](../../review/process.md) with
`execution_mode: fresh` and `scope: {range: <integration tip>..<environment branch>}`, on the code axis and on the
context and documentation axes when the slice touches those surfaces, as one concurrent group. On blocking findings,
spawn a fresh `ice-carver` to resolve them, re-run the affected verification, and re-run the review. Consider findings
stay in the report.

A review that returns no reviewed target is a failed attempt, never a pass.

### Integrate

Integration is serialized across the whole program: one slice at a time, in the order slices became `reviewed`. Record
that order in the ledger's queue position when marking a slice `queued`.

For the slice at the head of the queue, spawn an isolated `ice-carver` pinned to the slice's environment to rebase the
environment's branch onto the integration line and run the slice gate there. It aborts a rebase it cannot settle
mechanically and reports the conflict.

On green, the lead fast-forwards the integration line to the environment's branch from the integration environment's
worktree — a fast-forward-only merge, the lead's one routine ref move — and marks the slice `integrated` with its
commit. A conflict or a red gate is a failed attempt. A slice is never integrated on a gate run that predates its
rebase.

### Context budget

A large context re-read on every small turn is the run's most avoidable cost, so the charter sets two budgets: one for
each isolated role and a lower one for the lead, whose turns are many and small.

**Roles.** Where the harness exposes a running role's context use, the lead reads it for every role in flight on each
turn it already takes — it never takes a turn only to poll. A role past its budget is turned over, not left to grow: ask
it, where the harness can address a running role, to commit or leave its work in place, write a handoff to its report —
what is done, what remains, what it learned — and stop; otherwise stop it. Then spawn a fresh role of the same kind
carrying the handoff path. A turnover is not an attempt. A second turnover on the same slice means the slice is too
large: send it back to step 3 to be re-cut.

**The lead.** The lead keeps its own context small by construction — results of ten lines, reports by path, state on
disk — and handles the results that have arrived together in one turn rather than one turn each. On reaching its budget
it stops dispatching, records every result received, brings `plan.md` current, and asks the human caller to summarize
its context or start a fresh session on the program directory. Roles already in flight keep running meanwhile.

Where the harness exposes no context use, say so in the journal once and rely on slice size alone.

### On failure

Each failed build, verification, review round, or integration is one attempt. At the attempt cap, save the slice's
commit as the ref `held/<slice-id>`, reset the environment's branch to the integration line's tip so the environment is
free, mark the slice `held`, and ask: retry with the human caller's guidance, starting from the saved ref; send the
slice back to step 3 to be re-cut; or park it. That reset is the only one the run performs, and only on a commit the run
made.

Parking is the human caller's answer, never the lead's default. A parked slice is recorded in the register with its ref
and attempt history, and every slice that depends on it is marked `parked` with that dependency as the reason.

## 7. Checkpoint

A checkpoint is due when every slice of its milestone is `integrated` or `parked`. Let slices in flight finish, dispatch
nothing new, then run the following on the integration environment and write the result to `checkpoints/`:

1. **The full gate.**
2. **Acceptance of the boundary.** Spawn a `backend-verifier` — and a `frontend-verifier` where the program has a
   browser surface — to exercise the milestone's stated outcome from its requirements' acceptance bullets against the
   running system. It is given the requirements, not the slices or their tests.
3. **Drift.** Execute [`../../review/process.md`](../../review/process.md) on the architecture axis with
   `scope: {range: <previous checkpoint>..<integration tip>}`, against the shared contracts and the backlog's
   engineering constraints.
4. **Backlog reconciliation.** Where the build proved a spec or contract wrong, have it corrected in place and the
   affected remaining slices re-cut, through step 3's roles; un-park whatever a since-made decision or repaired
   dependency unblocks; record each epic's progress in the form the planning framework allows short of delivery.

Each blocking finding becomes a **repair slice**: step 3's slice author writes its file from the finding, its gate
passes it, and it enters the ledger ahead of every `ready` slice and runs through the same loop. Consider findings are
listed in the checkpoint report and go no further. The lead never changes the integration line outside a slice.

Then evaluate the halt conditions, record the checkpoint in the journal, and resume dispatching.

## 8. Close

When the terminal condition holds or nothing unparked remains, run a final checkpoint over the terminal milestone. Run
its repair slices and re-run the checkpoint, at most twice; findings still open go under Gaps, and the final report's
verdict is `incomplete`.

Return the final report: the verdict; per target repository, the integration line and its commit range; the slices
integrated and parked, by epic; the register in full; and each checkpoint's verdict. State plainly that nothing was
pushed — delivery is the human caller's decision — and that the register is the list of what to review first.

Write a retrospective titled "Ice age retrospective — \<program\>" to `<retrospectives-dir>/<yyyy-mm-dd>-<name>.md`,
resolved per [`../../artifact-storage.md`](../../artifact-storage.md), with the sections **What Went Well**, **What
Didn't Go Well**, **Harness / Context Improvements**, and **What We Skipped**.

## Halting

Asking is the default response to trouble; halting is for trouble that leaves nothing to dispatch. Halt, record why in
the journal, and report to the human caller when:

- the full gate is red on the integration line and one repair slice has not restored it;
- every slice that is not `integrated` or `parked` waits on an unanswered question;
- the parked share of in-scope epics, or of slices, passes the charter's threshold (default one third);
- environments or a required runtime capability fail across the pool.

## Resuming

A session handed an existing program directory rebuilds its position before dispatching anything:

1. Read the charter. Without an `Approved:` line the run was never approved: return to step 1.
2. Read `plan.md` for the position and intent the last session recorded.
3. Read `refinement.md`, the ledger, `questions.md`, and the tail of the journal. Ask again every question still
   unanswered. A refinement row left mid-pass restarts that pass for that epic from its author, keeping its revise
   count.
4. Reconcile the ledger with version control, which wins. Find slices by their `Slice:` trailer: one on the integration
   line is `integrated`; one on its environment's branch re-enters the loop at the stage after its last recorded state;
   a slice marked `building` with no trailer commit returns to `ready`, keeping its attempt count and its environment.
5. Run the slice gate on the integration line before building on it.
6. Record the resume in the journal, correct `plan.md` where reconciliation changed it, and continue from the first
   incomplete step.

An environment left with uncommitted work by an interrupted role is inspected, not reset: that work is handed to the
slice's next attempt as its starting point.
