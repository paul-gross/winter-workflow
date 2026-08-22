# Distill — process

A **rewrite** procedure for existing markdown — agent-facing or human-facing — that has grown by accretion: bloated,
stale, or written for weaker models than the ones now reading it. Distill re-composes each file into only what a current
reader needs. It preserves meaning, never policy: the output requires exactly what the input required, minus what is
demonstrably dead.

Distill operates **per file**. A target set of many files — a directory, a glob, a repo — is a batch of independent
single-file distills, each rewritten in place from its own facts. Cross-file restructuring (merging siblings, regrouping
a directory, moving facts between owners) is not performed here; where the work surfaces that need, it is returned as an
escalation.

Runtime operations follow [`../runtime-ports.md`](../runtime-ports.md).

## Where this fits

| Method                                                       | Verb    | Scope                                   | Question                                              |
| ------------------------------------------------------------ | ------- | --------------------------------------- | ----------------------------------------------------- |
| [Context review axis](../review/axes/context.md)             | Report  | Diff or paths                           | Does this agent-facing change follow the conventions? |
| [Documentation review axis](../review/axes/documentation.md) | Report  | Diff                                    | Do the public docs match the code?                    |
| `distill` (this process)                                     | Rewrite | Current-state files, each independently | What is the smallest, current form of this file?      |

The review axes find problems and prescribe direction without writing replacement content; distill writes the
replacement. Distill is for **existing** content only — authoring a new document follows the target's authoring
conventions directly.

## Roles

Two one-shot spawns of the canonical `distiller` role, each in a fresh isolated context, split the work: an **extraction
pass** reduces every target file to its atomic facts, and a **composition pass** writes every replacement from those
facts alone. The coordinating executor performs only mechanical operations between them — scrambling the fact files and
installing the finished replacements — and never authors or alters content itself.

**Why the writer never sees the source.** A rewrite degrades into trimming whenever the source's presentation is
available to imitate: its structure, section order, and sentences leak into the output even under instructions to ignore
them. The composition pass therefore receives only fact lines in randomized order — it cannot inherit what it has never
seen, and the scramble removes the ordering hints extraction might otherwise smuggle through. The same isolation keeps
the output free of retrospective framing: a spawn with no session history has no transition to narrate. Do not
substitute an inline rewrite, a fork of the current context, or a single agent playing both passes.

