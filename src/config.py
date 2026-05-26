"""
src/config.py — ACOSP Configuration Management
===============================================
Environment-driven configuration with pydantic-settings, secure secret handling,
and runtime validation.
"""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings

from src.models import ComplianceFramework


class DatabaseSettings(BaseSettings):
    """Database connection configuration."""

    host: str = Field(default="localhost")
    port: int = Field(default=5432)
    user: str = Field(default="acosp")
    password: str = Field(default="changeme")
    database: str = Field(default="acosp")
    pool_size: int = Field(default=10)
    max_overflow: int = Field(default=20)

    class Config:
        env_prefix = "ACOSP_DB_"
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def connection_string(self) -> str:
        """Generate SQLAlchemy connection string."""
        return (
            f"postgresql+psycopg2://{self.user}:{self.password}@"
            f"{self.host}:{self.port}/{self.database}"
        )


class LLMSettings(BaseSettings):
    """LLM provider configuration."""

    provider: str = Field(default="anthropic")
    api_key: str = Field(default="")
    model: str = Field(default="claude-sonnet-4-20250514")
    temperature: float = Field(default=0.2, ge=0.0, le=2.0)
    max_tokens: int = Field(default=4096)

    class Config:
        env_prefix = "ACOSP_LLM_"
        env_file = ".env"
        env_file_encoding = "utf-8"


class ToolsSettings(BaseSettings):
    """External tools configuration."""

    nmap_binary: str = Field(default="nmap")
    nmap_timeout: int = Field(default=300)
    metasploit_host: str = Field(default="127.0.0.1")
    metasploit_port: int = Field(default=55553)
    metasploit_user: str = Field(default="")
    metasploit_password: str = Field(default="")
    custom_exploit_dir: str = Field(default="exploits/")

    class Config:
        env_prefix = "ACOSP_TOOLS_"
        env_file = ".env"
        env_file_encoding = "utf-8"


class MissionSettings(BaseSettings):
    """Mission configuration."""

    default_intensity: int = Field(default=2, ge=1, le=5)
    risk_threshold: float = Field(default=0.75, ge=0.0, le=1.0)
    max_iterations: int = Field(default=10, ge=1)
    strict_cleanup: bool = Field(default=True)

    class Config:
        env_prefix = "ACOSP_MISSION_"
        env_file = ".env"
        env_file_encoding = "utf-8"


class PlatformSettings(BaseSettings):
    """Platform-level configuration."""

    name: str = Field(default="ACOSP")
    version: str = Field(default="1.0.0")
    log_level: str = Field(default="INFO")
    log_format: str = Field(default="json")
    report_output_dir: str = Field(default="reports/")
    enable_trace_ids: bool = Field(default=True)

    class Config:
        env_prefix = "ACOSP_"
        env_file = ".env"
        env_file_encoding = "utf-8"


class ComplianceSettings(BaseSettings):
    """Compliance and audit configuration."""

    default_framework: ComplianceFramework = Field(default=ComplianceFramework.NIST_CSF)
    auto_report: bool = Field(default=True)
    report_formats: list[str] = Field(default_factory=lambda: ["json", "markdown"])

    class Config:
        env_prefix = "ACOSP_COMPLIANCE_"
        env_file = ".env"
        env_file_encoding = "utf-8"


class ACOSPConfig(BaseSettings):
    """Root configuration object — aggregates all subsystem configs."""

    platform: PlatformSettings = Field(default_factory=PlatformSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    llm: LLMSettings = Field(default_factory=LLMSettings)
    tools: ToolsSettings = Field(default_factory=ToolsSettings)
    mission: MissionSettings = Field(default_factory=MissionSettings)
    compliance: ComplianceSettings = Field(default_factory=ComplianceSettings)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @classmethod
    def from_toml(cls, config_path: str) -> ACOSPConfig:
        """
        Load configuration from a TOML file.

        Parameters
        ----------
        config_path : str
            Path to the TOML configuration file.

        Returns
        -------
        ACOSPConfig
            Merged configuration object.
        """
        import tomllib
        from pathlib import Path

        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_file, "rb") as f:
            toml_data = tomllib.load(f)

        # Extract subsections and merge with environment overrides
        platform_cfg = toml_data.get("platform", {})
        db_cfg = toml_data.get("database", {})
        llm_cfg = toml_data.get("llm", {})
        tools_cfg = toml_data.get("tools", {})
        mission_cfg = toml_data.get("mission", {})
        compliance_cfg = toml_data.get("compliance", {})

        return cls(
            platform=PlatformSettings(**platform_cfg),
            database=DatabaseSettings(**db_cfg),
            llm=LLMSettings(**llm_cfg),
            tools=ToolsSettings(**tools_cfg),
            mission=MissionSettings(**mission_cfg),
            compliance=ComplianceSettings(**compliance_cfg),
        )
