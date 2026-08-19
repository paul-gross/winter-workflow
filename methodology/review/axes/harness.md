# Harness review axis

This axis reviews the seam between an application and its agentic harness. It determines whether verifier tooling, agent
context, and conventions kept pace with application change, and whether the application is shaped so agents can develop
and verify it productively.

Boundaries with sibling axes:

- Claim an application finding only when it has an agentic-development ramification.
- Never claim a purely structural concern without an agent-productivity consequence — route it to the `code` axis.
- Never adjudicate authoring-convention conformance for agent-facing markdown: claim only currency or seam drift, and
  route pure conformance issues to the `context` axis.

## Inputs

The axis consumes the semantic review inputs prepared by the review process at [../process.md](../process.md), plus this
axis's additions from its execution scaffold: transcript candidate working directories and the evidence time window. For
diff scopes, also inspect the commit list from the base through the reviewed head.

## Criteria discovery

Start at the workspace and target agent-context entrypoints and follow their routes to the declared owners of
application facts, harness conventions, verification contracts, and agent-facing integration facts relevant to the
change. Review against declared standards rather than personal preferences, and cite the owning source for
convention-backed findings.

- Follow target-owned hubs into the applicable extension indexes, context facts, architecture owners, contribution
  conventions, and harness artifact guidance, and never assign authority to a familiar filename merely because it
  exists.
- Read existing documentation before reverse-engineering the target.
- Treat methodology as reusable operational procedure: read a methodology leaf when the changed harness participates in
  that operation, but never use it as a generic owner of application architecture, product behavior, or style facts.
- When no owner is reachable for a fact needed to judge the seam, report the missing or ambiguous route rather than
  inventing a convention.

## Application checklist

- **Agent-navigable architecture** — whether module boundaries, naming, locality, and structure match a discoverable
  mental model, or agents will repeatedly misroute work.
- **Observability** — whether logs, traces, status surfaces, debug endpoints, or structured errors would let agents
  understand runtime behavior more directly.
- **Types and inline constraints** — whether type annotations or short comments would preserve invariants, ownership, or
  non-obvious constraints agents otherwise reverse-engineer.
- **Configurability and pluggability** — whether DI seams, feature flags, test doubles, or environment switches are
  needed to make verification possible or efficient.

## Harness-change checklist

- **Agent-context currency** — whether canonical agents, skills, entrypoints, and `context/` or `methodology/` docs
  still name valid modules, commands, examples, and subsystem behavior.
- **Verification tooling currency** — whether backend-verifier references, fixture helpers, CLI test scaffolds, frontend
  selectors, seed data, and other verification tools kept pace with the change.
- **Feedforward and feedback** — whether schemas, examples, agent guidance, methodology or context, hooks, linters, or
  verifier scenarios would prevent the evidenced mistakes.
- **Recent-mistake evidence** — whether git history or transcripts show recurring simple mistakes that better context or
  verification could prevent.
- **New standards** — whether the evidence justifies a convention such as an ordering rule, DI location, or fixture
  pattern.

## Evidence method

1. Read the complete review material, then the surrounding application and harness content.
2. Walk both checklists explicitly, recording a finding or skipping each item — never inventing findings to fill the
   list.
3. Mine scoped git history for recent-mistake evidence.
4. Execute the complete procedure at [../transcript-evidence.md](../transcript-evidence.md) with the supplied candidate
   working directories, time window, and changed paths or symbols.
5. Correlate application changes, harness state, and repeated mistake evidence, reporting only concrete gaps with an
   agent-productivity or verification ramification.

### Git-history mining

Scope the mining to the changed area and the supplied time window. Look for reverts, sequential fixups in the same area,
explicit correction commits, repeated touches to the same lines, and `fix(...): actually ...` patterns. A single fixup
is noise; a repeated pattern is evidence. Useful commands:

- `git log --oneline -n 50 -- <changed-paths>`
- `git log --grep='revert\|hot.?fix\|oops\|undo' --oneline -n 50 -- <changed-paths>`
- `git log --since='2 months ago' --oneline -- <changed-paths>`

## Execution bounds

Do not run tests, builds, or services.

## Findings

Each finding names the checklist item it maps to and carries one-line evidence from the change, git history, or
transcript; its location may be a canonical artifact and section as well as a file and line range.

## Severity

- **must-fix** — concrete, near-certain gaps likely to cause repeated agent mistakes or block verification, including
  stale verifier references, context naming removed APIs, a missing seam that makes verification impossible, or
  recurring evidence of the same mistake.
- **consider** — non-blocking improvements likely to shorten agent loops, such as an observability hint, a useful
  convention, a feedforward example, or stronger typing.
- **notes** — brief acknowledgments of strong seam improvements and concise routing of out-of-scope concerns.

## Output

Output follows the shared reporting contract at [../reporting.md](../reporting.md). For a remote target, fetch the diff
with the appropriate forge CLI and return findings to the caller unless the semantic inputs explicitly request remote
inline comments.

Append an `## Evidence sources` section after the normal report, included even when no findings exist. It carries one
line for git history stating what was searched and what surfaced, and one transcript line in the exact form required by
[../transcript-evidence.md](../transcript-evidence.md).
