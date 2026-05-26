"""
tests/conftest.py — Pytest Configuration & Fixtures
====================================================
Global fixtures and configuration for the ACOSP test suite.
"""

import pytest


@pytest.fixture
def sample_discovery_result():
    """Fixture: sample discovery result."""
    return [
        {
            "ip": "192.168.1.100",
            "hostname": "web-server",
            "open_ports": [22, 80, 443],
            "os_guess": "Linux",
        },
        {
            "ip": "192.168.1.101",
            "hostname": "db-server",
            "open_ports": [5432, 22],
            "os_guess": "PostgreSQL",
        },
    ]


@pytest.fixture
def sample_attack_plan():
    """Fixture: sample attack plan."""
    return [
        {
            "technique_id": "T1566.001",
            "tool": "nmap",
            "arguments": {"target": "192.168.1.0/24", "flags": ["-sV"]},
            "priority": 1,
            "risk_score": 0.3,
        },
        {
            "technique_id": "T1595.002",
            "tool": "metasploit",
            "arguments": {"module": "exploit/multi/handler"},
            "priority": 2,
            "risk_score": 0.6,
        },
    ]


@pytest.fixture
def sample_vulnerability():
    """Fixture: sample vulnerability."""
    return {
        "cve_id": "CVE-2024-1234",
        "title": "Remote Code Execution in OpenSSH",
        "severity": "CRITICAL",
        "cvss_score": 9.8,
        "epss_score": 0.97,
        "kev": True,
        "exploit_available": True,
    }


@pytest.fixture
def mock_session_id():
    """Fixture: mock session ID."""
    return "test-session-abc-123-def-456"


@pytest.fixture
def mock_trace_id():
    """Fixture: mock trace ID."""
    return "trace-xyz-789-uvw"
