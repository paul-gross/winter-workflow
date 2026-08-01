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
| `facets` | a non-empty list of facet names, or omitted to mean every facet in the registry at execution time |
| `scope` | a normalized review scope; scope values, their discovery, and their review material are owned by the [shared review process](../process.md) |

Default an omitted `scope` to `branch-vs-base`. Scope companions such as `pinned_scope` and `review_bases` pass through under the scope owner's semantics. Reject a malformed scope with the owner's valid values; reject an empty explicit facet list.

## Steps

### 1. Establish the facet set

Bind the supplied facet list, or enumerate the facet registry when `facets` is omitted. Deduplicate names and preserve caller order. Facets without a registry entry stay in the set — they are handled by discovery, not rejected.

### 2. Establish the change-set

For the implicit local scopes, execute [change-set discovery](../change-set.md) and collect its reviewable entries and delivery blockers. Validate explicit range, paths, or remote scopes under the scope owner's semantics. Zero reviewable targets and no blockers: report `no changes to review` and stop without spawning.

### 3. Spawn the facet lead

Spawn the **facet lead**: a fresh isolated context with judgment model intent whose task is to execute steps 4–7 of this process. The lead is cold — no session history, no author framing — and its runtime must support the [fork port](../../runtime-ports.md#fork-the-current-context) from within the lead's own context.

The lead's task carries the facet set, the normalized scope, every change-set entry with its absolute worktree path and base ref, all delivery blockers, and the path to this process document. If the adapter cannot provide a forkable lead context, this process permits the fork port's briefing fallback; the final report must label that degradation.

### 4. Gather the shared orientation

The lead builds the context every facet reviewer will inherit. Read, across all in-scope repositories:

- the review material for the scope — stat then full diff per entry, plus untracked files for `uncommitted` — as declared by the scope owner;
- the commit messages across each entry's reviewed range, for diff scopes;
- an inventory of changed files and surfaces per repository;
- the critically important adjacent context: the workspace and target agent-context entrypoints, followed just far enough to understand what the change claims to do and where its obligations live.

Close the phase by stating, in context, the change's intent and a per-repository map of its changed surface. Gathering orients; it does not judge. The lead records no findings in this phase and does not deep-dive — depth belongs to the facet reviewers, and a lead that exhausts its context investigating has failed the facets that inherit it.

### 5. Fork one reviewer per facet

Fork the lead's context once per facet in one concurrent group. Each fork's charter:

1. **Facet and scope** — the facet name and the change-set it inherits from the gathered orientation.
2. **Discover your criteria** — resolve the facet against the facet registry. A registered facet: read its methodology document and execute every step of it against the inherited change-set. An unregistered facet: discover the declared owners of that concern through the workspace and target agent-context entrypoints, review against those declarations plus general judgment for the concern, and report the absence of a registered methodology as a finding so the registry can grow.
3. **Deep-dive beyond the orientation** — read whatever the facet's judgment requires: callers, neighbors, conventions, generated artifacts. The inherited context is a starting point, not a boundary.
4. **Return findings, not investigation** — substantiate every finding, then return one findings report per the [reporting contract](../reporting.md), followed by a coverage note of one line per area inspected.

### 6. Converge

Await the full concurrent group. A fork that fails or cannot execute leaves its facet **unreviewed**; record it as such and never silently drop it.

### 7. Aggregate

The lead is the closing gate — it converges the facet reports into one review the way a verify finale closes a build phase:

- **Dedup across facets.** The same defect surfaced through two lenses becomes one finding citing both facets, at the highest severity either assigned.
- **Resolve contradictions.** When two facet reports make incompatible claims, investigate and settle which is right before reporting either; never present both or average them.
- **Re-rank with the whole-change view.** A facet sees only its own concern and inflates locally; the lead re-ranks severity across the union under the shared severity buckets and renumbers findings into one id sequence per the reporting contract.
- **Preserve the record.** Keep each facet's coverage note, every reported gap, and the list of unreviewed facets in the final report.

Return the aggregated report as the lead's single result.

### 8. Relay

The calling session relays the lead's report per the reporting contract's relay semantics, with a preamble naming the facet set, scope, and target count. Label a briefing-fallback execution in the preamble.
