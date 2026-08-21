---
description: One aggregated review of a change-set across the review facets the caller names, each judged in its own focused context. Use when asked for a faceted or multi-facet review; the facets must be named.
argument-hint: "<facet>[,<facet>...] [uncommitted | <ref|range> | <paths> | <PR|MR>]"
allowed-tools: Bash, Read, Agent
---

The procedure for this skill is at `winter-workflow:/methodology/review/faceted/process.md`.

## Execute

Translate `$ARGUMENTS` into `{facets, scope}` before reading the procedure:

- The first token is required and binds `facets` to its comma-separated values. An empty invocation is invalid: stop and
  tell the caller the facets must be named, pointing at the facet registry the procedure declares; nothing runs without
  them.
- Map the remainder to `scope`: an empty remainder to `branch-vs-base`, literal `uncommitted` to that scope, existing
  paths to `{paths: [<values>]}`, a forge PR/MR locator to `{remote: <locator>, feedback: default}`, and a verified git
  ref or range to `{range: <value>}`. Reject any other remainder.

Read `winter-workflow:/methodology/review/faceted/process.md` and execute every step with those semantic inputs.
