# Snowball — process

Snowball makes a small, focused change to existing code — fix a bug, tweak a behavior, adjust an existing function, restore a regression — as one packed throw at one spot, with no resident coordination and no phased plan. It composes arctic-explorer, then ice-carver, then a verifier into a tight investigate-change-verify loop: exactly three canonical roles, all used through the isolated-role port. Snowball creates no resident workers and no shared assignment queue, keeping it composable as a primitive that can run directly for a human caller or as another process's contained sub-step without nesting coordination contexts; every role invocation is a self-contained one-shot.

Snowball meets the shared definition of done for feature work owned by [`../../completion.md`](../../completion.md) — the tested-and-docs-updated bar — through its runtime-verification step and the delivery-surfaces accounting in its final report.

Snowball executes its coordination through the semantic operations in [`../../runtime-ports.md`](../../runtime-ports.md). Every isolated-role invocation carries, before its role-specific task, the one-shot default declared at [`../../runtime-ports.md#spawn-an-isolated-role`](../../runtime-ports.md#spawn-an-isolated-role), scoped to this snowball operation — the steps below call this "the isolated-role restrictions".

## Inputs

- **Change request** — a concrete description of the small change; may initially be absent when a human caller is available to clarify it.
- **Work-target hint** (optional) — an environment, repository, or path identifying the worktree.
- **Workspace context** — target setup and connection details discoverable from workspace context files or computed environment variables.
- **Human-caller channel** (required) — used for required clarification, verifier choice, escalation, and the final report.

## Outputs

- On success: an uncommitted implementation in one worktree plus the final report.
- On bail-out or environment failure: the prescribed escalation report plus the worktree's current uncommitted state.

## 1. Capture the change request

Capture the change request in one or two sentences. If it is not concrete, ask the human caller once — "What change do you want, and how will we know it worked?" — then stop until they answer.

## 2. Pin the worktree

A snowball runs against exactly one worktree, identified from the work-target hint or by asking the human caller which feature environment or repository. Record the absolute worktree path; every isolated role receives it in its task and must not leave it.

## 3. Investigate

Spawn the canonical `arctic-explorer` role in a one-shot isolated context and await its result, supplying the isolated-role restrictions, the captured change request, and the absolute worktree path with the instruction to investigate there. Its task: read the relevant code, logs, and tests; locate where the change belongs; trace bug-shaped requests to a root cause; identify the existing code to adjust for tweak-shaped requests; and keep the investigation tight, producing no broader documentation as a side effect, because snowball is for small localized work.

The arctic-explorer returns:

- **Location** — the specific file and line(s) where the change belongs: the defect's site for bugs, the code being adjusted for tweaks.
- **Change sketch** — the smallest edit that achieves the goal, such as a few lines or a single function.
- **Smoke check** — a single concrete probe that distinguishes done from not-done — one test name, one curl, one page load — which becomes the verifier's pass criterion.
- **Scope estimate** — either `snowball` (small and localized, roughly at most ~50 lines across ~3 files) or `bigger-than-a-snowball` (multi-module, requiring design decisions, a refactor, or root-cause analysis it cannot bound).
- **Verifier kind** — `backend` (API, CLI, script, or database) or `frontend` (rendered UI), or a statement that the kind is genuinely ambiguous.

## 4. Pick the verifier

Map the verifier kind: `backend` to the canonical `backend-verifier` role, `frontend` to the canonical `frontend-verifier` role; an ambiguous kind means asking the human caller to choose through the human-caller port.

## 5. Dev-verify loop

The loop runs at most three iterations, each an ice-carver run followed by a verifier run.

**Implement.** Each iteration spawns the canonical `ice-carver` role in a one-shot isolated context with workhorse model intent and awaits its result, supplying:

- the isolated-role restrictions;
- the absolute worktree path;
- the arctic-explorer's location and change sketch verbatim;
- for iterations after the first, the previous verifier's failure report (status, expected versus observed, error excerpts) with the instruction to address those specifically;
- the constraints to keep the change minimal, not refactor, not add error handling for impossible scenarios, and not commit;
- the reporting requirement: files with line ranges changed plus a one-sentence summary.

**Verify.** Each iteration then spawns the selected verifier role in a one-shot isolated context and awaits its result, supplying:

- the isolated-role restrictions;
- the absolute worktree path;
- for a backend verifier, the base URL and port pulled from `workspace:/context/project/project-setup.md` or the environment's computed variables via `winter env <env>`, asking the human caller when neither yields them;
- the original change description as the change to confirm;
- the arctic-explorer's smoke check as the single probe deciding pass or fail — not a full regression sweep;
- explicit pass criteria describing what done looks like (for example: the named test goes green, the curl returns 200 with the expected field, the page renders the new label without console errors);
- the return shape: a verdict of pass or fail — on fail, the observed status or output, what was expected, any console or log excerpts, and a diagnosis hint when obvious; on pass, a one-line confirmation of what was checked.

**Branch on the verdict.** Pass exits the loop to the final report. Fail before the third iteration starts the next iteration with the failure report folded into the ice-carver's prompt. Fail on the third iteration is a cap hit and triggers the bail-out.

When the verifier reports the service unreachable or a similar environment failure (services not running, port not open), stop the loop and tell the human caller: snowball does not start services. Suggest running `winter service up <env>` — the run phase per `workspace:/context/environment-lifecycle.md` — and rerunning the process.

## The bail-out

Defined once — the single canonical exit that every other step references. Snowball bails to glacier when any of these holds:

- the arctic-explorer's scope estimate is `bigger-than-a-snowball`;
- the change sketch implies architectural change, refactor, or root-cause work;
- the dev-verify loop's three-iteration cap is hit.

Snowball never spawns winter-architect, cold-reviewer, or context-reviewer; needing any of them means the work has outgrown snowball, which triggers the bail-out. The loop is capped because a snowball unresolved after three dev-verify cycles is no longer a snowball — the investigation was wrong, the change is bigger than estimated, or the request masks a deeper issue — so bail rather than burn context in a stuck loop.

On bail-out: stop and spawn no further roles, present the investigation (and for a cap hit, the iteration trace) to the human caller verbatim, recommend escalating to the glacier process with the same change description, and exit. A cap-hit escalation carries: the original change request in one line, the arctic-explorer's investigation (location and change sketch as returned), and per iteration one line for the dev change plus one line summarizing the verifier failure — never full verifier reports, since three of them defeat the bail-out's purpose and the human caller can request detail.

## 6. Final report

On pass, report to the human caller in three to five bullets:

- the change requested, in one line;
- the location the arctic-explorer found (file and line);
- the implementation (files and line ranges changed);
- what smoke check passed;
- the delivery surfaces — a snowball is still one slice of a feature delivery, so name which surfaces beyond the code the change owes, each carried in the same change or noted as N/A;
- that nothing is committed — the human caller decides when to commit, with the `commit` operation suggested; [`../../delivery/commit/conventions.md`](../../delivery/commit/conventions.md) owns the message conventions.

A structural code review wanted after a clean snowball runs separately through the shared review process at [`../../review/process.md`](../../review/process.md) with the code axis ([`../../review/axes/code.md`](../../review/axes/code.md)).
