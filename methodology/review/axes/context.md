# Context review axis

This axis reviews agent-facing configuration and markdown against the workspace's documented authoring conventions. The review surface includes canonical agents, skills, commands, agent-context entrypoints, and `context/` or `methodology/` documentation; the axis enforces clarity, single-source-of-truth, non-duplication, and one truthful purpose per file. It consumes the semantic review inputs prepared by the review process at [../process.md](../process.md).

Boundaries:

- The exclusions the surface classifier at [../agent-context-surface.md](../agent-context-surface.md) declares are out of scope here.
- Source-code architecture and the application-to-harness seam are out of scope.
- When duplication crosses into public documentation, own and report only the agent-facing side and route the public side to the `documentation` axis.

## Criteria discovery

Load documented standards before reviewing, and review against those standards rather than personal preferences. Discover criteria by starting at the workspace and target agent-context entrypoints and following every include and explicit route relevant to the changed area until reaching the declared owner of the applicable authoring, placement, naming, tooling, or reference facts.

- Look for cross-cutting path, naming, tooling, and reference rules, file-type-specific authoring rules, and adjacent canonical examples.
- Read linked repo hubs, context indexes, installed convention owners, and file-type guidance as criteria sources.
- Discover authoritative frontmatter, model, tool, prompt-shape, and projection requirements from the live harness conventions rather than assuming one harness's schema.
- Methodology leaves are owners of reusable operations only: they are criteria when the target explicitly routes the reviewed operation there, never generic sources of target facts.
- Peer files beside each touched agent, skill, command, or context document serve as implementation evidence and examples, not as a replacement owner when a declared convention exists.
- When entrypoints conflict, terminate before an owner, or leave a relevant convention unowned, report that routing or ownership gap rather than selecting an assumed canonical file.
- When a relevant convention is missing or ambiguous, report that gap rather than inventing a rule.
- Where the target declares no placement convention, review against this fallback baseline and note the missing declared standard so the target can bootstrap one: agent-context entrypoints route to detailed facts and methodology rather than duplicating them, and `context/` owns facts and constraints about the target while `methodology/` owns reusable ways of performing operations.

## Artifact kinds

- **Agents** are canonical source definitions projected into each harness's native artifact: review the canonical source, never a generated projection. A relative reference that assumes the canonical agent directory can break after projection. Use the live installation facts at `workspace:/context/winter-cli/configuration/extensions.md#what-gets-symlinked` plus the active projected artifact for harness-specific agent identity.
- **Skills** use harness-dependent installation mechanisms under a workspace-configurable prefix: review the source skill, then resolve its references from the active harness's installed artifact according to the live facts at `workspace:/context/winter-cli/configuration/extensions.md#what-gets-symlinked`.
- **Commands** are simpler user-invocable prompts and still need precise scope and references.
- Never assume every harness installs via symlink or that source-relative reference behavior is universal.
- Cross-context references use the workspace's declared `<context>:<path>` notation and must survive installation and projection.

## Checklist

- **Identity and boundary clarity** — one clear role or purpose, explicit capabilities, and no contradictory instructions.
- **Frontmatter correctness** — required and permitted fields, valid tool grants, model selection, and routing-quality descriptions.
- **Tool appropriateness** — only the capabilities the artifact needs, with invocation-specific restrictions kept in the caller where required.
- **Actionability and ambiguity** — imperative, executable instructions with one reasonable interpretation.
- **Reference correctness** — current paths, anchors, prefixes, and references that resolve from the installed or projected runtime location.
- **Routing completeness** — new or moved content reachable from the appropriate hub without bloating always-loaded entrypoints.
- **Placement and naming** — placement, names, and prefixes following the discovered conventions.
- **Overlap and ownership** — no competing source of truth or duplicated procedure, with dependencies pointing from adapters to reusable owners.

## Evidence method

1. Enumerate only the agent-facing files in scope; for a paths scope, classify the current-state files with the classifier at [../agent-context-surface.md](../agent-context-surface.md).
2. Resolve references from the runtime location in which each artifact is consumed, not merely from its source location.
3. Compare each file with governing conventions and adjacent canonical examples.
4. Scan the in-scope agent-facing surface for duplicated or conflicting ownership. A duplication audit identifies the canonical owner, the exact duplicate or conflict, what should be removed, and how other files should reference the owner.

## Findings

Be direct in each finding: cite the governing convention and section when one exists — and say explicitly when no documented convention applies — then explain the concrete conflict or gap and prescribe the minimal consolidation or correction direction.

## Severity

- **must-fix** — conflicting instructions, invalid runtime configuration, broken runtime references, or duplication that creates contradictory sources of truth.
- **consider** — non-conflicting duplication, missing conventions, unclear boundaries, weak routing, or other improvements that reduce ambiguity and drift.

## Output

Output follows the shared reporting contract at [../reporting.md](../reporting.md). For a remote target, fetch the material with the appropriate forge CLI and return findings to the caller unless the semantic inputs explicitly request remote inline comments.
