#!/usr/bin/env python3
"""Exercise scripts/lint-agents.py against deliberately broken fixtures.

Each case is an isolated `tests/fixtures/<case>/agents/` tree holding one agent
.md. We drive the lint the way `winter lint` does — via `WINTER_LINT_PATHS` —
and assert on the parsed NDJSON findings: the lint must flag each missing /
invalid key, stay silent for well-formed agents (and for the `README.md` /
`agents/docs/` files that share the valid fixture's directory), and pass clean
over the real `agents/` tree.

Run directly: `python3 tests/test_lint_agents.py` (stdlib only, no deps).
This is a developer check; the lint itself ships only through `winter lint`.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LINT = REPO_ROOT / "scripts" / "lint-agents.py"
FIXTURES = REPO_ROOT / "tests" / "fixtures"

failures = 0


def run_lint(scope: Path) -> list[dict]:
    """Run the lint over one scope path, returning parsed NDJSON findings."""
    env = os.environ.copy()
    env["WINTER_LINT_PATHS"] = str(scope)
    env["WINTER_WORKSPACE_DIR"] = str(REPO_ROOT)
    env.pop("WINTER_EXT_DIR", None)  # ownership falls back to the script's module
    result = subprocess.run(
        [sys.executable, str(LINT)],
        cwd=str(REPO_ROOT),
        env=env,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(f"lint exited {result.returncode} (must be 0): {result.stderr}")
    findings = [json.loads(line) for line in result.stdout.splitlines() if line.strip()]
    for f in findings:
        assert f.get("check") == "agent-frontmatter", f"unexpected check: {f}"
    return findings


def assert_fail(case: str, expected: str) -> None:
    global failures
    findings = run_lint(FIXTURES / case)
    fails = [f for f in findings if f.get("status") == "fail"]
    if not fails:
        print(f"NOT OK  {case:<20} expected a failure finding, got none")
        failures += 1
    elif not any(expected in f.get("message", "") for f in fails):
        print(f"NOT OK  {case:<20} no finding mentioned {expected!r}; got {[f['message'] for f in fails]}")
        failures += 1
    elif not all(f.get("file") for f in fails):
        print(f"NOT OK  {case:<20} a finding lacked a file path: {fails}")
        failures += 1
    else:
        print(f'ok      {case:<20} fails on "{expected}"')


def assert_pass(case: str, scope: Path) -> None:
    global failures
    findings = run_lint(scope)
    if findings:
        print(f"NOT OK  {case:<20} expected no findings, got {[f['message'] for f in findings]}")
        failures += 1
    else:
        print(f"ok      {case:<20} passes clean")


def assert_warn(case: str, expected: str) -> None:
    """A case that should warn (not fail): a warn finding matching `expected`,
    and no fail findings."""
    global failures
    findings = run_lint(FIXTURES / case)
    warns = [f for f in findings if f.get("status") == "warn"]
    fails = [f for f in findings if f.get("status") == "fail"]
    if fails:
        print(f"NOT OK  {case:<20} expected no fails, got {[f['message'] for f in fails]}")
        failures += 1
    elif not any(expected in f.get("message", "") for f in warns):
        print(f"NOT OK  {case:<20} no warn mentioned {expected!r}; got {[f['message'] for f in warns]}")
        failures += 1
    else:
        print(f'ok      {case:<20} warns on "{expected}"')


assert_pass("valid", FIXTURES / "valid")
assert_pass("wildcard-tools", FIXTURES / "wildcard-tools")

assert_fail("missing-description", "description: missing or empty")
assert_fail("empty-description", "description: missing or empty")
assert_fail("missing-tools", "tools: missing")
assert_fail("empty-tools", "tools: empty list")
assert_fail("bad-tools-type", "tools: must be a non-empty list")
assert_fail("missing-model", "model: missing")
assert_fail("invalid-model", "model: 'gpt-4' invalid")
assert_fail("no-frontmatter", "missing or empty YAML frontmatter")

# allowed-tools footgun: a fail when it stands in for a missing `tools`, a warn
# when it is dead noise beside a valid `tools`.
assert_fail("allowed-tools-instead", "the grant is unintended")
assert_warn("allowed-tools-dead", "ignored on agents")

# Parser robustness — author-written frontmatter that YAML accepts must not
# false-fail, and malformed values must not pass silently.
assert_pass("trailing-comment-ok", FIXTURES / "trailing-comment-ok")
assert_pass("trailing-comment-wildcard", FIXTURES / "trailing-comment-wildcard")
assert_pass("model-space-before-colon", FIXTURES / "model-space-before-colon")
assert_fail("unterminated-flow", "tools: must be a non-empty list")
assert_fail("empty-block-item", "tools: empty list")
assert_fail("comment-only-bullet", "tools: empty list")

# Canonical-schema override block checks.
assert_pass("valid-override-blocks", FIXTURES / "valid-override-blocks")
assert_fail("unknown-override-block", "unknown override block")
assert_fail("override-block-scalar", "must be a YAML mapping")
assert_fail("override-block-sequence", "must be a YAML mapping")

# The real shipped agents must all pass — the lint is only useful if green
# against master. Scoping at the repo root also confirms the `fixtures/` prune
# keeps the broken fixtures above from leaking into a real run.
assert_pass("agents (real)", REPO_ROOT)

# `winter lint --changed` over a changed *fixture file* (named directly, not
# walked) must not flag it — the fixtures are this lint's own test data, not
# real agents. Proves the path-based prune in _collect_agent_files.
assert_pass(
    "changed fixture file",
    FIXTURES / "missing-tools" / "agents" / "a.md",
)

print()
if failures:
    print(f"test_lint_agents: {failures} assertion(s) failed.")
    sys.exit(1)
print("test_lint_agents: all assertions passed.")
