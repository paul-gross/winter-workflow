#!/usr/bin/env python3
"""Deterministic measurement half of the `optimize-context` skill.

This script is the mechanical evidence-gathering step that
`methodology/optimize-context/process.md` invokes; the process reads its JSON
output and does the judgment work (classification narrative, operator
approval, applying the approved `skillOverrides` subset). Nothing here writes
markdown or decides what to keep — it only measures and reports.

Two scopes, kept apart everywhere in the output:

  machine-global  Per-skill / per-subagent invocation counts, mined from
                   every `~/.claude/projects/**/*.jsonl` session transcript on
                   this machine — never scoped to one repo or workspace.
  target-scoped   The always-loaded surfaces of one target directory: its
                   memory-file `@import` chain, its extension hub (`index.md`),
                   its agent definitions, and its skill descriptions. Prefers
                   the installed form (`.claude/agents/`, `.claude/skills/`)
                   when the target is a live workspace root, falling back to
                   the source form (`agents/`, `skills/`) when it is an
                   extension checkout.

Two subcommands:

  measure  Emit the full JSON report (counts + inventory + classification).
  apply    Merge an operator-approved `skillOverrides` object into a
           `settings.json`, touching no other key. This is the *only* file
           mutation this script (or the skill built on it) ever performs.

Read-only over `~/.claude/projects`: `measure` never writes there. Stdlib
only, so it runs the same way `scripts/lint-agents.py` and
`scripts/lint-methodology.py` do — no extra dependency to install first.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tomllib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = 1
DEFAULT_TRANSCRIPTS_DIR = Path.home() / ".claude" / "projects"
DEFAULT_TOO_NEW_DAYS = 30
TOKEN_CHARS_PER_TOKEN = 4  # rough char/token heuristic; every *_tokens_est field is an estimate, not a real tokenizer count
MANIFEST = "winter-ext.toml"
WORKSPACE_CONFIG = Path(".winter") / "config.toml"
VALID_OVERRIDE_VALUES = ("on", "name-only", "user-invocable-only", "off")
DEFAULT_OVERRIDE_VALUE = "user-invocable-only"
AGENT_EXCLUDE_NAMES = {"README.md"}
AGENT_EXCLUDE_DIRS = {"docs"}

_SKILL_TOOL_RE = re.compile(r'"skill"\s*:\s*"([^"]*)"')
_COMMAND_NAME_RE = re.compile(r"<command-name>\s*/?\s*([^<]*?)\s*</command-name>")
_SUBAGENT_RE = re.compile(r'"subagent_type"\s*:\s*"([^"]*)"')
# An import token may be a bare relative path (`context/index.md`), a
# dot-relative one (`./x.md`, `../x.md`), a dotfile-rooted one
# (`.winter/ext/context/index.md`), or a home-rooted one (`~/x.md`).
_IMPORT_RE = re.compile(r"(?<![\w@])@((?:~|\.{1,2})?/?[A-Za-z0-9_][A-Za-z0-9_./-]*\.md)")
_KEY_RE = re.compile(r"^([A-Za-z0-9_-]+)[ \t]*:(.*)$")
_SKILL_KEY_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9_-]*[A-Za-z0-9])?$")


# ─────────────────────────────── frontmatter ────────────────────────────────


def _strip_quotes(s: str) -> str:
    s = s.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in ("'", '"'):
        return s[1:-1]
    return s


def _frontmatter_blocks(text: str) -> dict[str, dict]:
    """Map each top-level YAML key in a leading `---` fence to its inline value
    and indented body lines. Returns `{}` when there is no frontmatter fence."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    body_lines: list[str] = []
    for line in lines[1:]:
        if line.strip() == "---":
            break
        body_lines.append(line)
    else:
        return {}  # unterminated fence

    blocks: dict[str, dict] = {}
    cur: str | None = None
    for line in body_lines:
        if line and not line[0].isspace():
            m = _KEY_RE.match(line)
            if m:
                cur = m.group(1)
                blocks[cur] = {"inline": m.group(2).strip(), "body": []}
            else:
                cur = None
            continue
        if cur is not None:
            blocks[cur]["body"].append(line)
    return blocks


