# Distill — process

A **rewrite** procedure for existing markdown — agent-facing or human-facing — that has grown by accretion: bloated, stale, or written for weaker models than the ones now reading it. Distill re-composes each file into only what a current reader needs. It preserves meaning, never policy: the output requires exactly what the input required, minus what is demonstrably dead.

Runtime operations follow [`../runtime-ports.md`](../runtime-ports.md).

## Where this fits

| Method | Verb | Scope | Question |
|--------|------|-------|----------|
| [Context review axis](../review/axes/context.md) | Report | Diff or paths | Does this agent-facing change follow the conventions? |
| [Documentation review axis](../review/axes/documentation.md) | Report | Diff | Do the public docs match the code? |
| `distill` (this process) | Rewrite | Current-state files | What is the smallest, current, well-placed form of this content? |

The review axes find problems and prescribe direction without writing replacement content; distill writes the replacement. Distill is for **existing** content only — authoring a new document follows the target's authoring conventions directly.

## Roles

All discovery and writing runs in the canonical `distiller` role, spawned in a fresh isolated context; the coordinating executor never edits the targets itself.

**Why the writer is always cold.** A session that produced or discussed the content carries that history into the prose: the rewrite comes out framed as a change — "previously X, now Y" — rather than as the current state, exactly the retrospective framing the authoring conventions forbid. A cold distiller sees only what the files say today, so it has nothing to narrate a transition from. Do not substitute an inline rewrite or a fork of the current context for the isolated spawn.

