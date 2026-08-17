# Build processes

The router for the four build processes: pick the process by the shape of the work before executing one.

| Process | Choose when… |
|---------|--------------|
| [snowball](./snowball/process.md) | …the work is a small localized change to existing code — a bug fix, tweak, adjustment, or regression repair — confined to one worktree. |
| [glacier](./glacier/process.md) | …the work is one feature built to a plan — mid-sized or large, net-new or multi-module, carrying a plan and/or acceptance criteria, workable as-is or as a discrete phase of a larger plan. |
| [flurry](./flurry/process.md) | …the work is a defined batch of several small, mostly independent feature asks delivered together, fanned out in parallel across multiple feature environments. |
| [iceberg](./iceberg/process.md) | …the work is ad hoc — unplanned, unphased instructions arriving conversationally, especially several in flight across different work targets — and the default is delegation through a standing coordinator. |

## Close calls

- **Snowball vs. glacier** is weight: snowball is one packed throw at one spot, and work that turns out to need design, phasing, or additional roles bails from snowball to glacier.
- **Flurry vs. glacier** is track shape: glacier drives one feature down one linear track; flurry runs many small features across many parallel tracks.
- **Flurry vs. iceberg** both spread work across multiple environments. Flurry is a closed batch — a known set of asks run to completion and closed by one aggregated review phase — driven by a single lead with no team; iceberg is an open-ended conversational stream handled by a standing coordinator running a live team.

## Model intent

Across all four processes, isolated `ice-carver` invocations use **workhorse** model intent (Sonnet/Terra class): ice-carver is the routine implementation role, and more capable model tiers are reserved for orchestration and judgment.
