# BEACON COMPUTING INITIATIVE
# Developer Seal: CJB-DEV-2026
# Component: BCIBot Agent Action Tests v0.3.0
import unittest
from unittest.mock import patch
from nexus import agent

class AgentTests(unittest.TestCase):
    def test_catalog(self):
        self.assertEqual(agent.catalog()["mode"], "READ_ONLY")
        self.assertIn("firewall.modify", agent.catalog()["disabled"])

    def test_block_disallowed_actions(self):
        for name in ("firewall.modify", "shell.execute", "network.scan"):
            with self.assertRaises(PermissionError):
                agent.execute(name)

    def test_explicit_allowlist_execution(self):
        with patch.dict(agent.ACTIONS, {"test.read": ("Test", lambda: {"ok": True})},
                        clear=True):
            self.assertTrue(agent.execute("test.read")["data"]["ok"])

    def test_all_actions_checked_before_any_run(self):
        called = []
        with patch.dict(agent.ACTIONS, {"test.read": ("Test", lambda: called.append(1))},
                        clear=True):
            with self.assertRaises(PermissionError):
                agent.analyze("Review", ["test.read", "firewall.modify"])
        self.assertEqual(called, [])

    def test_duplicate_actions_blocked(self):
        with self.assertRaises(ValueError):
            agent.analyze("Review", ["host.summary", "host.summary"])

    def test_agent_model_has_no_tools(self):
        with patch.dict(agent.ACTIONS, {"test.read": ("Test", lambda: {"ok": True})},
                        clear=True), patch.object(agent, "audit"), \
             patch.object(agent.core, "_json_response",
                          return_value={"message": {"content": "test.read observed"}}) as call:
            result = agent.analyze("Review", ["test.read"])
        self.assertTrue(result["citation_gate_passed"])
        self.assertFalse(result["semantic_validation"])
        self.assertEqual(result["authority"], "NONE")
        self.assertNotIn('"tools"', call.call_args.args[0].data.decode("utf-8"))

    def test_missing_citation_fails(self):
        with patch.dict(agent.ACTIONS, {"test.read": ("Test", lambda: {})},
                        clear=True), patch.object(agent, "audit"), \
             patch.object(agent.core, "_json_response",
                          return_value={"message": {"content": "Generic report"}}):
            result = agent.analyze("Review", ["test.read"])
        self.assertFalse(result["citation_gate_passed"])

    def test_invalid_questions(self):
        with self.assertRaises(ValueError):
            agent.analyze("", ["host.summary"])

if __name__ == "__main__":
    unittest.main()
