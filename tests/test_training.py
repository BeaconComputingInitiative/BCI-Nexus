# BEACON COMPUTING INITIATIVE
# Developer Seal: CJB-DEV-2026
# Component: Offline Training Inventory Test v0.4.0
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from nexus import training

class TestTraining(unittest.TestCase):
    def test_missing_path(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.dict(os.environ, {"BCI_TRAINING_ROOT": directory + "/missing"}):
                self.assertFalse(training.status()["available"])

    def test_dataset_inventory_is_read_only(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory) / "datasets" / "v1"
            folder.mkdir(parents=True)
            (folder / "train.jsonl").write_text('{"example":1}\n')
            with patch.dict(os.environ, {"BCI_TRAINING_ROOT": directory}):
                record = training.status()
            self.assertEqual(record["datasets"][0]["path"], "datasets/v1/train.jsonl")
            self.assertFalse(record["automatic_promotion"])
            self.assertEqual(record["mode"], "INSPECT_ONLY")
