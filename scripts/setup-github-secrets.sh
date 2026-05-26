#!/bin/bash
# Configure GitHub Secrets for Actions
# Run this from your repository root after installing GitHub CLI: https://cli.github.com

set -e

echo "========================================"
echo "GitHub Secrets Configuration"
echo "========================================"
echo ""

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI not found. Install from: https://cli.github.com"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ Not authenticated with GitHub CLI"
    echo "Run: gh auth login"
    exit 1
fi

echo "Adding secrets to GitHub repository..."
echo ""

# Add secrets from .env file
SECRETS=(
    "GITHUB_TOKEN"
    "SLACK_WEBHOOK"
    "PYPI_TOKEN"
    "HELM_REPO_URL"
)

for secret in "${SECRETS[@]}"; do
    value=$(grep "^${secret}=" .env | cut -d= -f2-)
    if [ -z "$value" ]; then
        echo "⚠️  Skipping $secret (not in .env)"
        continue
    fi
    
    echo "Setting $secret..."
    echo "$value" | gh secret set "$secret" 2>/dev/null && echo "  ✓ $secret configured" || echo "  ✗ Failed to set $secret"
done

echo ""
echo "✅ Secrets configured!"
echo ""
echo "Verify with: gh secret list"
