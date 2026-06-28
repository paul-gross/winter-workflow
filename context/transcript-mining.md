# Transcript mining — the per-harness session-history seam

`harness-reviewer` mines coding-session transcripts as one of its two evidence sources for recent-mistake findings (the other is git history). A transcript records the *process*, not just the result — failed tool calls, user corrections, walked-back assumptions, repeated attempts — so it surfaces harness gaps a clean final diff hides.

Where those sessions live and how they are shaped is **per harness**: Claude Code, codex, and opencode each store history in a different place, in a different layout, with different field names for the same events. This doc is the single source for that knowledge. Both [`../agents/harness-reviewer.md`](../agents/harness-reviewer.md) (the methodology) and [`./review.md`](./review.md) (the caller context) point here instead of hardcoding any one harness.

Winter is harness-agnostic; the mining must be too. An agent running under opencode or codex should get the same process-level signal a Claude Code session does, resolved through this seam.

## The seam

The work is the same three operations regardless of harness; only the *location*, *layout*, and *field names* vary:

1. **Locate** — find the sessions for a candidate cwd within a time window.
2. **Filter** — keep only sessions that touch the diff's changed paths or symbols.
3. **Extract** — pull the failure signals out of that harness's message format.

The **conceptual failure signals are constant** across harnesses (see [§Failure signals](#failure-signals)); what differs is the JSON envelope that encodes them. Resolve the harness first, then apply that harness's procedure below.

**Scope every read.** Transcripts are large — often multi-megabyte per session. Never load a whole session blindly: locate, then filter, then read a small window around each signal hit.

**Per-machine.** All three stores are local to the machine where the work happened — a fresh checkout or CI box has none. That is not an error; it is the universal fallback (below).

## Supported harnesses

| Harness | History root (env override) | Layout |
|---------|-----------------------------|--------|
| Claude Code | `~/.claude/projects/<encoded-cwd>/` (`CLAUDE_CONFIG_DIR` replaces `~/.claude`) | per-session `<uuid>.jsonl`; cwd encoded into the directory name, `/` → `-` |
| codex | `~/.codex/sessions/YYYY/MM/DD/` (`CODEX_HOME` replaces `~/.codex`) | per-session `rollout-*.jsonl`, date-bucketed; cwd recorded *inside* the file, not the path |
| opencode | `~/.local/share/opencode/storage/` (`OPENCODE_DATA_DIR` replaces `~/.local/share/opencode`) | per-**message** fan-out: `message/{sessionID}/msg_*.json` + a `session/{projectHash}/{sessionID}.json` index |

The opencode row describes its **file-based storage mode**; a given opencode version may instead keep history in a SQLite store (`~/.local/share/opencode/opencode.db`), in which case the `storage/` probe below correctly returns absent and routes to the fallback. Verify the layout against the opencode version in use before relying on the file-based steps.

Add a harness here only when someone runs it; until then its absence simply routes to the git-history-only fallback.

## Detecting which harness to mine

Probe for each harness's history root, honoring its env override, and mine every one that is present (a machine may have run more than one):

```bash
test -d "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/projects"     && echo "claude code present"
test -d "${CODEX_HOME:-$HOME/.codex}/sessions"             && echo "codex present"
test -d "${OPENCODE_DATA_DIR:-$HOME/.local/share/opencode}/storage" && echo "opencode present"
```

**Universal fallback.** If *no* supported harness's history root exists for any plausible cwd, detection yields nothing and mining falls back to git-history-only, recorded per [§Evidence sources](#evidence-sources). The reviewer owns this fallback as methodology — see [`../agents/harness-reviewer.md`](../agents/harness-reviewer.md).

## Per-harness mining

For each present harness, run *locate → filter → extract*. Enumerate candidate cwds the same way for all three: the workspace root, every in-scope worktree path, and each one's project source checkout.

### Claude Code

- **Locate** — the cwd is encoded into the directory name with `/` → `-`, so `/home/user/projects/foo` → `-home-user-projects-foo`. <!-- winter-lint:example -->

  ```bash
  root="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/projects"
  ls "$root/" | grep -F "$(pwd | tr / -)"
  find "$root/<encoded-cwd>/" -name '*.jsonl' -mtime -30
  ```

- **Filter** — each line also carries a `"cwd"` field, but filename overlap is the cheap first pass: only open sessions that mention a changed path or symbol. When the changed paths are themselves common harness vocabulary (an agent or doc referenced workspace-wide), the bare basename overmatches — tighten to the full path with extension, or require co-occurrence with an `Edit`/`Write` tool call against the file.

  ```bash
  grep -l -F -f <(git diff --name-only <base>...HEAD) "$root/<encoded-cwd>/"*.jsonl
  ```

- **Extract** — JSONL, one record per line. User turns are `"type":"user"`; tool failures are tool-result blocks carrying `"is_error":true` (and `tool_use_error`). Grep for those plus the constant correction phrases, and read a small window around each hit.

### codex

- **Locate** — sessions are **date-bucketed**, not cwd-bucketed: `${CODEX_HOME:-~/.codex}/sessions/YYYY/MM/DD/rollout-*.jsonl`. Walk the date directories overlapping the diff's time window.

  ```bash
  find "${CODEX_HOME:-$HOME/.codex}/sessions/" -name 'rollout-*.jsonl' -mtime -30
  ```

- **Filter** — the cwd lives *inside* the file: the first line is a `{"type":"session_meta","payload":{"cwd":"…","timestamp":"…"}}` record. Read that line to match the session to a candidate cwd, then grep the body for changed-path overlap as with Claude.

- **Extract** — JSONL of `response_item` records (plus `event_msg`/`turn_context`). The signal-bearing payloads:
  - User turns: `{"type":"message","role":"user","content":[…]}` — grep the text for the correction phrases.
  - Tool calls: `function_call` (and `custom_tool_call`, e.g. `apply_patch`); their results are `function_call_output` / `custom_tool_call_output`.
  - **Tool failures have no `is_error` flag** — codex records the result as text in the output's `"output"` string. Detect them by failure text in that string: `Process exited with code [1-9]`, `Exit code: [1-9]`, `error`, `failed`. Read the surrounding turn to confirm it is a real failure, not a matched substring.

### opencode

- **Reassemble first.** opencode fans one session out across many files: `message/{sessionID}/msg_*.json` is **one file per message**, not per session. Collect every `msg_*.json` under a session id and order them into a single conversation view *before* extracting any signal — a per-file pass sees individual messages with no notion of repeats or back-and-forth.

  ```bash
  store="${OPENCODE_DATA_DIR:-$HOME/.local/share/opencode}/storage"
  ls "$store/session/"*/                       # session indices, per project hash
  ls "$store/message/<sessionID>/"msg_*.json   # the per-message fan-out to reassemble
  ```

- **Locate / filter** — the `session/{projectHash}/{sessionID}.json` index records the session's project directory; match it to a candidate cwd. Where that mapping is unavailable, fall back to filtering by changed-path mentions in the reassembled view.

- **Extract** — each message JSON carries a `"role"` (`"user"` / `"assistant"`); tool activity is a part with `"type":"tool"` whose `state` object holds a `"status"`. A failed tool call is `"status":"error"` (with an `"error"` field / `"errorText"`). Grep the reassembled view for user-role correction phrases and for tool parts in the `error` status.

## Failure signals

The signals to hunt are the same for every harness; only the field names that encode them differ (per the per-harness sections above). What stays constant:

- **User corrections** — natural-language phrases in a user turn, identical across harnesses: `that's not what`, `no, I meant`, `wrong`, `actually`, `undo`, `revert`, `that's incorrect`. The envelope differs (`type:user` line vs. `role:user` message vs. `role:user` part); the phrases do not.
- **Tool errors** — a tool call that failed against its target. Encoded as `is_error:true` (Claude), nonzero-exit / error text in the output string (codex), or a tool part with `state.status:error` (opencode).
- **Repeated attempts** — the same file edited 4+ times, or the same command retried with small variations, within one session. Count tool calls against the same target in the reassembled session.
- **Walked-back assumptions** — the agent asserting one thing, reading more, then asserting the opposite.

How a reviewer turns these hits into findings — quote-plus-target, the recurring-vs-one-off bar, reporting an empty result — is reviewer methodology, owned by [`../agents/harness-reviewer.md`](../agents/harness-reviewer.md), not restated here.

## Evidence sources

The reviewer's `## Evidence sources` section must carry one transcript line that names **which harness's history was searched** and what surfaced — e.g. "codex transcripts (`~/.codex/sessions`, since base commit): one repeated-edit pattern in `foo.py`", or "opencode transcripts: present, no relevant patterns". When the universal fallback fired, say so explicitly: "no supported harness history present — git-history-only". The reader must be able to tell process-level evidence from git-only evidence at a glance.