def _scalar_value(block: dict | None) -> str:
    """The effective string value of a frontmatter key: an inline scalar, a
    `|`/`>` block-scalar body, or a bare multi-line continuation."""
    if block is None:
        return ""
    inline = block["inline"]
    if inline[:1] in ("|", ">"):
        return "\n".join(l.strip() for l in block["body"] if l.strip())
    if inline:
        return _strip_quotes(inline)
    return "\n".join(l.strip() for l in block["body"] if l.strip())


# ─────────────────────────────── git dating ─────────────────────────────────


def find_git_root(path: Path) -> Path | None:
    cur = path if path.is_dir() else path.parent
    while True:
        if (cur / ".git").exists():
            return cur
        if cur.parent == cur:
            return None
        cur = cur.parent


_COMMIT_MARK = "\x01"


def added_date(path: Path) -> tuple[str | None, str | None, bool]:
    """`(iso_date, commit_sha, renamed)` for `path`'s defining file, dated by
    when it arrived at its *current* name — the commit of the most recent
    `git log --follow` rename into this path, or (when it was never renamed)
    the commit that first introduced it. `renamed` is `True` only in the
    former case, so a caller can see that the date does not reach back to the
    file's original creation under a different name. `(None, None, False)`
    when `path` is not inside a git repo, is not tracked, or git is
    unavailable."""
    repo_root = find_git_root(path)
    if repo_root is None:
        return None, None, False
    try:
        rel = path.resolve().relative_to(repo_root.resolve())
    except ValueError:
        return None, None, False
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_root), "log", "--follow", "--name-status", f"--format={_COMMIT_MARK}%H|%aI", "--", str(rel)],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None, None, False
    if result.returncode != 0:
        return None, None, False

    rel_posix = rel.as_posix()
    renamed_iso, renamed_sha = None, None
    oldest_add_iso, oldest_add_sha = None, None
    # git log lists commits newest-first, so the first rename-into-`rel_posix`
    # we see is the most recent one, and the last add-of-`rel_posix` we see
    # (after walking every commit) is the original creation.
    for block in result.stdout.split(_COMMIT_MARK):
        block = block.strip("\n")
        if not block:
            continue
        lines = block.splitlines()
        sha, _, iso = lines[0].partition("|")
        for status_line in lines[1:]:
            if not status_line.strip():
                continue
            fields = status_line.split("\t")
            status, name_fields = fields[0], fields[1:]
            if status.startswith("A") and name_fields and name_fields[0] == rel_posix:
                oldest_add_iso, oldest_add_sha = iso, sha
            elif status.startswith("R") and len(name_fields) >= 2 and name_fields[-1] == rel_posix and renamed_iso is None:
                renamed_iso, renamed_sha = iso, sha

    if renamed_iso:
        return renamed_iso, renamed_sha, True
    return oldest_add_iso, oldest_add_sha, False


def _age_days(iso_date: str | None) -> int | None:
    if not iso_date:
        return None
    try:
        dt = datetime.fromisoformat(iso_date)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return (datetime.now(timezone.utc) - dt).days


# ─────────────────────────────── inventory ──────────────────────────────────


def _workspace_prefix_override(target: Path, ext_name: str | None) -> str | None:
    """The per-`[[standalone_repository]]` `prefix` override for `ext_name` in
    the nearest `.winter/config.toml` above `target`, if any — this beats the
    extension's own `winter-ext.toml` default (see
    `context/winter-cli/configuration/repositories.md`)."""
    if not ext_name:
        return None
    cur = target
    while True:
        config = cur / WORKSPACE_CONFIG
        if config.is_file():
            try:
                with config.open("rb") as fh:
                    data = tomllib.load(fh)
            except (OSError, tomllib.TOMLDecodeError):
                return None
            for entry in data.get("standalone_repository", []):
                if isinstance(entry, dict) and entry.get("name") == ext_name:
                    prefix = entry.get("prefix")
                    return prefix if isinstance(prefix, str) and prefix else None
            return None
        if cur.parent == cur:
            return None
        cur = cur.parent


