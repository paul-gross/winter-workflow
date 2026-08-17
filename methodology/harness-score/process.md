# Harness score — process

A codebase-scoped maturity scoring procedure: gather evidence, apply the frozen rubric, and emit an HTML report plus a JSON sidecar. Any agent may execute it, as a standalone operation or as a substep — the caller supplies the target path; this document owns the reusable procedure.

Runtime operations follow [`../runtime-ports.md`](../runtime-ports.md).

## Where this fits

| Method | Question |
|--------|----------|
| `harness-score` (this process) | Where does the codebase sit on the maturity matrix today, over the whole codebase? |
| [Code review axis](../review/axes/code.md) | Is this diff architecturally sound? |
| [Harness review axis](../review/axes/harness.md) | Does the harness keep pace with this diff? |

## Input

The single input is **`target_path`** — the absolute path of the existing codebase directory to score.

The executor's working directory never selects the target: target-scoped commands either run with `target_path` as their working directory or use absolute paths rooted there.

## The rubric

The rubric lives at [`./rubric.md`](./rubric.md), frozen at the version recorded in its own header. Its [scoring rules](./rubric.md#scoring-rules) are the single source of truth — read them there as part of applying the rubric; never paraphrase, tighten, or improvise on them at scoring time. If the rubric fits the target poorly, that is material for a deliberate future rubric edit with a version bump, never something to adjust during a scoring run.

## Steps

### 1. Resolve the scores directory

Reports land in the winter space's `scores` artifact directory. Resolve it exactly once through the artifact-directory runtime operation and ensure it exists, following [`../artifact-storage.md`](../artifact-storage.md) — that file owns artifact kinds, naming, and consumer policy. If resolution fails or returns an empty value, stop before searching for prior reports: an empty directory value would broaden the prior-report lookup outside the artifact store.

### 2. Find the prior report

The prior report for delta purposes is the most recent JSON file matching `<scores-dir>/*-<project>.json` whose rubric version equals this run's rubric version; recency is decided by sorting filenames, since the date prefix sorts chronologically. Prior reports at a different rubric version are ignored for delta computation.

### 3. Gather the evidence

Spawn the canonical `arctic-explorer` role in a one-shot isolated context. Its job is evidence gathering only — the current executor does the scoring itself from the returned inventory plus the conversation. The invocation must direct the role to:

- read the rubric file itself and walk each dimension's diagnostic questions and evidence-to-look-for lists;
- produce an inventory of evidence — file paths, command outputs, doc references — for each of the rubric's 10 dimensions, explicitly not stages and not scores;
- scope itself to `target_path`: run target-scoped commands from that directory and search the target's repository content, configuration, documentation surfaces, and git history as each dimension warrants, without inspecting the executor's working directory unless that is the same path;
- stay read-only: no writing or editing documentation, no requesting a follow-up context review, no applying any default documentation-integration behavior it otherwise carries;
- run without resident peers or a shared assignment queue, return one evidence inventory through the isolated-result channel, perform no follow-on coordination, and stop when the inventory is complete;
- return a short bullet list of evidence per dimension with file paths or git-log outputs, calling out explicitly any dimension with no evidence.

### 4. Score every dimension

Assign every one of the 10 dimensions four things: a stage, evidence citations, a rationale, and a next-stage suggestion.

- **Evidence** — one to three citations drawn from the arctic-explorer inventory, each a file path plus a one-sentence description of what it shows.
- **Rationale** — one to two sentences explaining the stage choice given the evidence.
- **Next-stage suggestion** — a single concrete change (one file, one tool, one PR) the target project's maintainer could act on in an afternoon, never something vague like "improve documentation".

Fresh-context isolation deliberately does not apply to this step: fresh code and harness reviews isolate to avoid absorbing author framing of a diff, but harness scoring judges a whole codebase and benefits from the caller's framing of why they care — only the evidence-gathering arctic-explorer is one-shot and self-contained. A fully fresh score, if wanted, is obtained by running the whole process in a fresh session.

### 5. Compute deltas

When a prior report at the same rubric version exists:

- Record per-dimension stage movement as prior stage to new stage, marked ↑, ↓, or =.
- Classify each prior evidence citation as still valid (its file path still exists and still contains the cited content) or gone stale (path gone or content substantially changed), and list the stale citations so the reader can see what shifted underneath the old score.

The deltas section exists so that weekly runs can track movement over time for the same project. When prior reports exist only at an older rubric version, the deltas section notes the rubric-version bump. When no prior sidecar at the same rubric version exists at all, the report has no deltas section and its header instead notes "baseline run; no prior report".

### 6. Emit the report and sidecar

Artifact filenames use `<date-stamp>-<project>`: the current date in `YYYY-MM-DD` form plus the basename of `target_path`. One report per project per day — a same-day rerun overwrites the same `YYYY-MM-DD-<project>.html` and `.json` files, and a same-day duplicate that must coexist uses the `YYYY-MM-DD-HHMM-<project>` form per the [naming rules](../html-report.md#naming).

**HTML report** — written to `<scores-dir>/<date-stamp>-<project>.html`, rendered by following [`./report.md`](./report.md), the harness-score HTML guide that layers the harness-score specifics onto the generic standard in [`../html-report.md`](../html-report.md).

**JSON sidecar** — written to `<scores-dir>/<date-stamp>-<project>.json`, with exactly these top-level keys:

| Key | Value |
|-----|-------|
| `schema_version` | The integer `1` |
| `rubric_version` | e.g. `"v1"` |
| `skill_version` | e.g. `"v1"` |
| `target` | The `target_path` |
| `project` | The basename |
| `generated_at` | ISO-8601 UTC timestamp, date-only or full |
| `prior_report` | The filename of the prior JSON, or `null` |
| `scores` | An array |

Each entry of the `scores` array carries exactly: `dimension_index` (integer), `dimension` (the dimension name, e.g. `"Context Engineering"`), `cluster` (e.g. `"Foundation"`), `stage` (a number such as `3.0`), `evidence` (an array of objects each with `path` and `note` keys), `rationale` (a sentence or two), and `next_stage` (the concrete suggestion).

Keys, their ordering, and their types must stay stable across runs at a given rubric version — the next run reads the sidecar to find the prior report and compute deltas. The `rubric_version` value must equal the rubric's actual version: the next run filters prior reports by it, and a mismatch breaks delta computation. If this cannot be satisfied, fail loudly rather than emit a sidecar at the wrong version.

### 7. Tell the caller

End by telling the caller (user or invoking agent) the report path in one sentence. Findings are not summarized inline — the report is the answer; give a verbal summary only if the caller asks afterward.
