#!/usr/bin/env python3
"""Agent-frontmatter completeness lint for winter-workflow.

Every agent definition this module ships must declare three frontmatter keys so
that spawn-time behavior is deterministic:

  description  non-empty string  — without it the agent is invisible to the
                                   routing logic of skills that pick a subagent.
  tools        non-empty list,   — without it spawn-time tool access opens
               or the literal "*"  wider than intended.
  model        haiku|sonnet|opus — without it the agent inherits the spawner's
                                   model (a cost-discipline regression).

This is a `winter lint` check (see `winter-cli` setup.md "Lint checks"). It runs
with the lint env contract and emits NDJSON findings on stdout — it is wired in
via the `lint` field of this module's `winter-ext.toml` and is meant to run
*only* through `winter lint` (no standalone task runner). It always exits 0; a
violation is a finding, not a process failure.

KEY NAME — `tools`, not `allowed-tools`: the Claude Code *agent* frontmatter key
is `tools` (`allowed-tools` is the skills/commands key). Every agents/*.md here
uses `tools`, so that is what we validate. We also guard the inverse footgun:
Claude Code *silently ignores* an `allowed-tools` key on an agent, so an author
who writes it — as issue #1's own table suggested — believes they restricted
tool access while the agent actually gets the wide default grant. The check
flags `allowed-tools`: a `fail` when it stands in for a missing `tools`, a
`warn` when it is dead noise beside a valid `tools`.

SCOPE — winter-workflow's own agents only. The check walks WINTER_LINT_PATHS,
keeps each `*.md` that lives directly under an `agents/` directory (excluding
`README.md` and the `agents/docs/` prose), and then keeps only those whose
owning module (nearest `winter-ext.toml`) is this module. Agents owned by other
modules are silently skipped — enforcing the same rule elsewhere is out of scope.

Env contract (from `winter lint`):
  WINTER_EXT_DIR        this module's installed directory (defines ownership)
  WINTER_WORKSPACE_DIR  absolute workspace root (for relative finding paths)
  WINTER_LINT_PATHS     newline-delimited absolute paths in scope (files or dirs)
  WINTER_LINT_SCOPE     scope kind (all/repo/env/changed) — informational

Standalone (for the test harness): pass scope paths as argv; ownership falls
back to the module containing this script.
"""

from __future__ import annotations

import json
import os
import re
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

CHECK = "agent-frontmatter"
MANIFEST = "winter-ext.toml"
VALID_MODELS = ("haiku", "sonnet", "opus")

# Top-level canonical common keys — anything else at the top level must be a
# recognised vendor override block (claude / codex / opencode).
_COMMON_KEYS: frozenset[str] = frozenset({"name", "description", "model", "tools", "allowed-tools"})
_VALID_OVERRIDE_BLOCKS: frozenset[str] = frozenset({"claude", "codex", "opencode"})

# Directories never worth walking. `fixtures` is pruned so an `--all` / repo
# scope never descends into this lint's own deliberately-broken test fixtures;
# the test harness reaches them by pointing the scope *inside* a fixture case.
PRUNE_DIRS = frozenset(
    {".git", ".venv", "node_modules", "__pycache__", ".mypy_cache", ".ruff_cache", "fixtures"}
)

_KEY_RE = re.compile(r"^([A-Za-z0-9_-]+)[ \t]*:(.*)$")


@dataclass(frozen=True)
class Finding:
    status: str
    message: str
    file: str | None = None
    line: int | None = None
    remediation: str | None = None

    def to_json(self) -> str:
        payload: dict[str, object] = {"check": CHECK, "status": self.status, "message": self.message}
        if self.file is not None:
            payload["file"] = self.file
        if self.line is not None:
            payload["line"] = self.line
        if self.remediation is not None:
            payload["remediation"] = self.remediation
        return json.dumps(payload)


# ── module ownership ─────────────────────────────────────────────────────────


def _module_name(manifest_path: Path) -> str:
    """A module's identity — the `name` from its (TOML) winter-ext.toml, falling
    back to the manifest's directory name."""
    try:
        with manifest_path.open("rb") as fh:
            data = tomllib.load(fh)
    except (OSError, tomllib.TOMLDecodeError):
        data = {}
    name = data.get("name")
    return name if isinstance(name, str) and name else manifest_path.parent.name


def _owning_module(path: Path) -> str | None:
    """Name of the nearest ancestor module (dir with a winter-ext.toml), or None."""
    cur = path if path.is_dir() else path.parent
    while True:
        manifest = cur / MANIFEST
        if manifest.is_file():
            return _module_name(manifest)
        if cur.parent == cur:
            return None
        cur = cur.parent


def _own_module_name(script_path: Path) -> str:
    """This check's owning module: WINTER_EXT_DIR when dispatched, else the
    module containing this script (the standalone / test path)."""
    ext_dir = os.environ.get("WINTER_EXT_DIR")
    if ext_dir:
        return _module_name(Path(ext_dir) / MANIFEST)
    return _owning_module(script_path) or "winter-workflow"


# ── frontmatter parsing ────────────────────────────────────────────────────


