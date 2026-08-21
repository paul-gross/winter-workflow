#!/usr/bin/env python3
"""Focused stdlib-only tests for scripts/context-usage.py.

Builds small synthetic target repos (git-tracked, so the added-date step has
real history to read) and synthetic transcripts directories, then exercises
the `measure` and `apply` subcommands against them.

No `unittest.TestCase`: every `test_*` function below is a plain,
pytest-discoverable function built on bare `assert`, matching
`tests/test_lint_agents.py`'s stdlib-only style rather than importing a test
framework that isn't otherwise a dependency of this repo.

Run directly: `python3 tests/test_context_usage.py`.
"""

from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "context-usage.py"


def _git_env(date: str) -> dict[str, str]:
    env = os.environ.copy()
    env.update(
        {
            "GIT_AUTHOR_NAME": "Test",
            "GIT_AUTHOR_EMAIL": "test@example.com",
            "GIT_COMMITTER_NAME": "Test",
            "GIT_COMMITTER_EMAIL": "test@example.com",
            "GIT_AUTHOR_DATE": date,
            "GIT_COMMITTER_DATE": date,
        }
    )
    return env


def _commit_all(repo: Path, date: str, message: str) -> None:
    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-q", "-m", message],
        check=True,
        capture_output=True,
        text=True,
        env=_git_env(date),
    )


def _rename(repo: Path, src: str, dst: str, date: str, message: str) -> None:
    (repo / dst).parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "-C", str(repo), "mv", src, dst], check=True, capture_output=True, text=True)
    _commit_all(repo, date, message)


