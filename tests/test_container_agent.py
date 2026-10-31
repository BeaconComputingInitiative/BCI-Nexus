# BEACON COMPUTING INITIATIVE
# Developer Seal: CJB-DEV-2026
# Component: Offline Docker Shell Validation v0.4.0
import unittest
from nexus import container_agent, agent_client

class TestDockerAgent(unittest.TestCase):
    def test_bounds(self):
        self.assertEqual(container_agent.validate_command("pwd"), "pwd")
        for value in ("", " ", "a" * 4001, "\x00", None, []):
            with self.subTest(value=str(value)[:15]):
                with self.assertRaises(ValueError):
                    container_agent.validate_command(value)

    def test_api_loopback_and_route_gate(self):
        self.assertEqual(agent_client.BASE, "http://127.0.0.1:11436")
        with self.assertRaises(ValueError):
            agent_client.call("POST", "/host/shell", {"command": "pwd"})

    def test_container_registry_does_not_authorize_host(self):
        self.assertIn("workspace.list", container_agent.ACTIONS)
        self.assertNotIn("bcilock.authorize", container_agent.ACTIONS)
        self.assertNotIn("firewall.modify", container_agent.ACTIONS)
