"""
src/__init__.py — ACOSP Package Initialization
===============================================
Exports public API and configures structured logging on import.
"""

from __future__ import annotations

__version__ = "1.0.0"
__author__ = "ACOSP Team"
__license__ = "Proprietary"

# Public API exports
from src.async_orchestrator import (
    coordinate_agents_async,
    generate_attack_plan_async,
    run_mission_async,
)
from src.config import ACOSPConfig
from src.exceptions import ACOSPError
from src.models import (
    AttackPlanSchema,
    ComplianceFramework,
    DiscoveryModel,
    FindingRecord,
    SeverityLevel,
    TelemetryEvent,
    VulnerabilityData,
)
from src.observability import (
    configure_logging,
    generate_trace_id,
    get_trace_id,
    set_trace_id,
)

__all__ = [
    "ACOSPConfig",
    "ACOSPError",
    "AttackPlanSchema",
    "ComplianceFramework",
    "DiscoveryModel",
    "FindingRecord",
    "SeverityLevel",
    "TelemetryEvent",
    "VulnerabilityData",
    "configure_logging",
    "coordinate_agents_async",
    "generate_attack_plan_async",
    "generate_trace_id",
    "get_trace_id",
    "run_mission_async",
    "set_trace_id",
]
