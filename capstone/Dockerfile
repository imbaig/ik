# syntax=docker/dockerfile:1
FROM python:3.12-slim@sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b AS runtime
ARG PACKAGE_REVISION
LABEL org.opencontainers.image.title="Music Store v0 preview" \
      org.opencontainers.image.version="v0.0.0-preview" \
      org.opencontainers.image.revision="${PACKAGE_REVISION}" \
      app.input_source_revision="7d137081b579b49128068d9dcc4be009cfea9def"
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src GRADIO_ANALYTICS_ENABLED=False \
    HOST=0.0.0.0 PORT=7860 APP_ACCESS_MODE=required \
    CHINOOK_CACHE_DIR=/app/data/chinook PACKAGE_REVISION=${PACKAGE_REVISION}
WORKDIR /app
COPY requirements.lock /app/requirements.lock
COPY src /app/src
COPY data/provenance.json data/CHINOOK-LICENSE.txt /app/data/
RUN --mount=type=secret,id=proxy_ca \
    if [ -f /run/secrets/proxy_ca ]; then export PIP_CERT=/run/secrets/proxy_ca SSL_CERT_FILE=/run/secrets/proxy_ca; fi; \
    python -m pip install --no-cache-dir -r requirements.lock && \
    python -c 'from music_store.db import initialize_database; from pathlib import Path; db=initialize_database(Path("/app/data/chinook")); db.close()' && \
    python -c 'import os; from music_store.deployment import metadata; metadata(os.environ)' && \
    groupadd --gid 10001 app && useradd --uid 10001 --gid 10001 --create-home app && \
    chmod -R a+rX /app && mkdir -p /app/.cache && chown app:app /app/.cache && chmod -R a-w /app/data
USER 10001:10001
EXPOSE 7860
HEALTHCHECK --interval=10s --timeout=3s --start-period=25s --retries=3 \
    CMD python -c 'import json,os,urllib.request; u="http://127.0.0.1:"+os.environ.get("PORT","7860")+"/healthz"; r=urllib.request.build_opener(urllib.request.ProxyHandler({})).open(u,timeout=2); assert json.load(r)["ready"]'
CMD ["python", "-m", "music_store.deployment"]

# Explicitly selected smoke target only; not included in the default production image.
FROM runtime AS smoke
COPY --chmod=0444 tests/ui_harness.py deployment/smoke_entry.py /opt/
CMD ["python", "/opt/smoke_entry.py"]

# Default final target is always production.
FROM runtime AS production
