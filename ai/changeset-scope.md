# Change-set scope — reviewing a feature env as one change

A logical change in this workspace often spans **several repos in one feature env** — a `winter-cli` command and the `ai/` reference that documents it, a convention and its mirror downstream. The `/wf-*` review skills review the *change-set*, not a single repo: each discovers every in-scope repo in the env and hands the whole set to **one reviewer per axis**, so a change in one repo that contradicts something left stale in another is caught by a reviewer that holds both at once.

This doc is the single source for that discovery. The review skills reference it; do not re-derive the steps in each skill.

## When this applies

Only inside a **feature environment** (a per-repo worktree under `<workspace>/<env>/`). Run from a standalone repo or a source checkout, the skills behave exactly as their single-repo path describes — there is no env to fan out over. Detection and the collapse rule below make that automatic.

## Step 1 — Detect the feature env

From the repo worktree you were invoked in:

```bash
toplevel="$(git rev-parse --show-toplevel)"
env_file="$(dirname "$toplevel")/.winter.env"
```

- `$env_file` exists and contains `WINTER_ENV=<name>` → you are in feature env `<name>`; continue to Step 2.
- `$env_file` is absent → **not in a feature env.** Skip the rest of this doc; the change-set is the current repo alone, and the skill proceeds on its single-repo path.

`.winter.env` sits at the env root (`<workspace>/<env>/.winter.env`) and is the canonical env marker — see `workspace:/ai/setup-project-setup.md`.

## Step 2 — List the in-scope repos via the CLI

Run the read-only status command and read its JSON directly — do not hand-roll `git rev-list` loops across repos:

```bash
winter ws status <name> --json
```

Each entry in `repos[]` carries the fields you need. Note the two levels: `branch`, `ahead`, `dirty_count`, `tracking_*`, and `tracking_ref_present` sit at the **entry top level**, while `name`, `pinned`, and the env path are nested under the entry's `worktree` object:

| Field | Use |
|-------|-----|
| `worktree.repository.name` | repo name |
| `worktree.repository.pinned` | pinned repos track main, never a feature branch |
| `worktree.environment.path` | env root; worktree path = `<this>/<repository.name>` |
| `branch` | the worktree's local branch |
| `ahead` / `tracking_branch` / `tracking_ahead` | divergence vs `origin/<main>` and vs the tracked upstream |
| `dirty_count` | uncommitted working-tree files |
| `tracking_ref_present` | whether the upstream ref has been fetched |

Select the in-scope set by the skill's mode:

| Mode | Repo is in scope when | Per-repo diff base |
|------|-----------------------|--------------------|
| **branch-vs-base** (single-axis skills, default) | `ahead > 0` | `origin/<main>` |
| **uncommitted** (single-axis skills, `uncommitted` arg) | `dirty_count > 0` | working tree vs `HEAD` |
| **unpushed** (`/wf-pre-push`) | non-pinned: `tracking_ahead > 0` **or** `ahead > 0`; pinned: `tracking_ahead > 0` | `origin/<main>` |

The **unpushed** predicate is exactly what `winter ws push` would push — it mirrors `_has_commits_to_push` in `workspace:/projects/winter/tools/winter-cli/src/winter_cli/modules/workspace/workspace_push_service.py`. Reuse that computation through `winter ws status --json`; if the push rule changes, that file is the source of truth to re-check.

The worktree path for each in-scope repo is `<worktree.environment.path>/<worktree.repository.name>` — an absolute path the reviewer can `cd` into.

## Step 3 — Resolve each repo's base ref

For **branch-vs-base** and **unpushed** modes, resolve `origin/<main>` *inside each in-scope worktree* with the standard ladder (the first ref that exists is `<base>`):

```bash
git rev-parse --verify origin/master 2>/dev/null \
  || git rev-parse --verify origin/main 2>/dev/null \
  || git rev-parse --verify master 2>/dev/null \
  || git rev-parse --verify main
```

Different repos may resolve to different base refs; resolve per repo, never assume one base for the whole env. **Uncommitted** mode needs no base.

## Step 4 — Collapse to single-repo when the set is small

If the in-scope set has **0 repos**, there is nothing to review — report it and stop. If it has **exactly 1 repo**, there is no cross-repo dimension: review that one repo exactly as the single-repo path, with no union framing and no cross-repo consistency pass.

Only when **≥2 repos** are in scope does the change-set span the env: hand the union to one reviewer per axis, and (for `/wf-pre-push`) run the cross-repo consistency pass.
