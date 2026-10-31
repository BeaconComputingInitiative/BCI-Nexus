# BEACON COMPUTING INITIATIVE
# Developer Seal: CJB-DEV-2026
# Component: BCI Nexus network observer tests v0.2.0
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest
from unittest.mock import patch

from nexus import network

SAMPLE = {
    "interface": "wlan0", "gateway": "192.0.2.1",
    "addresses": ["192.0.2.10"], "ssid": "authorized-test-ap",
    "bssid": "02:00:00:00:00:01",
}


class NetworkTests(unittest.TestCase):
    def test_stable_snapshot_hash(self):
        self.assertEqual(network.event(SAMPLE)["snapshot_sha256"],
                         network.event(SAMPLE)["snapshot_sha256"])

    def test_changed_snapshot_hash(self):
        other = dict(SAMPLE, gateway="192.0.2.254")
        self.assertNotEqual(network.event(SAMPLE)["snapshot_sha256"],
                            network.event(other)["snapshot_sha256"])

    def test_sqlite_deduplicates(self):
        with TemporaryDirectory() as folder:
            path = Path(folder) / "state.sqlite3"
            self.assertTrue(network.insert_if_changed(network.event(SAMPLE), path))
            self.assertFalse(network.insert_if_changed(network.event(SAMPLE), path))
            self.assertTrue(network.insert_if_changed(
                network.event(dict(SAMPLE, gateway="192.0.2.254")), path))

    def test_only_local_command_reads(self):
        results = [
            json.dumps([{"dev": "wlan0", "gateway": "192.0.2.1"}]),
            json.dumps([{"ifname": "wlan0", "addr_info": [{"local": "192.0.2.10"}]}]),
            "Connected to 02:00:00:00:00:01\nSSID: authorized-test-ap\n",
        ]
        with patch("nexus.network.run_readonly", side_effect=results) as reader:
            self.assertEqual(network.get_local_network(), SAMPLE)
        self.assertEqual([c.args[0][0] for c in reader.call_args_list],
                         ["ip", "ip", "iw"])

    def test_poll_interval_guard(self):
        with self.assertRaises(ValueError):
            network.watch(1)

    def test_event_contract(self):
        record = network.event(SAMPLE)
        self.assertEqual(record["schema"], "bci.nexus.network-change.v1")
        self.assertEqual(len(record["snapshot_sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
