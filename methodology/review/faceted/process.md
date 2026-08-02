# Faceted review

Run one review over a change-set by fanning a single gathered context out across many review **facets** — one forked reviewer per facet, converged by the lead into one aggregated report.

A facet is any named review concern. Every registered review axis is a facet, and so is any concern a caller names that no methodology covers yet.

## Open-closed facet contract

This process is open to new facets and closed to modification by them. It never enumerates facets and never binds to a specific facet's methodology; it discovers both at execution time:

- The [review axes index](../axes/index.md) is the **facet registry**: every axis registered there is an available facet, and registering a new one is a registry change, never a change to this process.
- A facet with no registry entry is still reviewable: its reviewer discovers the target's declared conventions for that concern and reports the missing methodology as a gap (step 5).

## Inputs

| Input | Values |
|-------|--------|
| `facets` | a non-empty list of facet names — **required**; there is no default facet set |
| `scope` | a normalized review scope; scope values, their discovery, their review material, and the omitted-scope default are owned by the [shared review process](../process.md) |

Reject an omitted or empty facet list: nothing runs until the caller names the facets. Scope companions such as `pinned_scope` and `review_bases` pass through under the scope owner's semantics; reject a malformed scope with the owner's valid values.

## Steps

### 1. Establish the facet set

Bind the supplied facet list; deduplicate names and preserve caller order. Facets without a registry entry stay in the set — they are handled by discovery, not rejected.

Reject a facet whose registered methodology declares required evidence inputs that only the shared review process's execution scaffold constructs, rather than deriving from the change-set and target context — today, the `harness` axis — and likewise a facet whose registered subject is not the gathered change-set — today, the `plan` axis, which reviews a current-state plan artifact. Name the rejected facet and route the caller to the shared review process for it; run the remaining facets.

### 2. Establish the change-set

For the implicit local scopes, execute [change-set discovery](../change-set.md) and apply its collapse and zero-target handling, collecting its reviewable entries and delivery blockers. Validate explicit range, paths, or remote scopes under the scope owner's semantics.

### 3. Spawn the facet lead

Spawn the canonical `faceted-reviewer` role in a fresh isolated context with judgment model intent; its task is to execute steps 4–7 of this process. The lead is cold — no session history, no author framing — and its runtime must support the [fork port](../../runtime-ports.md#fork-the-current-context) from within the lead's own context.

The lead's task carries the facet set, the normalized scope, every change-set entry with its absolute worktree path and base ref, all delivery blockers, and the path to this process document.

**Fallback.** If the lead's runtime cannot fork, this process permits the fork port's briefing fallback, executed by the lead itself: the same lead gathers (step 4), writes the orientation briefing from its gathered context, spawns one isolated reviewer per facet carrying the briefing and the step 5 charter, and aggregates (step 7). Only the fork mechanism is replaced — the gather and the aggregation stay with the lead. If the lead's runtime can neither fork nor spawn isolated roles, return `unsupported-capability`. A briefing-fallback run must be labeled in the final report.

### 4. Gather the shared orientation

The lead builds the context every facet reviewer will inherit. Read, across all in-scope repositories:

- the review material for the scope, assembled exactly as the scope owner's execution scaffold declares it;
- the commit messages across each entry's reviewed range, for diff scopes;
- an inventory of changed files and surfaces per repository;
- the critically important adjacent context: the workspace and target agent-context entrypoints, followed just far enough to understand what the change claims to do and where its obligations live.

Close the phase by stating, in context, the change's intent and a per-repository map of its changed surface. Gathering orients; it does not judge. The lead records no findings in this phase and does not deep-dive — depth belongs to the facet reviewers, and a lead that exhausts its context investigating has failed the facets that inherit it.

### 5. Fork one reviewer per facet

Fork the lead's context once per facet in one concurrent group. Each fork's charter:

1. **Review-only restrictions** — do not modify files; do not run builds, services, or the target's test suite; no execution beyond the targeted probes the facet's methodology permits; spawn nothing; return one findings report and stop.
2. **Facet and scope** — the facet name and the change-set it inherits from the gathered orientation.
3. **Discover your criteria** — resolve the facet against the facet registry. A registered facet: read its methodology document and execute every step of it against the inherited change-set. An unregistered facet: discover the declared owners of that concern through the workspace and target agent-context entrypoints, review against those declarations plus general judgment for the concern, and report the absence of a registered methodology as a finding so the registry can grow.
4. **Cross-repository rule** — when the change-set spans multiple repositories, carry the shared review process's cross-repository instruction, verbatim, into the charter.
5. **Deep-dive beyond the orientation** — read whatever the facet's judgment requires: callers, neighbors, conventions, generated artifacts. The inherited context is a starting point, not a boundary.
6. **Return findings to the lead, never to a remote review** — substantiate every finding, then return one findings report per the [reporting contract](../reporting.md), followed by a coverage note of one line per area inspected. Regardless of the scope's `feedback` value, a fork never posts remotely; remote feedback is the lead's job after aggregation (step 7).

### 6. Converge

Await the full concurrent group. A fork that fails or cannot execute leaves its facet **unreviewed**; record it as such and never silently drop it.

### 7. Aggregate

The lead is the closing gate — it converges the facet reports into one review the way a verify finale closes a build phase:

- **Dedup across facets.** The same defect surfaced through two lenses becomes one finding citing both facets, at the highest severity either assigned.
- **Resolve contradictions.** When two facet reports make incompatible claims, investigate and settle which is right before reporting either; never present both or average them.
- **Re-rank with the whole-change view.** A facet sees only its own concern and inflates locally; the lead re-ranks severity across the union under the shared severity buckets and renumbers findings into one id sequence per the reporting contract.
- **Preserve the record.** Keep each facet's coverage note, every reported gap, every delivery blocker collected in step 2, and the list of unreviewed and rejected facets in the final report.
- **Deliver remote feedback last.** For a remote scope, the lead applies the reporting contract's remote-feedback semantics to the aggregated, renumbered report: an omitted or `default` feedback value resolves to `report` for a multi-facet review, and `inline` posts the aggregated findings only after dedup and renumbering are complete.

Return the aggregated report as the lead's single result.

### 8. Relay

The calling session relays the lead's report per the reporting contract's relay semantics, with a preamble naming the facet set, scope, and target count. Label a briefing-fallback execution in the preamble.
