# BEACON COMPUTING INITIATIVE
# Developer Seal: CJB-DEV-2026
# Component: Docker Unix Socket Acceptance Tests v0.4.1
from pathlib import Path
from socketserver import ThreadingUnixStreamServer
from unittest.mock import patch
import tempfile
import threading
import unittest
from nexus import container_agent, agent_client

class TestDockerAgent(unittest.TestCase):
    def test_bounds(self):
        self.assertEqual(container_agent.validate_command("pwd"), "pwd")
        for value in ("", " ", "a" * 4001, "\x00", None, []):
            with self.subTest(value=str(value)[:15]):
                with self.assertRaises(ValueError):
                    container_agent.validate_command(value)

    def test_socket_route_gate(self):
        self.assertEqual(agent_client.SOCKET_FILE.name, "agent.sock")
        with self.assertRaises(ValueError):
            agent_client.call("POST", "/host/shell", {"command": "pwd"})

    def test_missing_socket_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(RuntimeError):
                agent_client.verify_socket(Path(directory) / "missing.sock")

    def test_authenticated_unix_transport(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "agent.sock"
            server = ThreadingUnixStreamServer(str(path), container_agent.Handler)
            path.chmod(0o600)
            container_agent.Handler.key = "a" * 60
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                with patch.object(agent_client, "SOCKET_FILE", path), \
                     patch.object(agent_client, "token", return_value="a" * 60):
                    result = agent_client.health()
                    self.assertEqual(result["scope"], "CONTAINER_ONLY")
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=3)

    def test_container_registry_does_not_authorize_host(self):
        self.assertIn("workspace.list", container_agent.ACTIONS)
        self.assertNotIn("bcilock.authorize", container_agent.ACTIONS)
        self.assertNotIn("firewall.modify", container_agent.ACTIONS)
