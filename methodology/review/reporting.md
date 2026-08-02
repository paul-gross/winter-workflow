# Review reporting contract

Use this output contract for every review axis and execution mode.

## Findings report

Organize the report into these sections:

- `## must-fix`: issues that should block acceptance.
- `## consider`: non-blocking improvements.
- `## notes`: optional brief acknowledgments and out-of-scope routing. Keep this section short.
- `## gaps`: optional process feedback on why a must-fix escaped upstream verification — see [Gaps](#gaps).

Give every `must-fix` and `consider` finding, and every gap, a distinct id. Prefix must-fix ids with `M`, consider ids with `C`, and gap ids with `G`, using one number sequence across all of them. Two must-fixes, a consideration, and a gap are `M1`, `M2`, `C3`, and `G4`; never restart or reuse a number.

An aggregator that merges several reports renumbers into one sequence. Renumbering rewrites the must-fix ids a gap references along with the findings themselves — a gap left pointing at its pre-merge number is a silently wrong reference rather than a visibly broken one. When merged must-fixes carried gaps of different forms, the merged finding keeps both rather than forcing one claim to absorb the other; identical claims collapse to one.

An aggregator that instead preserves each reviewer's original ids qualifies a gap's referenced ids the same way it qualifies the gap itself, so `M1` resolves to one reviewer's report rather than every reviewer's.

Each finding must be independently actionable and include:

- The id and concise problem statement.
- The target path and line or section.
- The concrete evidence and governing principle or convention when one applies.
- A specific correction direction without replacement content or a rewrite.

Apply the selected axis's severity semantics; the buckets do not replace its definitions.

If the target is clean on the selected axis, return one concise sentence instead of empty headings or padded praise. Axis-specific required evidence sections still follow that sentence.

## Gaps

The `## gaps` section carries process feedback rather than findings: why a must-fix reached review instead of being caught by the layers before it. Findings address the builder; a gap addresses whoever maintains the process and harness.

Write each gap as a one-line claim in exactly one of four forms, naming the must-fix id(s) it explains:

1. **Method exists, was not run** — name it: `G4: M1 — web:unit-test would have caught this; it was not run before delivery.`
2. **Method exists, ran, did not fire** — name why it missed: `G4: M1 escaped web:unit-test because jsdom does not evaluate container queries.`
3. **No method exists** — name the missing matrix row.
4. **Not verification-shaped** — route it to the [harness axis](./axes/harness.md) in one line instead of naming a method. Take this form rather than inventing an aspirational matrix row.

Name methods and rows in the vocabulary of the target's own verifiability matrix and the harness convention that governs it; this contract does not restate it. Reach that matrix the way any target artifact is reached — from the target's agent-context entrypoints, following its routes — rather than assuming a path.

A gap is a one-line claim, not an investigation, and the section must not inflate the cost of a review. Write at most one gap per must-fix, and only where one is real: a must-fix that is a novel judgment call review is the right layer to catch gets none, and a fabricated gap is worse than an absent one. `consider` findings carry no gaps.

A gap's sink is the human reading the relayed report, who owns the process it names. A caller that consumes reviews programmatically carries gaps through to its own human-facing output rather than routing them to a fixer; disposing of one against the target's verifiability matrix is that caller's decision, not an act this contract performs.

Do not file an axis's own missing-declaration or undeclared-ownership gaps here — those are findings in the bucket the axis assigns, and this section is only about why a must-fix escaped upstream verification.

Emit no `## gaps` heading when no gap applies, as with every other section.

## Remote feedback

A remote scope carries a normalized `feedback` value; each axis declares its own default. The values mean:

- `report`: return the findings to the caller without posting anything to the remote review.
- `inline`: post each `must-fix` and `consider` finding as a self-contained inline comment on the remote review through the available forge CLI (`gh`, `glab`, `tea`, or equivalent), each comment carrying its finding id, severity, violated principle or concern, proposed direction, and reasoning.
- `default`: apply the executing axis's declared default (`report` or `inline`).

Gaps are never posted to a remote review — they address the process, not the change — so return them to the caller alongside the posting summary on every remote run.

Preserve the same ids and severity semantics as a local report, and make each inline comment self-contained because readers may not see the comments together. Return a concise posting summary only when every attempted post succeeds. If any post fails, return the failure and the affected unposted findings to the caller, and never imply feedback was posted when the forge command failed.

## Relay

Present a completed single-axis report as-is with a one-line preamble naming the axis, execution mode, scope, and target count or path. Do not editorialize or argue with findings. A multi-axis process may synthesize findings under its own declared output contract instead.
