FROM python:3.13-slim

WORKDIR /app

# Copy project metadata
COPY pyproject.toml /app/

# Copy data
COPY data/ /app/data/

# Copy source code
COPY src/ /app/src/

# Install project and dependencies
RUN python -m pip install --no-cache-dir .

# Default command
CMD ["python", "-m", "pipeline.pipeline"]
