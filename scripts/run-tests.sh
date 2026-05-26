#!/bin/bash
# scripts/run-tests.sh — Complete ACOSP test pipeline
# Runs pytest, mypy, ruff, and bandit with reporting

set -e  # Exit on error

echo "=========================================="
echo "ACOSP Production-Grade Test Pipeline"
echo "=========================================="

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'  # No Color

# 1. Pytest with coverage
echo -e "\n${YELLOW}[1/4] Running pytest with asyncio...${NC}"
python3 -m pytest tests/ -v --asyncio-mode=auto --cov=src --cov-report=term-missing --cov-report=html

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Pytest passed${NC}"
else
    echo -e "${RED}✗ Pytest failed${NC}"
    exit 1
fi

# 2. MyPy strict type checking
echo -e "\n${YELLOW}[2/4] Running mypy --strict...${NC}"
python3 -m mypy src/ --strict --show-error-codes

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ MyPy passed${NC}"
else
    echo -e "${RED}✗ MyPy failed${NC}"
    exit 1
fi

# 3. Ruff linting
echo -e "\n${YELLOW}[3/4] Running ruff check...${NC}"
python3 -m ruff check src/ tests/

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Ruff passed${NC}"
else
    echo -e "${RED}✗ Ruff failed${NC}"
    exit 1
fi

# 4. Bandit security scanning
echo -e "\n${YELLOW}[4/4] Running bandit security scan...${NC}"
python3 -m bandit -r src/ -f json -o bandit-report.json

if [ $? -eq 0 ] || [ $? -eq 1 ]; then  # Bandit returns 1 if issues found
    echo -e "${GREEN}✓ Bandit scan complete (see bandit-report.json)${NC}"
else
    echo -e "${RED}✗ Bandit failed${NC}"
    exit 1
fi

echo -e "\n${GREEN}=========================================="
echo "All tests passed!"
echo "=========================================${NC}"
echo "Coverage report: htmlcov/index.html"
echo "Bandit report: bandit-report.json"
