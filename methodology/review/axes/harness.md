# Harness review axis

Review the seam between an application and its agentic harness. Determine whether verifier tooling, agent context, and conventions kept pace with application change, and whether the application is shaped so agents can develop and verify it productively.

## Inputs

Consume the semantic review inputs prepared by the [review process](../process.md): scope, in-scope targets, review material, cross-repo framing when applicable, transcript candidate working directories, evidence time window, and any remote-feedback destination.

## Discover the criteria

Read existing documentation before reverse-engineering the target.

1. Start at the workspace and target agent-context entrypoints and follow their routes to the declared owners of application facts, harness conventions, verification contracts, and agent-facing integration facts relevant to the change.
2. Follow target-owned hubs into the applicable extension indexes, context facts, architecture owners, contribution conventions, and harness artifact guidance. Do not assign authority to a familiar filename merely because it exists.
3. Treat methodology as reusable operational procedure. Read a methodology leaf when the changed harness participates in that operation, but do not use it as a generic owner of application architecture, product behavior, or style facts.
4. If no owner is reachable for a fact needed to judge the seam, report the missing or ambiguous route rather than inventing a convention.

Review against the declared standards rather than personal preferences, and cite the owning source for convention-backed findings.

## Evidence method

1. Read the complete review material, then surrounding application and harness content.
2. Walk both checklists below explicitly. Record a finding or skip each item; do not invent findings to fill the list.
3. Mine scoped git history for recent-mistake evidence.
4. Execute the complete [`../transcript-evidence.md`](../transcript-evidence.md) procedure with the supplied candidate working directories, time window, and changed paths or symbols.
5. Correlate application changes, harness state, and repeated mistake evidence. Report only concrete gaps with an agent-productivity or verification ramification.

### Git-history evidence

Scope history to the changed area and the supplied time window. Useful commands include:

```bash
git log --oneline -n 50 -- <changed-paths>
git log --grep='revert\|hot.?fix\|oops\|undo' --oneline -n 50 -- <changed-paths>
git log --since='2 months ago' --oneline -- <changed-paths>
```

For diff scopes, also inspect the commit list from the base through the reviewed head. Look for reverts, sequential fixups in the same area, explicit correction commits, repeated touches to the same lines, and `fix(...): actually ...` patterns. A single fixup is noise; a repeated pattern is evidence.

## Harness-change checklist

1. **Verification tooling currency**: did backend-verifier references, fixture helpers, CLI test scaffolds, frontend selectors, seed data, and other verification tools keep pace with the change?
2. **Agent-context currency**: do canonical agents, skills, entrypoints, and `context/` or `methodology/` docs still name valid modules, commands, examples, and subsystem behavior?
3. **Recent-mistake evidence**: do git history or transcripts show recurring simple mistakes that better context or verification could prevent?
4. **Feedforward and feedback**: would schemas, examples, agent guidance, methodology/context, hooks, linters, or verifier scenarios prevent the evidenced mistakes?
5. **New standards**: does the evidence justify a convention such as an ordering rule, DI location, or fixture pattern?

## Application checklist

Only claim application findings with an agentic-development ramification.

1. **Observability**: would logs, traces, status surfaces, debug endpoints, or structured errors let agents understand runtime behavior more directly?
2. **Configurability and pluggability**: are DI seams, feature flags, test doubles, or environment switches needed to make verification possible or efficient?
3. **Agent-navigable architecture**: do module boundaries, naming, locality, and structure match a discoverable mental model, or will agents repeatedly misroute work?
4. **Types and inline constraints**: would type annotations or short comments preserve invariants, ownership, or non-obvious constraints agents otherwise reverse-engineer?

Do not claim a purely structural concern without an agent-productivity consequence; route it to the `code` axis. Do not adjudicate authoring-convention conformance for agent-facing markdown; claim only currency or seam drift and route pure conformance issues to `context`. Do not run tests, builds, or services.

## Severity

- **must-fix**: concrete, near-certain gaps likely to cause repeated agent mistakes or block verification, including stale verifier references, context naming removed APIs, a missing seam that makes verification impossible, or recurring evidence of the same mistake.
- **consider**: non-blocking improvements likely to shorten agent loops, such as an observability hint, a useful convention, a feedforward example, or stronger typing.
- **notes**: brief acknowledgments of strong seam improvements and concise routing of out-of-scope concerns.

## Output

Follow the shared [reporting contract](../reporting.md). Every finding must include:

- **Where**: file and line range, or canonical artifact and section.
- **What**: the gap and one-line evidence from the change, git history, or transcript.
- **Concern**: the checklist item it maps to.
- **Direction**: a concrete next step without replacement content.

Append `## Evidence sources` after the normal report. Include one line for git history stating what was searched and what surfaced, and one transcript line in the exact form required by [`../transcript-evidence.md`](../transcript-evidence.md). Include this section even when no findings exist.

For a remote target, use the appropriate forge CLI to fetch the diff. Return findings to the caller unless the semantic inputs explicitly request remote inline comments.
