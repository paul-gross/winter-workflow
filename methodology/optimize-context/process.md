# Optimize context — process

An **audit-and-apply** procedure for an agent session's standing context cost — the memory files and skill descriptions
loaded before any work begins, the agent definitions loaded when a subagent is spawned, and how often each installed
skill and subagent is actually invoked. It measures, classifies, and recommends; the only file it ever writes is a
`settings.json`'s `skillOverrides` key, and only the subset the operator approves.

Runtime operations follow [`../runtime-ports.md`](../runtime-ports.md).

## Where this fits

| Method                                       | Verb            | Scope                                   | Question                                                                    |
| -------------------------------------------- | --------------- | --------------------------------------- | --------------------------------------------------------------------------- |
| [Harness score](../harness-score/process.md) | Score           | Whole codebase, 10-dimension rubric     | Where does the codebase sit on the maturity matrix?                         |
| `optimize-context` (this process)            | Measure + apply | One target's standing context footprint | What does every session pay before work begins, and is it earning its keep? |
| [Distill](../distill/process.md)             | Rewrite         | One markdown file at a time             | What is the smallest, current form of this file?                            |

This process never rewrites markdown itself — an oversized memory file or skill description it finds is a finding for
[Distill](../distill/process.md), and a convention violation it finds is a finding for the
[context review axis](../review/axes/context.md). It writes exactly one kind of artifact: an operator-approved
`skillOverrides` merge.

## The measurement script

[`../../scripts/context-usage.py`](../../scripts/context-usage.py) is the deterministic, stdlib-only, read-only half of
this process; this document owns the judgment built on top of its output — presenting the two scopes, classifying
never-invoked entries, drafting recommendations, and applying only what the operator approves. Never restate its
counting, sizing, or schema by hand; invoke it and read its JSON.

Resolve `<script>` below to the absolute on-disk path of `scripts/context-usage.py` in this repo's own checkout — the
script lives at the repo root, not beside this document, so resolve it independently of wherever this file was read
from.

```bash
python3 <script> measure --target <target_path> [--transcripts-dir <dir>] [--too-new-days <n>]
```

Run `python3 <script> measure --help` for the full flag reference; `--target` is the only required one.

## Inputs

- **`target_path`** — the codebase or workspace root to audit, supplied by the caller. The executor's working directory
  never selects the target on its own; a caller that wants "the current directory" resolves that itself before invoking
  this process.
- **Human-caller channel** — for the approval gate and the settings-file confirmation in step 5.

## Outputs

- The **findings report** delivered to the human caller (step 3).
- Zero or more **restructuring findings** named for `distill` / `context-review`, never acted on directly (step 3).
- A **`skillOverrides` merge**, written to exactly one settings file, containing exactly the operator-approved entries
  (step 6) — the only file mutation this process performs.

## Steps

### 1. Resolve the target

Bind `target_path` to the supplied value. Confirm it exists and is readable before proceeding; a missing or unreadable
target stops the process rather than falling back to a guessed path.

### 2. Run the measurement script

