# Harness score — process

A **codebase-scoped** maturity scoring procedure: gather evidence, apply the frozen rubric at [`./rubric.md`](./rubric.md), and emit an HTML report plus a JSON sidecar under `~/.claude/winter/harness-scores/`. If a prior report exists for the same project at the same rubric version, the new report includes a deltas section so weekly runs can track movement.

Designed to be executed by any agent — whether reached via the `/wf-harness-score` slash command or invoked directly by another agent (e.g., a `/wf-blizzard` snowflake) that wants scoring as a substep. The skill at [`../../skills/harness-score/SKILL.md`](../../skills/harness-score/SKILL.md) is a thin entry point that hands execution to this document.

## Where this fits

| Skill | Scope | Question |
|-------|-------|----------|
| [`/cold-review`](../../skills/cold-review/SKILL.md) | Diff | Is the code architecturally sound? |
| [`/harness-review`](../../skills/harness-review/SKILL.md) | Diff | Does the harness keep pace with the change? |
| `/harness-score` (this process) | Whole codebase | Where on the maturity matrix is this codebase **today**? |

This process takes **no arguments**. The only target is the current working directory.

## Process

### 1. Resolve identity and report directory

```bash
project="$(basename "$PWD")"
report_dir="$HOME/.claude/winter/harness-scores"
mkdir -p "$report_dir"
date_stamp="$(date +%Y-%m-%d)"
```

`<project>` is `basename "$PWD"`. The report directory lives under the user's `~/.claude/` tree, **not** inside the target's working copy — scores are personal artifacts, not deliverables.

### 2. Find the prior report (if any)

Look for `~/.claude/winter/harness-scores/*-<project>.json` and pick the most recent **of the same rubric version** as this run. Sort by filename (the date prefix sorts chronologically). If none exist, skip the deltas section entirely. If older reports exist at a different rubric version, ignore them for delta purposes and note the version-bump in the report's deltas section.

```bash
ls "$report_dir"/*-"$project".json 2>/dev/null | sort | tail -n 5
```

### 3. Load the rubric

Read [`./rubric.md`](./rubric.md). It is **frozen** at the version recorded in its header. Do not improvise dimensions or stage criteria — score against what is written. If the rubric does not fit the target well, that is a v2 conversation (a deliberate edit + version bump in a future change), not a scoring-run conversation.

### 4. Spawn an `explorer` for evidence

Spawn an `explorer` subagent (see [`../../agents/explorer.md`](../../agents/explorer.md)). The explorer's job is **evidence gathering, not scoring**. The main agent (you) does the scoring.

Prepend this coordination preamble verbatim before the role-specific content:

> You are operating as a one-shot agent spawned to gather harness-score evidence. No shared task list exists. Report results to your caller via your final response only — do not call `SendMessage`, `TaskCreate`, or `TaskUpdate`. When your task is done, stop. **Do not write or edit any documentation, and do not ask the caller to spawn `context-reviewer` afterwards** — your default body's "Documentation Integration" guidance does not apply here; this run is read-only evidence gathering, not authoring.

The role-specific content must include:

1. **Goal** — produce an inventory of **evidence** (file paths, command outputs, doc references) for each of the 10 dimensions in the rubric. Not stages, not scores. Evidence.
2. **The full rubric** — read [`./rubric.md`](./rubric.md) and walk each dimension's diagnostic questions and "evidence to look for" lists.
3. **Scope** — the target is the current working directory (`$PWD`). Search the repo, the docs (any `ai/`, `docs/`, `AGENTS.md`, `CLAUDE.md`, `README.md`, `CONTRIBUTING.md`), the configs (`.pre-commit-config.yaml`, `pyproject.toml`, linter configs), and the git history (`git log`, `git log --oneline`) as appropriate per dimension. Adapt to whatever documentation cluster the target actually uses; do not assume a specific convention.
4. **Output shape** — for each dimension, a short bullet list of evidence with file paths or `git log` outputs. If a dimension has no evidence, say so explicitly.
5. **Stop** — do not propose stages. Scoring is the main agent's job.

Spawn in the foreground; you need the inventory before you can score.

### 5. Apply the rubric

For each of the 10 dimensions, decide:

