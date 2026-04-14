# Stage 1: Build stage — install Python dependencies
FROM python:3.13-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code

# Use uv for fast dependency installation
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install Python dependencies
COPY ./server/requirements.txt /code/
RUN uv pip install --system --no-cache -r requirements.txt

# Stage 2: Final image with runtime dependencies
FROM python:3.13-slim

# Metadata labels
LABEL maintainer="Sean Morley" \
      version="0.12.0" \
      description="AdventureLog — the ultimate self-hosted travel companion." \
      org.opencontainers.image.title="AdventureLog" \
      org.opencontainers.image.description="AdventureLog helps you plan, track, and share your adventures." \
      org.opencontainers.image.version="0.12.0" \
      org.opencontainers.image.authors="Sean Morley" \
      org.opencontainers.image.source="https://github.com/seanmorley15/AdventureLog" \
      org.opencontainers.image.vendor="Sean Morley" \
      org.opencontainers.image.licenses="GPL-3.0"

WORKDIR /code
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install runtime-only dependencies (no -dev packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
      postgresql-client \
      gdal-bin \
      nginx \
      memcached \
      supervisor \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy project code and configs
COPY ./server /code/
COPY ./nginx.conf /etc/nginx/nginx.conf
COPY ./supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY ./entrypoint.sh /code/entrypoint.sh
RUN chmod +x /code/entrypoint.sh \
    && mkdir -p /code/static /code/media

# Collect static files
RUN python3 manage.py collectstatic --noinput

# Expose ports
EXPOSE 80 8000

# Start with an entrypoint that runs init tasks then starts supervisord
ENTRYPOINT ["/code/entrypoint.sh"]

# Start supervisord to manage processes
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
