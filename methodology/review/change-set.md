# Change-set scope — reviewing a feature env as one change

A logical change often spans **several repos in one feature env**. Review the *change-set*, not a single repo: each discovers every in-scope repo in the env and hands the whole set to **one reviewer per axis**, so a change in one repo that contradicts something left stale in another is caught by a reviewer that holds both at once.

This doc is the single source for that discovery, used by the review process ([`./process.md`](./process.md)) and the [multi-axis delivery review](../delivery/review/process.md); do not re-derive the steps elsewhere. It governs the **env-wide** scopes only — branch-vs-base, uncommitted, and unpushed. The review process's **explicit** scopes (an arbitrary git `<ref|range>` or a `<paths>` set) name their own target in the current repo and skip the env fan-out below.

For `unpushed`, the caller also supplies semantic `pinned_scope: exclude|include|only`. These values correspond respectively to non-pinned worktrees, both pinned and non-pinned worktrees, or pinned worktrees only. The caller may also supply a documented, verified explicit review base for a worktree whose delivery upstream cannot be diffed; that base permits review but never removes a delivery blocker.

## When this applies

Only inside a **feature environment** (a per-repo worktree under `<workspace>/<env>/`). Run from a standalone repo or a source checkout, the executing process uses its single-repository path — there is no env to fan out over. Detection and the collapse rule below make that automatic.

## Step 1 — Detect the feature env

From the repo worktree you were invoked in:

```bash
toplevel="$(git rev-parse --show-toplevel)"
envdir="$(dirname "$toplevel")"
name="$(basename "$envdir")"
```

- `$envdir/.winter/config.toml` exists → `$toplevel` is a standalone repo at the workspace root — **not in a feature env.** Skip the rest of this doc; the change-set is the current repo alone, and the skill proceeds on its single-repo path.
- Otherwise run `winter ws status "$name" --json`. Success, with an `environments` array naming `<name>` → you are in feature env `<name>`, and you already hold the Step 2 output. An error (`No worktrees match`) → **not in a feature env** — same single-repo path as above.

No env marker file exists on disk — env identity derives from the directory layout and is confirmed by the read-only status call; runtime vars are computed and injected at dispatch time, never written to a file (see `workspace:/context/workspace-layout.md`).

## Step 2 — List the in-scope repos via the CLI

