#!/usr/bin/env python3
"""Run main.py with local .env temporarily disabled to avoid loading workspace secrets."""
import os
import sys
from pathlib import Path

os.environ.setdefault("PYTHON_DOTENV_DISABLED", "1")

env_path = Path(".env")
renamed = False
if env_path.exists():
    env_path.rename(".env.disabled_for_run")
    renamed = True

try:
    import subprocess

    cmd = [sys.executable, "main.py"] + sys.argv[1:]
    proc = subprocess.run(cmd)
    raise SystemExit(proc.returncode)
finally:
    if renamed:
        disabled = Path(".env.disabled_for_run")
        if disabled.exists():
            disabled.rename(".env")
