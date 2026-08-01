# Documentation review axis

Review external-facing public documentation against the code and behavior it describes. This axis covers what a human adopter or end-user reads to learn and use the project, not agent-facing material used to develop it.

## Inputs

Consume the semantic review inputs prepared by the [review process](../process.md): scope, in-scope targets, review material, cross-repo framing when applicable, and any remote-feedback destination.

## Surface

In scope:

- Rendered documentation sites and their source content, regardless of generator.
- User and adopter guides, tutorials, quickstarts, and user-facing CLI, API, or configuration references.
- User-facing portions of a public `README.md`, including what the project is and how a user runs it.

Out of scope:

- Agent-facing entrypoints, canonical agents, skills, commands, and `context/` or `methodology/` docs. Route their side of a cross-surface duplication to `context`.
- Harness-specific content and the application-to-harness seam. Route those concerns to `harness`.
- Source-code architecture. Read code only to determine whether public documentation describes it accurately; route structural concerns to `code`.

If the target ships no external-facing public documentation, return one sentence stating that there is no surface in scope and stop.

## Discover the criteria

Locate rather than assume the target's public-documentation surfaces, behavior facts, and authoring conventions.

1. Start at the workspace and target agent-context entrypoints, then follow their routes to the declared owners of product behavior, public-doc placement, and documentation-authoring facts relevant to the change.
2. Follow target-owned public-doc hubs and explicit links to the applicable guides or reference owners. A `README`, `CONTRIBUTING.md`, code symbol, or generated reference is authoritative only for the facts the target declares it owns.
3. Treat methodology as reusable operational procedure, not as the generic source for product behavior or public-doc style. Use it only when a declared documentation workflow governs the reviewed surface.
4. If the target does not route a needed behavior or documentation convention to an owner, report the missing or ambiguous ownership rather than choosing a likely source.

If the project documents a "docs reflect this change" invariant or surface-placement rule, apply and cite its owner. If no relevant convention exists, use general documentation-quality judgment and note the missing standard.

## Evidence method

1. Read the review material to identify changed behavior and changed documentation.
2. Locate the public documentation and distinguish it from agent-facing surfaces.
3. Discover the target's documentation conventions.
4. Walk every checklist item below. Record a concrete finding or skip it; do not invent findings to fill the list.
5. Tie each finding to a public page and section plus the code symbol, behavior, or canonical source that proves the gap.

## Checklist

1. **Accuracy and currency**: stale commands, renamed or removed options, changed defaults, outdated configuration keys, broken examples, or screenshots of removed UI.
2. **Audience completeness**: a new or changed user-facing command, flag, capability, or behavior with no corresponding public documentation.
3. **Single-source-of-truth**: authoritative details such as exact flag lists, schemas, or signatures copied instead of referenced. Report an already-diverged copy more severely than a copy that has not drifted yet.
4. **Clarity and navigation**: human-oriented writing, valid cross-links and anchors, and no orphaned pages introduced or exposed by the change.
5. **Convention conformance and placement**: target-specific README structure, voice, public-doc surface ownership, and distinctions such as consumable extension versus example/reference implementation.

## Severity

- **must-fix**: public documentation that is now wrong, a changed user-facing capability with no public coverage, or a copied canonical detail that has already diverged.
- **consider**: non-blocking clarity or navigation improvements, useful additional adopter guidance, or a copied authoritative detail that has not diverged yet.
- **notes**: brief acknowledgments of correct documentation and concise routing of out-of-scope concerns.

## Output

Follow the shared [reporting contract](../reporting.md). Every finding must identify the public page and section, the contradicting code behavior or canonical source, and a concrete next step without writing replacement content.

For a remote target, use the appropriate forge CLI to fetch the diff. Return findings to the caller unless the semantic inputs explicitly request remote inline comments.
