# syntax=docker/dockerfile:1.6
# Cerberus Memory Intelligence — Inspector Web UI
# Phase P3.5 · Production-ready image (Python 3.12 slim)
#
# Build:   docker build -t cerberus-inspector:local .
# Run:     docker run --rm -p 7331:7331 -v dm-cerbro-data:/data cerberus-inspector:local
#
# Multi-stage is unnecessary (pure-stdlib engine, no compiled deps).

FROM python:3.12-slim AS runtime

LABEL org.opencontainers.image.title="Cerberus Inspector" \
      org.opencontainers.image.description="Dev Maniac's Memory Intelligence — Localhost Management Plane" \
      org.opencontainers.image.source="https://devmaniacs.com.br" \
      org.opencontainers.image.licenses="Proprietary"

# Run as a dedicated non-root user.
RUN groupadd --system cerberus \
 && useradd --system --gid cerberus --home /data --shell /bin/false cerberus

WORKDIR /opt/sistemas/dm-cerebro

# System dependencies kept minimal. Python 3.12-slim ships with SQLite + FTS5.
# Add tini for proper signal handling under PID 1.
RUN apt-get update \
 && apt-get install -y --no-install-recommends tini ca-certificates curl \
 && rm -rf /var/lib/apt/lists/*

# Copy the engine package first to leverage Docker layer caching.
COPY engine/ /opt/sistemas/dm-cerebro/engine/
COPY bin/ /opt/sistemas/dm-cerebro/bin/

# Make CLI wrappers executable.
RUN if [ -d /opt/sistemas/dm-cerebro/bin ]; then \
      find /opt/sistemas/dm-cerebro/bin -type f -name "*.cmd" -exec chmod +x {} \; ; \
      find /opt/sistemas/dm-cerebro/bin -type f -name "*.ps1" -exec chmod +x {} \; ; \
    fi

# Create persistent data directory (mounted as a volume in compose).
RUN mkdir -p /data && chown -R cerberus:cerberus /data

ENV CERBERUS_ROOT=/data \
    CERBERUS_UI_HOST=0.0.0.0 \
    CERBERUS_UI_PORT=7331 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONIOENCODING=utf-8 \
    CERBERUS_AUTH_DISABLE=0

EXPOSE 7331

# Healthcheck: the dashboard must serve 200/401 on GET /.
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -fsS -o /dev/null -w "%{http_code}\n" http://127.0.0.1:7331/ \
    | grep -E '^(200|303)$' >/dev/null || exit 1

USER cerberus

# tini reaps zombies and forwards signals to the server (graceful shutdown).
ENTRYPOINT ["/usr/bin/tini", "--"]

CMD ["python", "-m", "engine.cli", "ui", \
     "--host", "0.0.0.0", \
     "--port", "7331", \
     "--no-browser"]