def _module_prefix(target: Path) -> str | None:
    """The install prefix this target's skills and agents are namespaced
    under (e.g. `wf`), or `None` when the target carries no `winter-ext.toml`
    — a live workspace root, or an unprefixed install. A consuming
    workspace's per-`[[standalone_repository]]` `prefix` override in
    `.winter/config.toml` takes precedence over the extension's own default."""
    manifest = target / MANIFEST
    if not manifest.is_file():
        return None
    try:
        with manifest.open("rb") as fh:
            data = tomllib.load(fh)
    except (OSError, tomllib.TOMLDecodeError):
        return None
    ext_name = data.get("name") if isinstance(data.get("name"), str) else None
    override = _workspace_prefix_override(target, ext_name)
    if override:
        return override
    prefix = data.get("prefix")
    return prefix if isinstance(prefix, str) and prefix else None


def _resolve_source(path: Path) -> Path:
    """Follow symlinks (an installed `.claude/skills/<name>` is typically one)
    to the file that actually defines this entry, for sizing and git dating."""
    try:
        return path.resolve()
    except OSError:
        return path


def _agent_added_date(resolved: Path, target: Path) -> tuple[str | None, str | None, bool]:
    """`added_date` for an installed agent, with a fallback: winter generates
    each installed `.claude/agents/<prefix>-<name>.md` as an untracked copy
    rather than a symlink, so it sits inside the workspace's own git repo yet
    carries no history of its own — `added_date` on it alone comes back
    empty. When it does, look for the tracked source definition under
    `target/.winter/ext/*/agents/<name>.md` by stripping the installed file's
    `<prefix>-` namespace, and date that instead. Sizing and content always
    come from `resolved` (the file a spawn actually loads); only the date is
    ever borrowed from the source checkout."""
    added, commit, renamed = added_date(resolved)
    if added is not None:
        return added, commit, renamed
    ext_root = target / ".winter" / "ext"
    if not ext_root.is_dir() or "-" not in resolved.stem:
        return added, commit, renamed
    _, _, bare_name = resolved.stem.partition("-")
    for ext_dir in sorted(p for p in ext_root.iterdir() if p.is_dir()):
        candidate = ext_dir / "agents" / f"{bare_name}.md"
        if candidate.is_file():
            c_added, c_commit, c_renamed = added_date(candidate.resolve())
            if c_added is not None:
                return c_added, c_commit, c_renamed
    return added, commit, renamed


@dataclass
class SkillEntry:
    name: str
    installed_name: str
    path: str
    description: str
    description_bytes: int
    description_tokens_est: int
    file_bytes: int
    added: str | None
    added_commit: str | None
    age_days: int | None
    renamed: bool


@dataclass
class AgentEntry:
    name: str
    path: str
    file_bytes: int
    added: str | None
    added_commit: str | None
    age_days: int | None
    renamed: bool


@dataclass
class FileEntry:
    path: str
    bytes: int


def discover_skills(target: Path) -> tuple[list[SkillEntry], str]:
    """`(entries, form)` — `form` is `"installed"` (`.claude/skills/`) or
    `"source"` (`skills/`), whichever the target actually has; installed is
    preferred because it is what a session opened at `target` truly loads."""
    installed_dir = target / ".claude" / "skills"
    source_dir = target / "skills"
    skills_dir, form = (installed_dir, "installed") if installed_dir.is_dir() else (source_dir, "source")
    entries: list[SkillEntry] = []
    if not skills_dir.is_dir():
        return entries, form
    for skill_dir in sorted(p for p in skills_dir.iterdir() if p.is_dir()):
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            continue
        source = _resolve_source(skill_md)
        try:
            text = source.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        blocks = _frontmatter_blocks(text)
        description = _scalar_value(blocks.get("description"))
        added, commit, renamed = added_date(source)
        entries.append(
            SkillEntry(
                name=source.parent.name,
                installed_name=skill_dir.name,
                path=str(source),
                description=description,
                description_bytes=len(description.encode("utf-8")),
                description_tokens_est=round(len(description.encode("utf-8")) / TOKEN_CHARS_PER_TOKEN),
                file_bytes=source.stat().st_size,
                added=added,
                added_commit=commit,
                age_days=_age_days(added),
                renamed=renamed,
            )
        )
    return entries, form


