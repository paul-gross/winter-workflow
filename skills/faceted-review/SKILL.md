---
description: Faceted review — a cold lead gathers the change-set context once, forks one reviewer per review facet (code, context, harness, documentation, or any named facet), and aggregates their findings into one report. Use when asked for a faceted, multi-facet, or full-spectrum review of a change.
argument-hint: "[<facet>[,<facet>...]] [uncommitted | <ref|range> | <paths> | <PR|MR>]"
allowed-tools: Bash, Read, Agent
---

The procedure for this skill is at `winter-workflow:/methodology/review/faceted/process.md`.

## Execute

Translate `$ARGUMENTS` into `{facets, scope}` before reading the procedure:

- A leading facet token binds `facets` to its comma-separated values and is removed: any token containing a comma, or a bare word that is not `uncommitted` and does not resolve to an existing path, a verified git ref or range, or a forge PR/MR locator. When a bare word matches both a facet name and a scope form, treat it as scope; the comma form (e.g. `code,`) forces the facet reading. Omission binds `facets` omitted (every registered facet).
- Map the remainder to `scope`: an empty remainder to `branch-vs-base`, literal `uncommitted` to that scope, existing paths to `{paths: [<values>]}`, a forge PR/MR locator to `{remote: <locator>, feedback: default}`, and a verified git ref or range to `{range: <value>}`. Reject any other remainder.

Read `winter-workflow:/methodology/review/faceted/process.md` and execute every step with those semantic inputs.
