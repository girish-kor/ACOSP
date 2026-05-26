# ACOSP - Autonomous Continuous Offensive Security Platform

[![codecov](https://codecov.io/gh/girish-kor/acosp/branch/main/graph/badge.svg)](https://codecov.io/gh/girish-kor/acosp)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)

Enterprise-grade autonomous security testing platform with LLM-powered reasoning, async orchestration, structured observability, and production-hardened resilience.

**[Quick Start](#quick-start)** | **[Installation](#installation)** | **[Usage](#usage)** | **[Configuration](#configuration)** | **[Workflows](#-github-actions--cicd-commands)** | **[API](#-api-reference)** | **[Deploy](#-deployment)**

---

## 🎯 Overview

**Use Cases:** Continuous Security Testing | Compliance Automation | Threat Simulation | Risk Quantification | Detection Engineering | Security Research

**Key Features:**
- 🔍 **Autonomous Discovery** – Passive/active recon, asset inventory, network topology mapping
- 🧠 **LLM-Powered Planning** – Claude-3 based reasoning for attack plan generation
- ⚙️ **Async Orchestration** – Non-blocking concurrent execution with retry logic
- 📊 **Structured Observability** – JSON logs, trace IDs, ELK/Splunk compatible
- 🛡️ **Production Hardened** – Pydantic V2, MyPy strict, Bandit/CodeQL/Trivy scanned
- 📋 **Compliance Integration** – NIST/PCI-DSS/ISO27001/SOC2 mapping

---

## 🏗️ Architecture

### System Components (Layered)

```
┌───────────────────────────────────────────────────────────────────┐
│                       ACOSP Platform                              │
├───────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ LAYER 1: Orchestration                                       │ │
│  │ • Orchestrator (async_orchestrator.py)                       │ │
│  │ • Configuration Management (pydantic-settings)               │ │
│  └────────────────────┬─────────────────────────────────────────┘ │
│                       ↓                                           │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ LAYER 2: Agent Coordination                                  │ │
│  │ ├─ Sensory:    Discovery, Fingerprint, Enumerate             │ │
│  │ ├─ Reasoning:  LLM Planning (Claude), Risk Evaluation        │ │
│  │ └─ Execution:  Tool Dispatch, Payload Obfuscation            │ │
│  └────────────────────┬─────────────────────────────────────────┘ │
│                       ↓                                           │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ LAYER 3: Observability                                       │ │
│  │ • structlog JSON logging                                     │ │
│  │ • Trace ID propagation (contextvars)                         │ │
│  │ • Exception hierarchy + Metrics                              │ │
│  └────────────────────┬─────────────────────────────────────────┘ │
│                       ↓                                           │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ LAYER 4: Data Persistence                                    │ │
│  │ • PostgreSQL + TimescaleDB                                   │ │
│  │ • Session Management & Findings Storage                      │ │
│  │ • Compliance Mapping & Reporting                             │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

### Mission Execution Flow

```
  ┌────────────┐
  │   START:   │
  │ Init Phase │
  └─────┬──────┘
        ↓
  ┌──────────────────────────────────┐
  │ 1. RECONNAISSANCE (Async)        │
  │ • Passive DNS Enumeration        │
  │ • Active Port Scanning (Nmap)    │
  │ • Service Fingerprinting         │
  │ • Network Topology Mapping       │
  └─────┬────────────────────────────┘
        ↓
  ┌──────────────────────────────────┐
  │ 2. PLANNING (LLM Reasoning)      │
  │ • Analyze Discovery Results      │
  │ • Generate Attack Plan           │
  │ • Estimate Risk & Impact         │
  └─────┬────────────────────────────┘
        ↓
  ┌──────────────────────────────────┐
  │ 3. RISK VALIDATION               │
  │ • Evaluate CVSS/EPSS Scores      │
  │ • Check Against Risk Thresholds  │
  │ • Request Approvals if Needed    │
  └─────┬────────────────────────────┘
        ↓
  ┌──────────────────────────────────┐
  │ 4. EXECUTION (Async + Retry)     │
  │ • Dispatch Tools (Nmap, MSF)     │
  │ • Monitor Output & Collect Data  │
  │ • Handle Failures Gracefully     │
  │ • Obfuscate Payloads             │
  └─────┬────────────────────────────┘
        ↓
  ┌──────────────────────────────────┐
  │ 5. REPORTING & COMPLIANCE        │
  │ • Generate Findings              │
  │ • Map to NIST/PCI-DSS/ISO27001   │
  │ • Create Executive Report        │
  │ • Store in TimescaleDB           │
  └─────┬────────────────────────────┘
        ↓
  ┌────────────┐
  │  COMPLETE  │
  └────────────┘
```

**Tech Stack:** asyncio | Pydantic V2 | LangChain + Claude | structlog | PostgreSQL/TimescaleDB | Docker (distroless) | Kubernetes/Helm

---

## 🚀 Quick Start

### 5-Minute Docker Startup

```bash
git clone https://github.com/girish-kor/acosp.git && cd acosp
cp .env.example .env                          # Configure env
docker-compose up -d                          # Start stack
docker-compose ps                             # Verify services
docker logs acosp-orchestrator                # Check logs
docker exec acosp-orchestrator python main.py --scope 192.168.1.0/24 --intensity 1
docker cp acosp-orchestrator:/app/reports/. ./reports/
docker-compose down -v
```

### Local Development

```bash
pip install -e ".[dev]"                       # Install deps
python -m pytest tests/ -v --cov=src          # Run tests
python -m ruff check src/ && python -m mypy src/ --strict  # Quality checks
python main.py --scope 10.0.0.0/8 --intensity 2
```

---

## 📦 Installation

**Requirements:** Python 3.11+ | Docker 20.10+ | Docker Compose 2.0+ | PostgreSQL 15+

### From Source
```bash
git clone https://github.com/girish-kor/acosp.git && cd acosp
python -m venv venv && source venv/bin/activate
pip install -e ".[dev]"
python -m pytest tests/ -q
```

### Docker
```bash
docker build -t acosp:1.0.0 .
docker run -it -e ACOSP_LOG_LEVEL=INFO -e ACOSP_DB_HOST=postgres \
  -v /path/to/reports:/app/reports acosp:1.0.0 --scope 192.168.1.0/24 --intensity 2
```

### Kubernetes
```bash
helm repo add acosp https://helm.repo.example.com && helm repo update
helm install acosp acosp/acosp --namespace acosp --create-namespace --values values.yaml
kubectl rollout status deployment/acosp -n acosp
```

---

## 💻 Usage

### CLI

```bash
python main.py [OPTIONS]

Options:
  --scope TEXT              Target scope (CIDR, domain, account ID) [required]
  --intensity INTEGER       Scan intensity 1-5 (1=stealthy, 5=aggressive) [default: 2]
  --config PATH             Configuration file [default: config/acosp.toml]
  --report-format TEXT      Output format: json|pdf|markdown [default: json]
  --help                    Show help
```

**Examples:**
```bash
python main.py --scope 192.168.0.0/16 --intensity 1                    # Reconnaissance only
python main.py --scope internal.example.com --intensity 5 --report-format markdown
python main.py --config config/production.toml --scope 10.0.0.0/8 --intensity 3
```

### Python API

```python
import asyncio
from src.async_orchestrator import run_mission_async
from src.config import ACOSPConfig

async def main():
    config = ACOSPConfig.from_toml("config/acosp.toml")
    await run_mission_async("test-session-001", "192.168.1.0/24", 2, config)

asyncio.run(main())
```

### Core Modules

| Module | Purpose |
|--------|---------|
| `src.async_orchestrator` | Mission lifecycle orchestration |
| `src.async_discovery_engine` | Asset discovery & fingerprinting |
| `src.config` | Configuration management |
| `src.models` | Pydantic V2 schemas |
| `src.exceptions` | Exception hierarchy + retry logic |
| `src.observability` | JSON logging + trace IDs |

---

## ⚙️ Configuration

### Environment Variables (Priority Order)
```bash
# Platform
ACOSP_LOG_LEVEL=INFO ACOSP_LOG_FORMAT=json ACOSP_REPORT_OUTPUT_DIR=reports/

# Database
ACOSP_DB_HOST=localhost ACOSP_DB_PORT=5432 ACOSP_DB_USER=acosp ACOSP_DB_PASSWORD=changeme

# LLM
ACOSP_LLM_PROVIDER=anthropic ACOSP_LLM_API_KEY=sk-... ACOSP_LLM_MODEL=claude-sonnet-4-20250514

# Mission
ACOSP_MISSION_DEFAULT_INTENSITY=2 ACOSP_MISSION_RISK_THRESHOLD=0.75 ACOSP_MISSION_MAX_ITERATIONS=10

# Tools
ACOSP_TOOLS_NMAP_BINARY=/usr/bin/nmap ACOSP_TOOLS_METASPLOIT_HOST=127.0.0.1 ACOSP_TOOLS_METASPLOIT_PORT=55553
```

### Config File (`config/acosp.toml`)
```toml
[platform]
name = "ACOSP"
version = "1.0.0"
log_level = "INFO"
log_format = "json"

[mission]
default_intensity = 2
risk_threshold = 0.75
max_iterations = 10

[database]
connection_string = "postgresql+psycopg2://acosp:password@localhost:5432/acosp"
pool_size = 10

[llm]
provider = "anthropic"
model = "claude-sonnet-4-20250514"
temperature = 0.2
max_tokens = 4096
```

### Intensity Levels
| Level | Use Case |
|-------|----------|
| 1 | Passive, stealthy reconnaissance |
| 2 | Balanced, standard testing |
| 3 | Active, concurrent assessment |
| 4 | Aggressive, parallel audit |
| 5 | Maximum, full red team simulation |

---

## 🛠️ Development

### Project Structure
```
acosp/
├── src/                    # Source code (Pydantic V2 models, orchestration)
├── tests/                  # 44 unit tests (64% coverage)
├── scripts/                # init-db.sql, run-tests.sh
├── .github/workflows/      # 4 CI/CD workflows
├── config/                 # acosp.toml configuration
├── Dockerfile              # Multi-stage production build
├── docker-compose.yaml     # Full stack (TimescaleDB + ACOSP)
├── pyproject.toml          # Project metadata
└── main.py                 # CLI entry point
```

### Testing & Quality

```bash
# Run tests
python -m pytest tests/ -v --cov=src --cov-report=html

# Code quality
python -m ruff check src/ tests/        # Lint
python -m black src/ tests/ --check     # Format
python -m mypy src/ --strict            # Type check
python -m bandit -r src/                # Security

# Parallel testing
python -m pytest tests/ -n auto
```

### Contributing

1. `git checkout -b feature/your-feature`
2. Make changes & test: `python -m pytest tests/ -v`
3. `git commit -m "feat: your feature"` (conventional commits)
4. Create Pull Request & address review

---

## 🚀 GitHub Actions & CI/CD Commands

**All workflows automated.** Manage via GitHub CLI (`gh`) or [web UI](https://github.com/YOUR_ORG/YOUR_REPO/actions).

### Workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| **ci-cd.yml** | Push (main/develop), PR | Lint, test, build Docker, validate compose |
| **deploy-manual.yml** | Manual (workflow_dispatch) | Deploy to staging/production via Helm |
| **release.yml** | Git tag (v*) or manual | Create release, push Docker image, publish PyPI |
| **security.yml** | Push (main/develop), PR, Daily 2AM UTC | CodeQL, dependency audit, secret scan, Trivy, Checkov |

### View & Manage Runs

```bash
gh run list                             # List all runs
gh run list --workflow=ci-cd.yml        # Filter by workflow
gh run view <RUN_ID> --log              # View logs
gh run watch <RUN_ID>                   # Watch in real-time
gh run rerun <RUN_ID>                   # Re-run workflow
gh run rerun <RUN_ID> --failed          # Re-run failed jobs only
gh run cancel <RUN_ID>                  # Cancel running workflow
```

### Trigger Workflows

```bash
# CI/CD (automatic on push/PR)
gh run list --workflow=ci-cd.yml --limit 1

# Manual Deployment
gh workflow run deploy-manual.yml -f environment=staging -f image_tag=latest -f replicas=3

# Release (git tag or manual)
git tag v1.0.0 && git push origin v1.0.0
# OR
gh workflow run release.yml -f version=1.0.0 -f release_type=minor

# Security Scan (automatic on push/PR, daily at 2 AM UTC)
gh run list --workflow=security.yml
```

### Artifacts & Reports

```bash
gh run download <RUN_ID> -n bandit-report
gh run download <RUN_ID> -n test-results-ubuntu-latest-3.11
gh run download <RUN_ID> -n trivy-results.sarif
unzip htmlcov.zip && open htmlcov/index.html
```

### Secrets Management

```bash
gh secret list                          # List secrets
gh secret set GITHUB_TOKEN -b "ghp_..."
gh secret set SLACK_WEBHOOK -b "xoxe..."
gh secret set PYPI_TOKEN -b "pypi-..."
gh secret delete SLACK_WEBHOOK
```

### Setup (GitHub Web UI)

1. **Secrets**: `Settings → Secrets and variables → Actions` → Add GITHUB_TOKEN, SLACK_WEBHOOK, PYPI_TOKEN
2. **Environments**: `Settings → Environments` → Create staging, production with required reviewers
3. **Branch Protection**: `Settings → Branches → main` → Require status checks: lint, typecheck, test, build-docker, compose-validate

### Docker Image Tags

```
ghcr.io/org/repo:develop-SHA123        # Develop branch
ghcr.io/org/repo:v1.2.3                # Release
ghcr.io/org/repo:latest                # Latest release
```

Pull: `docker pull ghcr.io/org/repo:v1.2.3` (requires `docker login ghcr.io`)

### Example Workflows

**CI/CD Test with PR:**
```bash
git checkout -b feature/my-feature && git commit -am "Add feature" && git push origin feature/my-feature
gh pr create --title "Add my feature" --body "Description"
gh run watch                            # Monitor
gh pr merge --auto --squash
```

**Production Deployment:**
```bash
git tag v1.2.3 && git push origin v1.2.3
gh run watch                            # Monitor release workflow
# OR manual: gh workflow run deploy-manual.yml -f environment=production -f image_tag=v1.2.3 -f replicas=5
```

**Security Audit:**
```bash
gh run list --workflow=security.yml --limit 1
gh run download <RUN_ID> -n bandit-report
```

### Troubleshooting

```bash
gh run view <RUN_ID> --log | grep -A 50 "FAILED"
gh run view <RUN_ID> --job <JOB_ID>
gh api runs/<RUN_ID>                    # Raw API response
gh run rerun <RUN_ID> --debug           # Enable debug logging
```

**See [WORKFLOW.md](WORKFLOW.md) for complete documentation.**

---

## 📚 API Reference

### Models

```python
class DiscoveryModel(BaseModel):
    ip: str
    hostname: str | None
    open_ports: list[int]
    os_guess: str | None

class VulnerabilityData(BaseModel):
    cve_id: str | None
    title: str
    severity: SeverityLevel
    cvss_score: float | None

class TelemetryEvent(BaseModel):
    timestamp: str
    session_id: str
    trace_id: str
    level: str
    message: str
    context: dict[str, Any]
```

### Orchestrator

```python
async def run_mission_async(
    session_id: str,
    target_scope: str,
    intensity_level: int,
    config: ACOSPConfig,
) -> None:
    """Execute full mission lifecycle."""

async def coordinate_agents_async(
    current_state: dict[str, Any],
    config: ACOSPConfig,
) -> None:
    """Coordinate discovery, planning, execution."""
```

### Discovery Engine

```python
async def perform_reconnaissance_async(scope: str) -> list[DiscoveryModel]:
    """Discover assets within scope."""

async def fingerprint_services_async(
    assets: list[DiscoveryModel]
) -> dict[str, AssetFingerprint]:
    """Fingerprint discovered services."""

async def map_network_topology_async(
    discovery_results: list[DiscoveryModel]
) -> nx.DiGraph:
    """Build network topology graph."""
```

### Exception Handling

```python
class ACOSPError(Exception):
    """Base exception for all ACOSP errors."""

@retry_with_backoff(max_attempts=3, initial_delay=1.0, max_delay=60.0, jitter=True)
def network_operation():
    """Automatically retry with exponential backoff."""
```

---

## 🚀 Deployment

### Docker Compose (Full Stack)

```bash
export ACOSP_LOG_LEVEL=WARNING
export ACOSP_DB_PASSWORD=$(openssl rand -base64 32)
export ACOSP_LLM_API_KEY=sk-...

docker-compose up -d
docker-compose ps
docker logs acosp-orchestrator
docker-compose exec acosp-orchestrator python main.py --scope 10.0.0.0/8 --intensity 2
docker cp acosp-orchestrator:/app/reports/. ./reports/
docker-compose down
```

### Kubernetes

```bash
kubectl create namespace acosp
helm repo add acosp https://helm.repo.example.com && helm repo update
helm install acosp acosp/acosp --namespace acosp --values production-values.yaml
kubectl rollout status deployment/acosp -n acosp
kubectl logs -n acosp -f deployment/acosp

# Upgrade
helm upgrade acosp acosp/acosp --namespace acosp --values production-values.yaml

# Rollback
helm rollback acosp 1 --namespace acosp
```

### Production Checklist

- [ ] Configuration reviewed & hardened
- [ ] Database backups configured
- [ ] Monitoring & alerting enabled
- [ ] Log aggregation (ELK/Splunk) ready
- [ ] Slack/email notifications set up
- [ ] Security scanning passed
- [ ] Load testing completed
- [ ] Rollback procedure documented
- [ ] Team training completed
- [ ] Legal/compliance approval obtained

---

## 🔐 Security

**Best Practices:** No hardcoded secrets (use env vars/GitHub Secrets) | Type-safe Pydantic V2 | Signed commits required | Security scanning on every push (Bandit, CodeQL, Trivy) | Dependency auditing (pip-audit, Dependabot) | Secret detection (TruffleHog) | Distroless runtime, non-root user | HTTPS only

**Report Security Issues:** security@acosp.internal (do NOT open public issues)

---

## 🆘 Troubleshooting

### Database Connection Failed
```bash
docker-compose ps timescaledb
docker logs timescaledb
docker exec timescaledb psql -U acosp -d acosp -c "SELECT 1"
docker exec timescaledb psql -U postgres -c "ALTER USER acosp PASSWORD 'newpassword'"
```

### Tests Failing
```bash
python -m pytest tests/ -vv --tb=short
python -m pytest tests/test_models.py::TestDiscoveryModel -vv
python --version  # Should be 3.11 or 3.12
pip install -e ".[dev]" --force-reinstall --no-deps
```

### Docker Build Fails
```bash
docker system df && docker builder prune -a
docker build --progress=plain -t acosp:test .
docker run -it --entrypoint /bin/bash -v $(pwd):/workspace python:3.11-slim-bookworm
```

### High Memory Usage
```bash
docker stats acosp-orchestrator
docker run --memory 2g acosp:1.0.0 ...
docker inspect acosp-orchestrator
```

### CI/CD Pipeline Failures
```bash
gh run list && gh run view <RUN_ID> --log
gh run rerun <RUN_ID>              # Re-run failed run
gh run rerun <RUN_ID> --failed     # Re-run failed jobs only
```

---

## 📊 Metrics & Statistics

| Metric | Value |
|--------|-------|
| Test Coverage | 64% (target: 60%+) |
| Tests | 44 passing |
| Python Versions | 3.11, 3.12 |
| Code Lines | ~3,500 |
| Workflows | 4 (CI/CD, Deploy, Release, Security) |
| Docker Image | ~450 MB (distroless runtime) |
| CI/CD Time | 15-20 minutes |
| Type Coverage | 100% (Pydantic V2) |

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [README.md](README.md) | This file - project overview & quick reference |
| [WORKFLOW.md](WORKFLOW.md) | GitHub Actions workflows - complete reference |
| [.env.example](.env.example) | Environment variables template |
| [config/acosp.toml](config/acosp.toml) | Configuration example |
| [Dockerfile](Dockerfile) | Multi-stage container build |
| [docker-compose.yaml](docker-compose.yaml) | Full stack orchestration |

---

## 🤝 Contributing

1. Fork & clone: `git clone https://github.com/YOUR-USERNAME/acosp.git`
2. Feature branch: `git checkout -b feature/your-feature`
3. Make changes & test: `python -m pytest tests/ -v`
4. Commit: `git commit -m "feat: add your feature"` (conventional commits)
5. Create PR & address review

---

## 📜 License

**ACOSP is proprietary software.** All rights reserved. Unauthorized copying, modification, or distribution is prohibited.

For licensing inquiries: legal@acosp.internal

---

## 📞 Support

| Channel | Use For |
|---------|---------|
| **[Issues](https://github.com/girish-kor/acosp/issues)** | Bug reports, feature requests |
| **[Discussions](https://github.com/girish-kor/acosp/discussions)** | Questions, ideas, feedback |
| **Email** | security@acosp.internal (vulnerabilities), legal@acosp.internal (licensing) |

---

## 📋 Version History & Roadmap

### v1.0.0 (Current)
✅ Production-grade async architecture | ✅ Pydantic V2 models | ✅ GitHub Actions CI/CD | ✅ Docker containerization | ✅ Comprehensive documentation | ✅ 44 unit tests (64% coverage) | ✅ Security hardening

### Planned
🔲 Multi-cloud support (AWS/Azure/GCP) | 🔲 Web UI dashboard | 🔲 GraphQL API | 🔲 Real-time collaboration | 🔲 Advanced analytics | 🔲 ML correlation | 🔲 Custom exploit plugins | 🔲 Federation | 🔲 Multi-tenant | 🔲 Cost tracking

---

## 🗺️ Quick Links

- **[GitHub Issues](https://github.com/girish-kor/acosp/issues)**
- **[GitHub Discussions](https://github.com/girish-kor/acosp/discussions)**
- **[GitHub Actions](https://github.com/girish-kor/acosp/actions)**
- **[Docker Hub](https://hub.docker.com/r/acosp/acosp)**
- **[Helm Charts](https://helm.repo.example.com)**

---

## 🙏 Acknowledgments

Claude-3 (LLM reasoning) | MITRE ATT&CK (framework) | NVD/CISA (vulnerability data) | Open source community

---

<div align="center">

![GitHub Issues](https://img.shields.io/github/issues/girish-kor/acosp)
![GitHub Pull Requests](https://img.shields.io/github/issues-pr/girish-kor/acosp)
![GitHub Stars](https://img.shields.io/github/stars/girish-kor/acosp)

**Made with ❤️ by the ACOSP Team** | © 2024 ACOSP. All rights reserved.

**[↑ Back to Top](#acosp---autonomous-continuous-offensive-security-platform)**

</div>