Invoke the script exactly as shown in [The measurement script](#the-measurement-script) against `target_path`, and parse
its JSON stdout. A non-zero exit or unparseable stdout stops the process here — report the script's stderr to the human
caller rather than improvising a partial audit.

Read `transcripts.evidence_note` before anything else in the report: `null` means full evidence: every scanned session
was readable. Any other value — including when `transcripts.available` is `false` — means the invocation counts below
are partial or absent, and carry that forward explicitly in steps 3 and 4 rather than treating a zero count as a
confirmed zero.

### 3. Report the two scopes separately

Present the script's output to the human caller as two clearly labeled sections — never blend them into one number:

**Machine-global — invocation counts.** Per-skill (`invocations.total`) and per-subagent counts, drawn from every local
session transcript on this machine, not just ones touching `target_path`. State `sessions_scanned`,
`sessions_unreadable`, and `directories_unreadable` so the caller can judge both the sample size and the evidence
quality, and state the transcript window (`oldest_session_at` to `newest_session_at`) so the caller can see how far back
the evidence actually reaches — an entry older than that window is not "confirmed zero over its full lifetime," only
"zero within the window scanned." Flag plainly whenever `evidence_note` is non-null.

**Target-scoped — always-loaded surfaces.** The inventory's `memory_files`, `hub_files`, `agents`, and `skills` entries
with their per-file byte sizes, and the `totals` block. Report `always_loaded_bytes` (skill descriptions, memory files,
and the hub — what every session opened at `target_path` actually pays) separately from `agent_definition_bytes` (paid
only when that agent is spawned) — never combine the two into one figure. Never attribute a machine-global count to this
section — the inventory answers "what does this target load," the counts answer "how often was it used," and only the
classification step in step 4 joins them.

Within the inventory, call out anything that reads as bloated on its own terms per `canon:auto-load-tax` and
`canon:admission-test` as a **restructuring finding**: name the file and the concern, and route it to `distill` (if the
fix is compression) or `context-review` (if the fix is a conventions violation) by naming the skill and the path. Do not
edit, rewrite, or summarize-in-place any of these files yourself; naming the finding is the whole job here.

### 4. Classify and draft recommendations

Walk `classification.never_invoked_skills` and `classification.never_invoked_agents`. For each entry:

- **`too_new_to_judge: true`** — report it as too new to judge, not as dead. State its `age_days` and the
  `--too-new-days` threshold so the caller can see why it was spared.
- **`too_new_to_judge: false` and `note` is `null`** — full evidence backs the zero. This is a candidate for a
  `skillOverrides` entry, keyed by the entry's `installed_name`. Draft a proposed value defaulting to the report's
  `default_override_value` (a human typing the slash command by name still works; only model-invocation routing on its
  description is turned off), so the standing cost measured for that skill's description drops to zero without removing
  the capability. Only propose a stricter value (`off`, or narrowing to `name-only`) when the human caller asks for it
  explicitly — the default is the conservative one.
- **`too_new_to_judge: false` and `note` is non-`null`** — the zero is not confirmed; report it as a finding with the
  `note` text, not as a `skillOverrides` candidate.
- **`too_new_to_judge: null`** (no git history to date it against) — report the entry with a note that it could not be
  dated, and do not draft a recommendation for it; classification needs a date to be trustworthy.

Subagents never get a `skillOverrides` entry — that key applies to skills only. A never-invoked agent is reported as a
finding for the human caller to act on directly; this process recommends nothing for it and writes nothing for it.

Present every draft as a table: skill name, current invocation total, age, and proposed override value. This is a
proposal, not a decision — nothing is written yet.

### 5. Get operator approval and resolve the settings file

Through the **ask the human caller** operation, present the draft table from step 4 and get an explicit approved subset
— which entries to write, and at what value (the caller may accept the default, pick a stricter value per entry, or drop
an entry entirely). Also confirm which settings file receives the merge: default the suggestion to
`<target_path>/.claude/settings.json` when `<target_path>/.claude/` exists (a project-scoped install), otherwise
`~/.claude/settings.json` (the user-level default) — but always state the resolved path and get it confirmed rather than
writing silently, since this key can affect every session opened against that scope. If no human-caller channel is
available, return `unsupported-capability` rather than writing anything.

Stop here without writing anything if the human caller approves no entries, or defers the decision.

### 6. Apply only the approved subset

First run with `--dry-run` and show the operator the exact `applied` delta the write will produce:

```bash
echo '<approved-entries-json>' | python3 <script> apply --settings <resolved-settings-path> --overrides - --dry-run
```

Once confirmed, run the same command without `--dry-run` to write it. The script merges into the file's existing
`skillOverrides` key without touching any other key, and creates the file (with only that key) if it does not exist yet.
Never pass the full draft table from step 4 — only the entries the human caller approved in step 5, at the values they
approved.

### 7. Report

Close with a summary to the human caller: the two-scope findings from step 3, every restructuring finding named for
`distill` / `context-review`, the classification table from step 4, and exactly which `skillOverrides` entries were
written (or, if none were approved, that nothing was written).
