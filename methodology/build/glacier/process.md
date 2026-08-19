# Glacier — process

Glacier drives one feature to completion on a single linear track: adopt or produce a plan, break it into ordered
phases, build and verify each phase one at a time, run a completion review over the uncommitted work, and write a
retrospective. It meets the shared definition of done for feature work owned by
[`../../completion.md`](../../completion.md) — the tested-and-docs-updated bar — for the feature it delivers: the tested
half is carried by closing every phase with the verify finale, and the docs-updated half by the completion review, which
spans the code, agent-facing, and public-docs axes over the uncommitted feature.

Glacier executes its coordination through the semantic operations in [`../../runtime-ports.md`](../../runtime-ports.md);
the executing session adapter resolves each operation for its harness. Every isolated-role invocation carries, before
its role-specific task, the one-shot default declared at
[`../../runtime-ports.md#spawn-an-isolated-role`](../../runtime-ports.md#spawn-an-isolated-role), scoped to this glacier
operation — the steps below call this "the isolated-role restrictions".

## Inputs

- **Feature or plan** — a feature description, named plan, refined work item, or inline plan; may initially be absent
  when a human caller is available to clarify it.
- **Work-target hint** (optional) — a feature environment, standalone repository, workspace branch, or path.
- **Documentation-root hint** (optional) — an existing planning or work-item directory.
- **Planning context** (when available) — the workspace's planning framework, verifiability matrix, and architecture
  guidance, handed to the planning process and the plan-review gate.
- **Human-caller channel** (required) — used for required planning approval, phase confirmation, environment gaps, and
  escalation decisions.

## Outputs

- The approved plan and phase record at `<documentation-root>/00-plan.md`.
- The feature implementation with every phase verified, left uncommitted for the human caller to commit.
- The automatic uncommitted delivery-review summary and, optionally, a closed review manifest.
- A retrospective at the location the retrospective step selects.

## 1. Frame the feature

Before any building, frame the feature in one or two sentences. If the supplied feature is not concrete, ask the human
caller once what the feature is and how completion will be recognized, then stop until they answer.

## 2. Resolve the work target

The work target is one of: a feature environment (spanning whichever of its repo worktrees the feature touches), a
standalone repository, or the workspace branch. Resolve it from the work-target hint or by asking the human caller.
Record it as absolute path(s) — every spawned agent works inside the target and never changes directory outside it.
Feature-environment work happens in the environment's repo worktrees, never in a source checkout under `projects/`.

## 3. Choose the documentation root

Work within the supplied or available planning framework, following its conventions for where plans, phases, and session
artifacts live and any plan-review gate it declares. When the workspace has no planning framework, gently suggest to the
human caller once that adopting one would help organization and observability, then proceed without blocking on it.

Decide the documentation root from how glacier was started: a work-item name or existing plan directory points there;
otherwise use the workflow artifact directory. Do not search for matching work items; create the directory if it does
not exist. The documentation root holds the plan and phase docs. When the feature arrived as a refined work item with
its own directory, use a `glacier/` subdirectory inside that item's directory; when the workspace has no planning
framework, resolve `<workflows-dir>` per [`../../artifact-storage.md`](../../artifact-storage.md) and use
`<workflows-dir>/<yyyy-mm-dd>-<name>/`, with `<name>` a short kebab-case slug derived from the feature.

## 4. Plan, gate, approve

Glacier owns the plan loop — author, gate, revise until convergence, then approve — composing the planning process
(which authors and revises the artifact) with the shared review process (which gates it). The plan axis owns what the
gate checks; glacier owns when the gate runs and the revision loop around it.

**Author.** Execute [`../../planning/process.md`](../../planning/process.md) with `feature_or_plan` set to the supplied
feature or plan, `plan_root` set to `<documentation-root>/00-plan.md` (or the planning framework's own plan location
when the framework supplied the documentation root), and `work_target` set to the recorded work-target path(s).
Glacier's planning targets the application's verifiability matrix and architecture guidance and is gated on both; treat
a missing matrix or missing guidance as a gap to surface to the human caller, never as something to invent around.

**Gate.** Execute the shared review process at [`../../review/process.md`](../../review/process.md) with the plan axis
([`../../review/axes/plan.md`](../../review/axes/plan.md)), scoped to the plan's directory or file, supplying the
work-target path(s) as the axis's work target. A planning framework that declares its own plan-review gate takes
precedence over the shipped plan axis; discover and invoke that gate from the runtime context rather than assuming a
particular agent, command, or file layout.

**Revise.** On must-fix findings, re-execute the planning process with `findings` set to the review report — its
revision step owns the shape of the fix, deletion first — escalate to the human caller any finding that needs a product
decision, then re-run the gate. Track per revision round the must-fix count and the plan's size: if the must-fix count
ever fails to strictly decrease, or three revision rounds pass without a clean verdict, stop the loop and escalate to
the human caller with the round history — counts, sizes, and unresolved findings. Rounds that produce plan mass instead
of a shrinking finding count signal a plan at the wrong altitude or a needed product decision, not a need for more
rounds.

**Approve.** Present the gated plan to the human caller and obtain approval before building; record the approved plan at
`<documentation-root>/00-plan.md`, superseding any pre-gate draft. Do not advance to building until the human caller
approves the plan, and an approval-time adjustment that changes the planned changes goes back through the plan gate
before building.

## 5. Break into phases

When the plan arrives already phased, adopt its phases; otherwise decompose the plan into ordered phases, each a
coherent, independently verifiable increment. Account for every surface the change owes — including surfaces outside the
code repo, such as a separate public-docs site — so each is a planned phase from the outset rather than something the
completion review catches later. Confirm the phase breakdown with the human caller, then write the confirmed phases into
`<documentation-root>/00-plan.md` alongside the plan.

Phases execute strictly in order: a phase starts only after the previous one passed verification, phases are never
reordered or run concurrently, and parallelism exists only inside a phase.

## 6. Build and verify each phase

Each phase runs a build-then-verify loop — implement with an ice-carver, close with the verify finale — with a hard cap
of three build-and-verify attempts per phase.

### Build

Spawn the canonical `ice-carver` role in a one-shot isolated context with workhorse model intent and await its result;
treat it as a full-stack engineer owning the phase's implementation across everything it touches, while runtime
verification belongs to the verify finale rather than the ice-carver. Each prompt is self-contained and carries:

- the isolated-role restrictions;
- the absolute work-target path(s);
- the phase goal plus a one-line feature framing;
- the path to `00-plan.md` for the full approach;
- for attempts after the first, the previous attempt's failing report verbatim, with instruction to address it
  specifically;
- the constraints to stay scoped to this phase, not start later phases, and not commit;
- the reporting requirement: files with line ranges changed plus a one-line summary.

When a phase's work divides into independent slices — disjoint files, no shared build artifact — you may spawn one
isolated ice-carver per slice as a single concurrent group; sequence slices that overlap, and when in doubt use one
ice-carver. A sliced phase still closes as one unit: await every slice's result, then run the verify finale once after
all slices have landed.

### Verify

To close a phase, spawn the canonical `verify-finale` role in a one-shot isolated context and await its result: it
verifies the change through a method declared in the application's verifiability matrix, builds a missing method (and
records its matrix row) when none covers the change rather than running an ad-hoc LLM pass, and fixes then re-verifies
until the method passes. Because the finale both verifies and fixes, its findings are not separately routed to an
ice-carver. Its prompt carries:

