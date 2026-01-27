FROM python:3.13-slim

# -----------------------------
# Runtime setup
# -----------------------------
WORKDIR /app

# Install uv (tiny, cache-friendly)
RUN pip install --no-cache-dir uv

# -----------------------------
# Dependency layer (cached)
# -----------------------------
# Copy dependency metadata + wheels from repo root
COPY pyproject.toml uv.lock ./
COPY dist/ ./dist/

# Install all dependencies + internal packages
RUN uv pip install --system --no-cache ./dist/*.whl

ENV PROJECT_ROOT=/app

# -----------------------------
# Data directory (externalized)
# -----------------------------
RUN mkdir -p /data
VOLUME ["/data"]
ENV DATA_DIR=/Data

# -----------------------------
# Entrypoint
# -----------------------------
ENTRYPOINT ["python", "-m", "pipeline.ingest_data"]
