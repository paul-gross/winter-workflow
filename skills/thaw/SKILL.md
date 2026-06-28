---
description: Make a small, focused change to existing code — bug fix, tweak, regression repair. Use for narrow, localized work on code that already exists.
argument-hint: "[change description]"
allowed-tools: Bash, Read, Glob, Grep, Agent, AskUserQuestion
---

# Thaw

`thaw` makes **small, focused changes to existing code** — fix a bug, tweak a behavior, adjust an existing function, restore a regression. It composes `explorer` → `developer` → `verifier` into a tight investigate-change-verify loop, without spinning up the full `blizzard` machinery.

The runtime verification (step 6b) and the delivery-surfaces accounting in its report (step 7) are how thaw meets the shared **Definition of done for feature work** ([`winter-workflow:/context/definition-of-done.md`](winter-workflow:/context/definition-of-done.md)) — the tested-and-docs-updated bar — for the change it delivers.

## Scope

`thaw` composes three role-pure agents (see [`winter-workflow:/agents/README.md`](winter-workflow:/agents/README.md)) in one-shot mode:

| Step | Agent | Purpose |
|------|-------|---------|
| 3 | `explorer` | investigate and scope the change |
| 6a | `developer` | implement the change |
| 6b | `backend-verifier` **or** `frontend-verifier` | confirm the change |

It does **not** spawn `architect`, `test-mediator`, `code-reviewer`, `runner`, or `context-reviewer`. If any of those are needed, the work has outgrown `thaw` — bail to `blizzard` (see step 4). If a structural code review is wanted after a clean thaw, run `cold-review` separately.

**Why no `TeamCreate`:** `thaw` does **not** create its own team. This is deliberate — it keeps `thaw` composable as a primitive. The skill can run standalone from a user-driven session, *and* a `blizzard` snowflake (or any other orchestrator) can invoke `thaw` as a contained sub-step without nesting teams or polluting the parent team's `TaskList`. Each agent spawn is a self-contained one-shot. The agents are role-pure and expect their caller to inject coordination context; the **coordination preamble** (next section) tells them they're operating one-shot with no shared task list.

## Coordination preamble (shared)

Every `thaw` spawn prompt must begin with this preamble, prepended verbatim before the role-specific task content. It tells the role-pure agent how to participate in a `thaw` invocation (no team, no shared `TaskList`, report inline):

> You are operating as a one-shot agent spawned by the `thaw` skill. No shared task list exists. Report results to the skill via your final response only — do not call `SendMessage`, `TaskCreate`, or `TaskUpdate`. When your task is done, stop.

The steps below reference this section as **"the coordination preamble"**; do not paraphrase — paste it verbatim.

## Steps

### 1. Frame the change

Capture the requested change in 1-2 sentences. Source:

- `$ARGUMENTS` if provided.
- Otherwise, the user's most recent description in conversation.

If neither yields something concrete, ask the user once: "What change do you want, and how will we know it worked?" Then stop until they answer.

### 2. Identify the worktree

A thaw runs against exactly one worktree. Determine it from:

- The user's message ("on alpha", "in beta/my-app", a file path).
- Otherwise ask: which feature env / repo?

Record the absolute worktree path. Every spawned agent receives it in their prompt — they must not `cd` elsewhere.

### 3. Spawn the explorer (investigate)

Foreground `Agent` call (`subagent_type: explorer`). Self-contained prompt — the explorer has no memory of this session.

The prompt must include:

