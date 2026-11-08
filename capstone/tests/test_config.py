import os

import pytest

from music_store.config import ConfigurationError, load_settings


def test_defaults_work_without_api_key():
    config = load_settings(None, {})
    assert config.port == 7860
    assert config.max_attempts == 2
    assert config.max_graph_steps == 12
    with pytest.raises(ConfigurationError, match="OPENAI_API_KEY"):
        config.require_llm()


def test_env_overrides_dotenv_without_global_mutation(tmp_path):
    path = tmp_path / ".env"
    path.write_text("MODEL_NAME=file-model\nPORT=8000\nOPENAI_API_KEY=not-a-real-key\n")
    before = dict(os.environ)
    config = load_settings(path, {"MODEL_NAME": "env-model"})
    assert config.model_name == "env-model"
    assert config.port == 8000
    config.require_llm()
    assert os.environ == before
    assert "not-a-real-key" not in repr(config)


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("PORT", "0"),
        ("PORT", "65536"),
        ("TEMPERATURE", "nan"),
        ("REQUEST_TIMEOUT_SECONDS", "0"),
        ("MAX_ATTEMPTS", "0"),
        ("MAX_GRAPH_STEPS", "-1"),
        ("MODEL_NAME", "  "),
        ("OPENAI_API_BASE", "http://remote.example/v1"),
        ("OPENAI_API_BASE", "https://user:secret@provider.example/v1"),
        ("OPENAI_API_BASE", "https://provider.example/v1?key=secret"),
    ],
)
def test_invalid_settings_rejected_without_values(key, value):
    with pytest.raises(ConfigurationError) as error:
        load_settings(None, {key: value})
    assert "secret" not in str(error.value)


def test_local_compatible_endpoint():
    assert load_settings(
        None, {"OPENAI_API_BASE": "http://localhost:1234/v1/"}
    ).openai_api_base == ("http://localhost:1234/v1")


def test_dotenv_does_not_interpolate_secrets(tmp_path):
    path = tmp_path / ".env"
    path.write_text("OPENAI_API_KEY=literal-${UNRELATED_SECRET}\n")
    config = load_settings(path, {})
    assert config.openai_api_key.get_secret_value() == "literal-${UNRELATED_SECRET}"


@pytest.mark.parametrize(
    "endpoint",
    [
        "https://provider.example:bad/v1",
        "https://provider.example:99999/v1",
        "https://provider.example:0/v1",
    ],
)
def test_invalid_endpoint_ports(endpoint):
    with pytest.raises(ConfigurationError, match="openai_api_base"):
        load_settings(None, {"OPENAI_API_BASE": endpoint})
