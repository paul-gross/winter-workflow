# Winter space — where generated artifacts live

The skills in this extension generate **artifacts that are not repo deliverables** — harness scores, review manifests, and per-session workflow docs and retrospectives. None of these belong to the code being worked on; they are winter's own output. They live in the **winter space**: a winter-resolved, winter-configurable directory tree, *not* a hardcoded location in any one code harness's home directory.

This doc is the single source for **how a skill or agent locates the winter space**. Every skill below reads its directory from here rather than building a path itself.

## The contract: `winter space <kind>`

Resolve an artifact directory by asking winter for it:

```bash
dir="$(winter space scores)"   # -> <space-root>/scores  (read-only: prints a path)
mkdir -p "$dir"                 # create it yourself before writing
```

`winter space <kind>` is a **pure, read-only** resolution: it prints the absolute directory for `<kind>` and does nothing else — no `mkdir`, no writes, no git. A skill **runs this command and writes into the path it returns**, creating the directory itself first; it never hardcodes a harness-home artifact path or assembles the path from a root and a sub-name on its own. That keeps the resolution (default location, configuration override, the sub-directory names) owned entirely by winter, so the same skill run under any code harness lands its output in the same winter-controlled tree.

> **Requires a winter that provides `winter space`.** The command, its configuration key, and the path-resolution rules are implemented in [winter](https://github.com/paul-gross/winter) itself; this extension only *consumes* the resolved value. If `winter space` is missing or errors, `$(winter space <kind>)` substitutes to the empty string — so a skill must **check the command succeeded and returned a non-empty path, and stop on failure** rather than write artifacts to a fallback (`""` → a relative or root path). Never silently degrade.

## The four kinds

| `<kind>` | Default directory | What lands here | Naming |
|----------|-------------------|-----------------|--------|
| `scores` | `workspace:/.winter/scores/` | `harness-score` HTML report + JSON sidecar | `<YYYY-MM-DD>-<project>.{html,json}` |
| `manifests` | `workspace:/.winter/manifests/` | `review-manifest` markdown document + JSON facts | `<YYYY-MM-DD>-<slug>.{md,json}` |
| `workflows` | `workspace:/.winter/workflows/` | per-session documentation root (`glacier`/`blizzard` plan, phase docs, activity logs) | `<YYYY-MM-DD>-<name>/` directory |
| `retrospectives` | `workspace:/.winter/retrospectives/` | the session retrospective | `<YYYY-MM-DD>-<name>.md` |

Same-day re-runs disambiguate with an `-<HHMM>` segment after the date, as each skill already documents.

## Resolution and configuration

- **Default (unconfigured)** — the space root is **workspace-relative**: `workspace:/.winter/`, so the four kinds default to `workspace:/.winter/{scores,manifests,workflows,retrospectives}`. Artifacts travel with the workspace checkout rather than scattering into a harness home directory.
- **Configurable root** — winter accepts an override that may be **workspace-relative** (the default form), **user-local** (e.g. `~/.winter/...`), or **absolute**. Whatever the form, `winter space <kind>` returns the fully-resolved absolute directory; skills are indifferent to which form was configured.

## Creating and ignoring the directory

`winter space` resolves a path but never creates or tracks it — that is the caller's job. A skill that writes artifacts first runs `mkdir -p "$(winter space <kind>)"`. Whether the directory is git-ignored is up to whoever owns the workspace: the in-workspace default (`workspace:/.winter/{scores,manifests,workflows,retrospectives}/`) is a natural `.gitignore` candidate, since these are generated artifacts rather than deliverables — add the entries to the workspace's `.gitignore` if you don't want them tracked. winter does not write ignore rules on your behalf.