1. **The coordination preamble** (verbatim, see above).
2. **Change request**: the 1-2 sentence description from step 1.
3. **Worktree path**: absolute path; instruction to investigate there.
4. **What to do**: read relevant code, logs, and tests; locate where the change belongs; for bug-shaped requests, trace to a root cause; for tweak-shaped requests, identify the existing code to adjust. Keep this investigation tight — `thaw` is for small, localized work, so the explorer should not produce broader documentation as a side effect of this call.
5. **What to return**:
   - **Location** — specific file + line(s) where the change belongs (the defect's site for bugs, the existing code being adjusted for tweaks).
   - **Change sketch** — the smallest edit that achieves the goal (a few lines, a single function, etc.).
   - **Scope estimate** — one of: **`thaw`** (small, localized, ≲ ~50 LOC across ≲ ~3 files) or **`bigger-than-a-thaw`** (multi-module, requires design decisions, refactor, or root-cause analysis the explorer cannot bound).
   - **Verifier kind** — `backend` (API/CLI/script/DB) or `frontend` (rendered UI). If genuinely ambiguous, say so.
   - **Smoke check** — a single concrete probe that distinguishes done from not-done (one test name, one curl, one page load). This becomes the verifier's pass criterion in step 6b.

### 4. Bail-out check

`thaw` bails to `blizzard` when **any** of these are true:

- The explorer's scope estimate is `bigger-than-a-thaw`.
- The change sketch implies architectural change, refactor, or root-cause work.
- The iteration cap in step 6 is hit (3 dev→verify cycles without a pass).

On bail:

- Stop. Do not spawn further agents.
- Present the investigation (and, for cap-hit, the iteration trace per step 6c) to the user verbatim.
- Recommend escalating to the `blizzard` skill with the same change description.
- Exit.

This is the single canonical bail-out — earlier and later sections reference back here.

### 5. Pick the verifier

From the explorer's `verifier kind`:

- `backend` → spawn `backend-verifier` in step 6.
- `frontend` → spawn `frontend-verifier` in step 6.
- ambiguous → ask the user with `AskUserQuestion` (backend vs. frontend).

### 6. Dev → Verify loop (hard cap: 3 iterations)

For each iteration `i` in `1..3`:

#### 6a. Spawn the developer

Foreground `Agent` call (`subagent_type: developer`). Self-contained prompt with:

1. **The coordination preamble** (verbatim).
2. **Worktree path** (absolute).
3. **Investigation** — the explorer's location and change sketch verbatim.
4. **Iteration history** — for `i > 1`, the previous verifier's failure report (status, expected vs. observed, error excerpts). Tell the developer to address those specifically.
5. **Constraints**: keep the change minimal; do not refactor; do not add error handling for scenarios that can't happen; do not commit.
6. **Reporting**: return a list of files + line ranges changed, and a one-sentence summary of what was changed.

#### 6b. Spawn the verifier

Foreground `Agent` call (`subagent_type: backend-verifier` or `frontend-verifier` per step 5). Self-contained prompt with:

1. **The coordination preamble** (verbatim).
2. **Worktree path** (absolute) and, for backend, the base URL/port. Pull connection details from `workspace:/context/project/setup-tmux.toml` or the worktree's `.winter.env`; if neither is present, ask the user.
3. **Change to confirm** — the original 1-2 sentence description.
4. **Smoke check** — the single concrete probe the explorer returned in step 3. The verifier runs **that probe** to decide pass/fail. Not a full regression sweep.
5. **What "done" looks like** — pass criteria for the smoke check (e.g., the named test returns green, the curl returns 200 with field X, the page renders the new label without console errors).
6. **What to return**:
   - **Verdict** — `pass` or `fail`.
   - On `fail`: status/output observed, what was expected, any console/log excerpts, a diagnosis hint if obvious.
   - On `pass`: a one-line confirmation of what was checked.

If the verifier reports **"service not reachable"** or similar environment failure (services not running, port not open), stop the loop and tell the user — `thaw` does not start services. Suggest they run `./up` (or the project's equivalent per `workspace:/context/project/setup-tmux.toml`) and re-invoke.

#### 6c. Branch on verdict

- `pass` → exit the loop, go to step 7.
- `fail` and `i < 3` → next iteration with the failure report folded into the developer's prompt.
- `fail` and `i == 3` → iteration cap hit. Bail per step 4, including in the escalation:
  - The original change request (one line).
  - The explorer's investigation (location + change sketch, as returned).
  - **Per iteration, one line for the dev change and one line summarizing the verifier failure.** Do not paste full verifier reports — three full reports defeat the bail-out's purpose. The user can ask for detail if they want it.

### 7. Report

On pass, summarize to the user in 3-5 bullets:

- **Change**: one-line description of what was requested.
- **Location**: the explorer's finding (file + line).
- **Implementation**: files + line ranges changed.
- **Verified**: what smoke check passed.
- **Delivery surfaces**: a thaw is still one slice of a feature delivery — which surfaces beyond the code does this change owe, each carried in the same change or a noted N/A.
- **Not committed** — the user decides when to commit (suggest `commit`).

## Why the loop is capped

A `thaw` that hasn't resolved in three dev→verify cycles is no longer a thaw — the investigation was wrong, the change is bigger than the explorer estimated, or the work item is masking a deeper issue. Bail per step 4 rather than burning context in a stuck loop.
