#!/usr/bin/env python3
"""Methodology-to-adapter dependency-boundary lint for winter-workflow.

Authored Markdown under this module's top-level ``methodology/`` directory may
name runtime ports such as ``cold-reviewer``, but it must not depend on skill
invocation syntax or refer back to the concrete adapters in ``skills/`` and
``agents/``. The adapters may depend on methodology; the reverse dependency
would make the methodology runtime-specific.

This is a ``winter lint`` check. It confines itself to ``WINTER_LINT_PATHS``,
emits one NDJSON finding per offending line, and always exits zero because a
violation is a lint finding rather than a script failure. For standalone use
and tests, scope paths may be passed as arguments.
"""

from __future__ import annotations

import json
import os
import re
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

CHECK = "methodology-boundary"
MANIFEST = "winter-ext.toml"
PRUNE_DIRS = frozenset(
    {".git", ".venv", "node_modules", "__pycache__", ".mypy_cache", ".ruff_cache", "fixtures"}
)

_INLINE_LINK_RE = re.compile(r"!?\[[^]\n]*\]\(\s*(?:<(?P<angle>[^>\n]+)>|(?P<plain>[^\s)\n]+))")
_REFERENCE_LINK_RE = re.compile(
    r"^\s{0,3}\[[^]\n]+\]:\s*(?:<(?P<angle>[^>\n]+)>|(?P<plain>\S+))"
)
_IMPORT_RE = re.compile(r"(?<![A-Za-z0-9_])@([^\s`]+)")
_INLINE_CODE_RE = re.compile(
    r"(?<!`)(?P<ticks>`+)(?!`)(?P<code>.+?)(?<!`)(?P=ticks)(?!`)"
)
_FENCE_RE = re.compile(r"^ {0,3}(?P<marker>`{3,}|~{3,})(?P<rest>.*)$")
_EXAMPLE_MARKER_RE = re.compile(r"<!--\s*winter-lint:\s*example\s*-->", re.IGNORECASE)


def _exempt_lines(lines: list[str]) -> set[int]:
    """1-based line numbers covered by an `<!-- winter-lint:example -->` marker.

    The marker exempts the whole **block** it sits in, not just its own physical
    line. `dprint` owns where lines break in this repo's markdown, so a marker
    parked at the end of a wrapped paragraph has to cover the illustration
    reflow pushed further up. A block is a run of non-blank lines — which is why
    a table's marker belongs inside a cell, the formatter putting a blank line
    between a table and any comment adjacent to it.
    """
    exempt: set[int] = set()
    start = 0
    marked = False
    for index, line in enumerate(lines):
        if line.strip():
            marked = marked or bool(_EXAMPLE_MARKER_RE.search(line))
            continue
        if marked:
            exempt.update(range(start + 1, index + 1))
        start = index + 1
        marked = False
    if marked:
        exempt.update(range(start + 1, len(lines) + 1))
    return exempt
_TARGET_TRIM = ".,;:!?)]}>\"'"


@dataclass(frozen=True)
class Finding:
    status: str
    message: str
    file: str
    line: int
    remediation: str

    def to_json(self) -> str:
        return json.dumps(
            {
                "check": CHECK,
                "status": self.status,
                "message": self.message,
                "file": self.file,
                "line": self.line,
                "remediation": self.remediation,
            }
        )


def _module_name(root: Path) -> str:
    try:
        with (root / MANIFEST).open("rb") as fh:
            data = tomllib.load(fh)
    except (OSError, tomllib.TOMLDecodeError):
        data = {}
    name = data.get("name")
    return name if isinstance(name, str) and name else root.name


def _module_root(path: Path) -> Path | None:
    current = path if path.is_dir() else path.parent
    while True:
        if (current / MANIFEST).is_file():
            return current
        if current.parent == current:
            return None
        current = current.parent


def _own_module_name() -> str:
    ext_dir = os.environ.get("WINTER_EXT_DIR")
    if ext_dir:
        return _module_name(Path(ext_dir))
    root = _module_root(Path(__file__).resolve())
    return _module_name(root) if root is not None else "winter-workflow"


def _methodology_owner(file: Path, own_module: str) -> Path | None:
    root = _module_root(file)
    if root is None or _module_name(root) != own_module:
        return None
    try:
        relative = file.resolve().relative_to(root.resolve())
    except ValueError:
        return None
    if file.suffix != ".md" or not relative.parts or relative.parts[0] != "methodology":
        return None
    return root


