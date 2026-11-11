"""Validated settings with explicit .env loading and process-environment precedence."""

import os
from pathlib import Path
from typing import Mapping
from urllib.parse import urlsplit

from dotenv import dotenv_values
from pydantic import BaseModel, ConfigDict, Field, SecretStr, ValidationError, field_validator


class ConfigurationError(ValueError):
    """Safe configuration failure that does not echo secret input values."""


class Settings(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", hide_input_in_errors=True)

    openai_api_key: SecretStr = Field(default=SecretStr(""), repr=False)
    model_name: str = Field(default="gpt-4o-mini", min_length=1, max_length=200)
    temperature: float = Field(default=0, ge=0, le=2, allow_inf_nan=False)
    openai_api_base: str = Field(default="https://api.openai.com/v1", repr=False)
    response_writer_enabled: bool = True
    model_max_tokens: int | None = Field(default=None, ge=128, le=4096)
    port: int = Field(default=7860, ge=1, le=65535)
    request_timeout_seconds: float = Field(default=30, gt=0, le=300, allow_inf_nan=False)
    max_attempts: int = Field(default=2, ge=1, le=5)
    max_graph_steps: int = Field(default=12, ge=1, le=100)
    host: str = "127.0.0.1"
    chinook_cache_dir: Path = Path(".cache/chinook")

    @field_validator("model_name")
    @classmethod
    def nonblank_model(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Model must not be blank")
        return value.strip()

    @field_validator("host")
    @classmethod
    def valid_host(cls, value: str) -> str:
        if value not in {"127.0.0.1", "localhost", "::1", "0.0.0.0"}:
            raise ValueError("Use a loopback host, or 0.0.0.0 inside a container")
        return value

    @field_validator("openai_api_base")
    @classmethod
    def valid_base(cls, value: str) -> str:
        parts = urlsplit(value)
        # Accessing .port validates syntax/range; Pydantic sanitizes ValueError.
        port = parts.port
        if port is not None and port < 1:
            raise ValueError("Endpoint port must be between 1 and 65535")
        local = parts.hostname in {"localhost", "127.0.0.1", "::1"}
        if (
            not parts.hostname
            or (parts.scheme != "https" and not (parts.scheme == "http" and local))
            or parts.username is not None
            or parts.password is not None
            or parts.query
            or parts.fragment
        ):
            raise ValueError("Use an HTTPS endpoint or local HTTP endpoint without credentials")
        return value.rstrip("/")

    def require_llm(self) -> None:
        if not self.openai_api_key.get_secret_value().strip():
            raise ConfigurationError("OPENAI_API_KEY is required for LLM mode")


def load_settings(
    env_file: Path | None = Path(".env"), environ: Mapping[str, str] | None = None
) -> Settings:
    """Read only declared settings; do not mutate os.environ or log input values."""
    keys = {
        "OPENAI_API_KEY": "openai_api_key",
        "MODEL_NAME": "model_name",
        "MODEL_MAX_TOKENS": "model_max_tokens",
        "RESPONSE_WRITER_ENABLED": "response_writer_enabled",
        "TEMPERATURE": "temperature",
        "OPENAI_API_BASE": "openai_api_base",
        "PORT": "port",
        "REQUEST_TIMEOUT_SECONDS": "request_timeout_seconds",
        "MAX_ATTEMPTS": "max_attempts",
        "MAX_GRAPH_STEPS": "max_graph_steps",
        "HOST": "host",
        "CHINOOK_CACHE_DIR": "chinook_cache_dir",
    }
    file_values = dotenv_values(env_file, interpolate=False) if env_file is not None else {}
    values = {**file_values, **(os.environ if environ is None else environ)}
    payload = {field: values[key] for key, field in keys.items() if values.get(key) is not None}
    try:
        return Settings.model_validate(payload)
    except ValidationError as exc:
        fields = sorted({str(error["loc"][0]) for error in exc.errors()})
        raise ConfigurationError("Invalid settings: " + ", ".join(fields)) from None
