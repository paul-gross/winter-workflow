---
description: Drive one feature to completion methodically on a single linear track, one ordered phase at a time. Use to build a feature step by step rather than all at once.
argument-hint: "[plan name or feature description]"
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, Agent, AskUserQuestion, Skill
---

# Glacier

Drive one feature to completion on a single linear track: adopt or produce a plan, break it into ordered phases, build-and-verify each phase one at a time, run a pre-push review, and write a retrospective. You spawn one role-pure subagent at a time (see [`winter-workflow:/agents/README.md`](winter-workflow:/agents/README.md)) and gate each handoff yourself.

Planning targets the application's **verifiability matrix** and **architecture guidance** and is gated on both (step 2); each phase is then closed by the tool-building **verify finale** (step 4), which verifies through a method declared in the matrix and builds a missing one rather than improvising.

## Definition of done

Glacier meets the shared **Definition of done for feature work** ([`winter-workflow:/context/definition-of-done.md`](winter-workflow:/context/definition-of-done.md)) — the tested-and-docs-updated bar — for the feature it delivers. Two mechanisms carry it:

- **Tested** — each phase is closed by the **verify finale** (step 4b), which verifies the phase's change through a method declared in the application's verifiability matrix, building the method (and recording its matrix row) when none exists rather than running an ad-hoc LLM pass. A green build or type-check is not a test.
- **Docs updated** — the **pre-push review** (step 5) spans the code, agent-facing, and public-docs axes before delivery.

Do not advance past a phase until its verify finale has passed.

Work within the planning framework you are given or that is available to you — its conventions for where plans, phases, and session artifacts live, and its **plan-review gate** (step 2). If no planning framework exists, gently suggest to the user that adopting one would help with organization and observability, then proceed: produce the plan with an `architect`, treat a missing verifiability matrix or architecture guidance as a gap to surface rather than invent around, and track the work in your winter space (see step 1).

## Coordination preamble (shared)

Every spawn prompt must begin with this preamble, prepended verbatim before the role-specific task content. It tells the role-pure agent it is operating one-shot with no team:

> You are operating as a one-shot agent spawned by the `glacier` skill. No shared task list exists. Report results to the skill via your final response only — do not call `SendMessage`, `TaskCreate`, or `TaskUpdate`. When your task is done, stop.

The steps below reference this section as **"the coordination preamble"**; do not paraphrase — paste it verbatim.

## Steps

### 1. Frame the feature, work target, and documentation root

Establish three things before any building:

- **The feature** — one or two sentences. Source: `$ARGUMENTS`, a named plan, or the user's most recent description. If none yields something concrete, ask the user once what the feature is and how you'll know it's done, then stop until they answer.
- **The work target** — one of: a **feature environment** (e.g. `beta/`, across whichever of its repo worktrees the feature touches), a **standalone repository**, or the **workspace branch** itself. Determine it from the user's message ("on beta", a repo name, a path) or ask. Record the **absolute path(s)**; spawned agents work within the target and never `cd` outside it. For feature-environment work, use the env's repo worktrees — never fall back to a source checkout under `projects/`.
- **The documentation root** — where the plan and phase docs live. Follow the workspace's planning-framework conventions: if the feature came in as a refined work item with its own directory, write a `glacier/` subdirectory inside it. If the workspace has no planning framework, track the work in your winter space as a workflow at `$(winter space workflows)/<yyyy-mm-dd>-<name>/` (short kebab-case `<name>` from the feature; see [`winter-workflow:/context/winter-space.md`](winter-workflow:/context/winter-space.md)). Decide from how glacier was started — a work-item name or an existing plan directory points there, otherwise use the winter space; don't search for matching items. Create the directory if it doesn't exist.

### 2. Establish the plan

Glacier's plan targets two artifacts the application's harness declares — its **verifiability matrix** (how the application's changes are asserted correct) and its **architecture guidance** (how its code must be shaped) — and is gated on both before any building. Run a single **plan-review gate** over the plan, checking two things: the **verifiability gate** (every planned change maps to a verification method, or schedules the work to build a missing one) and the **architecture gate** (the plan conforms to the application's architecture guidance). Your workspace's planning framework provides this gate and the plan builder that authors a plan; discover and invoke them from your runtime context rather than assuming a particular agent, skill, or file layout.

