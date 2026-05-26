#!/usr/bin/env python3
"""Run pytest with a cleaned environment to avoid leaking CI/local secrets into tests."""
import os
import sys
from pathlib import Path

# Prevent python-dotenv from loading any .env files
os.environ.setdefault("PYTHON_DOTENV_DISABLED", "1")

# If a .env file exists in the repo, temporarily rename it so pydantic doesn't load it.
env_path = Path(".env")
renamed = False
if env_path.exists():
    env_path.rename(".env.disabled_for_tests")
    renamed = True

# Common env var names that may interfere with Pydantic settings in tests
blocked_lower = {
    "github_token",
    "slack_webhook",
    "pypi_token",
    "helm_repo_url",
    "acosp_db_password",
    "github_pat",
}

# Remove both exact and case-insensitive variants
for k in list(os.environ.keys()):
    if k.lower() in blocked_lower:
        del os.environ[k]

import pytest

args = sys.argv[1:] or ["tests/", "-q", "--maxfail=1"]
try:
    raise SystemExit(pytest.main(args))
finally:
    # Restore the .env file if we renamed it
    if renamed:
        disabled = Path(".env.disabled_for_tests")
        if disabled.exists():
            disabled.rename(".env")
