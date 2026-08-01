# Snowball

## Inputs

- **Change request** — a concrete description of the small change to make; it may initially be absent when a human caller is available to clarify it.
- **Work-target hint** — optional environment, repository, or path identifying the worktree.
- **Human-caller channel** — available for required clarification, verifier choice, escalation, and the final report.
- **Workspace context** — target setup and connection details discoverable from workspace context or computed environment variables.

## Outputs

- On success, an uncommitted implementation in one worktree plus the step 7 report.
- On bail-out or environment failure, the prescribed escalation report and the current uncommitted worktree state.

The snowball process makes **small, focused changes to existing code** — fix a bug, tweak a behavior, adjust an existing function, restore a regression. It composes `arctic-explorer` → `ice-carver` → `verifier` into a tight investigate-change-verify loop — one packed throw at one spot, without resident coordination or a phased plan. Use the semantic operations in [`../../runtime-ports.md`](../../runtime-ports.md).

The runtime verification (step 6b) and the delivery-surfaces accounting in its report (step 7) are how snowball meets the shared **Definition of done for feature work** ([`winter-workflow:/methodology/completion.md`](winter-workflow:/methodology/completion.md)) — the tested-and-docs-updated bar — for the change it delivers.

## Scope

The process composes three canonical roles through the isolated-role port:

| Step | Canonical role | Purpose |
|------|----------------|---------|
| 3 | `arctic-explorer` | investigate and scope the change |
| 6a | `ice-carver` | implement the change |
| 6b | `backend-verifier` **or** `frontend-verifier` | confirm the change |

It does **not** spawn `winter-architect`, `cold-reviewer`, or `context-reviewer`. If any of those are needed, the work has outgrown `snowball` — bail to `glacier` (see step 4). If a structural code review is wanted after a clean snowball, run the code review process separately.

**Why no resident coordination:** `snowball` does **not** create resident workers or a shared assignment queue. This keeps it composable as a primitive: it can run directly for a human caller or as another process's contained sub-step without nesting coordination contexts. Each role invocation is a self-contained one-shot.

## Isolated-role restrictions

Every isolated role invocation carries these semantic restrictions before its role-specific task:

- Run as a one-shot isolated role for this Snowball operation, with no resident peers or shared assignment queue.
- Return the requested result once through the isolated-result channel; perform no follow-on coordination.
- Stop when the result is complete.

The steps below refer to these as **the isolated-role restrictions**.

## Steps

### 1. Frame the change

Capture the supplied **change request** in 1-2 sentences. If it is not concrete, ask the human caller once: "What change do you want, and how will we know it worked?" Then stop until they answer.

### 2. Identify the worktree

A snowball runs against exactly one worktree. Determine it from:

- The supplied work-target hint ("on alpha", "in beta/my-app", a file path).
- Otherwise ask: which feature env / repo?

Record the absolute worktree path. Every isolated role receives it in its task and must not leave it.

### 3. Run the arctic-explorer (investigate)

Spawn the canonical `arctic-explorer` role in a one-shot isolated context and await its result. The arctic-explorer has no memory of this session.

The prompt must include:

