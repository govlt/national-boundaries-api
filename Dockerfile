# Stage 1: Prepare SQLite database
FROM ghcr.io/osgeo/gdal:ubuntu-full-3.12.1 AS database-builder
WORKDIR /opt/database

RUN apt-get update && apt-get install -y csvkit &&  rm -rf /var/lib/apt/lists/*

COPY create-database.sh ./create-database.sh

RUN bash create-database.sh

# Multi stage poetry docker build https://medium.com/@albertazzir/blazing-fast-python-docker-builds-with-poetry-a78a66f5aed0
FROM python:3.14 AS builder

RUN pip install poetry==2.2.1

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR

# The runtime image, used to just run the code provided its virtual environment
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
