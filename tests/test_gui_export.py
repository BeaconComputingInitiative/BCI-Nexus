# BEACON COMPUTING INITIATIVE
# Developer Seal: CJB-DEV-2026
# Component: Sentinel Live Export Regression Tests v0.5.3
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from nexus import gui_export


class Label:
    def __init__(self, value):
        self.value = str(value)

    def text(self):
        return self.value

    def toPlainText(self):
        return self.value


class Table:
    def __init__(self, columns, rows):
        self.columns = columns
        self.rows = rows

    def columnCount(self):
        return len(self.columns)

    def rowCount(self):
        return len(self.rows)

    def horizontalHeaderItem(self, col):
        return Label(self.columns[col])

    def item(self, row, col):
        value = self.rows[row][col]
        return None if value is None else Label(value)


class Window:
    def __init__(self):
        self.indicators_table = Table(["UTC", "Indicator"], [["2026-10-31", "Beacon"]])
        self.dns_summary = Label("Queries: 1")
        self.dns_import_label = Label("Logs: none")
        self.dns_table = Table(["BSSID", "Queries"], [["AA:BB", "1"]])
        self.flow_text = Label("No edge flow imported")
        self.raw_table = Table(["Metric", "Value"], [["frames_total", "42"]])
        self.terminal_out = Label("[BCI] Capture initialized")
        self.current_snapshot = {"version": "test", "updated_at_utc": "2026-10-31T21:25:00Z"}
        self.status_lbl = Label("● API LIVE · SNAPSHOT FRESH")

    def selected_bssid(self):
        return None


class SentinelExports(unittest.TestCase):
    def test_five_views_available(self):
        self.assertEqual(len(gui_export.SECTIONS), 5)
        self.assertEqual(set(gui_export.capture_views(Window())),
                         set(gui_export.SECTION_KEYS))

    def test_export_is_latest_rendered_data(self):
        window = Window()
        first = gui_export.build_export(window)
        window.raw_table.rows[0][1] = "58"
        second = gui_export.build_export(window)
        self.assertEqual(first["data"]["prometheus_metrics"]["table"]["rows"][0][1], "42")
        self.assertEqual(second["data"]["prometheus_metrics"]["table"]["rows"][0][1], "58")
        self.assertEqual(second["source_updated_at_utc"], "2026-10-31T21:25:00Z")

    def test_selected_section_restricts_export(self):
        data = gui_export.build_export(Window(), "dns_observation")
        self.assertEqual(list(data["data"]), ["dns_observation"])
        with self.assertRaises(ValueError):
            gui_export.build_export(Window(), "unregistered")

    def test_sha256_sidecar_verifies_document(self):
        with TemporaryDirectory() as temporary:
            dest = Path(temporary) / "capture.json"
            document = gui_export.build_export(Window())
            saved, manifest, digest = gui_export.save_export(dest, document)
            self.assertEqual(hashlib.sha256(saved.read_bytes()).hexdigest(), digest)
            self.assertIn(digest + "  capture.json", manifest.read_text())
            self.assertEqual(saved.stat().st_mode & 0o777, 0o600)
            self.assertEqual(manifest.stat().st_mode & 0o777, 0o600)
            self.assertEqual(json.loads(saved.read_text())["developer_seal"],
                             "CJB-DEV-2026")

    def test_export_filename_is_utc(self):
        at = datetime(2026, 10, 31, 21, 30, tzinfo=timezone.utc)
        self.assertEqual(gui_export.filename("all", at),
                         "bci-sentinel-all-20261031T213000Z.json")

    def test_refuse_symlink_export_destination(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            destination = root / "capture.json"
            destination.symlink_to(root / "real.json")
            with self.assertRaises(PermissionError):
                gui_export.save_export(destination, gui_export.build_export(Window()))

if __name__ == "__main__":
    unittest.main()
