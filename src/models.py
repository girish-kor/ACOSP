"""
src/models.py — ACOSP Pydantic V2 Data Models
==============================================
Type-safe data structures with runtime validation for all internal
data flows, discovery results, attack plans, telemetry events, and
compliance artifacts.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


class ComplianceFramework(str, Enum):
    """Supported compliance framework identifiers."""

    SOC2 = "SOC2"
    ISO27001 = "ISO27001"
    NIST_CSF = "NIST_CSF"
    NIST_800_53 = "NIST_800_53"
    PCI_DSS = "PCI_DSS"


class SeverityLevel(str, Enum):
    """Standard severity classification."""

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class DiscoveryModel(BaseModel):
    """Discovered asset representation."""

    ip: str
    hostname: Optional[str] = None
    open_ports: list[int] = Field(default_factory=list)
    os_guess: Optional[str] = None
    mac_address: Optional[str] = None
    tags: list[str] = Field(default_factory=list)

    @field_validator("ip")
    @classmethod
    def validate_ip(cls, v: str) -> str:
        """Basic IP validation."""
        if not v or not any(c.isdigit() for c in v):
            raise ValueError(f"Invalid IP: {v}")
        return v


class ServiceFingerprint(BaseModel):
    """Service-level fingerprinting data."""

    port: int
    protocol: str
    service_name: Optional[str] = None
    product: Optional[str] = None
    version: Optional[str] = None
    cpe: list[str] = Field(default_factory=list)
    banners: dict[str, str] = Field(default_factory=dict)


class AssetFingerprint(BaseModel):
    """Complete fingerprint for a discovered asset."""

    ip: str
    os: Optional[str] = None
    os_family: Optional[str] = None
    os_version: Optional[str] = None
    services: list[ServiceFingerprint] = Field(default_factory=list)
    tls_certs: dict[int, str] = Field(default_factory=dict)


class VulnerabilityData(BaseModel):
    """CVE/vulnerability record."""

    cve_id: Optional[str] = None
    cwe_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    severity: SeverityLevel
    cvss_score: Optional[float] = Field(None, ge=0.0, le=10.0)
    epss_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    cpe: list[str] = Field(default_factory=list)
    kev: bool = False
    exploit_available: bool = False


class AttackAction(BaseModel):
    """Single attack action within a plan."""

    technique_id: str
    tool: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    priority: int = 0
    risk_score: float = Field(default=0.0, ge=0.0, le=1.0)
    stealth_score: float = Field(default=1.0, ge=0.0, le=1.0)
    estimated_impact: str = "unknown"


class AttackPlanSchema(BaseModel):
    """Validated attack plan."""

    session_id: str
    mission_goal: str
    target_scope: str
    actions: list[AttackAction] = Field(default_factory=list)
    validated: bool = False
    risk_threshold: float = Field(default=0.75, ge=0.0, le=1.0)


class TelemetryEvent(BaseModel):
    """Structured operational event."""

    timestamp: str  # ISO 8601
    session_id: str
    trace_id: str
    level: str
    message: str
    context: dict[str, Any] = Field(default_factory=dict)
    exception: Optional[dict[str, str]] = None


class FindingRecord(BaseModel):
    """Vulnerability finding with evidence."""

    session_id: str
    trace_id: str
    target_ip: str
    target_port: Optional[int] = None
    cve_id: Optional[str] = None
    title: str
    severity: SeverityLevel
    cvss_score: Optional[float] = Field(None, ge=0.0, le=10.0)
    evidence: str
    remediation: Optional[str] = None
    timestamp: str  # ISO 8601


class ComplianceControl(BaseModel):
    """Compliance control mapping."""

    control_id: str
    control_name: str
    status: str
    related_findings: list[str] = Field(default_factory=list)
    gap_description: Optional[str] = None


class ComplianceReport(BaseModel):
    """Full compliance mapping."""

    framework: ComplianceFramework
    timestamp: str  # ISO 8601
    controls: dict[str, ComplianceControl] = Field(default_factory=dict)
    gap_count: int = 0
    finding_count: int = 0


class MissionMetrics(BaseModel):
    """Real-time mission statistics."""

    timestamp: str  # ISO 8601
    session_id: str
    active_sessions: int = 0
    events_per_minute: float = 0.0
    open_findings: int = 0
    critical_findings: int = 0
    actions_dispatched: int = 0
    detection_events: int = 0
