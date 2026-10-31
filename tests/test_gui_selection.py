# BEACON COMPUTING INITIATIVE
# Developer Seal: CJB-DEV-2026
# Component: Compatible Sentinel Checkout Selection Tests v0.5.1
from pathlib import Path
from unittest.mock import patch
import os
import tempfile
import unittest
from nexus import gui


def make_sentinel(folder: Path, hook: bool) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "network_scope.py").write_text("# scope fixture\n", encoding="utf-8")
    parameters = "nexus_extension=None" if hook else ""
    (folder / "sentinel_gui.py").write_text(
        "def main(" + parameters + "):\n    pass\n", encoding="utf-8"
    )


class SentinelPathTests(unittest.TestCase):
    def test_prefers_current_checkout_over_legacy(self):
        with tempfile.TemporaryDirectory() as root:
            home = Path(root)
            base = home / "BCI"
            newer = base / "BCISentinel-"
            older = base / "Docker Projects/orbital"
            make_sentinel(newer, True)
            make_sentinel(older, False)
            with patch("pathlib.Path.home", return_value=home), \
                    patch.dict(os.environ, {"BCI_SENTINEL_DIR": ""}):
                self.assertEqual(gui.sentinel_path(), newer)

    def test_skips_outdated_checkout(self):
        with tempfile.TemporaryDirectory() as root:
            home = Path(root)
            base = home / "BCI"
            make_sentinel(base / "BCISentinel-", False)
            make_sentinel(base / "Docker Projects/orbital", True)
            with patch("pathlib.Path.home", return_value=home), \
                    patch.dict(os.environ, {"BCI_SENTINEL_DIR": ""}):
                self.assertEqual(gui.sentinel_path(), base / "Docker Projects/orbital")

    def test_invalid_explicit_path_fails_closed(self):
        with tempfile.TemporaryDirectory() as root:
            folder = Path(root) / "old"
            make_sentinel(folder, False)
            with patch.dict(os.environ, {"BCI_SENTINEL_DIR": str(folder)}):
                with self.assertRaisesRegex(RuntimeError, "incompatible"):
                    gui.sentinel_path()

    def test_malformed_source_is_not_accepted(self):
        with tempfile.TemporaryDirectory() as root:
            folder = Path(root)
            make_sentinel(folder, True)
            (folder / "sentinel_gui.py").write_text("def main(\n", encoding="utf-8")
            self.assertFalse(gui._supports_nexus_extension(folder))
