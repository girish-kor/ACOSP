# ACOSP — Autonomous Continuous Offensive Security Platform

> **Warning:** This platform is intended for authorised penetration testing and
> red-team engagements only.  Unauthorised use is illegal and unethical.

## Architecture

```
ACOSP/
├── main.py                   # Orchestrator & CLI entry point
├── src/
│   ├── agent_brain.py        # LLM-backed reasoning engine
│   ├── discovery_engine.py   # Recon, fingerprinting & vuln lookup
│   ├── handle_actions.py     # Exploit execution & lateral movement
│   └── telemetry.py          # Logging, persistence & compliance
├── tests/
│   └── test_core.py          # Unit test suite
├── config/
│   └── acosp.toml            # Platform configuration
├── reports/                  # Generated mission reports
├── docs/                     # Architecture & API documentation
└── requirements.txt          # Python dependencies
```

## Quick Start

```bash
# 1. Create and activate a virtual environment
python -m venv .venv

# Git Bash on Windows
source .venv/Scripts/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure the platform
cp config/acosp.toml config/acosp.local.toml
# Edit config/acosp.local.toml with your database DSN and LLM credentials

# 4. Run a mission (authorised scope only!)
python main.py --config config/acosp.local.toml --scope 10.0.0.0/24 --intensity 2

# 5. Run tests
python -m pytest tests/ -v
```

## Python Version

Requires **Python >= 3.11**.

## Licence

Proprietary — for authorised use only.