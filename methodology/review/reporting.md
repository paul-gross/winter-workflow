# Review reporting

The output contract for review findings. It binds every review axis and every execution mode. The severity buckets here do not replace the selected axis's severity semantics; the axis's definitions still apply.

## Sections

A findings report is organized into the sections `## must-fix`, `## consider`, optional `## notes`, and optional `## gaps`.

- `must-fix` holds issues that should block acceptance; `consider` holds non-blocking improvements.
- `notes` holds brief acknowledgments and out-of-scope routing and is kept short.
- Emit no heading for a section with no entries — `## gaps` included, like every other section.
- A target clean on the selected axis gets one concise sentence instead of empty headings or padded praise, with any axis-specific required evidence sections still following that sentence.

## Finding ids

Every must-fix, consider, and gap carries a distinct id: prefix `M` for must-fix, `C` for consider, and `G` for gap, numbered in one shared sequence across all three — two must-fixes, a consideration, and a gap are `M1`, `M2`, `C3`, `G4`. A number is never restarted or reused.

An aggregator that merges several reports renumbers all ids into one sequence. Renumbering must rewrite the must-fix ids a gap references along with the findings themselves, because a gap left pointing at its pre-merge number is a silently wrong reference rather than a visibly broken one. When merged must-fixes carried gaps of different forms, the merged finding keeps both gaps rather than forcing one claim to absorb the other, and identical gap claims collapse to one. An aggregator that instead preserves each reviewer's original ids qualifies a gap's referenced ids the same way it qualifies the gap itself, so an id like `M1` resolves to one specific reviewer's report rather than every reviewer's.

## Finding content

Each finding must be independently actionable and include:

- the id with a concise problem statement;
- the target path and line or section;
- the concrete evidence plus the governing principle or convention when one applies;
- a specific correction direction without replacement content or a rewrite.

## The gaps section

`## gaps` carries process feedback rather than findings: why a must-fix reached review instead of being caught by the layers before it. Findings address the builder; a gap addresses whoever maintains the process and harness. A gap's sink is the human reading the relayed report, who owns the process it names. A caller that consumes reviews programmatically carries gaps through to its own human-facing output rather than routing them to a fixer; disposing of a gap against the target's verifiability matrix is that caller's decision, not an act this contract performs.

Each gap is written as a one-line claim naming the must-fix id(s) it explains, in exactly one of four forms:

1. **A verification method exists but was not run** — name the method, as in `G4: M1 — web:unit-test would have caught this; it was not run before delivery.`
2. **The method exists and ran but did not fire** — name why it missed, as in `G4: M1 escaped web:unit-test because jsdom does not evaluate container queries.`
3. **No method exists** — name the missing verifiability-matrix row.
4. **The escape is not verification-shaped** — route it to the [harness axis](./axes/harness.md) in one line instead of naming a method, and take this form rather than inventing an aspirational matrix row.

Bounds:

- Write at most one gap per must-fix and only where one is real: a must-fix that is a novel judgment call review is the right layer to catch gets no gap, and a fabricated gap is worse than an absent one.
- `consider` findings carry no gaps.
- A gap is a one-line claim, not an investigation, and the gaps section must not inflate the cost of a review.
- An axis's own missing-declaration or undeclared-ownership issues are findings in whatever bucket the axis assigns, never gaps; the gaps section covers only why a must-fix escaped upstream verification.

Name methods and rows in the vocabulary of the target's own verifiability matrix and the harness convention that governs it; this contract does not restate that vocabulary. Reach the target's verifiability matrix the way any target artifact is reached — from the target's agent-context entrypoints, following its routes — never by assuming a path.

## Remote feedback

A remote scope carries a normalized `feedback` value of `report`, `inline`, or `default`, and each axis declares its own default.

| Value | Behavior |
|-------|----------|
| `report` | Return the findings to the caller without posting anything to the remote review. |
| `inline` | Post each `must-fix` and `consider` finding as a self-contained inline comment on the remote review through the available forge CLI (`gh`, `glab`, `tea`, or equivalent), each comment carrying its finding id, severity, violated principle or concern, proposed direction, and reasoning. |
| `default` | Apply the executing axis's declared default of `report` or `inline`. |

Remote runs preserve the same ids and severity semantics as a local report. Make each inline comment self-contained, because readers may not see the comments together. Gaps are never posted to a remote review because they address the process rather than the change; return them to the caller alongside the posting summary on every remote run.

Return a concise posting summary only when every attempted post succeeds; if any post fails, return the failure and the affected unposted findings to the caller, and never imply feedback was posted when the forge command failed.

## Relaying a report

Relay a completed single-axis report as-is, with a one-line preamble naming the axis, execution mode, scope, and target count or path, without editorializing or arguing with the findings. A multi-axis process may synthesize findings under its own declared output contract instead of relaying reports as-is.
