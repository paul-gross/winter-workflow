# Transcript evidence

The transcript-evidence procedure mines coding-session transcripts for process evidence a clean diff hides: failed tool calls, user corrections, walked-back assumptions, and repeated attempts. This document owns the complete reusable procedure — detection, scoping, extraction, evidence thresholds, fallback behavior, and output lines.

The same conceptual failure signals apply across harnesses, while each store's location and message envelope are respected per harness. A harness is added to the supported list only after its store and message schema have been verified in use.

## Inputs

Required inputs:

- the candidate working directories — the workspace root, every in-scope worktree, and each target's project source checkout;
- a time window tied to the review material;
- the changed paths and symbols used to filter relevant sessions.

## Store detection

Store detection honors the environment overrides and probes every root:

```bash
test -d "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/projects"
test -d "${CODEX_HOME:-$HOME/.codex}/sessions"
test -d "${OPENCODE_DATA_DIR:-$HOME/.local/share/opencode}/storage"
```

Probe every supported harness and mine every store found present; one machine may contain sessions from several harnesses. Presence of a store root means mining it for every candidate working directory. Treat absent local history as a normal condition, not an error. When no supported history store is present, fall back to git-history-only evidence and record the fallback exactly in the declared evidence-output form; never attempt guessed store paths.

## Operations

The operations, defined once here — each harness section below carries only what differs for its store:

- **Locate** sessions associated with a candidate working directory within the supplied time window.
- **Filter** to sessions mentioning a changed path or symbol.
- **Extract** only a small window around each relevant failure-signal hit.

Across all of them:

- Scope every read: session files can be multi-megabyte, so never load a whole transcript blindly.
- Reassemble any fan-out storage into chronological session views before counting repeated behavior.
- When filtering, tighten a common-basename match to a full path with extension, or to a write/edit tool call against the target, before trusting it.

## Failure signals

- **Tool error** — a call that failed against its target, encoded per harness as `is_error:true`, confirmed nonzero/error output text, or `state.status:error`.
- **User correction** — a phrase such as `that's not what`, `no, I meant`, `wrong`, `actually`, `undo`, `revert`, or `that's incorrect` in a user turn, confirmed to be correcting the agent rather than appearing in quoted content.
- **Walked-back assumption** — the agent asserting one fact, gathering more evidence, then asserting its opposite.
- **Repeated attempt** — four or more edits to the same file, or repeated variants of the same command within one session; context must still be inspected to distinguish deliberate iteration from confusion.

## Claude Code

The store is `~/.claude/projects/<encoded-cwd>/`, with `CLAUDE_CONFIG_DIR` replacing `~/.claude` when set; it holds one `<uuid>.jsonl` per session, and the cwd is encoded by replacing `/` with `-`.

**Locate.** Encode each candidate cwd by replacing `/` with `-`, so `/home/user/projects/foo` becomes `-home-user-projects-foo`. <!-- winter-lint:example --> With `root="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/projects"`, list `$root/` filtered by `grep -F "$(pwd | tr / -)"`, then `find "$root/<encoded-cwd>/" -name '*.jsonl' -mtime -30`, adjusting the age filter to the supplied time window.

**Filter.** Each JSONL record also carries a `cwd` field, but changed-path overlap is the cheap first pass — `grep -l -F -f <(git diff --name-only <base>...HEAD)` across the encoded-cwd directory's `*.jsonl` files.

**Extract.** User turns are records with `"type":"user"`, and tool failures are tool-result blocks carrying `"is_error":true` or `tool_use_error`; search those encodings plus the constant correction phrases, then read only a small surrounding window.

## codex

The store is `~/.codex/sessions/YYYY/MM/DD/`, with `CODEX_HOME` replacing `~/.codex` when set; sessions are date-bucketed `rollout-*.jsonl` files, and the cwd is stored inside each file.

**Locate.** Sessions are date-bucketed rather than cwd-bucketed — `find "${CODEX_HOME:-$HOME/.codex}/sessions/" -name 'rollout-*.jsonl'` with an `-mtime` filter, walking only date directories that overlap the supplied time window. Each session file's first line carries `session_meta.payload.cwd` identifying the working directory; discard files whose cwd is outside the candidate set.

**Extract.** The JSONL stream contains `response_item`, `event_msg`, and `turn_context` records; user turns are `message` payloads with `role: user`; tool calls are `function_call` or `custom_tool_call` and their results `function_call_output` or `custom_tool_call_output`. Tool failures have no dedicated boolean: confirm failure text in an output string — such as `Process exited with code [1-9]`, `Exit code: [1-9]`, `error`, or `failed` — by reading the surrounding turn, and never report a bare substring match without confirmation.

## opencode

The store is `~/.local/share/opencode/storage/`, with `OPENCODE_DATA_DIR` replacing `~/.local/share/opencode` when set; it uses per-message fan-out files plus session indexes. This procedure covers file-based storage only: versions using `~/.local/share/opencode/opencode.db` do not satisfy the file-store probe and follow the fallback unless a verified SQLite procedure is added to this document.

**Reassemble.** One session is spread across message files — collect all `message/{sessionID}/msg_*.json` files under the storage root and order them into one chronological view before any filtering or counting; session indexes live under `session/` in the same store.

**Locate.** Match `session/{projectHash}/{sessionID}.json` project-directory data to the candidate working directories; if that mapping is unavailable, filter the reassembled views by changed-path or symbol mentions and record that fallback.

**Extract.** Messages carry `role: user` or `role: assistant`; tool activity is a `type: tool` part whose `state.status` identifies failure, with `status: error` carrying `error` or `errorText`. Search user messages for correction phrases and tool parts for error status, then read a small surrounding window.

## Evidence thresholds and output

Call a mistake recurring only when equivalent evidence appears at least twice; a one-off is never promoted to a harness-gap finding. For each candidate pattern, capture one short quote plus the file, symbol, or command it concerns. Return extracted patterns to the consuming methodology as quote-plus-target evidence with the harness name and time window. When a present harness yields no relevant signals, record that it was checked and none surfaced.

The final review's `## Evidence sources` section must include one transcript line naming every searched harness and what surfaced, and that line must let the reader distinguish process-level transcript evidence from git-only evidence at a glance. Examples:

- `codex transcripts (~/.codex/sessions, since base commit): one repeated-edit pattern in foo.py`
- `opencode transcripts: present, no relevant patterns`
- `no supported harness history present — git-history-only`
