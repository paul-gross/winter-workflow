# Review process

Run one caller-neutral review over a change-set that may span several repositories. This process owns scope discovery, fresh-versus-inline execution, model intent, and the review-input scaffold. The selected [axis methodology](./axes/index.md) owns what to inspect and how to judge it; [reporting](./reporting.md) owns common output semantics. Runtime operations follow [`../runtime-ports.md`](../runtime-ports.md).

The unit of review is the **change-set**. One executor holds every in-scope repository at once so it can catch contradictions across repository boundaries. A standalone repository, or a feature environment with only one changed repository, naturally collapses to a single-repository review.

## Semantic inputs

Require callers to supply these normalized inputs rather than invocation-specific syntax:

| Input | Values |
|-------|--------|
| `axis` | any axis registered in [`./axes/index.md`](./axes/index.md) |
| `scope` | `branch-vs-base`, `uncommitted`, `unpushed`, `{range: <verified-ref-or-range>}`, `{paths: [<existing-path>...]}`, or `{remote: <PR-or-MR-locator>, feedback: default|report|inline}` |
| `execution_mode` | `fresh` or `inline` |
| `pinned_scope` | for `unpushed`: `exclude`, `include`, or `only` |
| `review_bases` | optional per-worktree verified refs, documented by the caller for an `unpushed` target whose upstream cannot be diffed |

Default omitted values to `scope: branch-vs-base` and `execution_mode: fresh`. For `unpushed`, an omitted `pinned_scope` takes the default owned by [`./change-set.md`](./change-set.md). Reject an axis not registered in the axes index, a malformed scope, an invalid pinned scope, nonexistent paths, or an unverified ref/range or review base with the valid semantic values. `unpushed` is reserved for a caller performing delivery review. A remote scope may identify GitHub, GitLab, Codeberg, or another forge target supported by an available CLI; its `feedback` member defaults according to the selected axis.

Session adapters own translation from their invocation syntax into these inputs. This process never reads or parses slash-command arguments.

## Axes

Axis documents are the canonical methodology; [`./axes/index.md`](./axes/index.md) owns the axis-to-methodology mapping. Runtime agent identifiers are ports for fresh execution only; they are not methodology owners.

| Axis | Fresh runtime port |
|------|--------------------|
| `code` | `cold-reviewer` |
| `correctness` | `cold-reviewer` |
| `architecture` | `cold-reviewer` |
| `qualities` | `cold-reviewer` |
| `tests` | `cold-reviewer` |
| `context` | `context-reviewer` |
| `harness` | `harness-reviewer` |
| `documentation` | `documentation-reviewer` |

Both execution modes consume the same selected methodology file. Do not copy an axis checklist into a prompt or adapter.

## Scope semantics

The three implicit local scopes fan out across a feature environment. Explicit local scopes operate only on the current repository. Remote scope operates on the identified forge review.

| Scope | Discovery | Review material |
|-------|-----------|-----------------|
| `branch-vs-base` | env-wide through [`./change-set.md`](./change-set.md) | each entry's merge-base-to-`HEAD` diff |
| `uncommitted` | env-wide through [`./change-set.md`](./change-set.md) | tracked diff from `HEAD` plus untracked, non-ignored files |
| `unpushed` | env-wide through [`./change-set.md`](./change-set.md), filtered by `pinned_scope` | each entry's configured-upstream-to-`HEAD` diff, or a labeled explicit review-base diff when required |
| `{range: value}` | current repository | range containing `..` or `...` as supplied; a single ref becomes `<ref>...HEAD` |
| `{paths: values}` | current repository | current state of the named files, with no diff |
| `{remote: locator, ...}` | identified forge review | remote diff and metadata fetched through the appropriate CLI |

Paths scope generalizes a current-state audit. The axis methodology filters the supplied set to its own surface.

### Discover the local change-set

For `branch-vs-base`, `uncommitted`, and `unpushed`, execute [`./change-set.md`](./change-set.md). It detects the feature environment, queries status, and returns reviewable `(repo, worktree-path, base-ref, review-base-kind)` entries plus any delivery blockers. Pass `pinned_scope` and `review_bases` for `unpushed`; do not apply pinned filtering to the other scopes.

- Zero reviewable repositories and no blockers: report `no changes to review` and stop without spawning.
- Any delivery blocker: preserve it in the result. A target without a review base is not sent to a reviewer and is reported as unreviewed.
- One repository, or execution outside a feature environment: use single-repository framing.
- Two or more repositories: give one executor the union and instruct it to review the targets as one change-set.

