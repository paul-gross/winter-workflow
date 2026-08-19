# Change-set discovery

This document owns change-set discovery: how a review scope fans out across every repository of one feature environment
so the whole set reaches one reviewer per axis. It is the single source for the discovery steps, consumed by the
[review process](./process.md) and the [multi-axis delivery review](../delivery/review/process.md); the steps must not
be re-derived anywhere else. A logical change often spans several repos in one feature environment, and only a reviewer
holding all of them at once can catch a change in one repo that contradicts something left stale in another.

It governs only the env-wide scopes — branch-vs-base, uncommitted, and unpushed. The review process's explicit scopes
skip the env fan-out entirely; their target semantics are owned by the
[review process's scope-semantics table](./process.md#scope-semantics). Env fan-out applies only inside a feature
environment, meaning a per-repo worktree under `<workspace>/<env>/`; run from a standalone repo or a source checkout
there is no env to fan out over and the executing process uses its single-repository path.

## Feature-env detection

Detection plus the small-set collapse rule below make the env-versus-single-repo choice automatic rather than
caller-supplied. Detection starts from the repo worktree the process was invoked in:

```bash
toplevel="$(git rev-parse --show-toplevel)"
envdir="$(dirname "$toplevel")"
name="$(basename "$envdir")"
```

- If `$envdir/.winter/config.toml` exists, the toplevel is a standalone repo at the workspace root, not a feature env,
  and the change-set is the current repo alone on the single-repo path.
- When that config probe fails and `winter ws status "$name" --json` succeeds with an `environments` array naming
  `$name`, you are in that feature env, and the same output already serves the repo-listing step.
- When the status call instead errors with `No worktrees match`, you are not in a feature env and the single-repo path
  applies.

No env marker file exists on disk: env identity derives from the directory layout and is confirmed by the read-only
status call, and runtime variables are computed and injected at dispatch time rather than written to files — owned by
`workspace:/context/workspace-layout.md`.

## Repo listing

Repo listing reads the JSON of the read-only `winter ws status <name> --json` directly, reusing the detection call's
output, and never hand-rolls `git rev-list` loops across repos. The status argument is a `<env>/<repo>` glob pattern and
a bare env name expands to `<name>/*`, so a bare name scopes the call to the whole env and `environments` comes back as
a one-element array. Iterate `environments[0].worktrees[]`, where each entry is one repo in the env; the per-field
schema (`WorktreeSnapshot`) is owned by `workspace:/context/winter-cli/usage/ws/status.md` — read field meanings there
and reuse those fields rather than deriving counts independently.

The worktree filesystem path is not carried as a status field; derive it as `<workspace.root_path>/<env.name>/<repo>`,
an absolute path the reviewer can `cd` into.

## branch-vs-base

Branch-vs-base answers how the branch differs from the target's mainline and is independent of push configuration. A
repo is in scope when `ahead > 0`, and its per-repo diff base is the integration base resolved inside that worktree.

For branch-vs-base only, resolve the integration base inside each in-scope worktree as the first ref that exists in the
ladder `origin/master`, `origin/main`, `master`, `main`, each probed with `git rev-parse --verify`. Different repos may
resolve different integration refs; resolve per repo and never assume one base for the whole env.

## uncommitted

A repo is in scope when `dirty > 0`, and its material is the working tree against `HEAD` including untracked files; this
scope resolves no base of its own (kind `head`). The status `dirty` count already includes untracked files, so the
in-scope predicate needs no adjustment for them.

The uncommitted change-set includes untracked, non-ignored files, not only tracked modifications: a new file the author
has not yet staged is uncommitted work that must be reviewed, yet `git diff HEAD` omits it. A reviewer on this scope
therefore reads `git diff HEAD` plus the files listed by `git ls-files --others --exclude-standard` — as their current
content for a prose review, or rendered as `git diff --no-index /dev/null <file>` whole-file additions where a unified
diff is needed. One consumer that needs untracked files rendered as whole-file diff additions is the review manifest's
hunk enumeration, at [./manifest/format.md#computing-diff_sha](./manifest/format.md#computing-diff_sha).

## unpushed

The caller supplies a semantic `pinned_scope` of `exclude`, `include`, or `only`. An omitted `pinned_scope` defaults to
`include`, the project-worktree scope of `winter ws push --include-pinned`, and this document is the single owner of
that default. `pinned_scope: exclude` corresponds to a bare default `winter ws push` and `only` to a pinned-only push;
the live pinned-push command behavior is owned by `workspace:/context/winter-cli/usage/ws/push.md` and
`workspace:/context/winter-cli/usage/ws/patterns.md`.

Apply `pinned_scope` before the unpushed predicate:

| `pinned_scope` | Selects                              |
| -------------- | ------------------------------------ |
| `exclude`      | non-pinned worktrees                 |
| `include`      | both pinned and non-pinned worktrees |
| `only`         | pinned worktrees only                |

After applying it, a repo is an ordinary target when `upstream` is non-empty, `tracking_ref_present` is true, and
`tracking_ahead > 0`; its diff base is the worktree's configured upstream. Never OR `ahead > 0` into the unpushed
in-scope predicate: a feature branch can remain ahead of its integration base after all of its commits have been pushed
to its configured upstream.

For unpushed only, each selected worktree's base is that worktree's own non-empty `upstream` field; verify the exact ref
inside that worktree and retain it in the returned target entry. A configured, resolvable upstream is reviewed as
`<upstream>...HEAD`. Never substitute `origin/<main>`, the integration-ref ladder, an env-wide feature branch, or a
sibling repository's upstream for a worktree's configured upstream.

On the single-repository path, resolve the repository's configured upstream directly from its branch tracking
configuration and apply the same unpushed rules; environment discovery and pinned filtering do not change what unpushed
means for the current repository.

### Delivery blockers and explicit review bases

For a worktree admitted by `pinned_scope` whose `upstream` is empty or whose `tracking_ref_present` is false, use
`ahead > 0` only to detect a delivery blocker: name the repo, never describe it as pushable, and never include it as an
ordinary configured-upstream target.

A repo with no configured upstream and local commits is a delivery blocker. A caller-supplied explicit review base —
documented, verified, and recorded — permits review with the target labeled `review-base: explicit`, while the missing-
or unresolved-upstream blocker persists until the delivery upstream resolves; without one, omit the target from diff
review and report it as unreviewed.

A configured upstream whose ref does not yet resolve locally gets no silent fallback: require and record an explicit
verified review base before reviewing, and label the target `review-base: explicit` so a first-push review is not
mistaken for an upstream diff.

## Review-base kinds

Every reviewable target carries the kind of base it was resolved against, not just the ref, so a consumer can tell a
mainline comparison from a delivery diff without re-deriving it; this document is the single owner of that kind
vocabulary.

| Kind          | Base                                                 |
| ------------- | ---------------------------------------------------- |
| `integration` | branch-vs-base — the repo's resolved integration ref |
| `upstream`    | unpushed — the configured upstream                   |
| `explicit`    | unpushed with a supplied review base                 |
| `head`        | uncommitted — `HEAD`                                 |

A ref or range the caller supplies outside env discovery also has kind `explicit`: the kind records where the base came
from, and a caller-named base is explicit however the review reached it.

## The returned change-set

The returned change-set contains the reviewable target entries plus any delivery blockers, and a blocker is part of the
result even when other repositories can still be reviewed.

- With zero reviewable repos and no blockers there is nothing to review — report that and stop; if blockers exist,
  return them even when no diff can be reviewed.
- With exactly one reviewable repo there is no cross-repo dimension: review that repo exactly as the single-repo path,
  with no union framing and no cross-repo consistency pass.
- Only with two or more in-scope repos does the change-set span the env: hand the union to one reviewer per axis and let
  a multi-axis delivery review run its cross-repository consistency pass.
