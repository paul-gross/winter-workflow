# Review reporting contract

Use this output contract for every review axis and execution mode.

## Findings report

Organize findings into these sections:

- `## must-fix`: issues that should block acceptance.
- `## consider`: non-blocking improvements.
- `## notes`: optional brief acknowledgments and out-of-scope routing. Keep this section short.

Give every `must-fix` and `consider` finding a distinct id. Prefix must-fix ids with `M` and consider ids with `C`, using one number sequence across both sections. Two must-fixes followed by two considerations are `M1`, `M2`, `C3`, and `C4`; never restart or reuse a number.

Each finding must be independently actionable and include:

- The id and concise problem statement.
- The target path and line or section.
- The concrete evidence and governing principle or convention when one applies.
- A specific correction direction without replacement content or a rewrite.

Apply the selected axis's severity semantics; the buckets do not replace its definitions.

If the target is clean on the selected axis, return one concise sentence instead of empty headings or padded praise. Axis-specific required evidence sections still follow that sentence.

## Remote feedback

When an axis directs findings to a remote review, preserve the same ids and severity semantics. Make each inline comment self-contained because readers may not see the comments together. Return the posting result or any posting failure to the caller; never imply feedback was posted when the forge command failed.

## Relay

Present a completed single-axis report as-is with a one-line preamble naming the axis, execution mode, scope, and target count or path. Do not editorialize or argue with findings. A multi-axis process may synthesize findings under its own declared output contract instead.
