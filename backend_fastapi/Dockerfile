ARG UV_VERSION=0.9.5
# Use Python 3.12 - best wheel availability for Alpine
ARG PYTHON_VERSION=3.12

FROM ghcr.io/astral-sh/uv:${UV_VERSION} AS uv

# ============================================================
# BUILDER STAGE - Compile dependencies once
# ============================================================
FROM python:${PYTHON_VERSION}-alpine AS builder
COPY --from=uv /uv /uvx /bin/
WORKDIR /app

# Install ONLY build dependencies (removed in final image)
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    postgresql-dev \
    git

# Pin Python version to avoid 3.14 auto-selection
ENV UV_PYTHON=python3.12

# Install dependencies (cached layer)
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev

# Copy app and install project
ADD . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable

# ============================================================
# RUNTIME STAGE - Minimal production image
# ============================================================
FROM python:${PYTHON_VERSION}-alpine AS base
ARG TZ=Europe/Paris
WORKDIR /app

# Critical: Add venv to PATH so Python finds packages WITHOUT uv
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TZ=${TZ}

# Install ONLY runtime dependencies (no gcc/build tools!)
RUN apk add --no-cache \
    libpq \
    tzdata \
    && cp /usr/share/zoneinfo/${TZ} /etc/localtime \
    && apk del tzdata

# Create non-root user
RUN addgroup -g 1000 -S user && \
    adduser -u 1000 -S user -G user -s /sbin/nologin

# Copy app and pre-built venv from builder
ADD --chown=1000:1000 . /app
COPY --from=builder --chown=1000:1000 /app/.venv /app/.venv

USER user

# ============================================================
# DEVELOPMENT TARGET
# ============================================================
FROM base AS dev
# Use uvicorn directly from venv (no uv overhead)
CMD ["uvicorn", "app.server:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ============================================================
# PRODUCTION TARGET
# ============================================================
FROM base AS server
# Direct uvicorn execution - fastest startup, no uv checking
CMD ["uvicorn", "app.server:app", "--host", "0.0.0.0", "--port", "8000"]