- the isolated-role restrictions;
- the absolute work-target path(s);
- for runtime verification, the base URL and port from `workspace:/context/project/project-setup.md` or the
  environment's computed variables via `winter env <env>`, asking the human caller when neither yields them;
- the phase goal and the ice-carver's reported change, so the finale knows what behavior to assert;
- the directive to verify through the matrix, build and record any missing method first, then fix what verification
  surfaces and re-verify until passing.

The one seam the finale cannot drive: when its runtime capabilities cannot perform a declared browser-driven matrix
method, spawn the canonical `frontend-verifier` role in a one-shot isolated context for that method — carrying the
isolated-role restrictions, the work-target path(s), the base URL/port, and the declared browser exercise — while the
finale closes everything else.

A phase passes only when its verification passes in full — the verify finale and any frontend-verifier split off for a
browser-driven method. A green build or type-check never counts as a test; phases close against runtime behavior.
Glacier does not start services: when verification needs services that are not running, the finale reports that
condition rather than guessing, and glacier tells the human caller to run `winter service up <env>` — the run phase per
`workspace:/context/environment-lifecycle.md` — and rerun the process.

### On failure

When the finale escalates something it cannot resolve in its own retries or that only the human can decide, or a
split-off frontend-verifier reports a failure (it only verifies and cannot fix), re-task the same phase: spawn a fresh
ice-carver at attempt plus one with the failing report folded into the attempt history, then re-run the finale. Do not
blindly re-spawn the finale or verifier against the same build.