def discover_agents(target: Path) -> tuple[list[AgentEntry], str]:
    installed_dir = target / ".claude" / "agents"
    source_dir = target / "agents"
    agents_dir, form = (installed_dir, "installed") if installed_dir.is_dir() else (source_dir, "source")
    entries: list[AgentEntry] = []
    if not agents_dir.is_dir():
        return entries, form
    for agent_md in sorted(agents_dir.glob("*.md")):
        if agent_md.name in AGENT_EXCLUDE_NAMES:
            continue
        if any(part in AGENT_EXCLUDE_DIRS for part in agent_md.relative_to(agents_dir).parts[:-1]):
            continue
        source = _resolve_source(agent_md)
        try:
            text = source.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        blocks = _frontmatter_blocks(text)
        name = _scalar_value(blocks.get("name")) or agent_md.stem
        added, commit, renamed = _agent_added_date(source, target)
        entries.append(
            AgentEntry(
                name=name,
                path=str(source),
                file_bytes=source.stat().st_size,
                added=added,
                added_commit=commit,
                age_days=_age_days(added),
                renamed=renamed,
            )
        )
    return entries, form


@dataclass
class MemoryDiscovery:
    entries: list[FileEntry]
    unresolved_imports: int  # `@import` tokens matched but not found on disk under any base
    truncated: bool  # `max_files` or `max_depth` cut this walk short — the totals below undercount


def _resolve_import_token(token: str, bases: tuple[Path, ...]) -> Path | None:
    if token.startswith("~/") or token == "~":
        expanded = Path(token).expanduser()
        return expanded if expanded.is_file() else None
    if Path(token).is_absolute():
        candidate = Path(token)
        return candidate if candidate.is_file() else None
    for base in bases:
        candidate = (base / token).resolve()
        if candidate.is_file():
            return candidate
    return None


def discover_memory_files(target: Path, max_files: int = 200, max_depth: int = 8) -> MemoryDiscovery:
    """The `@import` chain reachable from this target's own `CLAUDE.md` /
    `AGENTS.md` entrypoints — the memory files a session opened at `target`
    loads before any work begins. Empty for a target with neither (e.g. an
    extension checkout, which has no memory-file entrypoint of its own)."""
    seeds = [target / "CLAUDE.md", target / "AGENTS.md"]
    visited: set[Path] = set()
    entries: list[FileEntry] = []
    unresolved_imports = 0
    truncated = False
    queue: list[tuple[Path, int]] = [(p, 0) for p in seeds if p.is_file()]
    while queue:
        if len(entries) >= max_files:
            truncated = True
            break
        path, depth = queue.pop(0)
        try:
            resolved = path.resolve()
        except OSError:
            continue
        if resolved in visited:
            continue
        if depth > max_depth:
            truncated = True
            continue
        visited.add(resolved)
        try:
            text = resolved.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        entries.append(FileEntry(path=str(resolved), bytes=resolved.stat().st_size))
        for m in _IMPORT_RE.finditer(text):
            candidate = _resolve_import_token(m.group(1), (resolved.parent, target))
            if candidate is None:
                unresolved_imports += 1
            else:
                queue.append((candidate, depth + 1))
    return MemoryDiscovery(entries=entries, unresolved_imports=unresolved_imports, truncated=truncated)


def discover_hub(target: Path) -> list[FileEntry]:
    """This target's `index.md`, when it has one — the extension hub every
    consuming workspace's memory chain eagerly `@`-imports once installed."""
    hub = target / "index.md"
    if not hub.is_file():
        return []
    return [FileEntry(path=str(hub.resolve()), bytes=hub.stat().st_size)]


# ─────────────────────────────── transcripts ─────────────────────────────────