- **Stage** — 1 to 5. Half-stages (e.g., 3.5) are allowed when evidence straddles two stages. When in doubt, pick the lower stage and explain.
- **Evidence** — 1 to 3 citations from the explorer's inventory. Each citation is a file path + a one-sentence description of what it shows. If you cannot point at a file (or a command output), the evidence does not exist for scoring purposes.
- **Rationale** — 1 to 2 sentences explaining the stage choice given the evidence.
- **Next-stage suggestion** — one concrete change: one file, one tool, one PR. Not "improve documentation"; write something the target project's maintainer could act on in an afternoon.

Follow the rubric's scoring rules verbatim (see [`./rubric.md#scoring-rules`](./rubric.md#scoring-rules)). They are the single source of truth — do not paraphrase or tighten them here.

### 6. Compute deltas (if a prior report exists)

If step 2 found a prior JSON sidecar at the same rubric version, compare:

- **Per-dimension stage movement** — `prior_stage → new_stage`. Mark `↑`, `↓`, or `=`.
- **Evidence still valid** — citations whose file paths still exist and still contain the cited content.
- **Evidence gone stale** — citations whose file paths no longer exist or whose content has changed substantially. List them so the reader can see what shifted underneath the old score.

If no prior report exists, the report has no deltas section — note "baseline run; no prior report" in the header instead.

### 7. Render the HTML report

Render the report following [`./report.md`](./report.md) — the harness-score HTML guide, which applies the generic standard in [`../llm-html-output.md`](../llm-html-output.md) and adds the harness specifics (Tailwind config, cluster colors, score-color bands, and the sidebar / profile-table / per-dimension-card structure).

Write to `$report_dir/<date_stamp>-<project>.html`.

### 8. Write the JSON sidecar

Write to `$report_dir/<date_stamp>-<project>.json`. Schema (stable across runs at this rubric version):

```json
{
  "schema_version": 1,
  "rubric_version": "v1",
  "skill_version": "v1",
  "target": "<absolute path to $PWD>",
  "project": "<basename>",
  "generated_at": "<ISO-8601 timestamp, UTC, date-only or full>",
  "prior_report": "<filename of prior JSON or null>",
  "scores": [
    {
      "dimension_index": 1,
      "dimension": "Context Engineering",
      "cluster": "Foundation",
      "stage": 3.0,
      "evidence": [
        {"path": "CLAUDE.md", "note": "single root index, last touched 2026-05-19"}
      ],
      "rationale": "Human-maintained index with manual loading; no progressive disclosure structure yet.",
      "next_stage": "Add a per-cluster doc directory and link it from CLAUDE.md."
    }
  ]
}
```

The sidecar is what the next run reads in step 2 to compute deltas. Keep keys, ordering, and types stable.

### 9. Report the path

Tell the caller (the user, or the agent that invoked this process) the report path in one sentence. Example:

> Report written to `~/.claude/winter/harness-scores/2026-05-25-winter-workflow.html` (sidecar JSON alongside).

Do not summarize the findings inline — the report **is** the answer. If the caller asks for a verbal summary, give one then; do not pre-empt their attention with a wall of text.

## Operational rules

The **scoring rules** (evidence-required, no averaging, half-stages, concrete next-stage suggestions, frozen rubric, documented-but-unenforced does not exceed stage 3) live in [`./rubric.md#scoring-rules`](./rubric.md#scoring-rules). Read them there as part of step 5. The rules below are **operational** rules specific to running this process.

- **One report per run per day.** Re-running on the same day overwrites the same `YYYY-MM-DD-<project>.{html,json}` files. For same-day duplicates, use the `YYYY-MM-DD-HHMM-<project>` suffix per [`../llm-html-output.md#naming`](../llm-html-output.md#naming).
- **Sidecar `rubric_version` must equal this rubric's version.** Step 8's JSON `rubric_version` is read by step 2 of the next run to filter prior reports. Mismatches break delta computation; if you cannot satisfy this, fail loudly rather than emit a sidecar at the wrong version.
- **No assumptions about the target's documentation convention.** This process is meant to work against any codebase. Where this document mentions `ai/`, `docs/`, `AGENTS.md`, etc., treat them as examples — the explorer should map them to whatever the target actually uses.

## Why "cold" doesn't apply here

`/cold-review` and `/harness-review` spawn a subagent with no session memory specifically to avoid absorbing author framing. Harness scoring is different — it scores a codebase, not a diff, and the scoring step itself is a deliberate exercise in judgment that benefits from the caller's framing of why they care. The explorer that gathers evidence is one-shot and self-contained; the main agent that scores reads the explorer's inventory plus the conversation. If a fully cold score is wanted, run the process in a fresh session.
