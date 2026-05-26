# GitHub Actions Workflows Documentation

## Overview

This repository uses a comprehensive CI/CD pipeline with four integrated GitHub Actions workflows that automate testing, building, security scanning, and deployment.

---

## Workflows

### 1. **CI/CD Pipeline** (`ci-cd.yml`)

**Triggers:**
- Push to: `main`, `develop`, `release/**` branches
- Pull requests to: `main`, `develop`
- Path filters: `src/`, `tests/`, `pyproject.toml`, `requirements.txt`, `Dockerfile`, `docker-compose.yaml`, `.github/workflows/`

**Jobs:**

| Job | Purpose | Status |
|-----|---------|--------|
| **lint** | Code quality checks (ruff, black, isort) | Required |
| **typecheck** | MyPy strict type checking | Optional (continue-on-error) |
| **security** | Bandit security scanning | Optional (continue-on-error) |
| **test** | Unit tests on Python 3.11/3.12, Ubuntu/Windows | Required |
| **audit** | Dependency vulnerability audit | Optional (continue-on-error) |
| **build-docker** | Multi-stage Docker image build & push to GHCR | Requires all tests pass |
| **compose-validate** | Docker Compose YAML validation | Requires tests pass |
| **scan-container** | Trivy container vulnerability scan | Runs after Docker build (pushes only) |
| **docs** | API documentation generation | Runs on main branch only |
| **deploy-staging** | Deploy to staging (develop branch only) | Conditional |
| **quality-summary** | Final quality report | Always runs |

**Environment Variables:**
```yaml
REGISTRY: ghcr.io
IMAGE_NAME: ${{ github.repository }}
PYTHON_VERSION: '3.11'
```

**Secrets Required:**
- `GITHUB_TOKEN` (auto-provided by GitHub Actions)

---

### 2. **Manual Deployment** (`deploy-manual.yml`)

**Triggers:**
- Manual trigger via GitHub UI (workflow_dispatch)

**Inputs:**
```yaml
environment:
  description: 'Target environment'
  options: [staging, production]
  default: staging

image_tag:
  description: 'Docker image tag to deploy'
  default: 'latest'

replicas:
  description: 'Number of replicas'
  default: '3'
```

**Jobs:**

| Job | Purpose |
|-----|---------|
| **deploy** | Deploy to selected environment using Helm + Kubernetes |
| **rollback** | Automatic rollback on deployment failure |

**Environment:**
- Uses GitHub Environments for branch protection & approvals

**Secrets Required:**
- `SLACK_WEBHOOK` (deployment notifications)
- `HELM_REPO_URL` (Helm chart repository)

---

### 3. **Release Pipeline** (`release.yml`)

**Triggers:**
- Push of git tags matching `v*` (e.g., `v1.0.0`)
- Manual trigger (workflow_dispatch)

**Manual Inputs:**
```yaml
version:
  description: 'Release version (e.g., 1.0.0)'
  required: true

release_type:
  description: 'Release type'
  options: [major, minor, patch]
  default: 'minor'
```

**Jobs:**

| Job | Purpose |
|-----|---------|
| **create-release** | Create GitHub Release with changelog |
| **build-release** | Build & push Docker image with version tag |
| **publish-pypi** | Publish Python package to PyPI |
| **update-docs** | Generate API docs & create PR |
| **announce** | Notify Slack & create deployment issue |

**Secrets Required:**
- `PYPI_TOKEN` (PyPI authentication)
- `SLACK_WEBHOOK` (release announcements)

---

### 4. **Security Scanning** (`security.yml`)

**Triggers:**
- Push to: `main`, `develop`
- Pull requests to: `main`
- Scheduled: Daily at 2 AM UTC

**Jobs:**

| Job | Purpose | Tool |
|-----|---------|------|
| **codeql** | SAST - Static Application Security Testing | GitHub CodeQL |
| **dependencies** | Scan for vulnerable dependencies | pip-audit, safety |
| **secrets** | Scan for exposed secrets | TruffleHog, detect-secrets |
| **bandit** | Python security issues | Bandit |
| **container-scan** | Container image vulnerabilities | Trivy |
| **infrastructure** | Infrastructure-as-Code scanning | Checkov |
| **report** | Security summary report | GitHub Step Summary |

