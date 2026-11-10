"""Provider-neutral container entrypoint. Normal startup never substitutes a fake service."""

import hmac
import os
import re
from pathlib import Path
from typing import Mapping

from music_store.config import ConfigurationError, load_settings
from music_store.db import DATASET_REVISION, DATASET_SHA256, initialize_database

SOURCE_REVISION = "7d137081b579b49128068d9dcc4be009cfea9def"
VERSION = "v0.0.0-preview"


def secret_value(name: str, environ: Mapping[str, str]) -> str:
    value, filename = environ.get(name, ""), environ.get(name + "_FILE", "")
    if value and filename:
        raise ConfigurationError("Choose one source for " + name)
    if filename:
        try:
            value = Path(filename).read_text().rstrip("\r\n")
        except (OSError, UnicodeError):
            raise ConfigurationError("Cannot read runtime secret for " + name) from None
    return value


def access_gate(environ: Mapping[str, str], host: str):
    mode = environ.get("APP_ACCESS_MODE", "required")
    if mode == "local-only":
        if host not in {"127.0.0.1", "localhost", "::1"}:
            raise ConfigurationError("local-only access requires a loopback HOST")
        return None
    if mode != "required":
        raise ConfigurationError("APP_ACCESS_MODE must be required or local-only")
    username = secret_value("APP_LOGIN_USER", environ)
    password = secret_value("APP_LOGIN_PASSWORD", environ)
    if not username.strip() or len(password) < 12:
        raise ConfigurationError(
            "Login requires APP_LOGIN_USER and a password of at least 12 characters"
        )

    def authenticate(user, supplied):
        # Bytes support non-ASCII values, and compare both fields without short-circuiting.
        return bool(
            hmac.compare_digest(user.encode(), username.encode())
            & hmac.compare_digest(supplied.encode(), password.encode())
        )

    return authenticate


def metadata(environ, *, smoke_test=False):
    revision = environ.get("PACKAGE_REVISION", "")
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ConfigurationError(
            "PACKAGE_REVISION must identify the exact 40-character packaging commit"
        )
    return {
        "version": VERSION,
        "input_source_revision": SOURCE_REVISION,
        "packaging_revision": revision,
        "dataset_revision": DATASET_REVISION,
        "dataset_sha256": DATASET_SHA256,
        "mode": "deterministic-test-only" if smoke_test else "provider-backed",
        "health_scope": "process and verified database, not provider/customer authentication",
    }


def serve(*, service_factory=None, smoke_test=False):
    """Explicit test images inject deterministic services; production requires a provider."""
    from music_store.model import build_conversation_service
    from music_store.telemetry import EventSink
    from music_store.ui import build_ui

    environ = dict(os.environ)
    # Container startup never loads a developer .env from a working directory.
    key = secret_value("OPENAI_API_KEY", environ)
    if key:
        environ["OPENAI_API_KEY"] = key
    settings = load_settings(env_file=None, environ=environ)
    auth = access_gate(environ, settings.host)
    version = metadata(environ, smoke_test=smoke_test)
    if service_factory is None:
        if smoke_test:
            raise ConfigurationError("Test mode requires an explicit test image harness")
        settings.require_llm()
    elif not smoke_test:
        raise ConfigurationError("A test service is not a production startup option")
    database = initialize_database(settings.chinook_cache_dir)
    try:
        service = (
            build_conversation_service(database, settings, telemetry=EventSink())
            if service_factory is None
            else service_factory(database)
        )
        demo = build_ui(
            service,
            test_banner="DETERMINISTIC CONTAINER TEST — NO PROVIDER" if smoke_test else None,
        )
        demo.launch(
            server_name=settings.host,
            server_port=settings.port,
            auth=auth,
            auth_message="Restricted demo access. This gate is not customer identity verification.",
            share=False,
            show_error=False,
            show_api=False,
            prevent_thread_lock=True,
            blocked_paths=["/run/secrets", "/app/data", "/app/.cache"],
        )

        def health():
            database.query("SELECT 1 AS ready")
            return {"ready": True, **version}

        # Existing Gradio server only; no new REST application/domain API layer.
        # Public operational metadata contains no user/profile/provider/key values.
        demo.app.add_api_route("/healthz", health, methods=["GET"], include_in_schema=False)
        demo.app.add_api_route(
            "/version", lambda: version, methods=["GET"], include_in_schema=False
        )
        demo.block_thread()
    finally:
        database.close()


def main():
    try:
        serve()
    except ConfigurationError as error:
        raise SystemExit(str(error)) from None


if __name__ == "__main__":
    main()
