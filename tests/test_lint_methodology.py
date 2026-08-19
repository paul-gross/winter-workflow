#!/usr/bin/env python3
"""Focused stdlib-only tests for scripts/lint-methodology.py."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LINT = REPO_ROOT / "scripts" / "lint-methodology.py"


class MethodologyLintTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp_dir.name) / "winter-workflow"
        self.repo.mkdir()
        (self.repo / "winter-ext.toml").write_text('name = "winter-workflow"\n')

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def write_methodology(self, relative: str, text: str) -> Path:
        path = self.repo / "methodology" / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def invoke_lint(
        self,
        lint_paths: str,
        *,
        ext_dir: Path | None = None,
        workspace_dir: Path | None = None,
    ) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["WINTER_EXT_DIR"] = str(ext_dir or self.repo)
        env["WINTER_WORKSPACE_DIR"] = str(workspace_dir or self.repo)
        env["WINTER_LINT_PATHS"] = lint_paths
        env["WINTER_LINT_SCOPE"] = "changed"
        return subprocess.run(
            [sys.executable, str(LINT)],
            cwd=self.repo,
            env=env,
            capture_output=True,
            text=True,
        )

    def run_lint(self, scope: Path | None = None) -> list[dict]:
        result = self.invoke_lint(str(scope or self.repo))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        findings = [json.loads(line) for line in result.stdout.splitlines() if line.strip()]
        for finding in findings:
            self.assertEqual(finding.get("check"), "methodology-boundary")
            self.assertEqual(finding.get("status"), "fail")
            self.assertTrue(finding.get("file"))
            self.assertIsInstance(finding.get("line"), int)
        return findings

    def test_passes_runtime_identifiers_and_target_path_examples(self) -> None:
        self.write_methodology(
            "review/process.md",
            "Spawn `cold-reviewer` for the code axis.\n"
            "Pass the runtime identifier `AskUserQuestion` to the coordinator.\n"
            "Agent-facing targets can include `agents/*.md` and `skills/**/SKILL.md`.\n",
        )

        self.assertEqual(self.run_lint(), [])

    def test_fails_on_arguments_invocation_syntax(self) -> None:
        self.write_methodology("build/process.md", "Read the mode from `$ARGUMENTS`.\n")

        findings = self.run_lint()

        self.assertEqual(len(findings), 1)
        self.assertIn("$ARGUMENTS", findings[0]["message"])
        self.assertEqual(findings[0]["line"], 1)

    def test_fails_on_relative_skill_and_agent_links(self) -> None:
        self.write_methodology(
            "review/process.md",
            "Use the [skill](../../skills/cold-review/SKILL.md).\n"
            "Spawn the [agent](../../agents/cold-reviewer.md).\n",
        )

        findings = self.run_lint()

        self.assertEqual(len(findings), 2)
        self.assertIn("skill adapters", findings[0]["message"])
        self.assertIn("agent adapters", findings[1]["message"])

    def test_fails_on_relative_skill_and_agent_code_spans(self) -> None:
        self.write_methodology(
            "review/process.md",
            "Do not read `../../skills/cold-review/SKILL.md`.\n",
        )
        self.write_methodology("process.md", "Do not read ``../agents/cold-reviewer.md``.\n")

        findings = self.run_lint()

        self.assertEqual(len(findings), 2)
        self.assertIn("agent adapters", findings[0]["message"])
        self.assertIn("skill adapters", findings[1]["message"])

    def test_fails_on_relative_skill_and_agent_imports(self) -> None:
        self.write_methodology(
            "review/process.md",
            "@../../skills/cold-review/SKILL.md\n"
            "Load @../../agents/cold-reviewer.md before continuing.\n",
        )

        findings = self.run_lint()

        self.assertEqual(len(findings), 2)
        self.assertIn("skill adapters", findings[0]["message"])
        self.assertIn("agent adapters", findings[1]["message"])

    def test_fails_on_canonical_skill_and_agent_references(self) -> None:
        self.write_methodology(
            "review/process.md",
            "Do not read `winter-workflow:/skills/cold-review/SKILL.md`.\n"
            "Do not link [the adapter](winter-workflow:/agents/cold-reviewer.md).\n",
        )

        findings = self.run_lint()

        self.assertEqual(len(findings), 2)
        self.assertIn("skill adapters", findings[0]["message"])
        self.assertIn("agent adapters", findings[1]["message"])

    def test_resolves_suffixes_for_relative_canonical_and_local_targets(self) -> None:
        self.write_methodology(
            "review/process.md",
            "Use [relative](../../skills/cold-review/SKILL.md?mode=fast#usage).\n"
            "@../../agents/cold-reviewer.md#prompt\n"
            "Read `../../skills/commit/SKILL.md?raw=1`.\n"
            "Use [canonical](winter-workflow:/agents/cold-reviewer.md#prompt?raw=1).\n"
            "@winter-workflow:/skills/cold-review/SKILL.md?mode=fast\n"
            "Read `winter-workflow:/agents/backend-verifier.md?raw=1#prompt`.\n"
            "Use [local](local:/skills/cold-review/SKILL.md#usage).\n"
            "@local:/agents/cold-reviewer.md?raw=1#prompt\n"
            "Read `local:/skills/commit/SKILL.md?mode=fast`.\n",
        )

        findings = self.run_lint()

        self.assertEqual(len(findings), 9)
        self.assertEqual([finding["line"] for finding in findings], list(range(1, 10)))
        self.assertIn("skill adapters", findings[0]["message"])
        self.assertIn("agent adapters", findings[1]["message"])
        self.assertIn("skill adapters", findings[2]["message"])
        self.assertIn("agent adapters", findings[3]["message"])
        self.assertIn("skill adapters", findings[4]["message"])
        self.assertIn("agent adapters", findings[5]["message"])
        self.assertIn("skill adapters", findings[6]["message"])
        self.assertIn("agent adapters", findings[7]["message"])
        self.assertIn("skill adapters", findings[8]["message"])

    def test_preserves_foreign_prefixed_adapter_targets_as_nonlocal(self) -> None:
        self.write_methodology(
            "review/process.md",
            "Use [foreign](winter-product:/skills/triage/SKILL.md#usage).\n"
            "@winter-context:/agents/reviewer.md?raw=1\n"
            "Read `another-module:/skills/example/SKILL.md?raw=1#usage`.\n",
        )

        self.assertEqual(self.run_lint(), [])

    def test_exempts_fenced_and_marked_examples(self) -> None:
        self.write_methodology(
            "review/process.md",
            "```md\n"
            "Read `$ARGUMENTS`.\n"
            "@../../skills/cold-review/SKILL.md\n"
            "`../../agents/cold-reviewer.md`\n"
            "winter-workflow:/skills/cold-review/SKILL.md\n"
            "```\n"
            "Example `$ARGUMENTS` and `../../agents/example.md`. "
            "<!-- winter-lint:example -->\n",
        )

        self.assertEqual(self.run_lint(), [])

    def test_marker_exempts_its_whole_block(self) -> None:
        # `dprint` wraps prose, so the marker lands on the paragraph's last line
        # while the illustration it exempts sits further up.
        self.write_methodology(
            "review/process.md",
            "Example `$ARGUMENTS` and `../../agents/example.md` shown only to\n"
            "illustrate the notation. <!-- winter-lint:example -->\n",
        )

        self.assertEqual(self.run_lint(), [])

    def test_marker_does_not_reach_across_a_blank_line(self) -> None:
        self.write_methodology(
            "review/process.md",
            "Illustration only. <!-- winter-lint:example -->\n\nRead `$ARGUMENTS`.\n",
        )

        self.assertNotEqual(self.run_lint(), [])

    def test_fences_close_only_with_matching_marker_and_opening_length(self) -> None:
        self.write_methodology(
            "review/process.md",
            "````md\n"
            "```\n"
            "Read `$ARGUMENTS`.\n"
            "~~~~\n"
            "@../../skills/cold-review/SKILL.md\n"
            "````\n"
            "Read `$ARGUMENTS`.\n"
            "~~~~md\n"
            "```\n"
            "Read `$ARGUMENTS`.\n"
            "~~~\n"
            "@../../agents/cold-reviewer.md\n"
            "~~~~\n"
            "Read `$ARGUMENTS`.\n",
        )

        findings = self.run_lint()

        self.assertEqual([finding["line"] for finding in findings], [7, 14])

    def test_emits_one_combined_finding_per_offending_line(self) -> None:
        self.write_methodology(
            "review/process.md",
            "Use `$ARGUMENTS`, [the skill](../../skills/cold-review/SKILL.md), "
            "and `../../agents/cold-reviewer.md`.\n",
        )

        findings = self.run_lint()

        self.assertEqual(len(findings), 1)
        self.assertIn("$ARGUMENTS", findings[0]["message"])
        self.assertIn("skill adapters", findings[0]["message"])
        self.assertIn("agent adapters", findings[0]["message"])
        self.assertIn("semantic inputs", findings[0]["remediation"])
        self.assertIn("runtime skill port", findings[0]["remediation"])
        self.assertIn("runtime agent port", findings[0]["remediation"])

    def test_real_methodology_tree_passes_clean(self) -> None:
        result = self.invoke_lint(
            str(REPO_ROOT),
            ext_dir=REPO_ROOT,
            workspace_dir=REPO_ROOT,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(result.stdout, "")

    def test_dispatcher_env_scope_emits_ndjson_and_exits_zero(self) -> None:
        skill = self.write_methodology(
            "review/skill.md", "Read `../../skills/cold-review/SKILL.md`.\n"
        )
        agent = self.write_methodology(
            "review/agent.md", "@../../agents/cold-reviewer.md\n"
        )
        result = self.invoke_lint(
            f"{skill}\n{agent}\n",
            workspace_dir=Path(self.temp_dir.name),
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        lines = result.stdout.splitlines()
        self.assertEqual(len(lines), 2)
        findings = [json.loads(line) for line in lines]
        self.assertEqual(
            [finding["file"] for finding in findings],
            [
                "winter-workflow/methodology/review/agent.md",
                "winter-workflow/methodology/review/skill.md",
            ],
        )
        for finding in findings:
            self.assertEqual(
                set(finding),
                {"check", "status", "message", "file", "line", "remediation"},
            )
            self.assertEqual(finding["check"], "methodology-boundary")
            self.assertEqual(finding["status"], "fail")


if __name__ == "__main__":
    unittest.main(verbosity=2)
