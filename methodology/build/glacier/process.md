# Glacier

## Inputs

- **Feature or plan** — a feature description, named plan, refined work item, or inline plan; it may initially be absent when a human caller is available to clarify it.
- **Work-target hint** — optional feature environment, standalone repository, workspace branch, or path.
- **Documentation-root hint** — optional existing planning or work-item directory.
- **Planning context** — the workspace's planning framework, plan-review gate, verifiability matrix, and architecture guidance when available.
- **Human-caller channel** — available for required planning approval, phase confirmation, environment gaps, and escalation decisions.

## Outputs

- An approved plan and phase record at `<documentation-root>/00-plan.md`.
- The feature implementation, with every phase verified, left uncommitted for the human caller.
- The automatic uncommitted delivery-review summary and an optional closed review manifest.
- A retrospective at the location selected in step 6.

Drive one feature to completion on a single linear track: adopt or produce a plan, break it into ordered phases, build-and-verify each phase one at a time, run a completion review over the uncommitted work, and write a retrospective. Use the semantic operations in [`../../runtime-ports.md`](../../runtime-ports.md); the executing session adapter resolves canonical roles, model intent, concurrency, human interaction, and result channels for its harness.

Planning targets the application's **verifiability matrix** and **architecture guidance** and is gated on both (step 2); each phase is then closed by the tool-building **verify finale** (step 4), which verifies through a method declared in the matrix and builds a missing one rather than improvising.

## Definition of done

Glacier meets the shared **Definition of done for feature work** ([`../../completion.md`](../../completion.md)) — the tested-and-docs-updated bar — for the feature it delivers. Two mechanisms carry it:

- **Tested** — each phase is closed by the **verify finale** (step 4b), which verifies the phase's change through a method declared in the application's verifiability matrix, building the method (and recording its matrix row) when none exists rather than running an ad-hoc LLM pass. A green build or type-check is not a test.
- **Docs updated** — the **completion review** (step 5) spans the code, agent-facing, and public-docs axes over the uncommitted feature before completion.

Do not advance past a phase until its verify finale has passed.

Work within the supplied or available planning framework — its conventions for where plans, phases, and session artifacts live, and its **plan-review gate** (step 2). If no planning framework exists, gently suggest to the human caller that adopting one would help with organization and observability, then proceed: produce the plan with a `winter-architect`, treat a missing verifiability matrix or architecture guidance as a gap to surface rather than invent around, and track the work in your winter space (see step 1).

## Isolated-role restrictions