Every `distiller` invocation carries, before its pass-specific task, the one-shot default declared by
[`../runtime-ports.md`](../runtime-ports.md#spawn-an-isolated-role), scoped to this distill operation.

## Inputs

- **Target set** — paths, a directory, or a glob whose markdown files are to be distilled, each independently.
- **Reader question, per target** — the one question a reader arrives at this file asking. Bind it from the routing
  entry that sends readers here (a hub's "read when…" cell), or from the caller. It is what the bar's load-bearing test
  is applied *against*: without it every span looks potentially useful, and the pass defaults to keeping all of them.
- **Cut target, per target** — the share of the baseline the extracted facts must fit within. Set it from the file's
  density (see [Setting the cut target](#setting-the-cut-target)); it is what converts per-span classification into
  ranking, and it is the difference between a distill and a reformat.
- **Human-caller channel** — for scope confirmation, disposition rulings on uncertain facts, and the final report.
- **Workspace context** — the target's agent-context entrypoints, discoverable from the workspace root or the target
  repo's hub.

## Outputs

- Each target file rewritten in place, uncommitted.
- The **distillation report**: per-file measurements, disposition totals, and every escalation.

## The distillation bar

The rewrite standard every output file is held to. The target's own discovered conventions bind placement, ownership,
structure, and references; this bar adds what no convention owner covers — the calibration of prose to its modern
reader.

**Meaning is preserved; policy is untouched.** Distill changes how content is written, never what it requires. Reality
is the authority for facts: a claim contradicted by the current code, config, or tooling is corrected or deleted after
verification. But a rule that seems wrong *in substance* — too strict, too loose, misconceived — is escalated to the
human caller as a finding, never silently rewritten into a different rule.

**Cut the padding.** Prose accretes hand-holding calibrated to the weakest model that ever read it. A current-generation
reader does not need:

- procedural walkthroughs of routine operations it performs unprompted;
- restatement or "remember to" / "make sure" reinforcement of a rule already stated once;
- motivational or persuasive framing around an instruction, or justification for why a feature exists;
- defensive enumeration of cases an intelligent reader infers from the rule;
- apologies, hedges, or meta-commentary about the document's own structure;
- editorial asides about what readers find confusing, as distinct from the disambiguation itself;
- a clause restating the clause immediately before it in different words.

**Cut what the reader already knows.** Distinct from padding, and the harder cut: prose that is true, stated once, free
of framing, and still not worth stating, because a competent reader arrives already knowing it. Telling a code reviewer
to look for defects; noting that a log does not repair what it records, that a read-only view cannot mutate, that an
idempotent call is safe to repeat when that is simply what idempotent means. Nothing marks these as filler — they read
as sober technical statements, which is exactly why they survive pass after pass and accumulate.

**Cut what does not exist yet.** Planned work, deferred gaps, and known limitations nobody is acting on are a roadmap
leaking into a reference. They read as candor and are usually accurate, which is why they survive; but a reader acting
on this file cannot act on them, and they rot silently, because nothing breaks when the plan changes. Prose about a
future state belongs wherever that work is tracked, not in the document describing the present one.

**Cut what the reader cannot act on.** True, non-obvious, and still inert: an implementation detail that no decision
turns on, an internal mechanism the reader neither configures nor observes. This is the residue of authors documenting
what they found interesting to build rather than what a reader needs to proceed, and it is the hardest deletion to
argue, because every individual sentence defends itself as accurate and non-trivial. Accuracy was never the bar.

The test for all four is the target's **reader question**, not abstract merit: if the reader acts correctly on this file
without the span, the span is dead weight, however true it is.

**Keep what changes behavior.** A sentence survives when it states a project-specific fact, a non-obvious or
counter-intuitive constraint, a decision rule, or a *why* that future judgment will need. The test: would a competent
agent with no document do this anyway? If yes, the sentence is dead weight; if no, it is load-bearing.

**A runnable surface outranks prose about it.** Where a reader can execute something — a `--help` contract, a config
scaffold the tool writes, a generated API spec — that surface is authoritative and cannot go stale, and prose restating
it is a second copy that can. Cite the surface instead of restating routine flag lists, per-flag defaults, exhaustive
status-code enumerations, and field-by-field shapes. What survives as prose is only what running the surface would not
tell you: why a default is what it is, which of two similar commands to reach for, a consequence spanning components, a
constraint the surface does not state.

**Links are dependencies, not decoration.** A reference survives only when the reader must follow it to act on this
document — a contract to execute, a method to apply, an owner to consult, a route to choose. Cut references that explain
by analogy, cite where an idea came from, or gesture sideways at related material the reader needs no part of. The test:
if the target file vanished, would this document stop working, or just lose a footnote?

**Human voice, agent density (HVAD).** Output is complete, natural sentences a human colleague would write — not
telegraphic fragments, keyword lists, or abbreviation soup. Density comes from selection (fewer sentences, each
load-bearing), never from a compressed style that trades readability for length.

**The source is evidence, not a draft.** The original's entire presentation — its structure, section order, headings,
emphasis, and sentences — is an accretion artifact that mirrors edit history, not decisions anyone made for the reader.
Only its facts enter the rewrite, restated. Every element of the output's presentation is chosen fresh; any resemblance
to the source is the best form happening to coincide, never inheritance.

**Name splits; don't execute them.** A file owes a split when it answers more than one reader question — when readers
with different tasks each wade through the others' material to reach their own. The test: name the question each section
answers; two or more distinct questions arriving with distinct readers means hub and spokes. Executing a split re-routes
hubs beyond the target file, so this per-file process returns a demanded split as an escalation naming the questions and
the proposed shape. The guard runs both ways: sections that all serve one reading stay together — every split charges
the reader a hop.

## Coordination steps

The executor coordinating this process:

### 1. Bind the target set, the readers, and the cut targets

Resolve the supplied target to a concrete list of markdown files. Exclude history-by-design files (changelogs,
retrospectives, migration notes, post-mortems — there the history *is* the content) and generated projections (distill
the canonical source instead). If the resolved set is ambiguous or surprisingly large, present it and ask the human
caller before proceeding; otherwise state the set and continue. Choose a scratch directory to hold the pass artifacts —
fact files and composed replacements.

Then bind, per file, the **reader question** and the **cut target** the extraction pass will be held to, and state both
to the human caller with the set. Both are inputs the pass cannot derive for itself: the reader question usually already
exists in whatever routes readers to the file, and the cut target follows from density.

#### Setting the cut target

Vary it per file; a single number across a set optimizes the average and wrecks the tails. Judge density by how much of
the file a competent reader could reconstruct unaided:

- **Reference-heavy** — flag lists, defaults, field shapes, much of it restating a runnable surface. Expect the largest
  reduction.
- **Standard** — procedure and configuration prose mixed with genuine constraints.
- **Hard-won** — dense operational fact where most sentences carry a constraint, an ordering requirement, or a
  consequence learned from a real failure. Ask for a modest reduction and expect the runnable-surface rule, not
  deletion, to supply most of it.

A target is a forcing function, not a quota. A pass that cannot meet one without dropping something load-bearing says
so, names the facts at issue, and overruns deliberately — an undeclared overrun is the failure this input exists to
prevent, and so is meeting the number by cutting protected material.

### 2. Spawn the extraction pass

Spawn the canonical `distiller` role in a one-shot isolated context and await its result. The prompt must include:

1. **The isolated-role restrictions** from [Roles](#roles).
2. **The target set** — absolute paths, with the exclusions already applied — and the scratch directory.
3. **What to do** — execute the [Extraction pass](#extraction-pass) below against exactly those files.
4. **What to return** — the extraction report that pass declares. The distiller cannot reach the human caller: where the
   procedure raises a question it resolves it by the two-direction rule in
   [Reduce each file to fact lines](#4-reduce-each-file-to-fact-lines) — technical doubt keeps, reader-value doubt cuts
   — and returns the question as an escalation either way.

Supply only the target set and these process references — never a summary of how the content came to be or what the
session was doing. That history is the contamination the cold spawn exists to exclude.

### 3. Scramble

Randomize the line order of each fact file mechanically — `shuf <fact-file> -o <scrambled-file>` — keeping the ordered
original for the audit trail. Only the scrambled copies go to the composition pass.

### 4. Spawn the composition pass

Spawn the `distiller` role again — fresh, one spawn for the whole batch — and await its result. The prompt must include:

1. **The isolated-role restrictions** from [Roles](#roles), plus the pass's own prohibition: the original files are
   off-limits — do not read, search for, or reconstruct them.
2. **Per target**: the scrambled fact file, the destination path the replacement will live at, and the
   consumption-surface classification from extraction.
3. **The convention-owner paths** extraction discovered, and the scratch directory to write replacements into.
4. **What to do** — execute the [Composition pass](#composition-pass) below.
5. **What to return** — the composition report that pass declares, with questions escalated under the same
   no-human-channel rule.

### 5. Install the replacements

Copy each composed file over its target verbatim. Installation is mechanical — the executor does not adjust content
while copying.

### 6. Close with an independent review

Run a fresh context review of the installed files through the [review process](../review/process.md) (`axis: context`,
paths scope); when public documentation was touched, run the `documentation` axis over those paths as well.

Fold must-fix findings back in by spawning the [fold-in variant](#fold-in-variant) of the composition pass — never by
editing inline. Each fold-in cycle ends by installing the revised replacements exactly as in step 5, so the next review
— and the final report — always describe what is on disk. Cap this at two fold-in cycles; unresolved findings after that
go to the human caller.

### 7. Report

Deliver the [distillation report](#the-distillation-report) to the human caller.

## Extraction pass

Executed by the `distiller` role against the caller-supplied target set.

### 1. Discover the governing conventions

Follow the workspace and target agent-context entrypoints to the declared owners of authoring, placement, naming, and
reference conventions. Those owners bind the rewrite; return their paths so the caller can hand them to the composition
pass. Where a needed convention is unowned or two owners conflict, record the gap as an escalation and proceed on the
distillation bar alone — do not invent a convention.

### 2. Classify each file by consumption surface

Classify agent-facing files with [`../review/agent-context-surface.md`](../review/agent-context-surface.md); classify
the rest as human-facing (README, docs site, guides). The surface sets the stakes:

- **Always-loaded** entrypoints (workspace/repo instruction files and everything they import) are paid for on every
  request — distill these hardest.
- **Routed** context and methodology docs are paid for when their trigger fires — optimize for the reader who arrived
  with that one question.
- **Definitions** (agents, skills, commands) are both routed prose and runtime configuration — their frontmatter and
  references must stay valid from the installed location.
- **Human-facing** docs keep a narrative allowance agent docs don't get, but every ownership and duplication rule still
  applies.

### 3. Measure the baseline

Record lines and words per file (`wc -l -w`). The report needs before/after evidence, not impressions.

### 4. Reduce each file to fact lines

Write one fact file per target into the caller's scratch directory. Walk the target and assign every span a disposition,
then hold the result to the file's cut target — ranking the surviving facts by how much the reader's success at the
stated question degrades without each one, and cutting from the bottom until they fit. Ranking is what the target buys:
classifying spans one at a time asks "is this useful?", which almost everything passes, while ranking asks "is this
worth more than what it displaces?", which is the question that actually discriminates.

| Disposition           | Meaning                                                                                                            |
| --------------------- | ------------------------------------------------------------------------------------------------------------------ |
| `extract`             | Current and load-bearing — becomes exactly one fact line                                                           |
| `pointer`             | Owned elsewhere — another document, or a surface the reader can run — becomes one line naming trigger and owner    |
| `delete-historical`   | Retrospective framing, superseded behavior, change narrative — no line                                             |
| `delete-obsolete`     | Describes something that no longer exists — verified against the code, config, or tool first; no line              |
| `delete-for-reader`   | Padding — framing, restatement, meta-commentary, hand-holding the bar names as dead weight — no line               |
| `delete-obvious`      | True and unpadded, but the reader already knows it; supplied by their competence, not this file — no line          |
| `delete-speculative`  | About what does not exist yet — planned work, deferred gaps, known limitations nobody is acting on — no line       |
| `delete-unactionable` | True, non-obvious, and still changes nothing the reader decides or does — no line                                  |
| `escalate-structural` | Load-bearing but owed to another file (merge, relocation, split material) — line kept in place, plus an escalation |

A fact line is atomic and self-contained: one fact, **restated in your own words**, understandable without its neighbors
— never a quoted or lightly reworded span, because inherited sentences become sentences the output inherits, defeating
the composition pass. Atomic means self-contained, **not maximally split**. Composition represents every fact line
exactly once, so the fact file is a list of obligations: a clause repeated across N lines becomes prose repeating it N
times. State a convention that covers several subjects once, scoped to all of them, rather than once per subject; and
let a line carry a bounded enumeration where the enumeration *is* the fact, rather than splitting a closed three-item
set into three lines. Before finishing a fact file, re-read it for lines asserting the same thing twice and merge them.
Frontmatter and other runtime configuration are facts too: capture the keys and their exact values. The fact file
carries nothing else — no headings, numbering, grouping, or blank lines; any structural hint leaks the source's shape
into a pass that must not see it.

Two duties guard the destructive dispositions. `delete-obsolete` requires checking the code, config, or tool the span
describes — staleness is verified, not assumed. And uncertainty resolves in **two different directions** depending on
what is uncertain. When the doubt is *technical* — whether a claim is still true, whether some caller depends on it,
whether the constraint bites in a case you cannot check — the span gets a fact line and an escalation, not a bin. When
the doubt is only about *reader value* — the fact is plainly true, you are unsure the reader needs it told — it is cut.
Collapsing these two into one conservative "keep" is what turns a distill into a reformat: reader-value doubt attaches
to nearly every span, so a single keep-when-unsure default retains nearly everything.

`delete-obvious` is separated from `delete-for-reader` because a single bin for both never gets used for both. Padding
announces itself — a recap paragraph, a "worth noting that", a lead-in — so a pass fills the bin with those, records a
respectable count, and never runs the harder test at all. Obviousness has no such tell: the span is sober, accurate, and
indistinguishable from signal except by asking what the reader already knows. Splitting the bins makes that question
unavoidable and its answer countable.

The same reasoning separates `delete-speculative` and `delete-unactionable`, which fail the same way for the same
reason: both name spans that are accurate and unpadded, so both are invisible to any check that looks for filler.

Read the counts accordingly. `delete-obvious`, `delete-speculative`, and `delete-unactionable` are the three that rest
on judgment alone; a file where all three came in at zero is evidence the tests were skipped, not evidence the file was
already lean — treat it as you would a test suite reporting no assertions.

### 5. Return the extraction report

Per file: the fact-file path, baseline measurements, disposition counts — stating the `delete-obvious`,
`delete-speculative`, and `delete-unactionable` counts on their own, since those are the ones most likely to be silently
zero — and the fact file's own size **against its cut target**, with any overrun declared and the facts that caused it
named. Plus, once for the batch: the convention-owner paths, the surface classifications, a summary of every deleted
span so the drops are auditable, and every escalation.

## Composition pass

Executed by a fresh `distiller` spawn. Its whole world is the caller-supplied inputs: per target, a scrambled fact file,
a destination path, and a surface classification, plus the convention owners and the scratch directory. The
[fold-in variant](#fold-in-variant) below is the only extension of that world. **The originals are off-limits** — every
fact available for the rewrite is a line in a fact file.

### 1. Read the conventions

Read the supplied convention owners; together with the [distillation bar](#the-distillation-bar), they bind structure,
naming, and references.

### 2. Compose each file

For each target independently, compose a whole replacement file from its fact lines alone. How those facts are presented
is yours to choose — the scrambled input carries no structure on purpose, and nothing here prescribes a form.
Runtime-configuration lines land in frontmatter with their exact values.

Write each replacement into the scratch directory in a single whole-file write, never as accumulated edits.

### 3. Verify each file

- **Coverage**: every fact line is represented in the output exactly once — the check that makes blind composition safe.
  A line that cannot be placed is still included, flagged as an escalation.
- **References**: every reference resolves from the destination path (the installed or projected location, not the
  scratch directory).
- **Measurements**: record lines and words (`wc -l -w`) per composed file.

### 4. Return the composition report

Per file: after-measurements, a one-line statement of the structure chosen, coverage confirmation, and any fact line
that was ambiguous to place with how it was resolved. Plus every escalation, including splits the divergence test
demanded.

### Fold-in variant

A fold-in spawn revises replacements against review findings instead of composing from nothing. Its world extends the
pass's inputs by exactly two items: each target's current replacement, and the must-fix findings that name it;
everything else carries over unchanged, including the off-limits originals. Findings direct structure, wording, and
references — the fact files remain the only source of facts, and a finding that would change what a fact requires is
escalated, not applied. Verify each revised file as in step 3, and extend the report with a per-finding statement of how
it was resolved.

## The distillation report

The executor assembles, from both pass reports and the review:

- **Per file**: before → after lines/words, and the achieved reduction against the file's cut target. A set that came in
  near its baseline is a finding about the pass, not a verdict that the corpus was already lean — say so plainly rather
  than presenting a reformat as a distillation.
- **Disposition totals**: span counts by disposition and the extraction pass's deleted-span summary, so the cuts are
  auditable. Report the three judgment-bearing deletions — `delete-obvious`, `delete-speculative`, `delete-unactionable`
  — separately from `delete-for-reader`; a batch whose counts there are zero or near it did not run those tests, and the
  report says so rather than letting the totals imply otherwise.
- **Review outcome**: findings from the independent review and how each was resolved.
- **Escalations**: every uncertain-fact question, suspected-wrong rule, convention gap, and cross-file structural
  recommendation (merge, relocation, split), for the human to rule on.
- **Not committed** — the human caller decides when to commit (suggest the `commit` operation).
- **Behavioral-eval note**: when the target harness declares a behavioral eval for context changes, a distill of
  always-loaded or routed files owes it — name it as owed.
