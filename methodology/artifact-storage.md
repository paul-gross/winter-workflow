# Winter-workflow artifact storage

Winter-workflow produces generated artifacts that are not deliverables of the target repository. This file owns only the extension's artifact kinds, file naming, and producer/consumer policy.

The Winter CLI owns the artifact-directory command, output contract, resolution rules, and defaults at `workspace:/context/winter-cli/usage/space.md`. Its configuration owner is `workspace:/context/winter-cli/configuration/space.md`. Consumers follow those live documents rather than copying their syntax or configuration facts here.

## Artifact kinds and naming

| Kind | What lands here | Naming |
|------|-----------------|--------|
| `scores` | `harness-score` HTML report and JSON sidecar | `<YYYY-MM-DD>-<project>.{html,json}` |
| `manifests` | `review-manifest` markdown document and JSON facts | `<YYYY-MM-DD>-<slug>.{md,json}` |
| `workflows` | per-session workflow documentation | `<YYYY-MM-DD>-<name>/` directory |
| `retrospectives` | session retrospective | `<YYYY-MM-DD>-<name>.md` |

When a same-day run must coexist with an existing artifact, insert `<HHMM>` after the date: `<YYYY-MM-DD>-<HHMM>-<project-or-slug>` or `<YYYY-MM-DD>-<HHMM>-<name>`.

## Consumer policy

- Request the named kind through the [artifact-directory runtime operation](./runtime-ports.md#resolve-a-workflow-artifact-directory); never hardcode a harness-owned path or construct a kind path from an assumed root.
- Stop if resolution fails or returns an empty value. Never substitute a relative, root, target-worktree, or other fallback path.
- Ensure the resolved destination exists before writing. Artifact producers do not modify repository ignore rules or treat generated artifacts as target deliverables.
- Pass the resolved directory to downstream steps as a semantic path such as `<scores-dir>` or `<manifests-dir>`; do not make those steps resolve it again.
