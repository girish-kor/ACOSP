"""
src/observability.py — ACOSP Structured Observability
======================================================
Centralized structlog configuration with ELK/Splunk-compatible JSON output,
unique trace IDs per mission, and context propagation.
"""

from __future__ import annotations

import contextvars
import json
import logging
import sys
import uuid
from datetime import datetime
from typing import Any

import structlog

# Context variable for trace ID propagation across async tasks
_trace_id_ctx: contextvars.ContextVar[str] = contextvars.ContextVar(
    "trace_id", default=""
)


def get_trace_id() -> str:
    """
    Retrieve or generate the current trace ID.

    Returns
    -------
    str
        Current trace ID or a newly generated UUID4.
    """
    current = _trace_id_ctx.get()
    if current:
        return current

    new_id = str(uuid.uuid4())
    _trace_id_ctx.set(new_id)
    return new_id


def set_trace_id(trace_id: str) -> None:
    """
    Set the trace ID for the current context.

    Parameters
    ----------
    trace_id : str
        Trace ID to set.
    """
    _trace_id_ctx.set(trace_id)


def generate_trace_id() -> str:
    """Generate a new trace ID and set it in context."""
    new_id = str(uuid.uuid4())
    _trace_id_ctx.set(new_id)
    return new_id


class TraceIDProcessor:
    """structlog processor that injects trace ID into every log record."""

    def __call__(
        self, logger: Any, method_name: str, event_dict: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Add trace_id to the event dictionary.

        Parameters
        ----------
        logger : Any
            Logger instance.
        method_name : str
            Name of the method called on the logger.
        event_dict : dict[str, Any]
            Event dictionary.

        Returns
        -------
        dict[str, Any]
            Updated event dictionary.
        """
        event_dict["trace_id"] = get_trace_id()
        return event_dict


class TimestampProcessor:
    """structlog processor that injects ISO 8601 timestamp."""

    def __call__(
        self, logger: Any, method_name: str, event_dict: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Add timestamp to the event dictionary.

        Parameters
        ----------
        logger : Any
            Logger instance.
        method_name : str
            Name of the method called on the logger.
        event_dict : dict[str, Any]
            Event dictionary.

        Returns
        -------
        dict[str, Any]
            Updated event dictionary.
        """
        event_dict["timestamp"] = datetime.utcnow().isoformat() + "Z"
        return event_dict


def configure_logging(log_level: str = "INFO", log_format: str = "json") -> None:
    """
    Configure structlog and stdlib logging for ACOSP.

    Parameters
    ----------
    log_level : str
        Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
    log_format : str
        Output format ('json' or 'console').
    """
    # Configure stdlib logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper(), logging.INFO),
    )

    # Determine processors based on format
    if log_format == "json":
        processors = [
            structlog.contextvars.merge_contextvars,
            TimestampProcessor(),
            TraceIDProcessor(),
            structlog.stdlib.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ]
    else:
        processors = [
            structlog.contextvars.merge_contextvars,
            TimestampProcessor(),
            TraceIDProcessor(),
            structlog.stdlib.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.dev.ConsoleRenderer(),
        ]

    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


class ObservabilityContext:
    """Context manager for trace ID and structured logging context."""

    def __init__(self, session_id: str, **context_data: Any):
        """
        Initialize observability context.

        Parameters
        ----------
        session_id : str
            Session identifier.
        **context_data : Any
            Additional context key/value pairs.
        """
        self.session_id = session_id
        self.trace_id = generate_trace_id()
        self.context_data = context_data
        self.token = None

    def __enter__(self) -> ObservabilityContext:
        """Enter context, setting trace ID and session context."""
        set_trace_id(self.trace_id)
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            session_id=self.session_id, trace_id=self.trace_id, **self.context_data
        )
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context, clearing context variables."""
        structlog.contextvars.clear_contextvars()
        _trace_id_ctx.set("")


async def async_observe_mission(
    session_id: str, mission_goal: str
) -> ObservabilityContext:
    """
    Create an async-compatible observability context for a mission.

    Parameters
    ----------
    session_id : str
        Session identifier.
    mission_goal : str
        Mission goal/objective.

    Returns
    -------
    ObservabilityContext
        Context manager.
    """
    return ObservabilityContext(
        session_id=session_id,
        mission_goal=mission_goal,
        mission_started_at=datetime.utcnow().isoformat(),
    )


def serialize_event_to_json(
    event_type: str, data: dict[str, Any], exception: Exception | None = None
) -> str:
    """
    Serialize an event to JSON for telemetry storage.

    Parameters
    ----------
    event_type : str
        Type of event (e.g., 'discovery', 'execution', 'finding').
    data : dict[str, Any]
        Event data.
    exception : Exception | None
        Optional exception object.

    Returns
    -------
    str
        JSON-serialized event.
    """
    payload = {
        "event_type": event_type,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "trace_id": get_trace_id(),
        "data": data,
    }

    if exception:
        payload["exception"] = {
            "type": type(exception).__name__,
            "message": str(exception),
        }

    return json.dumps(payload)