**Given** the user provided a plan — a refined work item with its own directory, or one stated inline — put it through the plan-review gate before adopting it. **Verdict clean (no must-fix)** → adopt it. **Must-fix findings** → route them back to the plan builder (or, with no framework, resolve them with the user) and re-review until clean.

**Otherwise** — produce one. With a planning framework, spawn its **plan builder** to author the plan against the verifiability matrix and architecture guidance, then run the plan-review gate, routing must-fix findings back until clean. With **no** planning framework, spawn an `architect` one-shot (coordination preamble + feature + work-target path(s); ask it to read the relevant code and return an implementation approach, not to write code), naming each change's verification method and architectural fit as far as the application's harness declares them and surfacing a missing matrix or architecture guidance as a gap rather than inventing around it. If the plan builder needs the codebase explored, fork an `explorer` (coordination preamble + the research question) for the digging and hand it the distilled finding rather than reading the code into your own context.

Either way, **present the plan to the user and get approval before building.** Write the approved plan to `<documentation-root>/00-plan.md` so the session has a record. Do not advance until the user approves or adjusts it.

### 3. Establish the phases

**Given** the plan is already phased (provided or written that way) — adopt those phases.

**Otherwise** — decompose the plan into ordered phases, each a coherent, independently verifiable increment. A feature delivery spans more than the code repo — when you break the work down, account for every surface the change owes, including any that lives outside the code (such as a separate public-docs site), so each is a planned phase from the outset rather than a pre-push catch. **Confirm the phase breakdown with the user** (`AskUserQuestion` or a short numbered list). Write the confirmed phases to `<documentation-root>/00-plan.md` alongside the plan.

**Phases execute strictly in order.** A phase starts only after the previous one has passed verification (step 4). Do not reorder or parallelize.

### 4. Per-phase build-and-verify loop (hard cap: 3 attempts per phase)

For each phase, in order, **build it with a `developer`, then close it with the verify finale**. Allow up to three build→verify attempts per phase.

#### 4a. Spawn the developer (implement the phase)

Foreground `Agent` call (`subagent_type: developer`). Treat this developer as a full-stack engineer who owns the phase's implementation across whatever it touches (backend, frontend, data, CLI); runtime verification is the finale's job (4b), not the developer's. Self-contained prompt with:

1. **The coordination preamble** (verbatim).
2. **Work-target path(s)** (absolute).
3. **Phase goal** — this phase's increment, plus the one-line feature framing for context.
4. **Plan reference** — the path to `00-plan.md` so the developer can read the full approach.
5. **Attempt history** — for attempt > 1, the previous attempt's failing report verbatim (the verify finale's escalation and/or the `frontend-verifier`'s findings); tell the developer to address it specifically.
6. **Constraints** — keep the change scoped to this phase; do not start on later phases; do not commit. A green build or type-check is not the bar — the verify finale closes the phase against runtime behavior.
7. **Reporting** — files + line ranges changed; a one-line summary. **If accumulating a review manifest** (see *Review manifest* below), also have the developer report, for each hunk it authored, a `{tier, claim, intent}` line per [`winter-workflow:/context/review-manifest/build-time.md`](winter-workflow:/context/review-manifest/build-time.md) — it knows its own intent, which a cold classifier never could.

#### 4b. Spawn the verify finale (close the phase)

Foreground `Agent` call (`subagent_type: verify-finale`). The [`verify-finale`](winter-workflow:/agents/verify-finale.md) agent closes the phase: it verifies the change through a method declared in the application's verifiability matrix, **builds a missing method** (and records its matrix row) when none covers the change rather than running an ad-hoc LLM pass, and **fixes and re-verifies** until the method passes. Self-contained prompt with:

1. **The coordination preamble** (verbatim).
2. **Work-target path(s)** (absolute); for runtime verification, the base URL/port from `workspace:/context/project/project-setup.md` or the target's `.winter.env` (ask the user if neither is present).
3. **Phase context** — the phase goal and the developer's reported change, so the finale knows what behavior to assert.
4. **What to do** — verify the phase through the verifiability matrix, building and recording a missing method before verifying, then fix what verification surfaces and re-verify until it passes.

