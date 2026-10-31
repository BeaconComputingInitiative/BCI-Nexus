# BEACON COMPUTING INITIATIVE
# Developer Seal: CJB-DEV-2026
# Component: Swarm Regression Tests v0.5.0
import subprocess
import unittest
from unittest.mock import patch
from nexus import swarm

def fake(output):
    return subprocess.CompletedProcess(["ip"], 0, output, "")

class SwarmTests(unittest.TestCase):
    def test_ssid_requires_approval(self):
        job = swarm.plan("pull the ssids around me")
        self.assertEqual(job.kind, "wifi.ssids")
        with self.assertRaises(PermissionError):
            swarm.execute(job)

    def test_nmap_private_scope(self):
        with patch.object(swarm, "_cmd", side_effect=[
            fake('[{"dev":"wlan0","metric":10}]'),
            fake('[{"addr_info":[{"family":"inet","local":"192.168.4.7","prefixlen":24}]}]')
        ]):
            job = swarm.plan("run an nmap scan on my network")
        self.assertEqual(job.host.target, "192.168.4.0/24")
        self.assertEqual(job.host.argv[:3], ("nmap", "-sn", "-n"))

    def test_explicit_destinations_not_autorouted(self):
        self.assertIsNone(swarm.classify("scan 8.8.8.8/32"))
        self.assertIsNone(swarm.classify("scan my network; echo test"))

    def test_advisory_specialists(self):
        job = swarm.plan("Explain BLE key rotation")
        self.assertEqual(job.kind, "advisory")
        self.assertIn("skeptic", job.roles)
        self.assertIsNone(job.host)