When a phase has not passed full verification within three attempts, stop and escalate to the human caller: name the
phase, summarize each attempt in one line (what was built and what the finale or verifier reported), and ask how to
proceed. Never silently continue to later phases atop an unverified one.

## 7. Accumulate a review manifest (when wanted)

Accumulate a review manifest only when it is wanted: the human caller asked for one, or the change is large or
mechanical-heavy enough that a tiered review order will save a human real attention. Skip it for a small feature that
fits in a glance — the manifest only earns its keep on changes big enough that a human would otherwise stop reading.

Accumulate the manifest while building rather than fresh-classifying at the end: intent captured while fresh yields a
higher-fidelity manifest than any after-the-fact classification. Accumulation follows
[`../../review/manifest/build-time.md`](../../review/manifest/build-time.md):

- Each ice-carver additionally reports a `{tier, claim, intent}` line for every hunk it authored, because the builder
  knows its own intent in a way no fresh classifier can.
- After each phase, append that phase's ice-carver-reported entries to the manifest's JSON facts at its retained
  `<manifests-dir>/<date>-<slug>.json` path.
- The verify finale also authors hunks — its fixes and any verification method or matrix row it builds — but reports no
  tier line; those hunks are classified at the manifest's close against the settled diff, where total-coverage
  enforcement catches them.

## 8. Completion review

When every phase has passed, run the completion review automatically — without waiting for the human caller to ask and
without using the pre-push binding, because glacier's work is deliberately uncommitted: execute
[`../../delivery/review/process.md`](../../delivery/review/process.md) with scope `uncommitted` and mode `blocking`.

On blocking findings, spawn a fresh isolated ice-carver with workhorse model intent to resolve them without committing,
rerun the verification methods affected by its edits, then rerun the same uncommitted delivery review, repeating until
no blocking findings remain. When a finding cannot be resolved without a human decision, or an environment capability is
unavailable, stop and escalate with the finding ids and the blocker — do not claim the definition of done. Preserve
consider findings and any review gaps in the final summary; neither blocks completion.

An accumulated review manifest is closed only after the blocking-finding loop settles: bind the authored entries to the
settled diff, enforce total coverage, run the adversarial manifest-auditor over the cheap tiers, and render the markdown
document, all per the close-the-manifest section of
[`../../review/manifest/build-time.md`](../../review/manifest/build-time.md); surface the manifest's `.md` path
alongside the completion-review summary so the human caller has both the findings and the tiered review order.

Glacier never commits or pushes. Once blocking findings are resolved, return the implementation, verification evidence,
completion-review summary, and any advisory findings and gaps to the human caller.

## 9. Retrospective

Write a retrospective once the work is delivered or the human caller calls it done: a markdown document titled "Glacier
Retrospective — \<feature\>" carrying the date, a one-line feature statement, and the sections **What Went Well**,
**What Didn't Go Well**, **Harness / Context Improvements**, and **What We Skipped**.

Harness / Context Improvements is the point of the retrospective: concrete, actionable changes to the harness, tooling,
agent docs, or conventions that would make the next glacier run faster, more accurate, or more autonomous — including
noting any doc corrected mid-session. What We Skipped records untested paths, deferred work, and known gaps.

When a planning framework supplied the documentation root, the retrospective lives at
`<documentation-root>/retrospective.md`; otherwise resolve `<retrospectives-dir>` per
[`../../artifact-storage.md`](../../artifact-storage.md) and write `<retrospectives-dir>/<yyyy-mm-dd>-<name>.md`, using
the same `<name>` as the workflow document.