The finale both verifies and fixes, so you do not separately route its findings to a developer. **The one seam it can't drive:** it runs on `Bash`, so a matrix method that needs a browser (a visual/UI exercise) is the one verification it can't perform — when the phase's declared method is browser-driven, spawn a `frontend-verifier` for that method (coordination preamble + work-target path(s) + the base URL/port from `workspace:/context/project/project-setup.md` or the target's `.winter.env` + the declared browser exercise to run) and let the finale close everything else.

If services aren't running and verification needs them, the finale should say so rather than guess — glacier does not start services. Tell the user to run `./up` (or the project equivalent per `workspace:/context/project/project-setup.md`) and re-invoke.

#### 4c. Gate and cap

A phase passes only when its verification passes in full — the verify finale, **and** any `frontend-verifier` split off for a browser-driven method (4b). Branch on the combined result:

- **Verification passes** (the finale passed, and any split-off `frontend-verifier` also passed) → advance to the next phase, or to step 5 if this was the last phase.
- **Verification fails** — the finale escalates (a failure it can't resolve in its own retries, or a gap only the user can decide), **or** a split-off `frontend-verifier` reports a failure (it verifies only; it cannot fix what it finds) → re-task the same phase: spawn a fresh `developer` (attempt + 1) with the failing report folded into the attempt history (the finale's escalation and/or the `frontend-verifier`'s findings), then re-run 4b. Don't re-spawn the finale or verifier blindly on the same build.
- **Cap** — if a phase hasn't passed its full verification in three attempts, **stop and escalate to the user**: name the phase, summarize each attempt in one line (what was built, what the finale or verifier reported), and ask how to proceed. Do not silently continue to later phases on an unverified one.

### Review manifest (optional — capture intent while building)

When a review manifest is wanted for this feature — the user asked for one, or the change is large or mechanical-heavy enough that a tiered review order will save a human real attention — **accumulate it as you build** rather than cold-classifying at the end. The builder knows *why* each hunk exists; capturing that intent while it is fresh produces a higher-fidelity manifest than any after-the-fact classification.

Follow [`winter-workflow:/context/review-manifest/build-time.md`](winter-workflow:/context/review-manifest/build-time.md): each phase's `developer` reports the `{tier, claim, intent}` for the hunks it authored (step 4a, item 7); after each phase you append those entries to the manifest's JSON facts at `$(winter space manifests)/<date>-<slug>.json`. The verify finale also authors hunks (its fixes, and any verification method or matrix row it builds) but reports no tier line — those are classified at the **close** step against the settled diff, where total-coverage enforcement catches them. You **close** the manifest at step 5 (below). Skip all of this for a small feature that fits in a glance — the manifest earns its keep only on a change big enough that a human would otherwise stop reading.

### 5. Pre-push review

When every phase has passed, run the review automatically — do not wait for the user to ask. Before reporting completion, **invoke `pre-push`** (via the `Skill` tool) over the change-set, then present the work **together with** the review's advisory summary so the user sees the findings as part of the result.

**If you accumulated a review manifest** (above), **close it here**: bind the authored entries to the settled diff, enforce total coverage, run the adversarial `manifest-auditor` over the cheap tiers, and render the markdown document — all per [`winter-workflow:/context/review-manifest/build-time.md`](winter-workflow:/context/review-manifest/build-time.md) §"Close the manifest". Surface the manifest's `.md` path alongside the pre-push summary, so the user has both the cross-axis findings and the tiered review order.

Do not push. The user decides whether to address findings (re-task a `developer`), push, or stop.

### 6. Retrospective

Once the work is delivered (or the user calls it done), write a retrospective. When a planning framework supplied the documentation root, write it there as `<documentation-root>/retrospective.md`. Otherwise — the winter-space default — write it to the winter space's `retrospectives` directory as `$(winter space retrospectives)/<yyyy-mm-dd>-<name>.md` (same `<name>` as the workflow doc; see [`winter-workflow:/context/winter-space.md`](winter-workflow:/context/winter-space.md)). Either way the structure is:

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
