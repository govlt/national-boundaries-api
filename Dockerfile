# Stage 1: Prepare SQLite database
FROM ghcr.io/osgeo/gdal:ubuntu-full-3.12.1 AS database-builder
WORKDIR /opt/database

RUN apt-get update && apt-get install -y csvkit && rm -rf /var/lib/apt/lists/*
COPY create-database.sh ./create-database.sh
RUN bash create-database.sh

# Stage 2: Build Python environment
FROM ghcr.io/astral-sh/uv:0.9-python3.14-trixie AS builder

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

FROM python:3.14-slim

WORKDIR /opt/app

# Required for using SpatialLite
RUN apt-get update && apt-get install -y \
  curl \
  spatialite-bin \
  libsqlite3-mod-spatialite \
  && rm -rf /var/lib/apt/lists/*

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    SPATIALITE_LIBRARY_PATH=mod_spatialite.so \
    SENTRY_DSN="" \
    SENTRY_ENVIRONMENT="production" \
    ROOT_URL="" \
    WORKERS=1

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY src/ src/
COPY --chmod=555 entrypoint.sh /opt/app/entrypoint.sh
COPY --from=database-builder --chmod=444 /opt/database/boundaries.sqlite /opt/database/data-sources/data-source-checksums.txt ./

ENTRYPOINT ["/opt/app/entrypoint.sh"]