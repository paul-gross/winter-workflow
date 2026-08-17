# Documentation review axis

This axis reviews external-facing public documentation against the code and behavior it describes. It covers what a human adopter or end-user reads to learn and use the project, not the agent-facing material used to develop it. The axis consumes the semantic review inputs prepared by the review process at [../process.md](../process.md).

In scope:

- The user-facing portions of a public `README.md`, including what the project is and how a user runs it.
- User and adopter guides, tutorials, quickstarts, and user-facing CLI, API, or configuration references.
- Rendered documentation sites and their source content, regardless of generator.

Out of scope:

- Source-code architecture — read code only to determine whether public documentation describes it accurately, and route structural concerns to the `code` axis.
- Harness-specific content and the application-to-harness seam — route those concerns to the `harness` axis.
- Agent-facing entrypoints, canonical agents, skills, commands, and `context/` or `methodology/` docs — route their side of a cross-surface duplication to the `context` axis.

When the target ships no external-facing public documentation, return one sentence stating there is no surface in scope and stop.

## Criteria discovery

Locate rather than assume the target's public-documentation surfaces, behavior facts, and authoring conventions. Start at the workspace and target agent-context entrypoints and follow their routes to the declared owners of product behavior, public-doc placement, and documentation-authoring facts relevant to the change.

- Follow target-owned public-doc hubs and explicit links to the applicable guides or reference owners; a `README`, `CONTRIBUTING.md`, code symbol, or generated reference is authoritative only for the facts the target declares it owns.
- Treat methodology as reusable operational procedure, not the generic source for product behavior or public-doc style, and use it only when a declared documentation workflow governs the reviewed surface.
- When the project documents a "docs reflect this change" invariant or a surface-placement rule, apply it and cite its owner.
- When the target does not route a needed behavior or documentation convention to an owner, report the missing or ambiguous ownership rather than choosing a likely source.
- When no relevant convention exists, use general documentation-quality judgment and note the missing standard.

## Checklist

- **Accuracy and currency** — stale commands, renamed or removed options, changed defaults, outdated configuration keys, broken examples, or screenshots of removed UI.
- **Audience completeness** — a new or changed user-facing command, flag, capability, or behavior with no corresponding public documentation.
- **Single-source-of-truth** — authoritative details such as exact flag lists, schemas, or signatures copied instead of referenced, with an already-diverged copy reported more severely than a copy that has not drifted yet.
- **Clarity and navigation** — human-oriented writing, valid cross-links and anchors, and no orphaned pages introduced or exposed by the change.
- **Convention conformance and placement** — target-specific README structure, voice, public-doc surface ownership, and distinctions such as consumable extension versus example or reference implementation.

## Evidence method

1. Read the review material to identify changed behavior and changed documentation.
2. Locate the public documentation and distinguish it from agent-facing surfaces.
3. Discover the target's documentation conventions.
4. Walk every checklist item and record a concrete finding or skip it — never invent findings to fill the list.
5. Tie each finding to a public page and section plus the code symbol, behavior, or canonical source that proves the gap.

## Severity

- **must-fix** — public documentation that is now wrong, a changed user-facing capability with no public coverage, or a copied canonical detail that has already diverged.
- **consider** — non-blocking clarity or navigation improvements, useful additional adopter guidance, or a copied authoritative detail that has not diverged yet.
- **notes** — brief acknowledgments of correct documentation and concise routing of out-of-scope concerns.

## Output

Output follows the shared reporting contract at [../reporting.md](../reporting.md). For a remote target, fetch the diff with the appropriate forge CLI and return findings to the caller unless the semantic inputs explicitly request remote inline comments.
