# BEACON COMPUTING INITIATIVE
# Developer Seal: CJB-DEV-2026
# Component: BCI Nexus evidence adapter tests v0.2.0
import os
import unittest
from datetime import datetime
from unittest.mock import patch

from nexus import core


def example():
    return {
        "schema": "bci.bcilock.telemetry.v1",
        "published_utc": "2026-10-31T13:57:00+00:00",
        "ttl_seconds": 25,
        "authentication": {"state": "EXPIRED", "lease_time_valid": False,
                           "effective_shadow": False, "enforcement": False},
        "audit": {"valid": True, "count": 5, "attested": False},
        "egress_v15": {
            "authorization_basis": "BLUETOOTH_PRESENCE_NOT_CRYPTOGRAPHIC_LEASE",
            "output_rule": "ACCEPT_RULE_PRESENT", "service_active": True,
        },
    }


class CoreTests(unittest.TestCase):
    def test_fresh(self):
        now = datetime.fromisoformat("2026-10-31T13:57:24+00:00")
        self.assertTrue(core.telemetry_fresh(example(), now))

    def test_expired(self):
        now = datetime.fromisoformat("2026-10-31T13:57:26+00:00")
        self.assertFalse(core.telemetry_fresh(example(), now))

    def test_future_not_fresh(self):
        now = datetime.fromisoformat("2026-10-31T13:56:59+00:00")
        self.assertFalse(core.telemetry_fresh(example(), now))

    def test_naive_timestamp_not_fresh(self):
        payload = example()
        payload["published_utc"] = "2026-10-31T13:57:00"
        self.assertFalse(core.telemetry_fresh(payload))

    def test_shadow_and_legacy_gate_separated(self):
        result = core.lock_summary(example())
        self.assertEqual(result["authority"], "OBSERVATION_ONLY")
        self.assertEqual(result["facts"][0]["value"]["state"], "EXPIRED")
        self.assertIs(result["facts"][0]["value"]["enforcement"], False)
        self.assertEqual(result["facts"][2]["value"]["output_rule"], "ACCEPT_RULE_PRESENT")

    def test_citations_require_all_three(self):
        self.assertTrue(core.citation_check("L001 L002 L003")["passed"])
        self.assertFalse(core.citation_check("L001 L002")["passed"])
        self.assertFalse(core.citation_check("L001 L002 L003 L999")["passed"])
        self.assertFalse(core.citation_check("L001 L002 L003")["semantic_validation"])

    def test_model_url_allowlist(self):
        with patch.dict(os.environ, {"BCI_OLLAMA_URL": "http://example.org/api/chat"}):
            with self.assertRaises(ValueError):
                core.ollama_url()

    def test_rollback_model_url(self):
        with patch.dict(os.environ,
                        {"BCI_OLLAMA_URL": "http://127.0.0.1:11434/api/chat"}):
            self.assertIn(":11434/", core.ollama_url())

    def test_stale_analysis_refused_before_network(self):
        with self.assertRaisesRegex(ValueError, "stale"):
            core.ask_about_lock("Review L001", example())


if __name__ == "__main__":
    unittest.main()