@dataclass
class TranscriptCounts:
    source_dir: str
    available: bool
    sessions_scanned: int = 0
    sessions_unreadable: int = 0  # individual *.jsonl files that could not be opened/read
    directories_unreadable: int = 0  # project directories os.walk could not even list
    oldest_session_at: str | None = None
    newest_session_at: str | None = None
    skill_tool_calls: dict[str, int] = field(default_factory=dict)
    skill_typed_commands: dict[str, int] = field(default_factory=dict)
    subagent_invocations: dict[str, int] = field(default_factory=dict)

    @property
    def evidence_note(self) -> str | None:
        """`None` when the scan is full evidence; otherwise names why a
        never-invoked entry drawn from these counts is not a confirmed zero."""
        if not self.available:
            return "no evidence"
        if self.sessions_scanned == 0:
            return "no evidence"
        if self.sessions_unreadable or self.directories_unreadable:
            return (
                f"partial evidence: {self.sessions_unreadable} session file(s) and "
                f"{self.directories_unreadable} director{'y' if self.directories_unreadable == 1 else 'ies'} unreadable"
            )
        return None


def scan_transcripts(transcripts_dir: Path) -> TranscriptCounts:
    counts = TranscriptCounts(source_dir=str(transcripts_dir), available=transcripts_dir.exists())
    if not counts.available:
        return counts

    def _on_error(_exc: OSError) -> None:
        counts.directories_unreadable += 1

    oldest_mtime: float | None = None
    newest_mtime: float | None = None
    for dirpath, _dirnames, filenames in os.walk(transcripts_dir, onerror=_on_error):
        for name in filenames:
            if not name.endswith(".jsonl"):
                continue
            fpath = Path(dirpath) / name
            counts.sessions_scanned += 1
            try:
                mtime = fpath.stat().st_mtime
                oldest_mtime = mtime if oldest_mtime is None else min(oldest_mtime, mtime)
                newest_mtime = mtime if newest_mtime is None else max(newest_mtime, mtime)
                with fpath.open("r", encoding="utf-8", errors="ignore") as fh:
                    for line in fh:
                        for m in _SKILL_TOOL_RE.finditer(line):
                            val = m.group(1)
                            if val:
                                counts.skill_tool_calls[val] = counts.skill_tool_calls.get(val, 0) + 1
                        for m in _COMMAND_NAME_RE.finditer(line):
                            val = m.group(1)
                            if val:
                                counts.skill_typed_commands[val] = counts.skill_typed_commands.get(val, 0) + 1
                        for m in _SUBAGENT_RE.finditer(line):
                            val = m.group(1)
                            if val:
                                counts.subagent_invocations[val] = counts.subagent_invocations.get(val, 0) + 1
            except OSError:
                counts.sessions_unreadable += 1
    if oldest_mtime is not None:
        counts.oldest_session_at = datetime.fromtimestamp(oldest_mtime, tz=timezone.utc).isoformat(timespec="seconds")
    if newest_mtime is not None:
        counts.newest_session_at = datetime.fromtimestamp(newest_mtime, tz=timezone.utc).isoformat(timespec="seconds")
    return counts


def _skill_candidates(name: str, prefix: str | None) -> set[str]:
    candidates = {name}
    if prefix:
        candidates.add(f"{prefix}-{name}")
    return candidates


# ─────────────────────────────── report ──────────────────────────────────────