def _strip_quotes(s: str) -> str:
    s = s.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in ("'", '"'):
        return s[1:-1]
    return s


def _comment_index(s: str) -> int | None:
    """Index of the first `#` that starts a YAML comment — at the start of the
    string or preceded by whitespace — else None."""
    for i, ch in enumerate(s):
        if ch == "#" and (i == 0 or s[i - 1] in " \t"):
            return i
    return None


def _strip_inline_comment(value: str) -> str:
    """Drop an unquoted trailing YAML comment from an inline scalar.

    YAML treats ` #...` (whitespace + hash) as a comment, so `model: opus # x`
    and `tools: * # all` carry a value of `opus` / `*`, not the literal text.
    A `#` inside a leading quoted span is kept verbatim (`"foo # bar"`).

    Lossy by design: a value that legitimately contains ` #` is shortened. That
    is safe only because callers test a value's *presence*, never read it back
    as content — keep that true if you add a caller."""
    s = value.strip()
    if s[:1] in ("'", '"'):
        end = s.find(s[0], 1)
        if end != -1:
            tail = s[end + 1 :]
            cut = _comment_index(tail)
            return (s[: end + 1] + (tail[:cut] if cut is not None else tail)).strip()
        return s  # unterminated quote — leave as-is
    cut = _comment_index(s)
    return (s[:cut] if cut is not None else s).strip()