1. **The isolated-role restrictions**.
2. **Change request**: the 1-2 sentence description from step 1.
3. **Worktree path**: absolute path; instruction to investigate there.
4. **What to do**: read relevant code, logs, and tests; locate where the change belongs; for bug-shaped requests, trace to a root cause; for tweak-shaped requests, identify the existing code to adjust. Keep this investigation tight — `snowball` is for small, localized work, so the arctic-explorer should not produce broader documentation as a side effect of this call.
5. **What to return**:
   - **Location** — specific file + line(s) where the change belongs (the defect's site for bugs, the existing code being adjusted for tweaks).
   - **Change sketch** — the smallest edit that achieves the goal (a few lines, a single function, etc.).
   - **Scope estimate** — one of: **`snowball`** (small, localized, ≲ ~50 LOC across ≲ ~3 files) or **`bigger-than-a-snowball`** (multi-module, requires design decisions, refactor, or root-cause analysis the arctic-explorer cannot bound).
   - **Verifier kind** — `backend` (API/CLI/script/DB) or `frontend` (rendered UI). If genuinely ambiguous, say so.
   - **Smoke check** — a single concrete probe that distinguishes done from not-done (one test name, one curl, one page load). This becomes the verifier's pass criterion in step 6b.

### 4. Bail-out check

`snowball` bails to `glacier` when **any** of these are true:

- The arctic-explorer's scope estimate is `bigger-than-a-snowball`.
- The change sketch implies architectural change, refactor, or root-cause work.
- The iteration cap in step 6 is hit (3 dev→verify cycles without a pass).

On bail:

- Stop. Do not spawn further roles.
- Present the investigation (and, for cap-hit, the iteration trace per step 6c) to the human caller verbatim.
- Recommend escalating to the `glacier` process with the same change description.
- Exit.

This is the single canonical bail-out — earlier and later sections reference back here.

### 5. Pick the verifier

From the arctic-explorer's `verifier kind`:

- `backend` → use the canonical `backend-verifier` role in step 6.
- `frontend` → use the canonical `frontend-verifier` role in step 6.
- ambiguous → ask the human caller to choose backend or frontend through the human-caller port.

### 6. Dev → Verify loop (hard cap: 3 iterations)

For each iteration `i` in `1..3`:

#### 6a. Run the ice-carver

Spawn the canonical `ice-carver` role in a one-shot isolated context with workhorse model intent, await its result, and supply:

1. **The isolated-role restrictions**.
2. **Worktree path** (absolute).
3. **Investigation** — the arctic-explorer's location and change sketch verbatim.
4. **Iteration history** — for `i > 1`, the previous verifier's failure report (status, expected vs. observed, error excerpts). Tell the ice-carver to address those specifically.
5. **Constraints**: keep the change minimal; do not refactor; do not add error handling for scenarios that can't happen; do not commit.
6. **Reporting**: return a list of files + line ranges changed, and a one-sentence summary of what was changed.

#### 6b. Run the verifier

Spawn the canonical `backend-verifier` or `frontend-verifier` role selected in step 5 in a one-shot isolated context, await its result, and supply:

1. **The isolated-role restrictions**.
2. **Worktree path** (absolute) and, for backend, the base URL/port. Pull connection details from `workspace:/context/project/project-setup.md` or the env's computed vars (`winter env <env>`); if neither yields them, ask the human caller.
3. **Change to confirm** — the original 1-2 sentence description.
4. **Smoke check** — the single concrete probe the arctic-explorer returned in step 3. The verifier runs **that probe** to decide pass/fail. Not a full regression sweep.
5. **What "done" looks like** — pass criteria for the smoke check (e.g., the named test returns green, the curl returns 200 with field X, the page renders the new label without console errors).
6. **What to return**:
   - **Verdict** — `pass` or `fail`.
   - On `fail`: status/output observed, what was expected, any console/log excerpts, a diagnosis hint if obvious.
   - On `pass`: a one-line confirmation of what was checked.

If the verifier reports **"service not reachable"** or similar environment failure (services not running, port not open), stop the loop and tell the human caller — `snowball` does not start services. Suggest they run `./up` (or the project's equivalent per `workspace:/context/project/project-setup.md`) and rerun the process.

#### 6c. Branch on verdict

- `pass` → exit the loop, go to step 7.
- `fail` and `i < 3` → next iteration with the failure report folded into the ice-carver's prompt.
- `fail` and `i == 3` → iteration cap hit. Bail per step 4, including in the escalation:
  - The original change request (one line).
  - The arctic-explorer's investigation (location + change sketch, as returned).
  - **Per iteration, one line for the dev change and one line summarizing the verifier failure.** Do not paste full verifier reports — three full reports defeat the bail-out's purpose. The human caller can ask for detail if they want it.

### 7. Report

On pass, summarize to the human caller in 3-5 bullets:

- **Change**: one-line description of what was requested.
- **Location**: the arctic-explorer's finding (file + line).
- **Implementation**: files + line ranges changed.
- **Verified**: what smoke check passed.
- **Delivery surfaces**: a snowball is still one slice of a feature delivery — which surfaces beyond the code does this change owe, each carried in the same change or a noted N/A.
- **Not committed** — the human caller decides when to commit (suggest the `commit` operation).

## Why the loop is capped

A `snowball` that hasn't resolved in three dev→verify cycles is no longer a snowball — the investigation was wrong, the change is bigger than the arctic-explorer estimated, or the work item is masking a deeper issue. Bail per step 4 rather than burning context in a stuck loop.
