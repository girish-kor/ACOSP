"""
tests/test_models.py — Pydantic Model Validation Tests
=======================================================
Comprehensive validation suite for all data models.
"""

import pytest
from pydantic import ValidationError

from src.models import (
    AttackAction,
    ComplianceFramework,
    DiscoveryModel,
    FindingRecord,
    SeverityLevel,
    VulnerabilityData,
)


class TestDiscoveryModel:
    """Tests for DiscoveryModel."""

    def test_valid_discovery_model(self):
        """Test valid discovery model creation."""
        asset = DiscoveryModel(
            ip="192.168.1.1",
            hostname="test-host",
            open_ports=[22, 80, 443],
            os_guess="Linux",
        )
        assert asset.ip == "192.168.1.1"
        assert asset.hostname == "test-host"
        assert len(asset.open_ports) == 3

    def test_invalid_ip_address(self):
        """Test IP validation."""
        with pytest.raises(ValidationError):
            DiscoveryModel(ip="not-an-ip")

    def test_minimal_discovery_model(self):
        """Test minimal discovery model."""
        asset = DiscoveryModel(ip="10.0.0.1")
        assert asset.hostname is None
        assert asset.open_ports == []


class TestVulnerabilityData:
    """Tests for VulnerabilityData."""

    def test_valid_vulnerability(self):
        """Test valid vulnerability creation."""
        vuln = VulnerabilityData(
            cve_id="CVE-2024-1234",
            title="Remote Code Execution",
            severity=SeverityLevel.CRITICAL,
            cvss_score=9.8,
            epss_score=0.97,
        )
        assert vuln.cve_id == "CVE-2024-1234"
        assert vuln.cvss_score == 9.8

    def test_cvss_score_bounds(self):
        """Test CVSS score validation."""
        with pytest.raises(ValidationError):
            VulnerabilityData(
                title="Test",
                severity=SeverityLevel.HIGH,
                cvss_score=10.5,  # Out of bounds
            )

    def test_severity_levels(self):
        """Test all severity levels."""
        for severity in SeverityLevel:
            vuln = VulnerabilityData(
                title="Test",
                severity=severity,
            )
            assert vuln.severity == severity


class TestAttackAction:
    """Tests for AttackAction."""

    def test_valid_attack_action(self):
        """Test valid attack action."""
        action = AttackAction(
            technique_id="T1566.001",
            tool="nmap",
            arguments={"target": "10.0.0.0/8", "flags": ["-sV"]},
            priority=1,
            risk_score=0.5,
        )
        assert action.technique_id == "T1566.001"
        assert action.risk_score == 0.5

    def test_risk_score_bounds(self):
        """Test risk score validation."""
        with pytest.raises(ValidationError):
            AttackAction(
                technique_id="T1566",
                tool="nmap",
                risk_score=1.5,  # Out of bounds
            )


class TestFindingRecord:
    """Tests for FindingRecord."""

    def test_valid_finding(self):
        """Test valid finding record."""
        finding = FindingRecord(
            session_id="abc-123",
            trace_id="def-456",
            target_ip="192.168.1.100",
            target_port=3389,
            cve_id="CVE-2024-5678",
            title="Windows RDP Vulnerability",
            severity=SeverityLevel.CRITICAL,
            cvss_score=9.0,
            evidence="Scanned target with nmap -sV, confirmed RDP on port 3389",
            timestamp="2024-01-01T12:00:00Z",
        )
        assert finding.cve_id == "CVE-2024-5678"
        assert finding.target_port == 3389


class TestComplianceFramework:
    """Tests for ComplianceFramework enum."""

    def test_all_frameworks_present(self):
        """Test all compliance frameworks."""
        frameworks = {
            ComplianceFramework.SOC2,
            ComplianceFramework.ISO27001,
            ComplianceFramework.NIST_CSF,
            ComplianceFramework.NIST_800_53,
            ComplianceFramework.PCI_DSS,
        }
        assert len(frameworks) == 5
