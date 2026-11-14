# Build processes

Pick the process by the shape of the work and the caller's selected mode before executing one.

| Process                                         | Choose when…                                                                                                                                                                                                                                                          |
| ----------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [rapid-iteration](./rapid-iteration/process.md) | …the caller explicitly wants responsive interactive iteration with deferred hardening rather than a completion pipeline.                                                                                                                                              |
| [snowball](./snowball/process.md)               | …the work is a small localized change to existing code — a bug fix, tweak, adjustment, or regression repair — confined to one worktree.                                                                                                                               |
| [glacier](./glacier/process.md)                 | …the work is one feature built to a plan — mid-sized or large, net-new or multi-module, carrying a plan and/or acceptance criteria, workable as-is or as a discrete phase of a larger plan.                                                                           |
| [flurry](./flurry/process.md)                   | …the work is a defined batch of several small, mostly independent feature asks delivered together, fanned out in parallel across multiple feature environments.                                                                                                       |
| [ice age](./ice-age/process.md)                 | …the work is a program — many epics and hundreds of changes, with a backlog that still needs refining — to be refined, sliced, built across many environments, and integrated, with the human answering questions as they arise, across as many sessions as it takes. |
| [iceberg](./iceberg/process.md)                 | …the work is ad hoc — unplanned, unphased instructions arriving conversationally, especially several in flight across different work targets — and the default is delegation through a standing coordinator.                                                          |

## Close calls

- **Rapid iteration vs. iceberg** is the completion contract: choose rapid iteration only for an explicitly selected
  deferred-hardening mode. Iceberg delegates an open-ended stream under the ordinary development contract.
- **Snowball vs. glacier** is weight: snowball is one packed throw at one spot, and work that turns out to need design,
  phasing, or additional roles bails from snowball to glacier.
- **Flurry vs. glacier** is track shape: glacier drives one feature down one linear track; flurry runs many small
  features across many parallel tracks.
- **Flurry vs. iceberg** both spread work across multiple environments. Flurry is a closed batch — a known set of asks
  run to completion and closed by one aggregated review phase — driven by a single lead with no team; iceberg is an
  open-ended conversational stream handled by a standing coordinator running a live team.
- **Glacier vs. ice age** is whether one plan can hold the work. Glacier builds one feature to one approved plan with
  the human at each gate; ice age builds many epics, writes the specs and slices itself, and replaces the per-step human
  gates with a short charter, independent gates, questions asked as they arise, and a register of what it decided.
- **Flurry vs. ice age** both fan work across environments. Flurry's batch is known, small, and independent, and closes
  in one session; ice age's slices are derived during the run, depend on each other, and land through a serialized
  integration gate.

## Model intent

Outside rapid iteration, isolated `ice-carver` invocations default to **workhorse** model intent (Sonnet/Terra class).
[Rapid iteration](./rapid-iteration/process.md#start) owns its implementation-tier selection, and ice age lets its
charter's model policy override any role's default.
