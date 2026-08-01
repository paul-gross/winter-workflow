# Context review axis

Review agent-facing configuration and markdown against the workspace's documented authoring conventions. The review surface includes canonical agents, skills, commands, agent-context entrypoints, and `context/` or `methodology/` documentation. Enforce clarity, single-source-of-truth, non-duplication, and one truthful purpose per file.

## Inputs

Consume the semantic review inputs prepared by the [review process](../process.md): scope, in-scope targets, review material, cross-repo framing when applicable, and any remote-feedback destination. For a paths scope, classify the current-state files with [`../agent-context-surface.md`](../agent-context-surface.md).

## Discover the criteria

Load documented standards before reviewing. Review against those standards, not personal preferences.

1. Start at the workspace and target agent-context entrypoints. Follow every include and explicit route relevant to the changed area until it reaches the declared owner of the applicable authoring, placement, naming, tooling, or reference facts.
2. Read linked repo hubs, context indexes, installed convention owners, and file-type guidance. Treat methodology leaves as owners of reusable operations only; they are criteria when the target explicitly routes the reviewed operation there, not generic sources of target facts.
3. Read peer files beside each touched agent, skill, command, or context document as implementation evidence and examples, not as a replacement owner when a declared convention exists.
4. If entrypoints conflict, terminate before an owner, or leave a relevant convention unowned, report that routing or ownership gap rather than selecting an assumed canonical file.

Look for cross-cutting path, naming, tooling, and reference rules; file-type-specific authoring rules; and adjacent canonical examples. If a relevant convention is missing or ambiguous, report that gap rather than inventing a rule. Cite the governing owner and section for every convention-backed finding; explicitly say when no documented convention applies.

## Evidence method

1. Enumerate only the agent-facing files in scope.
2. Resolve references from the runtime location in which each artifact is consumed, not merely from its source location.
3. Compare each file with governing conventions and adjacent canonical examples.
4. Scan the in-scope agent-facing surface for duplicated or conflicting ownership.
5. Report specific file and line evidence with a concrete consolidation or correction direction. Do not write replacement content.

## Artifact knowledge

- **Agents** are canonical source definitions projected into each harness's native artifact. Review the canonical source, never a generated projection, and use the live installation facts at `workspace:/context/winter-cli/configuration/extensions.md#what-gets-symlinked` plus the active projected artifact for harness-specific identity. A relative reference that assumes the canonical directory can break after projection.
- **Skills** use harness-dependent installation mechanisms under a workspace-configurable prefix. Review the source skill, then resolve its references from the active harness's installed artifact according to the live facts at `workspace:/context/winter-cli/configuration/extensions.md#what-gets-symlinked`; do not assume every harness uses a symlink or that source-relative behavior is universal.
- **Commands** are simpler user-invocable prompts and still need precise scope and references.
- **Agent-context entrypoints** are hierarchical routing files. They should route to detailed facts and methodology rather than duplicate them.
- **`context/`** owns facts and constraints about a target. **`methodology/`** owns reusable ways of performing operations. Keep those truths distinct.
- **Cross-context references** use the workspace's declared `<context>:<path>` notation and must survive installation and projection.

Discover authoritative frontmatter, model, tool, prompt-shape, and projection requirements from the live harness conventions rather than assuming one harness's schema.

## Checklist

- **Frontmatter correctness**: required and permitted fields, valid tool grants, model selection, and routing-quality descriptions.
- **Identity and boundary clarity**: one clear role or purpose, explicit capabilities, and no contradictory instructions.
- **Actionability and ambiguity**: imperative, executable instructions with one reasonable interpretation.
- **Tool appropriateness**: only the capabilities the artifact needs, with invocation-specific restrictions kept in the caller where required.
- **Overlap and ownership**: no competing source of truth or duplicated procedure; dependencies point from adapters to reusable owners.
- **Reference correctness**: current paths, anchors, prefixes, and references that resolve from the installed or projected runtime location.
- **Placement and naming**: facts in context, reusable methods in methodology, and names/prefixes following discovered conventions.
- **Routing completeness**: new or moved content is reachable from the appropriate hub without bloating always-loaded entrypoints.

For a duplication audit, identify the canonical owner, the exact duplicate or conflict, what should be removed, and how other files should reference the owner.

## Scope boundaries

Do not review source-code architecture or the application-to-harness seam. Do not investigate code to discover product capabilities, make product decisions, review backlog plans or future-roadmap initiatives, or review external-facing public documentation. When duplication crosses into public documentation, own and report only the agent-facing side and route the public side to the `documentation` axis.

## Severity

- **must-fix**: conflicting instructions, invalid runtime configuration, broken runtime references, or duplication that creates contradictory sources of truth.
- **consider**: non-conflicting duplication, missing conventions, unclear boundaries, weak routing, or other improvements that reduce ambiguity and drift.
- **notes**: brief acknowledgments and concise routing of out-of-scope concerns.

## Output

Follow the shared [reporting contract](../reporting.md). Be direct: identify the file and lines, cite the convention and section when one exists, explain the concrete conflict or gap, and prescribe the minimal diff direction without authoring the replacement.

For a remote target, use the appropriate forge CLI to fetch the material. Return findings to the caller unless the semantic inputs explicitly request remote inline comments.
