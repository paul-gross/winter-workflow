---
description: Drive one feature to completion through sequential subagent spawns on a single linear track — adopt or produce a plan, break it into ordered phases, build-and-verify each phase in order, run a pre-push review, and write a retrospective. Use to build a feature methodically, one phase at a time.
argument-hint: "[plan name or feature description]"
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, Agent, AskUserQuestion, Skill
---

# Glacier

Drive one feature to completion on a single linear track: adopt or produce a plan, break it into ordered phases, build-and-verify each phase one at a time, run a pre-push review, and write a retrospective. You spawn one role-pure subagent at a time (see [`winter-workflow:/agents/README.md`](winter-workflow:/agents/README.md)) and gate each handoff yourself.

The per-phase runtime verification (step 4) and pre-push review (step 5) are how glacier meets the shared **Definition of done for feature work** ([`winter-workflow:/index.md`](winter-workflow:/index.md)) — the tested-and-docs-updated bar — for the feature it delivers.

Work within the planning framework you are given or that is available to you — its conventions for where plans, phases, and session artifacts live. If no planning framework exists, gently suggest to the user that adopting one would help with organization and observability, then proceed, tracking the work in your winter space (see step 1).

## Coordination preamble (shared)

Every spawn prompt must begin with this preamble, prepended verbatim before the role-specific task content. It tells the role-pure agent it is operating one-shot with no team:

> You are operating as a one-shot agent spawned by the `glacier` skill. No shared task list exists. Report results to the skill via your final response only — do not call `SendMessage`, `TaskCreate`, or `TaskUpdate`. When your task is done, stop.

The steps below reference this section as **"the coordination preamble"**; do not paraphrase — paste it verbatim.

## Steps

### 1. Frame the feature, work target, and documentation root

Establish three things before any building:

- **The feature** — one or two sentences. Source: `$ARGUMENTS`, a named plan, or the user's most recent description. If none yields something concrete, ask the user once what the feature is and how you'll know it's done, then stop until they answer.
- **The work target** — one of: a **feature environment** (e.g. `beta/`, across whichever of its repo worktrees the feature touches), a **standalone repository**, or the **workspace branch** itself. Determine it from the user's message ("on beta", a repo name, a path) or ask. Record the **absolute path(s)**; spawned agents work within the target and never `cd` outside it. For feature-environment work, use the env's repo worktrees — never fall back to a source checkout under `projects/`.
- **The documentation root** — where the plan and retrospective live. Follow the workspace's planning-framework conventions: if the feature came in as a refined work item with its own directory, write a `glacier/` subdirectory inside it. If the workspace has no planning framework, track the work in your winter space as a workflow at `~/.claude/winter/workflows/<yyyy-mm-dd>-<name>/` (short kebab-case `<name>` from the feature). Decide from how glacier was started — a work-item name or an existing plan directory points there, otherwise use the winter space; don't search for matching items. Create the directory if it doesn't exist.

### 2. Establish the plan

**Given** the user provided a plan — adopt it. A refined work item with its own directory is a plan; so is a plan the user states inline.

**Otherwise** — produce one. Spawn an `architect` one-shot (coordination preamble + feature + work-target path(s); ask it to read the relevant code and return an implementation approach, not to write code). Then **present the plan to the user and get approval before building.** Write the approved plan to `<documentation-root>/00-plan.md` so the session has a record. Do not advance until the user approves or adjusts it.

### 3. Establish the phases

**Given** the plan is already phased (provided or written that way) — adopt those phases.

**Otherwise** — decompose the plan into ordered phases, each a coherent, independently verifiable increment. A feature delivery spans more than the code repo — when you break the work down, account for every surface the change owes, including any that lives outside the code (such as a separate public-docs site), so each is a planned phase from the outset rather than a pre-push catch. **Confirm the phase breakdown with the user** (`AskUserQuestion` or a short numbered list). Write the confirmed phases to `<documentation-root>/00-plan.md` alongside the plan.

**Phases execute strictly in order.** A phase starts only after the previous one has passed verification (step 4). Do not reorder or parallelize.

### 4. Per-phase build-and-verify loop (hard cap: 3 attempts per phase)

For each phase, in order, run up to three attempts:

#### 4a. Spawn the developer (implement **and** verify)