Every `distiller` invocation carries, before its role-specific task, the one-shot default declared by [`../runtime-ports.md`](../runtime-ports.md#spawn-an-isolated-role), scoped to this distill operation.

## Inputs

- **Target set** — paths, directories, or a repo whose markdown files are to be distilled.
- **Human-caller channel** — for scope confirmation, disposition rulings on uncertain facts, and the final report.
- **Workspace context** — the target's agent-context entrypoints, discoverable from the workspace root or the target repo's hub.

## Outputs

- Rewritten (possibly merged, split, moved, or deleted) files, uncommitted.
- The **distillation report**: per-file measurements, the fact ledger summary, and every escalation.

## The distillation bar

The rewrite standard every output file is held to. The target's own discovered conventions bind placement, ownership, structure, and references; this bar adds what no convention owner covers — the calibration of prose to its modern reader.

**Meaning is preserved; policy is untouched.** Distill changes how content is written and where it lives, never what it requires. Reality is the authority for facts: a claim contradicted by the current code, config, or tooling is corrected or deleted after verification. But a rule that seems wrong *in substance* — too strict, too loose, misconceived — is escalated to the human caller as a finding, never silently rewritten into a different rule.

**Cut what the reader no longer needs.** Prose accretes hand-holding calibrated to the weakest model that ever read it. A current-generation agent does not need:

- procedural walkthroughs of routine operations it performs unprompted;
- restatement or "remember to" / "make sure" reinforcement of a rule already stated once;
- motivational or persuasive framing around an instruction;
- defensive enumeration of cases an intelligent reader infers from the rule;
- apologies, hedges, or meta-commentary about the document itself.

**Keep what changes behavior.** A sentence survives when it states a project-specific fact, a non-obvious or counter-intuitive constraint, a decision rule, or a *why* that future judgment will need. The test: would a competent agent with no document do this anyway? If yes, the sentence is dead weight; if no, it is load-bearing.

**Links are dependencies, not decoration.** A reference survives only when the reader must follow it to act on this document — a contract to execute, a method to apply, an owner to consult, a route to choose. Cut references that explain by analogy, cite where an idea came from, or gesture sideways at related material the reader needs no part of. The test: if the target file vanished, would this document stop working, or just lose a footnote?

**Human voice, agent density.** Output is complete, natural sentences a human colleague would write — not telegraphic fragments, keyword lists, or abbreviation soup. Density comes from selection (fewer sentences, each load-bearing), never from a compressed style that trades readability for length.

**The source is evidence, not a draft.** Treat the original's entire presentation — its structure, section order, headings, emphasis, and sentences — as presumptively invalid: accretion artifacts that mirror edit history, not decisions anyone made for the reader. Only its facts enter the rewrite, restated. Every element of the output's presentation is chosen fresh; any resemblance to the source is the best form happening to coincide, never inheritance.

**Split when readers diverge.** A file owes a split when it answers more than one reader question — when readers with different tasks each wade through the others' material to reach their own. The test: name the question each section answers; two or more distinct questions arriving with distinct readers means hub and spokes, with detail pushed to the spokes and the hub row carrying only the read-trigger. The guard runs both ways: sections that all serve one reading stay together — every split charges the reader a hop. Total word count is not the measure here; placement is. Words moved from an always-loaded or hub surface down to a routed spoke are a win at constant mass, because each reader now pays only for their question.

## Coordination steps

The executor coordinating this process:

### 1. Bind the target set

Resolve the supplied target to a concrete list of markdown files. Exclude history-by-design files (changelogs, retrospectives, migration notes, post-mortems — there the history *is* the content) and generated projections (distill the canonical source instead). If the resolved set is ambiguous or surprisingly large, present it and ask the human caller before proceeding; otherwise state the set and continue.

### 2. Spawn the distiller

Spawn the canonical `distiller` role in a one-shot isolated context and await its result. The prompt must include:

1. **The isolated-role restrictions** from [Roles](#roles).
2. **The target set** — absolute paths, with the exclusions already applied.
3. **What to do** — execute the [Distillation procedure](#distillation-procedure) below against exactly those files.
4. **What to return** — the [distillation report](#the-distillation-report). The distiller cannot reach the human caller: where the procedure raises a question, it applies the conservative default (keep the span) and returns the question as an escalation.

Supply only the target set and these process references — never a summary of how the content came to be or what the session was doing. That history is the contamination the cold spawn exists to exclude.

### 3. Close with an independent review

Run a fresh context review of the touched agent-facing files through the [review process](../review/process.md) (`axis: context`, paths scope); when public documentation was touched, run the `documentation` axis over those paths as well.

Fold must-fix findings back in by re-spawning the `distiller` (fresh again) with the target files and the findings — the executor does not apply them inline. Cap this at two fold-in cycles; unresolved findings after that go to the human caller.

### 4. Report

Deliver the distiller's report to the human caller, extended with:

- **Review outcome**: findings from step 3 and how each was resolved.
- **Escalations**: every disposition question, suspected-wrong rule, and convention gap the distiller returned, for the human to rule on.
- **Not committed** — the human caller decides when to commit (suggest the `commit` operation).

## Distillation procedure

Executed by the `distiller` role against the caller-supplied target set.

### 1. Discover the governing conventions

Follow the workspace and target agent-context entrypoints to the declared owners of authoring, placement, naming, and reference conventions. Those owners bind the rewrite. Where a needed convention is unowned or two owners conflict, record the gap as an escalation and proceed on the distillation bar alone — do not invent a convention.

### 2. Classify each file by consumption surface

Classify agent-facing files with [`../review/agent-context-surface.md`](../review/agent-context-surface.md); classify the rest as human-facing (README, docs site, guides). The surface sets the stakes:

- **Always-loaded** entrypoints (workspace/repo instruction files and everything they import) are paid for on every request — distill these hardest, and push detail down to routed files.
- **Routed** context and methodology docs are paid for when their trigger fires — optimize for the reader who arrived with that one question.
- **Definitions** (agents, skills, commands) are both routed prose and runtime configuration — their frontmatter and references must stay valid from the installed location.
- **Human-facing** docs keep a narrative allowance agent docs don't get, but every ownership and duplication rule still applies.

### 3. Measure the baseline

Record lines and words per file (`wc -l -w`). The report needs before/after evidence, not impressions.

### 4. Build the fact ledger

Walk each file and assign every span of content a disposition:

| Disposition | Meaning |
|-------------|---------|
| `keep` | Current, load-bearing, correctly owned here |
| `condense` | Load-bearing but over-explained — keep the constraint, cut per the bar |
| `pointer` | Owned by another document — reduce to a read-trigger pointer at the owner |
| `relocate` | Load-bearing but owned by the wrong file — move to its owner |
| `delete-historical` | Retrospective framing, superseded behavior, change narrative |
| `delete-obsolete` | Describes something that no longer exists — verified against reality first |
| `delete-for-reader` | Hand-holding the bar names as dead weight for a current reader |

A `keep` or `condense` entry is an atomic fact **restated in your own words** — never a quoted or lightly reworded span. The ledger is the spec the new file is composed from; source sentences that enter it verbatim become sentences the output inherits, defeating the composition step.

Two duties guard the destructive dispositions. `delete-obsolete` requires checking the code, config, or tool the span describes — staleness is verified, not assumed. And any span whose load-bearing status is genuinely uncertain is kept and returned as an escalation, not binned.

### 5. Decide the structure

With ledgers in hand, decide each file's fate: it survives in place, merges into a sibling, splits into a hub and spokes, or is deleted because too little `keep` remains to justify a file. Splitting is decided by the bar's reader-divergence test, never by size alone. Apply the discovered structural conventions; every kept or relocated fact must remain reachable from its hub after the change.

### 6. Compose

Once the ledger and structure decisions are complete, **close the originals and consult them no further** — compose each new file from the ledger's restated facts alone, to the bar, in the structure decided above. Write pointers where the ledger says `pointer`; land relocated facts in their owners in the same change.

Composition is a whole-file write, never a sequence of span edits on the original — editing is how a rewrite silently degrades into trimming. Step 7's coverage check, not a small diff, is what makes this safe.

### 7. Verify and measure

- Every `keep` and `condense` fact in the ledger is present in the output — the coverage check that makes blind composition safe.
- Every reference in touched files resolves from the location it is consumed in (installed or projected, not just the source tree).
- Every `relocate` and `pointer` fact is present at its owner and reachable from the appropriate hub.
- Record after-measurements (`wc -l -w`) for every touched file.

### The distillation report

Return to the caller:

- **Per file**: before → after lines/words and the structural outcome (rewritten, merged into X, split, deleted).
- **Ledger totals**: span counts by disposition, so the deletions are auditable.
- **Escalations**: every uncertain-fact question, suspected-wrong rule, and convention gap, each with the file and the conservative action taken.
- **Behavioral-eval note**: when the target harness declares a behavioral eval for context changes, a distill of always-loaded or routed files owes it — name it as owed.
