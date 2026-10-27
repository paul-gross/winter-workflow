#!/usr/bin/env python3
"""Keep the artifact-storage kinds table and the winter-ext.toml exclude declaration in step."""

from __future__ import annotations

import re
import tomllib
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class ArtifactKindsTests(unittest.TestCase):
    def test_declared_space_kinds_match_artifact_storage_table(self) -> None:
        storage = (REPO_ROOT / "methodology" / "artifact-storage.md").read_text()
        table = storage.split("## Artifact kinds and naming", 1)[1].split("\n## ", 1)[0]
        documented = re.findall(r"^\| `([^`]+)`", table, flags=re.MULTILINE)
        manifest = tomllib.loads((REPO_ROOT / "winter-ext.toml").read_text())
        declared = manifest["excludes"]["space_kinds"]
        self.assertTrue(documented)
        self.assertEqual(sorted(declared), sorted(documented))


if __name__ == "__main__":
    unittest.main()
