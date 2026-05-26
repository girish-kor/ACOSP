"""
src/exceptions.py — ACOSP Exception Hierarchy
==============================================
Centralized exception types with context preservation and retry semantics.
"""

from __future__ import annotations

import functools
import random
import time
from typing import Any, Callable, TypeVar

import structlog

logger: structlog.BoundLogger = structlog.get_logger(__name__)

T = TypeVar("T")


class ACOSPException(Exception):
    """Base exception for all ACOSP errors."""

    def __init__(self, message: str, context: dict[str, Any] | None = None):
        """
        Parameters
        ----------
        message : str
            Human-readable error message.
        context : dict[str, Any] | None
            Optional contextual metadata.
        """
        super().__init__(message)
        self.message = message
        self.context = context or {}


class ConfigurationError(ACOSPException):
    """Configuration loading or validation failed."""

    pass


class DiscoveryError(ACOSPException):
    """Asset discovery operation failed."""

    pass


class FingerprintingError(ACOSPException):
    """Service fingerprinting operation failed."""

    pass


class PlanningError(ACOSPException):
    """Attack plan generation failed."""

    pass


class ValidationError(ACOSPException):
    """Risk validation or plan validation failed."""

    pass


class ExecutionError(ACOSPException):
    """Exploit execution failed."""

    pass


class ToolDispatchError(ACOSPException):
    """External tool execution failed."""

    pass


class TelemetryError(ACOSPException):
    """Telemetry operation failed."""

    pass


class DatabaseError(ACOSPException):
    """Database operation failed."""

    pass


def retry_with_backoff(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: tuple[type[Exception], ...] = (
        TimeoutError,
        ConnectionError,
        IOError,
    ),
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator implementing exponential backoff with jitter for network-bound tasks.

    Parameters
    ----------
    max_attempts : int
        Maximum number of retry attempts (default 3).
    initial_delay : float
        Initial delay in seconds (default 1.0).
    max_delay : float
        Maximum delay in seconds (default 60.0).
    backoff_factor : float
        Exponential backoff multiplier (default 2.0).
    jitter : bool
        If True, add random jitter to delay (default True).
    retryable_exceptions : tuple[type[Exception], ...]
        Exception types to catch and retry on.

    Returns
    -------
    Callable
        Decorated function with retry logic.

    Example
    -------
    >>> @retry_with_backoff(max_attempts=5, initial_delay=0.5)
    ... def network_call():
    ...     ...
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            attempt = 0
            current_delay = initial_delay

            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except retryable_exceptions as exc:
                    attempt += 1
                    if attempt >= max_attempts:
                        logger.error(
                            "retry_exhausted",
                            func=func.__name__,
                            attempts=attempt,
                            error=str(exc),
                        )
                        raise

                    # Calculate delay with optional jitter
                    if jitter:
                        delay = min(current_delay * random.uniform(0.8, 1.2), max_delay)
                    else:
                        delay = min(current_delay, max_delay)

                    logger.warning(
                        "retrying_after_backoff",
                        func=func.__name__,
                        attempt=attempt,
                        delay_sec=delay,
                        error=str(exc),
                    )

                    time.sleep(delay)
                    current_delay *= backoff_factor

            # Unreachable, but satisfy type checker
            raise RuntimeError(f"Retry logic failed for {func.__name__}")

        return wrapper

    return decorator


def async_retry_with_backoff(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: tuple[type[Exception], ...] = (
        TimeoutError,
        ConnectionError,
        IOError,
    ),
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Async version of retry_with_backoff decorator.

    Parameters are identical to :func:`retry_with_backoff`.

    Example
    -------
    >>> @async_retry_with_backoff(max_attempts=5)
    ... async def async_network_call():
    ...     ...
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            import asyncio

            attempt = 0
            current_delay = initial_delay

            while attempt < max_attempts:
                try:
                    return await func(*args, **kwargs)
                except retryable_exceptions as exc:
                    attempt += 1
                    if attempt >= max_attempts:
                        logger.error(
                            "async_retry_exhausted",
                            func=func.__name__,
                            attempts=attempt,
                            error=str(exc),
                        )
                        raise

                    if jitter:
                        delay = min(current_delay * random.uniform(0.8, 1.2), max_delay)
                    else:
                        delay = min(current_delay, max_delay)

                    logger.warning(
                        "async_retrying_after_backoff",
                        func=func.__name__,
                        attempt=attempt,
                        delay_sec=delay,
                        error=str(exc),
                    )

                    await asyncio.sleep(delay)
                    current_delay *= backoff_factor

            raise RuntimeError(f"Async retry logic failed for {func.__name__}")

        return wrapper

    return decorator