def build_report(target: Path, transcripts_dir: Path, too_new_days: int) -> dict:
    target = target.resolve()
    prefix = _module_prefix(target)
    counts = scan_transcripts(transcripts_dir)
    evidence_note = counts.evidence_note

    skills, skills_form = discover_skills(target)
    agents, agents_form = discover_agents(target)
    memory = discover_memory_files(target)
    hub_files = discover_hub(target)

    skill_rows = []
    never_invoked_skills = []
    for s in skills:
        candidates = _skill_candidates(s.installed_name, prefix) | _skill_candidates(s.name, prefix)
        tool_calls = sum(counts.skill_tool_calls.get(c, 0) for c in candidates)
        typed_commands = sum(counts.skill_typed_commands.get(c, 0) for c in candidates)
        total = tool_calls + typed_commands
        row = {
            "name": s.name,
            "installed_name": s.installed_name,
            "path": s.path,
            "description_bytes": s.description_bytes,
            "description_tokens_est": s.description_tokens_est,
            "file_bytes": s.file_bytes,
            "added": s.added,
            "added_commit": s.added_commit,
            "age_days": s.age_days,
            "renamed": s.renamed,
            "invocations": {"scope": "machine-global", "tool_calls": tool_calls, "typed_commands": typed_commands, "total": total},
        }
        skill_rows.append(row)
        if total == 0:
            too_new = s.age_days is not None and s.age_days < too_new_days
            never_invoked_skills.append(
                {
                    # `installed_name` is the key a `skillOverrides` entry must use — it is
                    # what the transcripts above are actually matched against via `prefix`.
                    "name": s.name,
                    "installed_name": s.installed_name,
                    "added": s.added,
                    "age_days": s.age_days,
                    "renamed": s.renamed,
                    "too_new_to_judge": too_new if s.age_days is not None else None,
                    "note": evidence_note,
                }
            )

    agent_rows = []
    never_invoked_agents = []
    for a in agents:
        invocations = counts.subagent_invocations.get(a.name, 0)
        agent_rows.append(
            {
                "name": a.name,
                "path": a.path,
                "file_bytes": a.file_bytes,
                "added": a.added,
                "added_commit": a.added_commit,
                "age_days": a.age_days,
                "renamed": a.renamed,
                "invocations": {"scope": "machine-global", "total": invocations},
            }
        )
        if invocations == 0:
            too_new = a.age_days is not None and a.age_days < too_new_days
            never_invoked_agents.append(
                {
                    "name": a.name,
                    "added": a.added,
                    "age_days": a.age_days,
                    "renamed": a.renamed,
                    "too_new_to_judge": too_new if a.age_days is not None else None,
                    "note": evidence_note,
                }
            )

    skill_description_bytes = sum(s.description_bytes for s in skills)
    agent_definition_bytes = sum(a.file_bytes for a in agents)
    memory_file_bytes = sum(f.bytes for f in memory.entries)
    hub_bytes = sum(f.bytes for f in hub_files)
    # Only the classes actually paid on every session opened at `target` — a
    # skill description, a memory file, and the extension hub. An agent
    # definition is paid only when that agent is spawned, so it is reported
    # separately below and never folded into this figure.
    always_loaded_bytes = skill_description_bytes + memory_file_bytes + hub_bytes

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "target": str(target),
        "prefix": prefix,
        "too_new_days": too_new_days,
        "default_override_value": DEFAULT_OVERRIDE_VALUE,
        "transcripts": {
            "scope": "machine-global",
            "source_dir": counts.source_dir,
            "available": counts.available,
            "sessions_scanned": counts.sessions_scanned,
            "sessions_unreadable": counts.sessions_unreadable,
            "directories_unreadable": counts.directories_unreadable,
            "oldest_session_at": counts.oldest_session_at,
            "newest_session_at": counts.newest_session_at,
            "evidence_note": evidence_note,
        },
        "inventory": {
            "scope": "target-scoped",
            "skills_form": skills_form,
            "agents_form": agents_form,
            "skills": skill_rows,
            "agents": agent_rows,
            "memory_files": [{"path": f.path, "bytes": f.bytes} for f in memory.entries],
            "hub_files": [{"path": f.path, "bytes": f.bytes} for f in hub_files],
            "memory_import_unresolved": memory.unresolved_imports,
            "memory_files_truncated": memory.truncated,
            "totals": {
                "skill_description_bytes": skill_description_bytes,
                "memory_file_bytes": memory_file_bytes,
                "hub_bytes": hub_bytes,
                "always_loaded_bytes": always_loaded_bytes,
                "always_loaded_tokens_est": round(always_loaded_bytes / TOKEN_CHARS_PER_TOKEN),
                "agent_definition_bytes": agent_definition_bytes,
                "agent_definition_tokens_est": round(agent_definition_bytes / TOKEN_CHARS_PER_TOKEN),
            },
        },
        "classification": {
            "never_invoked_skills": never_invoked_skills,
            "never_invoked_agents": never_invoked_agents,
        },
    }


# ─────────────────────────────── apply ───────────────────────────────────────


