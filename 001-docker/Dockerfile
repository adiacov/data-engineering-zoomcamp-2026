FROM python:3.13-slim

WORKDIR /app

# 1. Copy dependency files first (cache-friendly)
COPY requirements.txt .
# COPY pyproject.toml .

# 2. Install dependencies once
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copy source code last
COPY src/ ./src/

# 4. Ensure src is importable
ENV PYTHONPATH=/app/src

ENTRYPOINT ["python", "-m", "pipeline.ingest_data"]