def _frontmatter_lines(text: str) -> list[str] | None:
    """The YAML lines between the leading pair of `---` fences, or None if the
    file does not open with a frontmatter fence."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    body: list[str] = []
    for line in lines[1:]:
        if line.strip() == "---":
            return body
        body.append(line)
    return None  # no closing fence


def _top_level_blocks(lines: list[str]) -> dict[str, dict]:
    """Map each top-level key to its inline value and indented body lines."""
    blocks: dict[str, dict] = {}
    cur: str | None = None
    for line in lines:
        if line and not line[0].isspace():
            m = _KEY_RE.match(line)
            if m:
                cur = m.group(1)
                blocks[cur] = {"inline": _strip_inline_comment(m.group(2)), "body": []}
            else:
                cur = None
            continue
        if cur is not None:
            blocks[cur]["body"].append(line)
    return blocks


def _check_description(block: dict | None) -> str | None:
    msg = "description: missing or empty (must be a non-empty string)"
    if block is None:
        return msg
    inline = block["inline"]
    if inline[:1] in ("|", ">"):  # block scalar — value is the indented body
        return None if any(l.strip() for l in block["body"]) else msg
    if _strip_quotes(inline).strip():
        return None
    # No inline value: accept a plain multi-line continuation in the body.
    return None if any(l.strip() for l in block["body"]) else msg


def _check_model(block: dict | None) -> str | None:
    allowed = ", ".join(VALID_MODELS)
    if block is None or not _strip_quotes(block["inline"]).strip():
        return f"model: missing (must be one of: {allowed})"
    val = _strip_quotes(block["inline"]).strip()
    if val not in VALID_MODELS:
        return f"model: '{val}' invalid (must be one of: {allowed})"
    return None


def _check_tools(block: dict | None) -> str | None:
    rule = 'must be a non-empty list, or the literal "*"'
    if block is None:
        return f"tools: missing ({rule})"
    inline = block["inline"]
    empty_list = 'tools: empty list (must list at least one tool, or be "*")'
    if inline == "":
        # Expect a block sequence in the body: `- item` lines with content.
        dashes = [
            _strip_inline_comment(l.lstrip()[1:])
            for l in block["body"]
            if l.lstrip() == "-" or l.lstrip().startswith("- ")
        ]
        if any(dashes):
            return None
        if dashes:  # only empty bullets (`-` / `- `) — present but no items
            return empty_list
        return f"tools: missing ({rule})"
    if _strip_quotes(inline) == "*":
        return None
    if inline.startswith("["):  # flow sequence
        if not inline.endswith("]"):
            return f"tools: {rule}"  # unterminated `[` — malformed
        items = [x for x in (_strip_quotes(p).strip() for p in inline[1:-1].split(",")) if x]
        if not items:
            return empty_list
        return None
    return f"tools: {rule}"  # a bare scalar like `tools: Read`


def _override_block_findings(blocks: dict[str, dict], rel: str) -> list[Finding]:
    """Validate canonical-schema rules for per-vendor override blocks.

    Two checks:
    1. Any top-level key that is not a common field must be one of the three
       recognised vendor labels (claude / codex / opencode).  An unknown block
       name is a ``fail``.
    2. Every recognised vendor block must be a YAML mapping (not a scalar on
       the same line, not a sequence/list).  A non-mapping block is a ``fail``.
    """
    findings: list[Finding] = []
    for key, block in blocks.items():
        if key in _COMMON_KEYS:
            continue
        if key not in _VALID_OVERRIDE_BLOCKS:
            findings.append(
                Finding(
                    status="fail",
                    message=(
                        f"unknown override block {key!r}: top-level vendor blocks must be "
                        "one of: claude, codex, opencode"
                    ),
                    file=rel,
                    remediation=(
                        f"Remove or rename the '{key}:' block to one of: claude, codex, opencode"
                    ),
                )
            )
            continue
        # Recognised vendor block — must be a mapping (not a scalar or sequence).
        inline = block["inline"].strip()
        body_lines = block["body"]
        if inline:
            findings.append(
                Finding(
                    status="fail",
                    message=(
                        f"{key}: override block must be a YAML mapping, "
                        f"got a scalar value {inline!r}"
                    ),
                    file=rel,
                    remediation=(
                        f"Change `{key}: {inline}` to `{key}:` with an indented mapping body."
                    ),
                )
            )
        elif any(line.lstrip().startswith("- ") for line in body_lines):
            findings.append(
                Finding(
                    status="fail",
                    message=(
                        f"{key}: override block must be a YAML mapping, "
                        "got a sequence (list) value"
                    ),
                    file=rel,
                    remediation=(
                        f"Change `{key}:` body from list items to key-value pairs."
                    ),
                )
            )
    return findings


def _frontmatter_findings(file: Path, rel: str) -> list[Finding]:
    try:
        text = file.read_text(errors="replace")
    except OSError as exc:
        return [Finding(status="fail", message=f"could not read agent file: {exc}", file=rel)]

    lines = _frontmatter_lines(text)
    if lines is None:
        return [
            Finding(
                status="fail",
                message="missing or empty YAML frontmatter",
                file=rel,
                remediation="Open the file with a `---` fenced YAML block declaring description, tools, model.",
            )
        ]

    blocks = _top_level_blocks(lines)
    findings: list[Finding] = []

    desc = _check_description(blocks.get("description"))
    if desc is not None:
        findings.append(Finding(status="fail", message=desc, file=rel))

    findings.extend(_tools_findings(blocks, rel))

    model = _check_model(blocks.get("model"))
    if model is not None:
        findings.append(Finding(status="fail", message=model, file=rel))

    findings.extend(_override_block_findings(blocks, rel))

    return findings


def _tools_findings(blocks: dict[str, dict], rel: str) -> list[Finding]:
    """Validate the `tools` grant and guard the `allowed-tools` footgun.

    See the module docstring's "KEY NAME" note for the fail-vs-warn rationale.
    """
    tools_block = blocks.get("tools")
    has_allowed = "allowed-tools" in blocks

    if has_allowed and tools_block is None:
        return [
            Finding(
                status="fail",
                message="allowed-tools: agents declare their tool grant under `tools`; Claude Code "
                "ignores `allowed-tools` (the skills/commands key), so the grant is unintended",
                file=rel,
                remediation="Rename the `allowed-tools` key to `tools`.",
            )
        ]

    out: list[Finding] = []
    problem = _check_tools(tools_block)
    if problem is not None:
        out.append(Finding(status="fail", message=problem, file=rel))
    if has_allowed:
        out.append(
            Finding(
                status="warn",
                message="allowed-tools: ignored on agents (the skills/commands key); the tool grant is `tools`",
                file=rel,
                remediation="Remove the dead `allowed-tools` key.",
            )
        )
    return out


# ── scope collection ─────────────────────────────────────────────────────────


def _is_agent_file(path: Path) -> bool:
    return path.suffix == ".md" and path.parent.name == "agents" and path.name != "README.md"


def _collect_agent_files(paths: list[Path]) -> list[Path]:
    out: list[Path] = []
    seen: set[Path] = set()

    def add(p: Path) -> None:
        rp = p.resolve()
        if _is_agent_file(p) and rp not in seen:
            seen.add(rp)
            out.append(p)

    for p in paths:
        if p.is_file():
            # A file named directly in scope (e.g. `winter lint --changed` over a
            # changed file) bypasses the walk-time PRUNE_DIRS, so apply the prune
            # to its own path components here. This keeps the lint's own broken
            # fixtures out of a real run, while the test harness still reaches
            # them by scoping the fixture *directory* (walked, not named).
            if not any(part in PRUNE_DIRS for part in p.parts):
                add(p)
            continue
        for dirpath, dirnames, filenames in os.walk(p):
            dirnames[:] = [d for d in dirnames if d not in PRUNE_DIRS]
            for name in filenames:
                if name.endswith(".md"):
                    add(Path(dirpath) / name)
    return out


def _scope_paths() -> list[Path]:
    raw = os.environ.get("WINTER_LINT_PATHS")
    if raw is not None:
        return [Path(line) for line in raw.splitlines() if line.strip()]
    argv = [Path(a) for a in sys.argv[1:]]
    return argv or [Path.cwd()]


def _relpath(file: Path, workspace_root: Path) -> str:
    try:
        return str(file.resolve().relative_to(workspace_root.resolve()))
    except ValueError:
        return str(file)


def main() -> int:
    workspace_root = Path(os.environ.get("WINTER_WORKSPACE_DIR") or Path.cwd())
    own = _own_module_name(Path(__file__).resolve())

    findings: list[Finding] = []
    for file in _collect_agent_files(_scope_paths()):
        if _owning_module(file) != own:
            continue  # not our module's agent — out of scope
        findings.extend(_frontmatter_findings(file, _relpath(file, workspace_root)))

    for finding in findings:
        print(finding.to_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