def apply_overrides(settings_path: Path, overrides: dict[str, str], dry_run: bool) -> dict:
    """Merge `overrides` into `settings_path`'s `skillOverrides` key, touching no
    other key and creating the file (with only that key) if it does not exist
    yet. Returns the resulting settings document; writes it unless `dry_run`."""
    invalid_keys = {k for k in overrides if not _SKILL_KEY_RE.match(k)}
    if invalid_keys:
        raise ValueError(f"invalid skillOverrides key(s): {sorted(invalid_keys)!r} (must be a bare skill name)")
    invalid_values = {k: v for k, v in overrides.items() if v not in VALID_OVERRIDE_VALUES}
    if invalid_values:
        raise ValueError(f"invalid skillOverrides value(s): {invalid_values!r} (must be one of {VALID_OVERRIDE_VALUES})")

    if settings_path.is_file():
        try:
            settings = json.loads(settings_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"{settings_path} is not valid JSON: {exc}") from exc
    else:
        settings = {}
    if not isinstance(settings, dict):
        raise ValueError(f"{settings_path} does not contain a JSON object")

    existing = settings.get("skillOverrides")
    merged = dict(existing) if isinstance(existing, dict) else {}
    merged.update(overrides)
    settings["skillOverrides"] = merged

    if not dry_run:
        settings_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = settings_path.with_name(f"{settings_path.name}.tmp-{os.getpid()}")
        tmp_path.write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")
        os.replace(tmp_path, settings_path)
    return settings


# ─────────────────────────────── CLI ─────────────────────────────────────────


def _cmd_measure(args: argparse.Namespace) -> int:
    target = Path(args.target)
    if not target.is_dir():
        print(f"error: --target {target} is not a directory", file=sys.stderr)
        return 2
    report = build_report(target.resolve(), Path(args.transcripts_dir).expanduser(), args.too_new_days)
    print(json.dumps(report, indent=2))
    return 0


def _cmd_apply(args: argparse.Namespace) -> int:
    if args.overrides == "-":
        raw = sys.stdin.read()
    else:
        try:
            raw = Path(args.overrides).read_text(encoding="utf-8")
        except OSError as exc:
            print(f"error: could not read --overrides {args.overrides}: {exc}", file=sys.stderr)
            return 2
    try:
        overrides = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"error: overrides input is not valid JSON: {exc}", file=sys.stderr)
        return 2
    if not isinstance(overrides, dict) or not overrides:
        print("error: overrides input must be a non-empty JSON object of {skillName: overrideValue}", file=sys.stderr)
        return 2
    try:
        apply_overrides(Path(args.settings), overrides, args.dry_run)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    # Print only the delta just applied — never the full settings document,
    # which may hold unrelated keys (API keys, env vars) that must not be
    # echoed to stdout (and so into the session transcript).
    print(json.dumps({"settings_path": str(args.settings), "dry_run": args.dry_run, "applied": overrides}, indent=2))
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Measurement half of the optimize-context skill.")
    sub = parser.add_subparsers(dest="command", required=True)

    measure = sub.add_parser("measure", help="Emit the invocation-count + inventory + classification report as JSON.")
    measure.add_argument("--target", required=True, help="Codebase or workspace root to audit (target-scoped inventory).")
    measure.add_argument(
        "--transcripts-dir",
        default=str(DEFAULT_TRANSCRIPTS_DIR),
        help="Directory of *.jsonl session transcripts to mine (default: ~/.claude/projects).",
    )
    measure.add_argument(
        "--too-new-days",
        type=int,
        default=DEFAULT_TOO_NEW_DAYS,
        help=f"A never-invoked entry younger than this is 'too new to judge' rather than dead (default: {DEFAULT_TOO_NEW_DAYS}).",
    )
    measure.set_defaults(func=_cmd_measure)

    apply_p = sub.add_parser("apply", help="Merge operator-approved skillOverrides entries into a settings.json.")
    apply_p.add_argument("--settings", required=True, help="Path to the settings.json to merge into.")
    apply_p.add_argument("--overrides", required=True, help="Path to a JSON {skillName: overrideValue} file, or '-' for stdin.")
    apply_p.add_argument("--dry-run", action="store_true", help="Compute and print the merged result without writing it.")
    apply_p.set_defaults(func=_cmd_apply)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
