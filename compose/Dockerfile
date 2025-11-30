# syntax=docker/dockerfile:1
# Template Dockerfile for the tg-stream-service project (compose variant)
# Build with compose:   docker compose -f compose/docker-compose.yml build
# Run with compose:     docker compose -f compose/docker-compose.yml run --rm app
# Or direct docker build:
#   docker build -t tg-stream-service:dev -f compose/Dockerfile .

FROM python:3.13-slim AS base

# Prevent Python from writing .pyc files and enable unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Set working directory
WORKDIR /app

# System dependencies (add as needed)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy only project metadata first (leveraging Docker layer caching)
COPY pyproject.toml /app/

# If you later add dependencies to pyproject.toml and want to preinstall them,
# you can add steps here to install using your preferred tool (pip, uv, poetry, etc.).
# For now, there are no runtime dependencies.

# Copy the rest of the project (if any)
COPY . /app

# Create a non-root user for better security
RUN useradd -m appuser \
    && chown -R appuser:appuser /app
USER appuser

# Default command prints a helpful message. Override this in `docker run` or compose for your app.
CMD ["python", "-c", "print('tg-stream-service container template. Override CMD to run your app, e.g., python -m tg_stream_service')"]
