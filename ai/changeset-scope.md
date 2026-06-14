# Change-set scope — reviewing a feature env as one change

A logical change in this workspace often spans **several repos in one feature env** — a `winter-cli` command and the `ai/` reference that documents it, a convention and its mirror downstream. This extension's review skills review the *change-set*, not a single repo: each discovers every in-scope repo in the env and hands the whole set to **one reviewer per axis**, so a change in one repo that contradicts something left stale in another is caught by a reviewer that holds both at once.

This doc is the single source for that discovery, which the review engine ([`./review.md`](./review.md)) and `pre-push` reference; do not re-derive the steps elsewhere. It governs the **env-wide** scopes only — branch-vs-base, uncommitted, and unpushed. The engine's **explicit** scopes (an arbitrary git `<ref|range>` or a `<paths>` set) name their own target in the current repo and skip the env fan-out below.

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

The argument is a `<env>/<repo>` glob pattern (a bare `<name>` expands to `<name>/*`), so a bare env name scopes to that whole env. When scoped to one env this way, `environments` is a one-element array. Iterate `environments[0].worktrees[]` — each entry is one repo in the env:

| Field | Use |
|-------|-----|
| `repo` | repo name |
| `pinned` | pinned repos track main, never a feature branch |
| `branch` | the worktree's local branch |
| `ahead` / `upstream` / `tracking_ahead` | divergence vs `origin/<main>` and vs the tracked upstream |
| `dirty` | uncommitted working-tree files (staged + unstaged + untracked) |
| `tracking_ref_present` | whether the upstream ref has been fetched |

The worktree filesystem path is not carried as a field; derive it as `<workspace.root_path>/<env.name>/<repo>` — an absolute path the reviewer can `cd` into.

Select the in-scope set by the skill's mode:

| Mode | Repo is in scope when | Per-repo diff base |
|------|-----------------------|--------------------|
| **branch-vs-base** (single-axis skills, default) | `ahead > 0` | `origin/<main>` |
| **uncommitted** (single-axis skills, `uncommitted` arg) | `dirty > 0` | working tree vs `HEAD`, incl. untracked |
| **unpushed** (`pre-push`) | non-pinned: `tracking_ahead > 0` **or** `ahead > 0`; pinned: `tracking_ahead > 0` | `origin/<main>` |

The **unpushed** predicate is exactly what `winter ws push` would push — it mirrors `_has_commits_to_push` in `workspace:/projects/winter/tools/winter-cli/src/winter_cli/modules/workspace/workspace_push_service.py`. Reuse that computation through `winter ws status --json`; if the push rule changes, that file is the source of truth to re-check.

The **uncommitted** change-set includes **untracked, non-ignored files**, not only tracked modifications: a new file the author has not yet `git add`ed is uncommitted work and must be reviewed, but `git diff HEAD` omits it. A reviewer on the uncommitted scope reads `git diff HEAD` **and** the untracked files (`git ls-files --others --exclude-standard`) — as their current content for a prose review, or as `git diff --no-index /dev/null <file>` whole-file additions where a unified diff is needed (e.g. the review manifest's hunk enumeration; see `winter-workflow:/ai/review-manifest/format.md#computing-diff_sha`). `dirty` already counts untracked files, so the in-scope predicate needs no change.

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

Only when **≥2 repos** are in scope does the change-set span the env: hand the union to one reviewer per axis, and (for `pre-push`) run the cross-repo consistency pass.