Range and paths scopes skip environment discovery. Validate and normalize them in the current repository before execution.

For remote scope, identify the forge from the locator, verify that its CLI is available and authenticated, and fetch the review metadata and diff. Do not silently substitute a local branch when remote retrieval fails.

## Execution mode

### Fresh

Spawn the selected canonical role in a one-shot isolated context with **judgment model intent** (Opus/Sol class), supply the scaffold below, and await its result. The session adapter resolves the role's projected identity and model. Fresh execution has zero prior conversation context and is the default because it avoids the author's framing and design-history bias. Delivery review always uses fresh execution.

Override to a cheaper model only for a deliberately trivial scope and state the downgrade to the caller.

### Inline

The invoking agent executes the same scaffold and selected axis methodology in its current context without spawning. Inline execution is warm and therefore forfeits freshness; use it only when that bias is acceptable. It does not select a different checklist, evidence bar, severity rule, or report format.

## Execution scaffold

For fresh mode, construct a self-contained spawn prompt from the following parts. For inline mode, treat the same parts as self-instructions.

1. **One-shot restrictions.** For fresh mode, require the isolated-role default declared by [`../runtime-ports.md`](../runtime-ports.md#spawn-an-isolated-role), returning one categorized report.

2. **Semantic inputs.** State the normalized `axis`, `scope`, and `execution_mode`. For `unpushed`, also state `pinned_scope`, every target's configured upstream or labeled explicit review base, and all delivery blockers. Name every target with its absolute worktree path and base ref, the normalized explicit range or absolute path set, or the remote locator and feedback destination.

3. **Review material.** Supply commands or already-resolved material for the scope:

   - `branch-vs-base`: in each worktree, run `git diff <integration-base>...HEAD --stat`, then `git diff <integration-base>...HEAD`.
   - `unpushed`: in each reviewable worktree, run `git diff <configured-upstream-or-explicit-review-base>...HEAD --stat`, then the corresponding full diff. Preserve which base kind was used.
   - `uncommitted`: in each worktree, run `git diff HEAD --stat`, then `git diff HEAD`; also enumerate and read `git ls-files --others --exclude-standard` because `git diff HEAD` omits untracked work.
   - range: run `git diff <normalized-range> --stat`, then `git diff <normalized-range>`.
   - paths: enumerate and read the current state of every named file; do not synthesize a diff.
   - remote: provide the forge CLI and locator, then direct the executor to fetch the remote metadata and diff.

4. **Cross-repository rule.** For a local diff spanning multiple repositories, add verbatim:

   > Because you hold every in-scope repository at once, flag any cross-repository contradiction within your axis — a change in one repository that leaves a broken caller, dead reference, contradicting assumption, or stale mirror in another — as one finding.

5. **Axis execution.** Name the canonical axis file from [`./axes/index.md`](./axes/index.md) and direct the executor to read it and execute every step. Do not paraphrase its checklist or output rules.

6. **Harness evidence inputs.** For the `harness` axis, also supply:

   - Transcript candidate working directories: the workspace root, every in-scope worktree, and each target's project source checkout.
   - Evidence time window: since the base commit for diff scopes; approximately 30 days for uncommitted or current-state paths.
   - Changed paths and symbols extracted from the review material.
   - For diff scopes, the commit list from base to reviewed head or across the normalized range.

7. **Output owner.** Direct the executor to follow [`./reporting.md`](./reporting.md) and all axis-specific additions. For remote scope, preserve the selected axis's default feedback behavior unless `scope.feedback` explicitly overrides it.

## Relay

Relay a completed single-axis report according to [`./reporting.md`](./reporting.md). A multi-axis caller may synthesize the reports under its own declared contract.

If a [review manifest](./manifest/index.md) exists for the change-set, reconcile it after the review settles:

- If fixes or other edits changed the diff, its freshness binding is stale; regenerate it rather than leaving a manifest that describes an old diff.
- If a finding proves a `mechanical` or `pattern` hunk carried a decision, promote that hunk to `novel` or regenerate the manifest.
- If the diff did not change and no finding contradicted a cheap tier, leave the manifest intact.

## Optional attention ordering

A [review manifest](./manifest/index.md) can partition a large or mechanical-heavy diff into `mechanical`, `pattern`, and `novel` tiers before review. It is optional, advisory, and not an axis. Skip it when the diff already fits in a glance.
