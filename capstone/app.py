"""Local Music Store capstone entry point. Run: uv run python app.py."""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

os.environ.setdefault("GRADIO_ANALYTICS_ENABLED", "False")

from music_store.config import load_settings
from music_store.db import initialize_database
from music_store.model import build_conversation_service
from music_store.telemetry import EventSink
from music_store.ui import build_ui


def main():
    settings = load_settings()
    settings.require_llm()
    database = initialize_database(settings.chinook_cache_dir)
    try:
        service = build_conversation_service(database, settings, telemetry=EventSink())
        build_ui(service).launch(
            server_name=settings.host,
            server_port=settings.port,
            share=False,
            show_error=False,
            show_api=False,
        )
    finally:
        database.close()


if __name__ == "__main__":
    main()