def _collect_methodology_files(paths: list[Path], own_module: str) -> list[tuple[Path, Path]]:
    found: dict[Path, tuple[Path, Path]] = {}

    def add(path: Path) -> None:
        resolved = path.resolve()
        if resolved in found:
            return
        owner = _methodology_owner(path, own_module)
        if owner is not None:
            found[resolved] = (path, owner)

    for path in paths:
        if path.is_file():
            if not any(part in PRUNE_DIRS for part in path.parts):
                add(path)
            continue
        for dirpath, dirnames, filenames in os.walk(path):
            dirnames[:] = sorted(d for d in dirnames if d not in PRUNE_DIRS)
            for name in sorted(filenames):
                if name.endswith(".md"):
                    add(Path(dirpath) / name)

    return [found[key] for key in sorted(found, key=str)]


def _link_targets(line: str) -> list[str]:
    targets: list[str] = []
    for match in _INLINE_LINK_RE.finditer(line):
        targets.append(match.group("angle") or match.group("plain"))
    match = _REFERENCE_LINK_RE.match(line)
    if match:
        targets.append(match.group("angle") or match.group("plain"))
    return targets


def _import_targets(line: str) -> list[str]:
    return [match.group(1).rstrip(_TARGET_TRIM) for match in _IMPORT_RE.finditer(line)]


def _inline_code_targets(line: str) -> list[str]:
    return [match.group("code").strip() for match in _INLINE_CODE_RE.finditer(line)]


def _target_adapter(target: str, file: Path, module_root: Path) -> str | None:
    target = re.split(r"[?#]", target, maxsplit=1)[0]
    if not target:
        return None

    prefix, separator, prefixed_path = target.partition(":")
    if separator:
        if prefix not in {"local", _module_name(module_root)} or not prefixed_path.startswith("/"):
            return None
        destination = module_root / prefixed_path.lstrip("/")
    elif target.startswith("/"):
        destination = module_root / target.lstrip("/")
    else:
        destination = file.parent / target
    try:
        relative = destination.resolve().relative_to(module_root.resolve())
    except ValueError:
        return None
    if relative.parts and relative.parts[0] in {"skills", "agents"}:
        return relative.parts[0]
    return None


def _adapter_label(directory: str) -> str:
    return "skill" if directory == "skills" else "agent"


def _file_findings(file: Path, module_root: Path, rel: str) -> list[Finding]:
    try:
        lines = file.read_text(errors="replace").splitlines()
    except OSError as exc:
        return [
            Finding(
                status="fail",
                message=f"could not read methodology file: {exc}",
                file=rel,
                line=1,
                remediation="Make the methodology file readable.",
            )
        ]

    findings: list[Finding] = []
    exempt = _exempt_lines(lines)
    fence: tuple[str, int] | None = None
    for line_number, line in enumerate(lines, 1):
        fence_match = _FENCE_RE.match(line)
        if fence is not None:
            if (
                fence_match is not None
                and fence_match.group("marker")[0] == fence[0]
                and len(fence_match.group("marker")) >= fence[1]
                and not fence_match.group("rest").strip()
            ):
                fence = None
            continue
        if fence_match is not None:
            marker = fence_match.group("marker")
            fence = (marker[0], len(marker))
            continue
        if line_number in exempt:
            continue

        violations: list[tuple[str, str]] = []
        if "$ARGUMENTS" in line:
            violations.append(
                (
                    "`$ARGUMENTS` is skill-adapter invocation syntax, not methodology",
                    "Pass semantic inputs from the skill adapter into the methodology process.",
                )
            )

        targets = _link_targets(line) + _import_targets(line) + _inline_code_targets(line)
        adapters = {
            adapter
            for target in targets
            if (adapter := _target_adapter(target, file, module_root)) is not None
        }
        for adapter in sorted(adapters):
            label = _adapter_label(adapter)
            violations.append(
                (
                    f"methodology must not depend on top-level {label} adapters in `{adapter}/`",
                    f"Refer to methodology or name the runtime {label} port without linking to its adapter.",
                )
            )
        if violations:
            findings.append(
                Finding(
                    status="fail",
                    message="; ".join(message for message, _ in violations),
                    file=rel,
                    line=line_number,
                    remediation=" ".join(remediation for _, remediation in violations),
                )
            )
    return findings


def _scope_paths() -> list[Path]:
    raw = os.environ.get("WINTER_LINT_PATHS")
    if raw is not None:
        return [Path(line) for line in raw.splitlines() if line.strip()]
    paths = [Path(arg) for arg in sys.argv[1:]]
    return paths or [Path.cwd()]


def _relpath(file: Path, workspace_root: Path) -> str:
    try:
        return str(file.resolve().relative_to(workspace_root.resolve()))
    except ValueError:
        return str(file)


def main() -> int:
    workspace_root = Path(os.environ.get("WINTER_WORKSPACE_DIR") or Path.cwd())
    own_module = _own_module_name()
    findings: list[Finding] = []
    for file, module_root in _collect_methodology_files(_scope_paths(), own_module):
        findings.extend(_file_findings(file, module_root, _relpath(file, workspace_root)))
    for finding in findings:
        print(finding.to_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