**Secrets Required:**
- None (runs on code analysis only)

---

## Setup Instructions

### 1. Configure GitHub Secrets

Go to: `https://github.com/YOUR_ORG/YOUR_REPO/settings/secrets/actions`

Click **New repository secret** and add:

| Secret | Value | Source |
|--------|-------|--------|
| `GITHUB_TOKEN` | `github_pat_*` | `.env` file |
| `SLACK_WEBHOOK` | `xoxe.xoxp-*` | `.env` file |
| `PYPI_TOKEN` | `pypi-AgEI*` | `.env` file |
| `HELM_REPO_URL` | `https://charts.example.com` | Your Helm repo |

**Or use GitHub CLI:**
```bash
bash scripts/setup-github-secrets.sh
```

### 2. Configure GitHub Environments

For production deployments, set up GitHub Environments with required reviewers:

1. Go to: `https://github.com/YOUR_ORG/YOUR_REPO/settings/environments`
2. Create environment: `staging`
3. Create environment: `production`
4. Add required reviewers for `production`

### 3. Branch Protection Rules

Recommended rules for `main` branch:

```
✓ Require status checks to pass before merging:
  - lint
  - typecheck
  - test
  - build-docker
  - compose-validate

✓ Require code reviews: 1
✓ Dismiss stale pull request approvals
✓ Require branches to be up to date before merging
```

---

## Workflow Triggers & Examples

### Continuous Integration (CI)

**Trigger:** Create a pull request to `main` or `develop`

```bash
git checkout -b feature/new-feature
git commit -am "Add new feature"
git push origin feature/new-feature
# Open pull request on GitHub
```

**Result:**
- ✅ Linting checks
- ✅ Type checking
- ✅ Security scan
- ✅ Unit tests (Python 3.11, 3.12 on Ubuntu/Windows)
- ✅ Docker build
- ✅ Compose validation
- ✅ Quality summary

### Staging Deployment

**Trigger:** Push to `develop` branch

```bash
git checkout develop
git merge feature/new-feature
git push origin develop
```

**Result:**
- Runs full CI/CD pipeline
- Builds Docker image: `ghcr.io/org/repo:develop-SHA`
- Scans with Trivy
- Deploys to staging environment

### Production Release

**Trigger:** Create a git tag

```bash
git tag v1.2.3
git push origin v1.2.3
```

**Result:**
- Creates GitHub Release
- Builds & pushes Docker image: `ghcr.io/org/repo:v1.2.3`, `latest`
- Publishes to PyPI
- Updates documentation
- Announces release on Slack
- Creates deployment issue

**Or manually:** Go to Actions → Release → Run workflow → Enter version `1.2.3`

### Security Scanning

**Trigger:** Automatic (daily at 2 AM UTC) + on push to main/develop + PR to main

**Result:**
- CodeQL analysis
- Dependency vulnerability scan
- Secret detection
- Bandit Python security
- Container image scan
- Infrastructure compliance (Checkov)

---

## Docker Image Tags

Images are pushed to GitHub Container Registry with automatic tagging:

```
ghcr.io/org/repo:develop-SHA123      # Develop branch
ghcr.io/org/repo:main-SHA456         # Main branch
ghcr.io/org/repo:v1.2.3              # Release tag
ghcr.io/org/repo:latest              # Latest release
```

Pull images:
```bash
docker pull ghcr.io/org/repo:v1.2.3
docker login ghcr.io -u YOUR_GITHUB_USERNAME -p GITHUB_TOKEN
```

---

## Kubernetes Deployment

### Staging Deployment

Automatic when pushing to `develop`:

```bash
helm upgrade --install acosp acosp/acosp \
  --namespace acosp \
  --values values-staging.yaml \
  --set image.tag=develop-SHA
```

