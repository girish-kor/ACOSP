"""
tests/test_core.py — ACOSP Core Unit Test Suite
================================================
Unit test stubs for the reasoning engine and sensory layer.  Each test
class follows the Arrange / Act / Assert pattern and is designed to be
extended as implementation matures.

Run with:
    python -m pytest tests/ -v
"""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch
from typing import Any


# ---------------------------------------------------------------------------
# Reasoning Engine Tests
# ---------------------------------------------------------------------------


class TestGenerateAttackPlan(unittest.TestCase):
    """Unit tests for :func:`src.agent_brain.generate_attack_plan`."""

    def setUp(self) -> None:
        self.discovery_data: dict[str, Any] = {
            "assets": [{"ip": "10.0.0.1", "open_ports": [22, 80, 443]}],
            "fingerprints": {"10.0.0.1": {"os": "Linux 5.x", "services": []}},
            "topology": MagicMock(),
        }
        self.mission_goal = "full_compromise"

    def test_returns_list(self) -> None:
        """generate_attack_plan must always return a list."""
        from src.agent_brain import generate_attack_plan

        result = generate_attack_plan(
            discovery_data=self.discovery_data,
            mission_goal=self.mission_goal,
        )
        self.assertIsInstance(result, list)

    def test_raises_on_missing_assets_key(self) -> None:
        """Should raise ValueError when discovery_data lacks assets key."""
        from src.agent_brain import generate_attack_plan

        with self.assertRaises(ValueError):
            generate_attack_plan(
                discovery_data={},
                mission_goal=self.mission_goal,
            )

    def test_each_action_is_dict(self) -> None:
        """Every element of the returned plan must be a dict."""
        from src.agent_brain import generate_attack_plan

        plan = generate_attack_plan(
            discovery_data=self.discovery_data,
            mission_goal=self.mission_goal,
        )
        for action in plan:
            self.assertIsInstance(action, dict)


class TestEvaluateRisk(unittest.TestCase):
    """Unit tests for :func:`src.agent_brain.evaluate_risk`."""

    def test_score_within_bounds(self) -> None:
        """Risk score must be normalised to [0.0, 1.0]."""
        from src.agent_brain import evaluate_risk

        action = {"technique_id": "T1059.001", "tool": "metasploit"}
        score = evaluate_risk(action=action)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_returns_float(self) -> None:
        """evaluate_risk must return a float."""
        from src.agent_brain import evaluate_risk

        score = evaluate_risk(action={"technique_id": "T1078"})
        self.assertIsInstance(score, float)


class TestCalculateStealthScore(unittest.TestCase):
    """Unit tests for :func:`src.agent_brain.calculate_stealth_score`."""

    def test_empty_path_returns_max_stealth(self) -> None:
        """An empty exploit chain should return 1.0 (fully stealthy)."""
        from src.agent_brain import calculate_stealth_score

        self.assertEqual(calculate_stealth_score(path=[]), 1.0)

    def test_score_within_bounds(self) -> None:
        """Stealth score must be normalised to [0.0, 1.0]."""
        from src.agent_brain import calculate_stealth_score

        path = [
            {"technique_id": "T1595", "tool": "nmap"},
            {"technique_id": "T1059.001", "tool": "metasploit"},
        ]
        score = calculate_stealth_score(path=path)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)


# ---------------------------------------------------------------------------
# Sensory Layer Tests
# ---------------------------------------------------------------------------


class TestFingerprintServices(unittest.TestCase):
    """Unit tests for :func:`src.discovery_engine.fingerprint_services`."""

    def test_returns_dict_keyed_by_ip(self) -> None:
        """fingerprint_services must return a dict keyed by IP address."""
        from src.discovery_engine import fingerprint_services

        assets = [{"ip": "192.168.1.1", "open_ports": [80, 443]}]
        result = fingerprint_services(assets=assets)
        self.assertIsInstance(result, dict)

    def test_empty_assets_returns_empty_dict(self) -> None:
        """An empty asset list should yield an empty fingerprint dict."""
        from src.discovery_engine import fingerprint_services

        result = fingerprint_services(assets=[])
        self.assertEqual(result, {})

    def test_fingerprint_has_expected_keys(self) -> None:
        """Each fingerprint entry must contain os, services, banners, cpe."""
        from src.discovery_engine import fingerprint_services

        assets = [{"ip": "10.0.0.2", "open_ports": [22]}]
        result = fingerprint_services(assets=assets)

        for _ip, fingerprint in result.items():
            for key in ("os", "services", "banners", "cpe"):
                self.assertIn(key, fingerprint)


class TestQueryVulnerabilityDatabases(unittest.TestCase):
    """Unit tests for :func:`src.discovery_engine.query_vulnerability_databases`."""

    def test_returns_list(self) -> None:
        """query_vulnerability_databases must return a list."""
        from src.discovery_engine import query_vulnerability_databases

        result = query_vulnerability_databases(service_info={"cpe": []})
        self.assertIsInstance(result, list)

    def test_empty_cpe_returns_empty_list(self) -> None:
        """No CPE strings should yield no vulnerabilities."""
        from src.discovery_engine import query_vulnerability_databases

        result = query_vulnerability_databases(service_info={"cpe": []})
        self.assertEqual(result, [])


class TestPerformReconnaissance(unittest.TestCase):
    """Unit tests for :func:`src.discovery_engine.perform_reconnaissance`."""

    def test_returns_list(self) -> None:
        """perform_reconnaissance must return a list."""
        from src.discovery_engine import perform_reconnaissance

        result = perform_reconnaissance(scope="127.0.0.1/32")
        self.assertIsInstance(result, list)


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()

