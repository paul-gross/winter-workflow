# Transcript evidence procedure

Mine coding-session transcripts for process evidence that a clean diff hides: failed tool calls, user corrections, walked-back assumptions, and repeated attempts. This document owns the complete reusable transcript procedure, including detection, scoping, extraction, evidence thresholds, fallback behavior, and output lines.

## Inputs

Require:

- Candidate working directories: the workspace root, every in-scope worktree, and each target's project source checkout.
- A time window tied to the review material.
- Changed paths and symbols used to filter relevant sessions.

## Invariants

- Probe every supported harness and mine every present store; one machine may contain sessions from several harnesses.
- Scope every read. Session files can be multi-megabyte; never load a whole transcript blindly.
- Use the same conceptual signals across harnesses while respecting each store's location and message envelope.
- Treat absent local history as a normal condition, not an error.

## Procedure

For each supported harness, perform the same three operations:

1. **Locate** sessions associated with a candidate working directory and within the supplied time window.
2. **Filter** to sessions mentioning a changed path or symbol. Tighten common basename matches to a full path with extension or a write/edit call against the target.
3. **Extract** only a small window around each relevant failure-signal hit.

After extraction:

1. Reassemble any fan-out storage into chronological session views before counting repeated behavior.
2. For each candidate pattern, capture one short quote and the file, symbol, or command it concerns.
3. Call a mistake recurring only when equivalent evidence appears at least twice. A one-off is not a harness gap.
4. Count four or more edits to the same file, or repeated variants of the same command within one session, as a repeated-attempt signal; still inspect context to distinguish deliberate iteration from confusion.
5. If a present harness has no relevant signals, record that it was checked and none surfaced.
6. If no supported history store is present, fall back to git-history-only and record the fallback exactly as specified under [Evidence output](#evidence-output).

## Supported harnesses

| Harness | History root with override | Layout |
|---------|----------------------------|--------|
| Claude Code | `~/.claude/projects/<encoded-cwd>/`; `CLAUDE_CONFIG_DIR` replaces `~/.claude` | one `<uuid>.jsonl` per session; cwd encoded with `/` replaced by `-` |
| codex | `~/.codex/sessions/YYYY/MM/DD/`; `CODEX_HOME` replaces `~/.codex` | date-bucketed `rollout-*.jsonl`; cwd stored inside each file |
| opencode | `~/.local/share/opencode/storage/`; `OPENCODE_DATA_DIR` replaces `~/.local/share/opencode` | per-message fan-out plus session indexes |

The opencode procedure covers file-based storage. Versions using `~/.local/share/opencode/opencode.db` do not satisfy the file-store probe and therefore follow the fallback unless a verified SQLite procedure is added here.

Add a harness only after its store and message schema have been verified in use.

## Detect stores

Honor environment overrides and probe all roots:

```bash
test -d "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/projects" && echo "claude code present"
test -d "${CODEX_HOME:-$HOME/.codex}/sessions" && echo "codex present"
test -d "${OPENCODE_DATA_DIR:-$HOME/.local/share/opencode}/storage" && echo "opencode present"
```

Presence of a root means mine it for every candidate working directory. If none are present, do not attempt guessed paths; use the fallback.

## Claude Code

### Locate

Encode each candidate cwd by replacing `/` with `-`; `/home/user/projects/foo` becomes `-home-user-projects-foo`. <!-- winter-lint:example -->

```bash
root="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/projects"
ls "$root/" | grep -F "$(pwd | tr / -)"
find "$root/<encoded-cwd>/" -name '*.jsonl' -mtime -30
```

Adjust the age filter to the supplied time window.

### Filter

Each JSONL record also carries `cwd`, but changed-path overlap is the cheap first pass:

```bash
grep -l -F -f <(git diff --name-only <base>...HEAD) "$root/<encoded-cwd>/"*.jsonl
```

Tighten overmatching common names before extraction.

### Extract

User turns use `"type":"user"`. Tool failures are tool-result blocks with `"is_error":true` or `tool_use_error`. Search those encodings plus the constant correction phrases, then read only a small surrounding window.

## codex

### Locate

Sessions are date-bucketed rather than cwd-bucketed:

```bash
find "${CODEX_HOME:-$HOME/.codex}/sessions/" -name 'rollout-*.jsonl' -mtime -30
```

Walk only date directories overlapping the supplied time window. The first line's `session_meta.payload.cwd` identifies the working directory; discard files outside the candidate set.

### Filter

After cwd matching, keep sessions that mention changed paths or symbols. Tighten common-name matches before extraction.

### Extract

The JSONL stream contains `response_item`, `event_msg`, and `turn_context` records.

- User turns are `message` payloads with `role: user`.
- Tool calls are `function_call` or `custom_tool_call`; results are `function_call_output` or `custom_tool_call_output`.
- Tool failures have no dedicated boolean. Confirm failure text in an output string, such as `Process exited with code [1-9]`, `Exit code: [1-9]`, `error`, or `failed`, by reading the surrounding turn. Do not report a substring match without confirmation.

## opencode

### Reassemble

One session is spread across message files. Collect all `message/{sessionID}/msg_*.json` files and order them into one chronological view before filtering or counting:

```bash
store="${OPENCODE_DATA_DIR:-$HOME/.local/share/opencode}/storage"
ls "$store/session/"*/
ls "$store/message/<sessionID>/"msg_*.json
```

### Locate and filter

Match `session/{projectHash}/{sessionID}.json` project-directory data to the candidate working directories. If the mapping is unavailable, filter reassembled views by changed-path or symbol mentions and record that fallback.

### Extract

Messages carry `role: user` or `role: assistant`. Tool activity is a `type: tool` part whose `state.status` identifies failure; `status: error` carries `error` or `errorText`. Search user messages for correction phrases and tool parts for error status, then read a small surrounding window.

## Failure signals

The conceptual signals are constant across formats:

- **User corrections**: phrases such as `that's not what`, `no, I meant`, `wrong`, `actually`, `undo`, `revert`, and `that's incorrect` in a user turn. Confirm that the phrase corrects the agent rather than appearing in quoted content.
- **Tool errors**: a call that failed against its target, encoded as `is_error:true`, confirmed nonzero/error output text, or `state.status:error` according to the harness.
- **Repeated attempts**: four or more edits to the same file or retries of the same command with small variations in one reassembled session.
- **Walked-back assumptions**: the agent asserts one fact, gathers more evidence, then asserts its opposite.

## Evidence output

Return extracted patterns to the consuming methodology as quote-plus-target evidence with the harness name and time window. Do not promote a one-off into a harness-gap finding.

The final review's `## Evidence sources` section must include one transcript line naming every searched harness and what surfaced. Examples:

- `codex transcripts (~/.codex/sessions, since base commit): one repeated-edit pattern in foo.py`
- `opencode transcripts: present, no relevant patterns`
- `Claude Code and codex transcripts: present, no relevant patterns`
- `no supported harness history present — git-history-only`

The reader must be able to distinguish process-level transcript evidence from git-only evidence at a glance.
