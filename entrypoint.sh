#!/bin/sh

gunicorn --bind 0.0.0.0:80 --workers "${WORKERS}" -k src.workers.ApiWorker src.main:app