Foreground `Agent` call (`subagent_type: developer`). Treat this developer as a full-stack engineer who owns the phase end to end — implementation across whatever the phase touches (backend, frontend, data, CLI) and the runtime verification that it works. Self-contained prompt with:

1. **The coordination preamble** (verbatim).
2. **Work-target path(s)** (absolute); for runtime verification, the base URL/port from `workspace:/ai/project/setup-tmux.md` or the target's `.winter.env` (ask the user if neither is present).
3. **Phase goal** — this phase's increment, plus the one-line feature framing for context.
4. **Plan reference** — the path to `00-plan.md` so the developer can read the full approach.
5. **Attempt history** — for attempt > 1, the previous report's verification gap or failure verbatim; tell the developer to address it specifically.
6. **The dual mandate** — implement the phase, **then verify it at runtime**. A green build or typecheck is **not** verification. Run a real runtime probe appropriate to the change: execute the affected test(s), `curl` the endpoint and inspect the response, invoke the CLI and read its output, or load the page. Report exactly **what was run and what was observed**.
7. **Constraints** — keep the change scoped to this phase; do not start on later phases; do not commit.
8. **Reporting** — files + line ranges changed; the runtime probe(s) run and their observed output; a one-line verdict. **If accumulating a review manifest** (see *Review manifest* below), also have the developer report, for each hunk it authored, a `{tier, claim, intent}` line per [`winter-workflow:/ai/review-manifest/build-time.md`](winter-workflow:/ai/review-manifest/build-time.md) — it knows its own intent, which a cold classifier never could.

If services aren't running and the verification needs them, the developer should say so rather than guess — glacier does not start services. Tell the user to run `./up` (or the project equivalent per `workspace:/ai/project/setup-tmux.md`) and re-invoke.

#### 4b. Gate on verification adequacy

Read the developer's report and decide whether the verification was a **real runtime check**, not just a build:

- **Adequate** (an actual probe with observed output that distinguishes done from not-done) → advance to the next phase, or to step 5 if this was the last phase.
- **Missing or weak** (build/typecheck only, no probe described, or the probe doesn't actually exercise the phase's change) → **re-task the same role**: spawn a fresh `developer` (attempt + 1) with the gap named explicitly in the attempt history. The change may already be correct — the re-task can be verification-only if the implementation looks done.
- **Failed** (probe ran, change is wrong) → re-task with the failure folded in.

#### 4c. Cap

If a phase hasn't passed an adequate runtime check in three attempts, **stop and escalate to the user**: name the phase, summarize each attempt in one line (what was built, what verification was missing or failed), and ask how to proceed. Do not silently continue to later phases on an unverified one.

### Review manifest (optional — capture intent while building)

When a review manifest is wanted for this feature — the user asked for one, or the change is large or mechanical-heavy enough that a tiered review order will save a human real attention — **accumulate it as you build** rather than cold-classifying at the end. The builder knows *why* each hunk exists; capturing that intent while it is fresh produces a higher-fidelity manifest than any after-the-fact classification.

Follow [`winter-workflow:/ai/review-manifest/build-time.md`](winter-workflow:/ai/review-manifest/build-time.md): each phase's `developer` reports the `{tier, claim, intent}` for the hunks it authored (step 4a, item 8); after each phase you append those entries to the manifest's JSON facts at `~/.claude/winter/review-manifests/<date>-<slug>.json`. You **close** it at step 5 (below). Skip all of this for a small feature that fits in a glance — the manifest earns its keep only on a change big enough that a human would otherwise stop reading.

### 5. Pre-push review

When every phase has passed, run the review automatically — do not wait for the user to ask. Before reporting completion, **invoke `pre-push`** (via the `Skill` tool) over the change-set, then present the work **together with** the review's advisory summary so the user sees the findings as part of the result.

**If you accumulated a review manifest** (above), **close it here**: bind the authored entries to the settled diff, enforce total coverage, run the adversarial `manifest-auditor` over the cheap tiers, and render the markdown document — all per [`winter-workflow:/ai/review-manifest/build-time.md`](winter-workflow:/ai/review-manifest/build-time.md) §"Close the manifest". Surface the manifest's `.md` path alongside the pre-push summary, so the user has both the cross-axis findings and the tiered review order.

Do not push. The user decides whether to address findings (re-task a `developer`), push, or stop.

### 6. Retrospective

Once the work is delivered (or the user calls it done), write a retrospective to `<documentation-root>/retrospective.md`:

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