Run the read-only status command and read its JSON directly (Step 1's detection already ran it — reuse that output) — do not hand-roll `git rev-list` loops across repos:

```bash
winter ws status <name> --json
```

The argument is a `<env>/<repo>` glob pattern (a bare `<name>` expands to `<name>/*`), so a bare env name scopes to that whole env. When scoped to one env this way, `environments` is a one-element array. Iterate `environments[0].worktrees[]` — each entry is one repo in the env; the per-field schema (`WorktreeSnapshot`) is owned by `workspace:/context/winter-cli/usage/ws/status.md` — read the field meanings there rather than re-deriving them.

The worktree filesystem path is not carried as a field; derive it as `<workspace.root_path>/<env.name>/<repo>` — an absolute path the reviewer can `cd` into.

Select the in-scope set by the caller's semantic scope:

| Mode | Repo is in scope when | Per-repo diff base |
|------|-----------------------|--------------------|
| **branch-vs-base** | `ahead > 0` | the repo's integration base resolved in step 3 |
| **uncommitted** | `dirty > 0` | working tree vs `HEAD`, including untracked files |
| **unpushed** | after applying `pinned_scope`: `upstream` is non-empty, `tracking_ref_present` is true, and `tracking_ahead > 0`; a missing or unresolved upstream with `ahead > 0` is a delivery blocker, not an ordinary target | the worktree's configured `upstream`, handled in step 4 |

For `unpushed`, apply `pinned_scope` before the predicate: `exclude` selects non-pinned worktrees, `include` selects both, and `only` selects pinned worktrees. These are semantic equivalents of Winter push's pinned scopes; `workspace:/context/winter-cli/usage/ws/push.md` and `workspace:/context/winter-cli/usage/ws/patterns.md` own the live command behavior. Within that explicit pinned scope, include a worktree with non-empty `upstream` and `tracking_ref_present: true` only when `tracking_ahead > 0`. Do not OR `ahead > 0` into that predicate: a feature branch can remain ahead of its integration base after all of its commits have been pushed to its configured upstream. Reuse the status fields defined by `workspace:/context/winter-cli/usage/ws/status.md` rather than deriving counts independently.

For worktrees admitted by `pinned_scope` whose `upstream` is empty or whose `tracking_ref_present` is false, use `ahead > 0` only to detect a **delivery blocker**. Name the repo and do not describe it as pushable or include it as an ordinary configured-upstream target. It becomes reviewable only if the caller supplies and records an explicit verified review base; the missing- or unresolved-upstream blocker remains until the delivery upstream resolves.

The **uncommitted** change-set includes **untracked, non-ignored files**, not only tracked modifications: a new file the author has not yet `git add`ed is uncommitted work and must be reviewed, but `git diff HEAD` omits it. A reviewer on the uncommitted scope reads `git diff HEAD` **and** the untracked files (`git ls-files --others --exclude-standard`) — as their current content for a prose review, or as `git diff --no-index /dev/null <file>` whole-file additions where a unified diff is needed (e.g. the review manifest's hunk enumeration; see `winter-workflow:/methodology/review/manifest/format.md#computing-diff_sha`). `dirty` already counts untracked files, so the in-scope predicate needs no change.

## Step 3 — Resolve branch-vs-base integration refs

For **branch-vs-base** only, resolve the integration base *inside each in-scope worktree* with the standard ladder (the first ref that exists is `<base>`):

```bash
git rev-parse --verify origin/master 2>/dev/null \
  || git rev-parse --verify origin/main 2>/dev/null \
  || git rev-parse --verify master 2>/dev/null \
  || git rev-parse --verify main
```

Different repos may resolve to different integration refs; resolve per repo, never assume one base for the whole env. This scope answers how the branch differs from the target's mainline and is independent of push configuration. **Uncommitted** mode needs no base.

## Step 4 — Resolve unpushed delivery refs

For **unpushed** only, use each selected worktree's non-empty `upstream` field as that worktree's base. Verify the exact ref in that worktree and retain it in the returned target entry. Never substitute `origin/<main>`, the branch-vs-base ladder, an env-wide feature branch, or a sibling repository's upstream.

On the single-repository path, resolve that repository's configured upstream directly from its branch tracking configuration and apply the same rules below. Environment discovery and pinned filtering do not change what `unpushed` means for the current repository.

- Configured, resolvable upstream: review `<upstream>...HEAD`.
- No configured upstream and local commits: return a delivery blocker. If the caller supplied a documented explicit review base, review against that base while labeling the target `review-base: explicit` and keeping the blocker. Without one, omit that target from diff review and report it as unreviewed.
- Configured upstream whose ref does not yet resolve locally: do not silently fall back. Require and record an explicit verified review base before reviewing; label the target `review-base: explicit` so a first-push review is not mistaken for an upstream diff.

The returned change-set therefore contains reviewable target entries plus any delivery blockers. A blocker is part of the result even when other repositories can still be reviewed.

## Step 5 — Collapse to single-repo when the set is small

If the reviewable set has **0 repos** and there are no blockers, there is nothing to review — report it and stop. If blockers exist, return them even when no diff can be reviewed. If there is **exactly 1 reviewable repo**, there is no cross-repo dimension: review that one repo exactly as the single-repo path, with no union framing and no cross-repo consistency pass.

Only when **≥2 repos** are in scope does the change-set span the env: hand the union to one reviewer per axis, and let a multi-axis delivery review run its cross-repository consistency pass.
