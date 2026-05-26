"""
tests/test_config.py — Configuration Management Tests
======================================================
Tests for environment-driven configuration with pydantic-settings.
"""

import pytest

from src.config import ACOSPConfig, DatabaseSettings, LLMSettings


class TestDatabaseSettings:
    """Tests for DatabaseSettings."""

    def test_default_database_settings(self):
        """Test default database configuration."""
        db = DatabaseSettings()
        assert db.host == "localhost"
        assert db.port == 5432
        assert db.user == "acosp"

    def test_connection_string_generation(self):
        """Test database connection string generation."""
        db = DatabaseSettings(
            host="db.example.com",
            user="admin",
            password="secret",
            database="production",
        )
        expected = "postgresql+psycopg2://admin:secret@db.example.com:5432/production"
        assert db.connection_string == expected

    def test_env_override(self, monkeypatch):
        """Test environment variable override."""
        monkeypatch.setenv("ACOSP_DB_HOST", "env-host")
        monkeypatch.setenv("ACOSP_DB_PORT", "5433")
        db = DatabaseSettings()
        assert db.host == "env-host"
        assert db.port == 5433


class TestLLMSettings:
    """Tests for LLMSettings."""

    def test_default_llm_settings(self):
        """Test default LLM configuration."""
        llm = LLMSettings()
        assert llm.provider == "anthropic"
        assert llm.temperature == 0.2

    def test_temperature_bounds(self):
        """Test temperature validation."""
        llm = LLMSettings(temperature=0.5)
        assert llm.temperature == 0.5

    def test_invalid_temperature(self):
        """Test temperature out of bounds."""
        with pytest.raises(ValueError):
            LLMSettings(temperature=3.0)  # Out of bounds


class TestACOSPConfig:
    """Tests for root ACOSPConfig."""

    def test_root_config_defaults(self):
        """Test root config with defaults."""
        config = ACOSPConfig()
        assert config.platform.name == "ACOSP"
        assert config.database.host == "localhost"
        assert config.llm.provider == "anthropic"

    def test_from_toml_not_found(self):
        """Test TOML loading with missing file."""
        with pytest.raises(FileNotFoundError):
            ACOSPConfig.from_toml("nonexistent.toml")

    def test_nested_access(self):
        """Test nested config access."""
        config = ACOSPConfig()
        assert config.mission.default_intensity == 2
        assert config.mission.risk_threshold == 0.75
