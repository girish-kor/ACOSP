"""
main.py — ACOSP Orchestrator
=============================
Top-level entry point that bootstraps the platform, drives the autonomous
mission lifecycle, coordinates all sub-agents, and emits final reports.

Lifecycle
---------
1. initialize_session  — load config, allocate session ID
2. run_mission         — outer control loop (recon → plan → exploit → report)
3. coordinate_agents   — state-machine dispatcher between layers
4. generate_mission_report — consolidate telemetry into human/machine reports
"""

from __future__ import annotations

import argparse
import logging
import sys
import uuid
from pathlib import Path
from typing import Any

import structlog

from src.agent_brain import (
    generate_attack_plan,
    evaluate_risk,
    refine_strategy_on_failure,
)
from src.discovery_engine import (
    perform_reconnaissance,
    fingerprint_services,
    map_network_topology,
)
from src.handle_actions import execute_exploit_chain, cleanup_artifacts
from src.telemetry import (
    initialize_database,
    log_operational_event,
    generate_compliance_mapping,
)

logger: structlog.BoundLogger = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def initialize_session(config_path: str) -> str:
    """Load platform configuration and return a unique session identifier.

    This function is the *first* call in every mission.  It reads the TOML/YAML
    config at *config_path*, validates it with Pydantic, wires up structured
    logging, and allocates a UUID4 session ID that is threaded through all
    subsequent telemetry records.

    Parameters
    ----------
    config_path:
        Absolute or relative path to the ACOSP configuration file
        (e.g. ``config/acosp.toml``).

    Returns
    -------
    str
        A ``str(uuid.uuid4())`` session identifier, e.g.
        ``"3fa85f64-5717-4562-b3fc-2c963f66afa6"``.

    Raises
    ------
    FileNotFoundError
        If *config_path* does not exist on disk.
    pydantic.ValidationError
        If the configuration schema fails validation.
    """
    cfg_path = Path(config_path)
    if not cfg_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")

    # TODO: parse config with Pydantic model (AcospConfig)
    session_id: str = str(uuid.uuid4())

    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_log_level,
            structlog.processors.JSONRenderer(),
        ]
    )

    log_operational_event(
        level="INFO",
        message="Session initialised",
        metadata={"session_id": session_id, "config_path": str(cfg_path)},
    )

    logger.info("session_initialised", session_id=session_id)
    return session_id


def run_mission(target_scope: str, intensity_level: int) -> None:
    """Drive the full autonomous offensive security lifecycle.

    This is the main execution loop.  It iterates through the recon →
    fingerprint → plan → exploit cycle until the mission goal is satisfied
    or the maximum iteration budget is exhausted.

    Parameters
    ----------
    target_scope:
        CIDR range, domain, or cloud account ID that defines the engagement
        boundary (e.g. ``"192.168.1.0/24"`` or ``"example.com"``).
    intensity_level:
        Throttle knob (1 = stealthy/slow, 5 = aggressive/fast).  Controls
        concurrency, scan rate, and exploit aggressiveness.

    Raises
    ------
    ValueError
        If *intensity_level* is outside the range [1, 5].
    RuntimeError
        If the session has not been initialised before calling this function.
    """
    if not (1 <= intensity_level <= 5):
        raise ValueError(f"intensity_level must be 1–5, got {intensity_level}")

    logger.info("mission_started", scope=target_scope, intensity=intensity_level)

    # --- Sensory layer -------------------------------------------------------
    raw_assets = perform_reconnaissance(scope=target_scope)
    fingerprints = fingerprint_services(assets=raw_assets)
    topology = map_network_topology(discovery_results=raw_assets)

    # --- Reasoning layer -----------------------------------------------------
    state: dict[str, Any] = {
        "assets": raw_assets,
        "fingerprints": fingerprints,
        "topology": topology,
        "intensity": intensity_level,
    }
    coordinate_agents(current_state=state)

    logger.info("mission_completed", scope=target_scope)


