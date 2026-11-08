#!/usr/bin/env bash
# Run in the hosted environment from any working directory; no application key needed.
set -euo pipefail
script_directory="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd -- "$script_directory/.."
export OPENAI_API_KEY=''
export GRADIO_ANALYTICS_ENABLED='False'
python3 -m venv .cache/cloud-tools
.cache/cloud-tools/bin/python -m pip install uv==0.12.5
cloud_uv="$PWD/.cache/cloud-tools/bin/uv"
"$cloud_uv" sync --locked --python 3.12
PYTHONPATH=src "$cloud_uv" run --locked python -m music_store.db
"$cloud_uv" run --locked ruff check src tests app.py
"$cloud_uv" run --locked ruff format --check src tests app.py
"$cloud_uv" run --locked pytest -q --junitxml=test-results/cloud-setup.xml
