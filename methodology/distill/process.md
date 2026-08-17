# Distill — process

A **rewrite** procedure for existing markdown — agent-facing or human-facing — that has grown by accretion: bloated, stale, or written for weaker models than the ones now reading it. Distill re-composes each file into only what a current reader needs. It preserves meaning, never policy: the output requires exactly what the input required, minus what is demonstrably dead.

Distill operates **per file**. A target set of many files — a directory, a glob, a repo — is a batch of independent single-file distills, each rewritten in place from its own facts. Cross-file restructuring (merging siblings, regrouping a directory, moving facts between owners) is not performed here; where the work surfaces that need, it is returned as an escalation.

Runtime operations follow [`../runtime-ports.md`](../runtime-ports.md).

## Where this fits

| Method | Verb | Scope | Question |
|--------|------|-------|----------|
| [Context review axis](../review/axes/context.md) | Report | Diff or paths | Does this agent-facing change follow the conventions? |
| [Documentation review axis](../review/axes/documentation.md) | Report | Diff | Do the public docs match the code? |
| `distill` (this process) | Rewrite | Current-state files, each independently | What is the smallest, current form of this file? |

The review axes find problems and prescribe direction without writing replacement content; distill writes the replacement. Distill is for **existing** content only — authoring a new document follows the target's authoring conventions directly.

## Roles

Two one-shot spawns of the canonical `distiller` role, each in a fresh isolated context, split the work: an **extraction pass** reduces every target file to its atomic facts, and a **composition pass** writes every replacement from those facts alone. The coordinating executor performs only mechanical operations between them — scrambling the fact files and installing the finished replacements — and never authors or alters content itself.

**Why the writer never sees the source.** A rewrite degrades into trimming whenever the source's presentation is available to imitate: its structure, section order, and sentences leak into the output even under instructions to ignore them. The composition pass therefore receives only fact lines in randomized order — it cannot inherit what it has never seen, and the scramble removes the ordering hints extraction might otherwise smuggle through. The same isolation keeps the output free of retrospective framing: a spawn with no session history has no transition to narrate. Do not substitute an inline rewrite, a fork of the current context, or a single agent playing both passes.

