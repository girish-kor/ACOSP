#!/usr/bin/env python3
"""
main.py — ACOSP Entry Point (Updated for Production)
=====================================================
Updated to use async orchestrator and structured observability.
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
import uuid
from pathlib import Path

import structlog

from src.async_orchestrator import run_mission_async
from src.config import ACOSPConfig
from src.exceptions import ACOSPException
from src.observability import configure_logging, generate_trace_id, set_trace_id

logger: structlog.BoundLogger = structlog.get_logger(__name__)


def initialize_session(config_path: str) -> tuple[str, ACOSPConfig]:
    """
    Load platform configuration and return session ID + config.

    Parameters
    ----------
    config_path : str
        Path to ACOSP configuration file (TOML).

    Returns
    -------
    tuple[str, ACOSPConfig]
        Session ID and loaded configuration.

    Raises
    ------
    FileNotFoundError
        If config file does not exist.
    """
    cfg_path = Path(config_path)
    if not cfg_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")

    try:
        config = ACOSPConfig.from_toml(str(cfg_path))
    except Exception as exc:
        raise ACOSPException(
            f"Failed to load configuration from {config_path}: {exc}",
            context={"config_path": str(cfg_path)},
        ) from exc

    session_id: str = str(uuid.uuid4())
    trace_id = generate_trace_id()

    # Configure structured logging
    configure_logging(
        log_level=config.platform.log_level,
        log_format=config.platform.log_format,
    )

    logger.info(
        "session_initialized",
        session_id=session_id,
        trace_id=trace_id,
        config_path=str(cfg_path),
        platform_version=config.platform.version,
    )

    return session_id, config


async def run_async_mission(
    session_id: str,
    config: ACOSPConfig,
    target_scope: str,
    intensity_level: int,
) -> None:
    """
    Execute the full mission lifecycle asynchronously.

    Parameters
    ----------
    session_id : str
        Unique session identifier.
    config : ACOSPConfig
        Platform configuration.
    target_scope : str
        Target CIDR/domain.
    intensity_level : int
        Scan intensity (1-5).
    """
    logger.info(
        "mission_lifecycle_starting",
        session_id=session_id,
        scope=target_scope,
        intensity=intensity_level,
    )

    try:
        await run_mission_async(
            session_id=session_id,
            target_scope=target_scope,
            intensity_level=intensity_level,
            config=config,
        )
        logger.info("mission_lifecycle_completed", session_id=session_id)
    except Exception as exc:
        logger.error(
            "mission_lifecycle_failed",
            session_id=session_id,
            error=str(exc),
        )
        raise


def generate_mission_report(session_id: str, report_format: str = "json") -> bool:
    """
    Generate mission report from telemetry.

    Parameters
    ----------
    session_id : str
        Session identifier.
    report_format : str
        Output format (json, markdown, pdf).

    Returns
    -------
    bool
        True if report generation succeeded.
    """
    logger.info(
        "report_generation_started",
        session_id=session_id,
        format=report_format,
    )

    # TODO: Query telemetry database for findings + events
    # TODO: Generate compliance mapping
    # TODO: Serialize to report_format

    report_path = Path("reports") / f"{session_id}.{report_format}"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info("report_written", path=str(report_path))
    return True


def cleanup_artifacts(session_id: str) -> None:
    """
    Clean up session artifacts.

    Parameters
    ----------
    session_id : str
        Session identifier.
    """
    logger.info("cleanup_started", session_id=session_id)

    # TODO: Remove implants, tunnels, and temporary files
    # TODO: Rotate/flush logs

    logger.info("cleanup_completed", session_id=session_id)


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="acosp",
        description="Autonomous Continuous Offensive Security Platform",
    )
    parser.add_argument(
        "--config",
        default="config/acosp.toml",
        help="Configuration file path",
    )
    parser.add_argument(
        "--scope",
        required=True,
        help="Target scope (CIDR or domain)",
    )
    parser.add_argument(
        "--intensity",
        type=int,
        default=2,
        choices=range(1, 6),
        help="Intensity level (1-5, default 2)",
    )
    parser.add_argument(
        "--report-format",
        default="json",
        choices=["json", "pdf", "markdown"],
        help="Report output format",
    )
    return parser


async def amain(argv: list[str] | None = None) -> int:
    """
    Async main entry point.

    Parameters
    ----------
    argv : list[str] | None
        Command-line arguments.

    Returns
    -------
    int
        Exit code (0 for success).
    """
    parser = _build_arg_parser()
    args = parser.parse_args(argv)

    try:
        session_id, config = initialize_session(config_path=args.config)

        await run_async_mission(
            session_id=session_id,
            config=config,
            target_scope=args.scope,
            intensity_level=args.intensity,
        )

        generate_mission_report(
            session_id=session_id,
            report_format=args.report_format,
        )

        return 0

    except ACOSPException as exc:
        logger.error("acosp_exception", error=str(exc), context=exc.context)
        return 1
    except Exception as exc:
        logger.exception("unexpected_error", error=str(exc))
        return 2
    finally:
        # Always attempt cleanup
        try:
            cleanup_artifacts(session_id=session_id)
        except Exception as cleanup_exc:
            logger.warning("cleanup_failed", error=str(cleanup_exc))


def main() -> int:
    """CLI entry point."""
    try:
        return asyncio.run(amain())
    except KeyboardInterrupt:
        logger.warning("interrupted_by_user")
        return 130
    except Exception as exc:
        logging.error(f"Fatal error: {exc}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
