"""
tests/test_async_orchestrator.py — Async Orchestrator Tests
============================================================
Tests for async mission coordination with mock sensory/execution layers.
"""

import pytest

from src.async_orchestrator import (
    coordinate_agents_async,
    generate_attack_plan_async,
    run_mission_async,
    validate_plan_async,
)
from src.config import ACOSPConfig


@pytest.mark.asyncio
async def test_run_mission_async_invalid_intensity():
    """Test mission validation."""
    config = ACOSPConfig()
    with pytest.raises(ValueError):
        await run_mission_async(
            session_id="test-123",
            target_scope="192.168.1.0/24",
            intensity_level=10,  # Invalid
            config=config,
        )


@pytest.mark.asyncio
async def test_generate_attack_plan_async(mocker):
    """Test attack plan generation (mocked)."""
    config = ACOSPConfig()
    discovery_data = {"assets": [], "topology": {}}
    plan = await generate_attack_plan_async(
        discovery_data=discovery_data,
        mission_goal="full_compromise",
        config=config,
    )
    assert isinstance(plan, list)


@pytest.mark.asyncio
async def test_validate_plan_async():
    """Test plan validation."""
    plan = [
        {
            "technique_id": "T1566.001",
            "tool": "nmap",
            "arguments": {},
        }
    ]
    validated = await validate_plan_async(
        plan=plan,
        risk_threshold=0.75,
        current_state={},
    )
    assert isinstance(validated, list)


@pytest.mark.asyncio
async def test_coordinate_agents_async(mocker):
    """Test agent coordination."""
    config = ACOSPConfig()
    state = {
        "session_id": "test-123",
        "trace_id": "trace-456",
        "assets": [],
        "fingerprints": {},
        "topology": {},
        "intensity": 2,
    }
    await coordinate_agents_async(current_state=state, config=config)
    assert "validated_plan" in state or "execution_success" in state