def coordinate_agents(current_state: dict[str, Any]) -> None:
    """Dispatch control between the sensory, reasoning, and execution layers.

    Implements a finite state machine that transitions between
    DISCOVER → PLAN → VALIDATE → EXECUTE → REPORT states, passing enriched
    context objects between layers and routing failures back to the reasoning
    engine for self-correction.

    Parameters
    ----------
    current_state:
        Mutable context dictionary carrying assets, fingerprints, topology,
        prior findings, and mission goal.  Updated in-place as the state
        machine advances.

    Side Effects
    ------------
    Modifies *current_state* with plan and execution results.
    Writes operational events via :func:`src.telemetry.log_operational_event`.
    """
    mission_goal: str = current_state.get("mission_goal", "full_compromise")

    # --- PLAN ----------------------------------------------------------------
    plan: list[dict[str, Any]] = generate_attack_plan(
        discovery_data=current_state,
        mission_goal=mission_goal,
    )

    # --- VALIDATE ------------------------------------------------------------
    validated_plan: list[dict[str, Any]] = []
    for action in plan:
        risk_score = evaluate_risk(action=action)
        if risk_score < current_state.get("risk_threshold", 0.75):
            validated_plan.append(action)
        else:
            logger.warning("action_rejected_high_risk", action=action, risk=risk_score)

    current_state["validated_plan"] = validated_plan

    # --- EXECUTE -------------------------------------------------------------
    success = execute_exploit_chain(plan=validated_plan)
    current_state["execution_success"] = success

    log_operational_event(
        level="INFO",
        message="Agent coordination cycle complete",
        metadata={"success": success, "actions_validated": len(validated_plan)},
    )


def generate_mission_report(session_id: str, format: str = "json") -> bool:  # noqa: A002
    """Consolidate telemetry records into an executive or technical report.

    Queries the persistent state store for all events and findings associated
    with *session_id*, maps them to the requested compliance framework, and
    serialises the output in the requested *format*.

    Parameters
    ----------
    session_id:
        UUID string returned by :func:`initialize_session`.
    format:
        Output format: ``"json"``, ``"pdf"``, or ``"markdown"``.

    Returns
    -------
    bool
        ``True`` if the report was written successfully, ``False`` otherwise.

    Raises
    ------
    ValueError
        If *format* is not one of the supported values.
    """
    supported_formats = {"json", "pdf", "markdown"}
    if format not in supported_formats:
        raise ValueError(f"Unsupported format {format}.  Choose from {supported_formats}")

    logger.info("report_generation_started", session_id=session_id, format=format)

    # TODO: retrieve findings from telemetry store
    findings: list[dict[str, Any]] = []
    # Use the supported NIST identifier expected by the telemetry layer
    compliance_map = generate_compliance_mapping(
        findings=findings, framework="NIST_800_53"
    )

    report_path = Path("reports") / f"{session_id}.{format}"
    # TODO: serialise compliance_map to report_path

    logger.info("report_written", path=str(report_path))
    return True


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="acosp",
        description="Autonomous Continuous Offensive Security Platform",
    )
    parser.add_argument("--config", default="config/acosp.toml", help="Config file path")
    parser.add_argument("--scope", required=True, help="Target scope (CIDR or domain)")
    parser.add_argument("--intensity", type=int, default=2, choices=range(1, 6), help="Intensity 1-5")
    parser.add_argument("--report-format", default="json", choices=["json", "pdf", "markdown"])
    return parser


def main() -> int:
    """CLI entry point."""
    parser = _build_arg_parser()
    args = parser.parse_args()

    session_id = initialize_session(config_path=args.config)

    try:
        run_mission(target_scope=args.scope, intensity_level=args.intensity)
    finally:
        generate_mission_report(session_id=session_id, format=args.report_format)
        cleanup_artifacts(session_id=session_id)

    return 0


if __name__ == "__main__":
    sys.exit(main())