def _build_target_repo(target: Path) -> None:
    """A synthetic extension checkout (source form) with a mix of skills and
    agents used across the tests below."""
    subprocess.run(["git", "-C", str(target), "init", "-q"], check=True, capture_output=True, text=True)

    (target / "winter-ext.toml").write_text('name = "sample-ext"\nprefix = "wf"\n')
    _commit_all(target, "2026-01-01T00:00:00", "init manifest")

    # An old, never-invoked skill.
    old_skill = target / "skills" / "old-skill"
    old_skill.mkdir(parents=True)
    (old_skill / "SKILL.md").write_text("---\ndescription: An old skill nobody calls anymore.\n---\nbody\n")
    _commit_all(target, "2026-01-05T00:00:00", "add old-skill")

    # A skill invoked via both the tool-call and typed-command forms.
    used_skill = target / "skills" / "used-skill"
    used_skill.mkdir(parents=True)
    (used_skill / "SKILL.md").write_text("---\ndescription: A skill invoked plenty.\n---\nbody\n")
    _commit_all(target, "2026-01-06T00:00:00", "add used-skill")

    # A skill invoked only via the typed slash-command form.
    typed_only = target / "skills" / "typed-only-skill"
    typed_only.mkdir(parents=True)
    (typed_only / "SKILL.md").write_text("---\ndescription: Only ever typed by hand.\n---\nbody\n")
    _commit_all(target, "2026-01-06T00:00:00", "add typed-only-skill")

    # A recently-added, never-invoked skill — must be flagged too-new.
    brand_new = target / "skills" / "brand-new-skill"
    brand_new.mkdir(parents=True)
    (brand_new / "SKILL.md").write_text("---\ndescription: Freshly added, unused so far.\n---\nbody\n")
    recent = (datetime.now(timezone.utc) - timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%S")
    _commit_all(target, recent, "add brand-new-skill")

    # A name-prefix neighbour pair: "distill" must never be credited with
    # invocations of "distill-extra" (or vice versa) via substring matching.
    distill = target / "skills" / "distill"
    distill.mkdir(parents=True)
    (distill / "SKILL.md").write_text("---\ndescription: The short name.\n---\nbody\n")
    distill_extra = target / "skills" / "distill-extra"
    distill_extra.mkdir(parents=True)
    (distill_extra / "SKILL.md").write_text("---\ndescription: The longer, prefix-colliding name.\n---\nbody\n")
    _commit_all(target, "2026-01-06T12:00:00", "add distill + distill-extra")

    agents_dir = target / "agents"
    agents_dir.mkdir()
    (agents_dir / "README.md").write_text("# Agents\nNot an agent — must not be counted.\n")
    (agents_dir / "helper.md").write_text(
        "---\nname: helper\ndescription: N/A\nmodel: sonnet\ntools:\n  - Bash\n---\nbody\n"
    )
    (agents_dir / "idle-agent.md").write_text(
        "---\nname: idle-agent\ndescription: N/A\nmodel: sonnet\ntools:\n  - Bash\n---\nbody\n"
    )
    _commit_all(target, "2026-01-07T00:00:00", "add agents")

    (target / "nested").mkdir()
    (target / "nested" / "imported.md").write_text("Nested memory content.\n")
    (target / ".winter-hub").mkdir()
    (target / ".winter-hub" / "hub-only.md").write_text("Dot-prefixed hub-adjacent content.\n")
    (target / "AGENTS.md").write_text(
        "Root memory.\n@nested/imported.md\n@./nested/imported.md\n@.winter-hub/hub-only.md\n"
    )
    (target / "index.md").write_text("# Hub\nSome hub content.\n")
    _commit_all(target, "2026-01-08T00:00:00", "add memory + hub")

    # A skill renamed after creation: it must be dated by when it arrived at
    # its *current* name, not its original creation under the old name.
    renamed_skill = target / "skills" / "old-name"
    renamed_skill.mkdir(parents=True)
    (renamed_skill / "SKILL.md").write_text("---\ndescription: Will be renamed.\n---\nbody\n")
    _commit_all(target, "2026-01-10T00:00:00", "add old-name")
    _rename(target, "skills/old-name/SKILL.md", "skills/new-name/SKILL.md", "2026-01-20T00:00:00", "rename to new-name")


def _write_transcript(transcripts: Path, name: str, lines: list[str]) -> None:
    (transcripts / f"{name}.jsonl").write_text("\n".join(lines) + "\n")


def _measure(target: Path, transcripts: Path, too_new_days: int = 30) -> dict:
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "measure",
            "--target",
            str(target),
            "--transcripts-dir",
            str(transcripts),
            "--too-new-days",
            str(too_new_days),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def _skill(report: dict, name: str) -> dict:
    matches = [s for s in report["inventory"]["skills"] if s["name"] == name]
    assert len(matches) == 1, f"expected exactly one {name!r} entry"
    return matches[0]


def _agent(report: dict, name: str) -> dict:
    matches = [a for a in report["inventory"]["agents"] if a["name"] == name]
    assert len(matches) == 1, f"expected exactly one {name!r} entry"
    return matches[0]


@contextmanager
def _measure_fixture():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        target = root / "target-repo"
        transcripts = root / "transcripts"
        target.mkdir()
        transcripts.mkdir()
        _build_target_repo(target)
        yield target, transcripts


# ── measure: invocation counting ────────────────────────────────────────────


def test_counts_both_invocation_forms_and_prefix_stripping() -> None:
    with _measure_fixture() as (target, transcripts):
        _write_transcript(
            transcripts,
            "session-a",
            [
                '{"type":"tool_use","name":"Skill","input":{"skill":"wf-used-skill"}}',
                '{"type":"tool_use","name":"Skill","input":{"skill":"wf-used-skill"}}',
                '{"message":{"role":"user","content":"<command-message>used-skill</command-message>\\n<command-name>/wf-used-skill</command-name>"}}',
                '{"message":{"role":"user","content":"<command-name>/wf-typed-only-skill</command-name>"}}',
                '{"type":"tool_use","name":"Agent","input":{"subagent_type":"helper"}}',
                '{"type":"tool_use","name":"Agent","input":{"subagent_type":"helper"}}',
                '{"type":"tool_use","name":"Agent","input":{"subagent_type":"helper"}}',
            ],
        )
        report = _measure(target, transcripts)

        assert report["prefix"] == "wf"
        assert report["transcripts"]["scope"] == "machine-global"
        assert report["transcripts"]["available"] is True
        assert report["transcripts"]["sessions_scanned"] == 1

        used = _skill(report, "used-skill")
        assert used["invocations"] == {"scope": "machine-global", "tool_calls": 2, "typed_commands": 1, "total": 3}

        typed_only = _skill(report, "typed-only-skill")
        assert typed_only["invocations"] == {"scope": "machine-global", "tool_calls": 0, "typed_commands": 1, "total": 1}

        helper = _agent(report, "helper")
        assert helper["invocations"] == {"scope": "machine-global", "total": 3}


def test_name_prefix_neighbour_is_not_cross_credited() -> None:
    with _measure_fixture() as (target, transcripts):
        _write_transcript(
            transcripts,
            "session-a",
            ['{"type":"tool_use","name":"Skill","input":{"skill":"wf-distill-extra"}}'],
        )
        report = _measure(target, transcripts)

        distill = _skill(report, "distill")
        assert distill["invocations"]["total"] == 0

        distill_extra = _skill(report, "distill-extra")
        assert distill_extra["invocations"]["total"] == 1


# ── measure: dating and recency classification ──────────────────────────────


def test_never_invoked_skill_dated_and_not_flagged_too_new() -> None:
    with _measure_fixture() as (target, transcripts):
        _write_transcript(transcripts, "empty-session", ['{"note":"nothing relevant here"}'])
        report = _measure(target, transcripts)

        old = _skill(report, "old-skill")
        assert old["invocations"]["total"] == 0
        assert old["added"] is not None
        assert old["added_commit"] is not None
        assert old["age_days"] > 30
        assert old["renamed"] is False

        old_finding = next(e for e in report["classification"]["never_invoked_skills"] if e["name"] == "old-skill")
        assert old_finding["too_new_to_judge"] is False
        assert old_finding["installed_name"] == "old-skill"


def test_recently_added_never_invoked_skill_is_flagged_too_new() -> None:
    with _measure_fixture() as (target, transcripts):
        _write_transcript(transcripts, "empty-session", ['{"note":"nothing relevant here"}'])
        report = _measure(target, transcripts)

        brand_new = _skill(report, "brand-new-skill")
        assert brand_new["invocations"]["total"] == 0
        assert brand_new["age_days"] < 30

        finding = next(e for e in report["classification"]["never_invoked_skills"] if e["name"] == "brand-new-skill")
        assert finding["too_new_to_judge"] is True, "a skill added 2 days ago must be too-new, not dead"


def test_renamed_skill_is_dated_by_current_name_not_original_creation() -> None:
    with _measure_fixture() as (target, transcripts):
        _write_transcript(transcripts, "empty-session", ['{"note":"nothing relevant here"}'])
        report = _measure(target, transcripts)

        renamed = _skill(report, "new-name")
        assert renamed["renamed"] is True
        # Dated by the 2026-01-20 rename commit, not the 2026-01-10 original add.
        assert renamed["added"].startswith("2026-01-20")


def test_idle_agent_never_invoked_readme_excluded() -> None:
    with _measure_fixture() as (target, transcripts):
        _write_transcript(transcripts, "empty-session", ['{"note":"nothing relevant here"}'])
        report = _measure(target, transcripts)

        idle = _agent(report, "idle-agent")
        assert idle["invocations"]["total"] == 0
        never_invoked_agent_names = {e["name"] for e in report["classification"]["never_invoked_agents"]}
        assert "idle-agent" in never_invoked_agent_names

        agent_names = {a["name"] for a in report["inventory"]["agents"]}
        assert "README" not in agent_names
        assert len(report["inventory"]["agents"]) == 2  # helper + idle-agent, not README.md


# ── measure: memory-file import chain, hub, and byte-total scoping ─────────


def test_memory_file_import_chain_includes_dot_and_relative_forms() -> None:
    with _measure_fixture() as (target, transcripts):
        _write_transcript(transcripts, "empty-session", ['{"note":"nothing relevant here"}'])
        report = _measure(target, transcripts)

        memory_paths = {Path(f["path"]).name for f in report["inventory"]["memory_files"]}
        # AGENTS.md imports the same nested file twice — bare-relative
        # (`@nested/imported.md`) and dot-relative (`@./nested/imported.md`)
        # — plus a dot-prefixed directory (`@.winter-hub/hub-only.md`).
        assert memory_paths == {"AGENTS.md", "imported.md", "hub-only.md"}

        hub = report["inventory"]["hub_files"]
        assert len(hub) == 1
        assert Path(hub[0]["path"]).name == "index.md"
        assert hub[0]["bytes"] == (target / "index.md").stat().st_size

        assert report["inventory"]["memory_import_unresolved"] == 0
        assert report["inventory"]["memory_files_truncated"] is False

        totals = report["inventory"]["totals"]
        expected_memory_bytes = (
            (target / "AGENTS.md").stat().st_size
            + (target / "nested" / "imported.md").stat().st_size
            + (target / ".winter-hub" / "hub-only.md").stat().st_size
        )
        assert totals["memory_file_bytes"] == expected_memory_bytes
        assert totals["hub_bytes"] == hub[0]["bytes"]
        # `always_loaded_bytes` is the standing per-session cost — skill
        # descriptions, memory files, and the hub — and must exclude agent
        # definition bytes, which are only paid when an agent is spawned.
        assert totals["always_loaded_bytes"] == (
            totals["skill_description_bytes"] + totals["memory_file_bytes"] + totals["hub_bytes"]
        )
        assert "grand_total_bytes" not in totals
        assert totals["agent_definition_bytes"] > 0


def test_unresolvable_import_is_counted_not_silently_dropped() -> None:
    with _measure_fixture() as (target, transcripts):
        (target / "AGENTS.md").write_text("Root memory.\n@does-not-exist.md\n")
        _write_transcript(transcripts, "empty-session", ['{"note":"nothing relevant here"}'])
        report = _measure(target, transcripts)

        assert report["inventory"]["memory_import_unresolved"] == 1


# ── measure: transcript evidence quality ────────────────────────────────────


def test_no_transcripts_dir_is_reported_as_no_evidence_not_confirmed_dead() -> None:
    with _measure_fixture() as (target, transcripts):
        missing = transcripts.parent / "does-not-exist"
        report = _measure(target, missing)

        assert report["transcripts"]["available"] is False
        assert report["transcripts"]["sessions_scanned"] == 0
        assert report["transcripts"]["evidence_note"] == "no evidence"

        for skill in report["inventory"]["skills"]:
            assert skill["invocations"]["total"] == 0
        for entry in report["classification"]["never_invoked_skills"]:
            assert entry["note"] == "no evidence"


def test_existing_but_empty_transcripts_dir_is_reported_as_no_evidence() -> None:
    with _measure_fixture() as (target, transcripts):
        # `transcripts` exists (created by the fixture) but holds no *.jsonl
        # files — `available` is true, yet zero sessions were actually
        # scanned, so this must still read as no evidence, not a confirmed
        # zero over "the whole store."
        report = _measure(target, transcripts)

        assert report["transcripts"]["available"] is True
        assert report["transcripts"]["sessions_scanned"] == 0
        assert report["transcripts"]["evidence_note"] == "no evidence"
        for entry in report["classification"]["never_invoked_skills"]:
            assert entry["note"] == "no evidence"


def test_unreadable_project_directory_is_reported_as_partial_not_full_evidence() -> None:
    with _measure_fixture() as (target, transcripts):
        _write_transcript(transcripts, "readable-session", ['{"note":"nothing relevant here"}'])
        locked = transcripts / "locked-project"
        locked.mkdir()
        (locked / "unreadable-session.jsonl").write_text('{"note":"nothing relevant here"}\n')
        original_mode = locked.stat().st_mode
        locked.chmod(0)
        try:
            report = _measure(target, transcripts)
        finally:
            locked.chmod(stat.S_IMODE(original_mode))

        # A permission-denied project directory must not read as full
        # evidence: `available` stays true (the store exists), but the
        # partial-evidence signal must be visible and every never-invoked
        # entry's note must carry it rather than reporting `None`.
        assert report["transcripts"]["available"] is True
        assert report["transcripts"]["directories_unreadable"] == 1
        assert report["transcripts"]["evidence_note"] is not None
        for entry in report["classification"]["never_invoked_skills"]:
            assert entry["note"] is not None


def test_scopes_are_labeled_and_kept_apart() -> None:
    with _measure_fixture() as (target, transcripts):
        _write_transcript(transcripts, "empty-session", ['{"note":"nothing relevant here"}'])
        report = _measure(target, transcripts)

        assert report["transcripts"]["scope"] == "machine-global"
        assert report["inventory"]["scope"] == "target-scoped"
        for skill in report["inventory"]["skills"]:
            assert skill["invocations"]["scope"] == "machine-global"
        for agent in report["inventory"]["agents"]:
            assert agent["invocations"]["scope"] == "machine-global"


# ── measure: installed form (workspace root) ────────────────────────────────


def test_installed_form_uses_installed_name_for_skills_and_dates_generated_agent_copies() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        ws = root / "workspace"
        ws.mkdir()
        transcripts = root / "transcripts"
        transcripts.mkdir()

        # The tracked extension checkout a workspace installs from.
        ext = ws / ".winter" / "ext" / "sample"
        ext.mkdir(parents=True)
        subprocess.run(["git", "-C", str(ext), "init", "-q"], check=True, capture_output=True, text=True)
        (ext / "winter-ext.toml").write_text('name = "sample-ext"\nprefix = "wf"\n')
        (ext / "agents").mkdir()
        (ext / "agents" / "helper.md").write_text(
            "---\nname: helper\ndescription: N/A\nmodel: sonnet\ntools:\n  - Bash\n---\nbody\n"
        )
        _commit_all(ext, "2026-02-01T00:00:00", "add helper agent")
        (ext / "skills").mkdir()
        skill_source = ext / "skills" / "cold-review"
        skill_source.mkdir()
        (skill_source / "SKILL.md").write_text("---\ndescription: Installed-form skill.\n---\nbody\n")
        _commit_all(ext, "2026-02-02T00:00:00", "add cold-review skill")

        # The workspace root is its own (separate) git repo, committed before
        # the generated `.claude/` surfaces exist below — so the agent copy
        # `git add -A` would otherwise pick up stays genuinely untracked,
        # exactly the shape that defeats a naive "inside a git repo" check.
        subprocess.run(["git", "-C", str(ws), "init", "-q"], check=True, capture_output=True, text=True)
        (ws / "README.md").write_text("workspace\n")
        _commit_all(ws, "2026-02-03T00:00:00", "init workspace repo")

        # The installed surfaces winter actually generates: a skill is
        # symlinked (dateable via the symlink target); an agent is a plain
        # untracked copy winter generates into the workspace's own repo (not
        # dateable through itself — must fall back to the tracked source).
        (ws / ".claude" / "skills").mkdir(parents=True)
        (ws / ".claude" / "skills" / "wf-cold-review").symlink_to(skill_source)
        (ws / ".claude" / "agents").mkdir(parents=True)
        (ws / ".claude" / "agents" / "wf-helper.md").write_text((ext / "agents" / "helper.md").read_text())

        report = _measure(ws, transcripts)

        assert report["inventory"]["skills_form"] == "installed"
        assert report["inventory"]["agents_form"] == "installed"

        skill = _skill(report, "cold-review")
        assert skill["installed_name"] == "wf-cold-review"

        agent = _agent(report, "helper")
        assert agent["added"] is not None, "an untracked generated agent copy must fall back to its tracked source"
        assert agent["added"].startswith("2026-02-01")


# ── apply ────────────────────────────────────────────────────────────────


def _apply(
    settings_path: Path,
    overrides_path: Path,
    overrides: dict,
    *,
    dry_run: bool = False,
) -> subprocess.CompletedProcess[str]:
    overrides_path.write_text(json.dumps(overrides))
    args = [
        sys.executable,
        str(SCRIPT),
        "apply",
        "--settings",
        str(settings_path),
        "--overrides",
        str(overrides_path),
    ]
    if dry_run:
        args.append("--dry-run")
    return subprocess.run(args, capture_output=True, text=True)


@contextmanager
def _apply_fixture():
    with tempfile.TemporaryDirectory() as tmp:
        yield Path(tmp) / "settings.json", Path(tmp) / "overrides.json"


def test_merges_into_existing_settings_without_touching_other_keys() -> None:
    with _apply_fixture() as (settings_path, overrides_path):
        settings_path.write_text(json.dumps({"model": "claude-fable-5[1m]", "skillOverrides": {"kept-skill": "off"}}))
        result = _apply(settings_path, overrides_path, {"review-manifest": "user-invocable-only"})
        assert result.returncode == 0, result.stderr

        written = json.loads(settings_path.read_text())
        assert written["model"] == "claude-fable-5[1m]"
        assert written["skillOverrides"]["kept-skill"] == "off"
        assert written["skillOverrides"]["review-manifest"] == "user-invocable-only"


def test_creates_settings_file_when_absent() -> None:
    with _apply_fixture() as (settings_path, overrides_path):
        assert not settings_path.exists()
        result = _apply(settings_path, overrides_path, {"harness-score": "off"})
        assert result.returncode == 0, result.stderr
        written = json.loads(settings_path.read_text())
        assert written == {"skillOverrides": {"harness-score": "off"}}


def test_dry_run_does_not_write() -> None:
    with _apply_fixture() as (settings_path, overrides_path):
        result = _apply(settings_path, overrides_path, {"harness-score": "off"}, dry_run=True)
        assert result.returncode == 0, result.stderr
        assert not settings_path.exists()
        printed = json.loads(result.stdout)
        assert printed["applied"] == {"harness-score": "off"}
        assert printed["dry_run"] is True


def test_apply_output_is_delta_only_and_never_echoes_unrelated_settings() -> None:
    with _apply_fixture() as (settings_path, overrides_path):
        settings_path.write_text(json.dumps({"env": {"ANTHROPIC_API_KEY": "sk-should-not-echo"}}))
        result = _apply(settings_path, overrides_path, {"harness-score": "off"})
        assert result.returncode == 0, result.stderr

        printed = json.loads(result.stdout)
        assert printed == {"settings_path": str(settings_path), "dry_run": False, "applied": {"harness-score": "off"}}
        assert "sk-should-not-echo" not in result.stdout

        written = json.loads(settings_path.read_text())
        assert written["env"]["ANTHROPIC_API_KEY"] == "sk-should-not-echo"


def test_rejects_invalid_override_value_and_leaves_existing_settings_untouched() -> None:
    with _apply_fixture() as (settings_path, overrides_path):
        original = json.dumps({"skillOverrides": {"kept-skill": "off"}})
        settings_path.write_text(original)
        result = _apply(settings_path, overrides_path, {"harness-score": "always"})
        assert result.returncode != 0
        assert "invalid skillOverrides value" in result.stderr
        assert settings_path.read_text() == original, "a rejected apply must not touch an existing settings file"


def test_rejects_invalid_override_key() -> None:
    with _apply_fixture() as (settings_path, overrides_path):
        result = _apply(settings_path, overrides_path, {"not a valid key!": "off"})
        assert result.returncode != 0
        assert not settings_path.exists()
        assert "invalid skillOverrides key" in result.stderr


# ── runner ───────────────────────────────────────────────────────────────

_TESTS = [(name, fn) for name, fn in sorted(globals().items()) if name.startswith("test_") and callable(fn)]


def main() -> int:
    failures = 0
    for name, fn in _TESTS:
        try:
            fn()
        except AssertionError as exc:
            print(f"NOT OK  {name}: {exc}")
            failures += 1
        else:
            print(f"ok      {name}")
    print()
    if failures:
        print(f"test_context_usage: {failures} of {len(_TESTS)} assertion(s) failed.")
        return 1
    print(f"test_context_usage: all {len(_TESTS)} test(s) passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
