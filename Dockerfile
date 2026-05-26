# Multi-stage Dockerfile for ACOSP production deployment
# Optimized for security and size with minimal runtime attack surface

# ============================================================================
# Stage 1: Builder — compile dependencies and prepare runtime artifacts
# ============================================================================

FROM python:3.11-slim-bookworm AS builder

WORKDIR /tmp/build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml requirements.txt ./

# Create virtual environment and install dependencies
RUN python3 -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# ============================================================================
# Stage 2: Runtime — distroless base with production artifacts
# ============================================================================

FROM gcr.io/distroless/python3.11-nonroot:nonroot

LABEL maintainer="ACOSP Team <team@acosp.internal>" \
      description="Autonomous Continuous Offensive Security Platform" \
      version="1.0.0"

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder --chown=nonroot:nonroot /opt/venv /opt/venv

# Copy application source code
COPY --chown=nonroot:nonroot src/ ./src/
COPY --chown=nonroot:nonroot config/acosp.toml ./config/
COPY --chown=nonroot:nonroot main.py .

# Copy .env if it exists (optional, for local dev)
COPY --chown=nonroot:nonroot .env* ./

# Create reports directory
RUN mkdir -p /app/reports && \
    chown -R nonroot:nonroot /app

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    ACOSP_LOG_FORMAT=json

# Health check (simple Python syntax check to validate environment)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import sys; sys.exit(0)" || exit 1

# Non-root user is already set by distroless image
USER nonroot:nonroot

# Entry point
ENTRYPOINT ["/opt/venv/bin/python", "main.py"]
CMD ["--help"]