### Production Deployment

Manual via GitHub Actions UI:

1. Go to: `https://github.com/YOUR_ORG/YOUR_REPO/actions/workflows/deploy-manual.yml`
2. Click **Run workflow**
3. Select:
   - Environment: `production`
   - Image tag: `v1.2.3`
   - Replicas: `5`
4. Click **Run workflow**

**Requires:**
- Production GitHub Environment with required approvers
- Kubernetes cluster configured
- Helm charts in `acosp/acosp` repository

---

## Monitoring & Debugging

### View Workflow Runs

```
https://github.com/YOUR_ORG/YOUR_REPO/actions
```

### View Step Logs

1. Click workflow run
2. Click job name
3. Expand step to see detailed logs

### Common Issues

**Test failures:**
```bash
# Run tests locally
pytest tests/ -v --cov=src

# Run linting
ruff check src/ tests/
black src/ tests/ --check
isort src/ tests/ --check-only
```

**Docker build failures:**
```bash
# Build locally
docker build -t acosp:test .

# Check Dockerfile syntax
docker build --progress=plain -t acosp:test .
```

**Compose validation failures:**
```bash
# Validate locally
docker-compose config

# Run with verbose output
docker-compose up --verbose
```

---

## Environment Variables

### CI/CD Pipeline

| Variable | Default | Usage |
|----------|---------|-------|
| `PYTHON_VERSION` | `3.11` | Python version for testing |
| `REGISTRY` | `ghcr.io` | Container registry |
| `IMAGE_NAME` | `${{ github.repository }}` | Image name |

### Runtime (docker-compose)

```yaml
ACOSP_LOG_LEVEL: INFO
ACOSP_LOG_FORMAT: json
ACOSP_DB_HOST: timescaledb
ACOSP_DB_PORT: 5432
ACOSP_DB_USER: acosp
ACOSP_DB_PASSWORD: changeme  # Change in production
ACOSP_LLM_PROVIDER: anthropic
ACOSP_LLM_MODEL: claude-sonnet-4-20250514
ACOSP_MISSION_DEFAULT_INTENSITY: 2
```

---

## Best Practices

### Code Quality
- ✅ Maintain >90% test coverage
- ✅ Run linting before commit: `pre-commit install`
- ✅ Use type hints: `mypy --strict`
- ✅ Follow PEP 8: `black` + `isort`

### Security
- ✅ Never commit secrets to repository
- ✅ Use GitHub Secrets for credentials
- ✅ Review Trivy & Bandit reports
- ✅ Keep dependencies updated

### Deployment
- ✅ Always deploy staging first
- ✅ Require approval for production
- ✅ Tag releases semantically: `vMAJOR.MINOR.PATCH`
- ✅ Write release notes in changelog

### Monitoring
- ✅ Check workflow runs after every push
- ✅ Review security scan reports
- ✅ Monitor Slack notifications
- ✅ Archive test reports

---

## Troubleshooting

### Workflow Won't Start
- Check branch protection rules
- Verify workflow file is in `.github/workflows/`
- Ensure YAML syntax is valid

### Tests Fail Locally But Pass in CI
- Check Python version: `python --version`
- Install dev dependencies: `pip install -e ".[dev]"`
- Run exact CI command: `pytest tests/ -v --cov=src`

### Docker Build Fails
- Check Dockerfile syntax
- Verify all COPY paths exist
- Test locally: `docker build -t test .`
- Check base image availability

### Deployment Fails
- Verify Kubernetes cluster is reachable
- Check Helm values in `values-staging.yaml`
- Ensure secrets are configured
- Review deployment logs: `kubectl logs -f deployment/acosp`

---

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker CLI Reference](https://docs.docker.com/reference/cli/docker/)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Helm Documentation](https://helm.sh/docs/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [PyPI Publishing](https://packaging.python.org/guides/publishing-package-distribution-releases-to-pypi/)

---

**Last Updated:** 2024
**Version:** 1.0.0