Every `distiller` invocation carries, before its pass-specific task, the one-shot default declared by [`../runtime-ports.md`](../runtime-ports.md#spawn-an-isolated-role), scoped to this distill operation.

## Inputs

- **Target set** — paths, a directory, or a glob whose markdown files are to be distilled, each independently.
- **Human-caller channel** — for scope confirmation, disposition rulings on uncertain facts, and the final report.
- **Workspace context** — the target's agent-context entrypoints, discoverable from the workspace root or the target repo's hub.

## Outputs

- Each target file rewritten in place, uncommitted.
- The **distillation report**: per-file measurements, disposition totals, and every escalation.

## The distillation bar

The rewrite standard every output file is held to. The target's own discovered conventions bind placement, ownership, structure, and references; this bar adds what no convention owner covers — the calibration of prose to its modern reader.

**Meaning is preserved; policy is untouched.** Distill changes how content is written, never what it requires. Reality is the authority for facts: a claim contradicted by the current code, config, or tooling is corrected or deleted after verification. But a rule that seems wrong *in substance* — too strict, too loose, misconceived — is escalated to the human caller as a finding, never silently rewritten into a different rule.

**Cut what the reader no longer needs.** Prose accretes hand-holding calibrated to the weakest model that ever read it. A current-generation agent does not need:

- procedural walkthroughs of routine operations it performs unprompted;
- restatement or "remember to" / "make sure" reinforcement of a rule already stated once;
- motivational or persuasive framing around an instruction;
- defensive enumeration of cases an intelligent reader infers from the rule;
- apologies, hedges, or meta-commentary about the document itself.

**Keep what changes behavior.** A sentence survives when it states a project-specific fact, a non-obvious or counter-intuitive constraint, a decision rule, or a *why* that future judgment will need. The test: would a competent agent with no document do this anyway? If yes, the sentence is dead weight; if no, it is load-bearing.

**Links are dependencies, not decoration.** A reference survives only when the reader must follow it to act on this document — a contract to execute, a method to apply, an owner to consult, a route to choose. Cut references that explain by analogy, cite where an idea came from, or gesture sideways at related material the reader needs no part of. The test: if the target file vanished, would this document stop working, or just lose a footnote?

**Human voice, agent density.** Output is complete, natural sentences a human colleague would write — not telegraphic fragments, keyword lists, or abbreviation soup. Density comes from selection (fewer sentences, each load-bearing), never from a compressed style that trades readability for length.

**The source is evidence, not a draft.** The original's entire presentation — its structure, section order, headings, emphasis, and sentences — is an accretion artifact that mirrors edit history, not decisions anyone made for the reader. Only its facts enter the rewrite, restated. Every element of the output's presentation is chosen fresh; any resemblance to the source is the best form happening to coincide, never inheritance.

**Name splits; don't execute them.** A file owes a split when it answers more than one reader question — when readers with different tasks each wade through the others' material to reach their own. The test: name the question each section answers; two or more distinct questions arriving with distinct readers means hub and spokes. Executing a split re-routes hubs beyond the target file, so this per-file process returns a demanded split as an escalation naming the questions and the proposed shape. The guard runs both ways: sections that all serve one reading stay together — every split charges the reader a hop.

## Coordination steps

The executor coordinating this process:

### 1. Bind the target set

Resolve the supplied target to a concrete list of markdown files. Exclude history-by-design files (changelogs, retrospectives, migration notes, post-mortems — there the history *is* the content) and generated projections (distill the canonical source instead). If the resolved set is ambiguous or surprisingly large, present it and ask the human caller before proceeding; otherwise state the set and continue. Choose a scratch directory to hold the pass artifacts — fact files and composed replacements.

### 2. Spawn the extraction pass

Spawn the canonical `distiller` role in a one-shot isolated context and await its result. The prompt must include:

1. **The isolated-role restrictions** from [Roles](#roles).
2. **The target set** — absolute paths, with the exclusions already applied — and the scratch directory.
3. **What to do** — execute the [Extraction pass](#extraction-pass) below against exactly those files.
4. **What to return** — the extraction report that pass declares. The distiller cannot reach the human caller: where the procedure raises a question, it applies the conservative default (keep the fact) and returns the question as an escalation.

Supply only the target set and these process references — never a summary of how the content came to be or what the session was doing. That history is the contamination the cold spawn exists to exclude.

### 3. Scramble

Randomize the line order of each fact file mechanically — `shuf <fact-file> -o <scrambled-file>` — keeping the ordered original for the audit trail. Only the scrambled copies go to the composition pass.

### 4. Spawn the composition pass

Spawn the `distiller` role again — fresh, one spawn for the whole batch — and await its result. The prompt must include:

1. **The isolated-role restrictions** from [Roles](#roles), plus the pass's own prohibition: the original files are off-limits — do not read, search for, or reconstruct them.
2. **Per target**: the scrambled fact file, the destination path the replacement will live at, and the consumption-surface classification from extraction.
3. **The convention-owner paths** extraction discovered, and the scratch directory to write replacements into.
4. **What to do** — execute the [Composition pass](#composition-pass) below.
5. **What to return** — the composition report that pass declares, with questions escalated under the same no-human-channel rule.

### 5. Install the replacements

Copy each composed file over its target verbatim. Installation is mechanical — the executor does not adjust content while copying.

### 6. Close with an independent review

Run a fresh context review of the installed files through the [review process](../review/process.md) (`axis: context`, paths scope); when public documentation was touched, run the `documentation` axis over those paths as well.

Fold must-fix findings back in by spawning the [fold-in variant](#fold-in-variant) of the composition pass — never by editing inline. Each fold-in cycle ends by installing the revised replacements exactly as in step 5, so the next review — and the final report — always describe what is on disk. Cap this at two fold-in cycles; unresolved findings after that go to the human caller.

### 7. Report

Deliver the [distillation report](#the-distillation-report) to the human caller.

## Extraction pass

Executed by the `distiller` role against the caller-supplied target set.

### 1. Discover the governing conventions

Follow the workspace and target agent-context entrypoints to the declared owners of authoring, placement, naming, and reference conventions. Those owners bind the rewrite; return their paths so the caller can hand them to the composition pass. Where a needed convention is unowned or two owners conflict, record the gap as an escalation and proceed on the distillation bar alone — do not invent a convention.

### 2. Classify each file by consumption surface

Classify agent-facing files with [`../review/agent-context-surface.md`](../review/agent-context-surface.md); classify the rest as human-facing (README, docs site, guides). The surface sets the stakes:

- **Always-loaded** entrypoints (workspace/repo instruction files and everything they import) are paid for on every request — distill these hardest.
- **Routed** context and methodology docs are paid for when their trigger fires — optimize for the reader who arrived with that one question.
- **Definitions** (agents, skills, commands) are both routed prose and runtime configuration — their frontmatter and references must stay valid from the installed location.
- **Human-facing** docs keep a narrative allowance agent docs don't get, but every ownership and duplication rule still applies.

### 3. Measure the baseline

Record lines and words per file (`wc -l -w`). The report needs before/after evidence, not impressions.

### 4. Reduce each file to fact lines

Write one fact file per target into the caller's scratch directory. Walk the target and assign every span a disposition:

| Disposition | Meaning |
|-------------|---------|
| `extract` | Current and load-bearing — becomes exactly one fact line |
| `pointer` | Owned by another document — becomes one line stating the read-trigger and the owner's path |
| `delete-historical` | Retrospective framing, superseded behavior, change narrative — no line |
| `delete-obsolete` | Describes something that no longer exists — verified against the code, config, or tool first; no line |
| `delete-for-reader` | Hand-holding the bar names as dead weight for a current reader — no line |
| `escalate-structural` | Load-bearing but owed to another file (merge, relocation, split material) — line kept in place, plus an escalation |

A fact line is atomic and self-contained: one fact, **restated in your own words**, understandable without its neighbors — never a quoted or lightly reworded span, because inherited sentences become sentences the output inherits, defeating the composition pass. Frontmatter and other runtime configuration are facts too: capture the keys and their exact values. The fact file carries nothing else — no headings, numbering, grouping, or blank lines; any structural hint leaks the source's shape into a pass that must not see it.

Two duties guard the destructive dispositions. `delete-obsolete` requires checking the code, config, or tool the span describes — staleness is verified, not assumed. And any span whose load-bearing status is genuinely uncertain gets a fact line and an escalation, not a bin.

### 5. Return the extraction report

Per file: the fact-file path, baseline measurements, and disposition counts. Plus, once for the batch: the convention-owner paths, the surface classifications, a summary of every deleted span so the drops are auditable, and every escalation.

## Composition pass

Executed by a fresh `distiller` spawn. Its whole world is the caller-supplied inputs: per target, a scrambled fact file, a destination path, and a surface classification, plus the convention owners and the scratch directory. The [fold-in variant](#fold-in-variant) below is the only extension of that world. **The originals are off-limits** — every fact available for the rewrite is a line in a fact file.

### 1. Read the conventions

Read the supplied convention owners; together with the [distillation bar](#the-distillation-bar), they bind structure, naming, and references.

### 2. Compose each file

For each target independently, compose a whole replacement file from its fact lines alone. Grouping, ordering, and headings are yours to choose from what the facts need — the scrambled input carries no structure on purpose. Runtime-configuration lines land in frontmatter with their exact values; everything else is prose to the bar. Write each replacement into the scratch directory in a single whole-file write, never as accumulated edits.

### 3. Verify each file

- **Coverage**: every fact line is represented in the output exactly once — the check that makes blind composition safe. A line that cannot be placed is still included, flagged as an escalation.
- **References**: every reference resolves from the destination path (the installed or projected location, not the scratch directory).
- **Measurements**: record lines and words (`wc -l -w`) per composed file.

### 4. Return the composition report

Per file: after-measurements, a one-line statement of the structure chosen, coverage confirmation, and any fact line that was ambiguous to place with how it was resolved. Plus every escalation, including splits the divergence test demanded.

### Fold-in variant

A fold-in spawn revises replacements against review findings instead of composing from nothing. Its world extends the pass's inputs by exactly two items: each target's current replacement, and the must-fix findings that name it; everything else carries over unchanged, including the off-limits originals. Findings direct structure, wording, and references — the fact files remain the only source of facts, and a finding that would change what a fact requires is escalated, not applied. Verify each revised file as in step 3, and extend the report with a per-finding statement of how it was resolved.

## The distillation report

The executor assembles, from both pass reports and the review:

- **Per file**: before → after lines/words.
- **Disposition totals**: span counts by disposition and the extraction pass's deleted-span summary, so the cuts are auditable.
- **Review outcome**: findings from the independent review and how each was resolved.
- **Escalations**: every uncertain-fact question, suspected-wrong rule, convention gap, and cross-file structural recommendation (merge, relocation, split), for the human to rule on.
- **Not committed** — the human caller decides when to commit (suggest the `commit` operation).
- **Behavioral-eval note**: when the target harness declares a behavioral eval for context changes, a distill of always-loaded or routed files owes it — name it as owed.