Every isolated role invocation carries, before its role-specific task, the one-shot default declared by [`../../runtime-ports.md`](../../runtime-ports.md#spawn-an-isolated-role), scoped to this Glacier operation. The steps below refer to it as **the isolated-role restrictions**.

## Steps

### 1. Frame the feature, work target, and documentation root

Establish three things before any building:

- **The feature** — one or two sentences from the supplied feature or plan. If it is not concrete, ask the human caller once what the feature is and how you'll know it's done, then stop until they answer.
- **The work target** — one of: a **feature environment** (e.g. `beta/`, across whichever of its repo worktrees the feature touches), a **standalone repository**, or the **workspace branch** itself. Determine it from the supplied work-target hint ("on beta", a repo name, a path) or ask the human caller. Record the **absolute path(s)**; spawned agents work within the target and never `cd` outside it. For feature-environment work, use the env's repo worktrees — never fall back to a source checkout under `projects/`.
- **The documentation root** — where the plan and phase docs live. Follow the workspace's planning-framework conventions: if the feature came in as a refined work item with its own directory, write a `glacier/` subdirectory inside it. If the workspace has no planning framework, resolve `<workflows-dir>` under [`../../artifact-storage.md`](../../artifact-storage.md) and use `<workflows-dir>/<yyyy-mm-dd>-<name>/` (short kebab-case `<name>` from the feature). Decide from how glacier was started — a work-item name or an existing plan directory points there, otherwise use the workflow artifact directory; don't search for matching items. Create the directory if it doesn't exist.

### 2. Establish the plan

Glacier's plan targets two artifacts the application's harness declares — its **verifiability matrix** (how the application's changes are asserted correct) and its **architecture guidance** (how its code must be shaped) — and is gated on both before any building. Run a single **plan-review gate** over the plan, checking two things: the **verifiability gate** (every planned change maps to a verification method, or schedules the work to build a missing one) and the **architecture gate** (the plan conforms to the application's architecture guidance). The workspace's planning framework provides this gate and the plan builder that authors a plan; discover and invoke them from the runtime context rather than assuming a particular agent, command, or file layout.

**Given** the supplied input includes a plan — a refined work item with its own directory, or one stated inline — put it through the plan-review gate before adopting it. **Verdict clean (no must-fix)** → adopt it. **Must-fix findings** → route them back to the plan builder (or, with no framework, resolve them with the human caller) and re-review until clean.

**Otherwise** — produce one. With a planning framework, run its **plan builder** in an isolated context to author the plan against the verifiability matrix and architecture guidance, then run the plan-review gate, routing must-fix findings back until clean. With **no** planning framework, spawn the canonical `winter-architect` role in a one-shot isolated context (isolated-role restrictions + feature + work-target path(s); ask it to read the relevant code and return an implementation approach, not to write code), naming each change's verification method and architectural fit as far as the application's harness declares them and surfacing a missing matrix or architecture guidance as a gap rather than inventing around it. If the plan builder needs the codebase explored, spawn an isolated `arctic-explorer` (isolated-role restrictions + the research question), await its result, and hand the distilled finding to the builder rather than reading the code into your own context.

Either way, **present the plan to the human caller and get approval before building.** Write the approved plan to `<documentation-root>/00-plan.md` so the session has a record. Do not advance until the human caller approves or adjusts it.

### 3. Establish the phases

**Given** the plan is already phased (provided or written that way) — adopt those phases.

**Otherwise** — decompose the plan into ordered phases, each a coherent, independently verifiable increment. A feature delivery spans more than the code repo — when you break the work down, account for every surface the change owes, including any that lives outside the code (such as a separate public-docs site), so each is a planned phase from the outset rather than a completion-review catch. **Confirm the phase breakdown with the human caller** through the human-caller port. Write the confirmed phases to `<documentation-root>/00-plan.md` alongside the plan.

**Phases execute strictly in order.** A phase starts only after the previous one has passed verification (step 4). Do not reorder phases or run two phases at once — parallelism lives *inside* a phase (step 4a), never across phases.

### 4. Per-phase build-and-verify loop (hard cap: 3 attempts per phase)

For each phase, in order, **build it with an `ice-carver`, then close it with the verify finale**. Allow up to three build→verify attempts per phase.

#### 4a. Run the ice-carver (implement the phase)

Spawn the canonical `ice-carver` role in a one-shot isolated context with workhorse model intent and await its result. Treat this ice-carver as a full-stack engineer who owns the phase's implementation across whatever it touches (backend, frontend, data, CLI); runtime verification is the finale's job (4b), not the ice-carver's.

When a phase's work splits into **independent slices** — disjoint files, no shared build artifact — you may spawn one isolated `ice-carver` per slice as one concurrent group instead of a single ice-carver. Sequence slices that overlap; when in doubt, use one ice-carver. The phase still closes as one unit: await every slice result, then run the verify finale (4b) once after every slice has landed.

Each ice-carver's self-contained prompt carries:

1. **The isolated-role restrictions**.
2. **Work-target path(s)** (absolute).
3. **Phase goal** — this phase's increment, plus the one-line feature framing for context.
4. **Plan reference** — the path to `00-plan.md` so the ice-carver can read the full approach.
5. **Attempt history** — for attempt > 1, the previous attempt's failing report verbatim (the verify finale's escalation and/or the `frontend-verifier`'s findings); tell the ice-carver to address it specifically.
6. **Constraints** — keep the change scoped to this phase; do not start on later phases; do not commit. A green build or type-check is not the bar — the verify finale closes the phase against runtime behavior.
7. **Reporting** — files + line ranges changed; a one-line summary. **If accumulating a review manifest** (see *Review manifest* below), also have the ice-carver report, for each hunk it authored, a `{tier, claim, intent}` line per [`../../review/manifest/build-time.md`](../../review/manifest/build-time.md) — it knows its own intent, which a fresh classifier never could.

#### 4b. Run the verify finale (close the phase)

Spawn the canonical `verify-finale` role in a one-shot isolated context and await its result. It closes the phase by verifying the change through a method declared in the application's verifiability matrix, **building a missing method** (and recording its matrix row) when none covers the change rather than running an ad-hoc LLM pass, and **fixing and re-verifying** until the method passes. Supply:

1. **The isolated-role restrictions**.
2. **Work-target path(s)** (absolute); for runtime verification, the base URL/port from `workspace:/context/project/project-setup.md` or the env's computed vars (`winter env <env>`) — ask the human caller if neither yields them.
3. **Phase context** — the phase goal and the ice-carver's reported change, so the finale knows what behavior to assert.
4. **What to do** — verify the phase through the verifiability matrix, building and recording a missing method before verifying, then fix what verification surfaces and re-verify until it passes.

The finale both verifies and fixes, so you do not separately route its findings to an ice-carver. **The one seam it can't drive:** when its runtime capabilities cannot perform a declared browser-driven matrix method, spawn the canonical `frontend-verifier` role in a one-shot isolated context for that method (isolated-role restrictions + work-target path(s) + the base URL/port from `workspace:/context/project/project-setup.md` or `winter env <env>` + the declared browser exercise) and let the finale close everything else.

If services aren't running and verification needs them, the finale should say so rather than guess — glacier does not start services. Tell the human caller to run `./up` (or the project equivalent per `workspace:/context/project/project-setup.md`) and rerun the process.

#### 4c. Gate and cap

A phase passes only when its verification passes in full — the verify finale, **and** any `frontend-verifier` split off for a browser-driven method (4b). Branch on the combined result:

- **Verification passes** (the finale passed, and any split-off `frontend-verifier` also passed) → advance to the next phase, or to step 5 if this was the last phase.
- **Verification fails** — the finale escalates (a failure it can't resolve in its own retries, or a gap only the human caller can decide), **or** a split-off `frontend-verifier` reports a failure (it verifies only; it cannot fix what it finds) → re-task the same phase: spawn a fresh `ice-carver` (attempt + 1) with the failing report folded into the attempt history (the finale's escalation and/or the `frontend-verifier`'s findings), then re-run 4b. Don't re-spawn the finale or verifier blindly on the same build.
- **Cap** — if a phase hasn't passed its full verification in three attempts, **stop and escalate to the human caller**: name the phase, summarize each attempt in one line (what was built, what the finale or verifier reported), and ask how to proceed. Do not silently continue to later phases on an unverified one.

### Review manifest (optional — capture intent while building)

When a review manifest is wanted for this feature — the human caller asked for one, or the change is large or mechanical-heavy enough that a tiered review order will save a human real attention — **accumulate it as you build** rather than fresh-classifying at the end. The builder knows *why* each hunk exists; capturing that intent while it is fresh produces a higher-fidelity manifest than any after-the-fact classification.

Follow [`../../review/manifest/build-time.md`](../../review/manifest/build-time.md): each phase's `ice-carver` reports the `{tier, claim, intent}` for the hunks it authored (step 4a, item 7); after each phase you append those entries to the manifest's JSON facts at its retained `<manifests-dir>/<date>-<slug>.json` path. The verify finale also authors hunks (its fixes, and any verification method or matrix row it builds) but reports no tier line — those are classified at the **close** step against the settled diff, where total-coverage enforcement catches them. You **close** the manifest at step 5 (below). Skip all of this for a small feature that fits in a glance — the manifest earns its keep only on a change big enough that a human would otherwise stop reading.

### 5. Completion review

When every phase has passed, review the work automatically — do not wait for the human caller to ask and do not use the pre-push binding. Glacier's work is deliberately uncommitted, so execute [`../../delivery/review/process.md`](../../delivery/review/process.md) with `scope: uncommitted` and `mode: blocking`.

If the result contains blocking findings, spawn a fresh isolated `ice-carver` with workhorse model intent to resolve them without committing, rerun the verification methods affected by its edits, then rerun the same uncommitted delivery review. Continue until the review returns no blocking findings. If a finding cannot be resolved without a human decision or an environment capability is unavailable, stop and escalate with the finding ids and blocker; do not claim the Definition of Done. Preserve `consider` findings in the final summary, but they do not block completion.

**If you accumulated a review manifest** (above), **close it only after the blocking-finding loop settles**: bind the authored entries to the settled diff, enforce total coverage, run the adversarial `manifest-auditor` over the cheap tiers, and render the markdown document — all per [`../../review/manifest/build-time.md`](../../review/manifest/build-time.md) §"Close the manifest". Surface the manifest's `.md` path alongside the completion-review summary, so the human caller has both the cross-axis findings and the tiered review order.

Do not commit or push. Once blocking findings are resolved, return the implementation, verification evidence, completion-review summary, and any advisory findings to the human caller.

### 6. Retrospective

Once the work is delivered (or the human caller calls it done), write a retrospective. When a planning framework supplied the documentation root, write it there as `<documentation-root>/retrospective.md`. Otherwise resolve `<retrospectives-dir>` under [`../../artifact-storage.md`](../../artifact-storage.md) and write `<retrospectives-dir>/<yyyy-mm-dd>-<name>.md` (same `<name>` as the workflow doc). Either way the structure is:

```markdown
# Glacier Retrospective — <feature>
## Date: YYYY-MM-DD
## Feature: <one line>

## What Went Well

## What Didn't Go Well

## Harness / Context Improvements
<concrete, actionable changes to the harness, tooling, agent docs, or conventions
that would make the next glacier run faster, more accurate, or more autonomous —
e.g. a stale doc you corrected, a verification probe that should be documented, a
missing convention. This section is the point of the retrospective.>

## What We Skipped
<untested paths, deferred work, known gaps>
```

Keep it honest and specific — the **Harness / Context Improvements** section is what feeds the next run. If you corrected a doc mid-session, note it here too.
