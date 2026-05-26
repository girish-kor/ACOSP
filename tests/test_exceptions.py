"""
tests/test_exceptions.py — Exception & Retry Decorator Tests
=============================================================
Tests for exception hierarchy and retry logic.
"""

import asyncio
import time

import pytest

from src.exceptions import (
    ExecutionError,
    async_retry_with_backoff,
    retry_with_backoff,
)


class TestRetryDecorator:
    """Tests for retry_with_backoff decorator."""

    def test_success_first_try(self):
        """Test immediate success (no retries)."""
        call_count = 0

        @retry_with_backoff(max_attempts=3, initial_delay=0.01)
        def success_fn():
            nonlocal call_count
            call_count += 1
            return "success"

        result = success_fn()
        assert result == "success"
        assert call_count == 1

    def test_retry_with_eventual_success(self):
        """Test retry with eventual success."""
        call_count = 0

        @retry_with_backoff(max_attempts=3, initial_delay=0.01, jitter=False)
        def flaky_fn():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Network error")
            return "success"

        result = flaky_fn()
        assert result == "success"
        assert call_count == 3

    def test_max_attempts_exceeded(self):
        """Test max attempts exhaustion."""

        @retry_with_backoff(max_attempts=2, initial_delay=0.01)
        def always_fail():
            raise ConnectionError("Network error")

        with pytest.raises(ConnectionError):
            always_fail()

    def test_non_retryable_exception(self):
        """Test non-retryable exception."""

        @retry_with_backoff(
            max_attempts=3,
            retryable_exceptions=(ConnectionError,),
        )
        def non_retryable():
            raise ValueError("Invalid value")

        with pytest.raises(ValueError):
            non_retryable()


class TestAsyncRetryDecorator:
    """Tests for async_retry_with_backoff decorator."""

    @pytest.mark.asyncio
    async def test_async_success_first_try(self):
        """Test async immediate success."""
        call_count = 0

        @async_retry_with_backoff(max_attempts=3, initial_delay=0.01)
        async def async_success():
            nonlocal call_count
            call_count += 1
            return "success"

        result = await async_success()
        assert result == "success"
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_async_retry_eventual_success(self):
        """Test async retry with eventual success."""
        call_count = 0

        @async_retry_with_backoff(max_attempts=3, initial_delay=0.01, jitter=False)
        async def async_flaky():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise TimeoutError("Timeout")
            return "success"

        result = await async_flaky()
        assert result == "success"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_async_max_attempts_exceeded(self):
        """Test async max attempts exhaustion."""

        @async_retry_with_backoff(max_attempts=2, initial_delay=0.01)
        async def async_fail():
            raise TimeoutError("Timeout")

        with pytest.raises(TimeoutError):
            await async_fail()


class TestExecutionError:
    """Tests for ACOSPException hierarchy."""

    def test_execution_error_with_context(self):
        """Test exception with context."""
        error = ExecutionError(
            "Tool execution failed",
            context={"tool": "nmap", "target": "192.168.1.0/24"},
        )
        assert error.message == "Tool execution failed"
        assert error.context["tool"] == "nmap"
