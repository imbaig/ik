"""Release configuration tests only; test credentials are synthetic, not application keys."""

import pytest

from music_store.config import ConfigurationError
from music_store.deployment import SOURCE_REVISION, access_gate, metadata, secret_value


def test_default_gate_fails_closed_and_never_echoes_values():
    with pytest.raises(ConfigurationError, match="Login requires") as error:
        access_gate({"APP_LOGIN_USER": "test-user", "APP_LOGIN_PASSWORD": "short"}, "0.0.0.0")
    assert "short" not in str(error.value)
    with pytest.raises(ConfigurationError):
        access_gate({}, "0.0.0.0")


def test_required_gate_accepts_only_correct_pair_and_supports_unicode():
    gate = access_gate(
        {"APP_LOGIN_USER": "test-user", "APP_LOGIN_PASSWORD": "test-only-passphraseé"}, "0.0.0.0"
    )
    assert gate("test-user", "test-only-passphraseé")
    assert not gate("wrong", "test-only-passphraseé")
    assert not gate("test-user", "wrong")


def test_local_optout_rejects_container_wide_bind():
    assert access_gate({"APP_ACCESS_MODE": "local-only"}, "127.0.0.1") is None
    for host in ("0.0.0.0", "unexpected"):
        with pytest.raises(ConfigurationError, match="loopback"):
            access_gate({"APP_ACCESS_MODE": "local-only"}, host)
    with pytest.raises(ConfigurationError):
        access_gate({"APP_ACCESS_MODE": "disabled"}, "127.0.0.1")


def test_runtime_secret_file_and_ambiguity(tmp_path):
    path = tmp_path / "secret"
    path.write_text("test-only-long-passphrase\n")
    assert (
        secret_value("APP_LOGIN_PASSWORD", {"APP_LOGIN_PASSWORD_FILE": str(path)})
        == "test-only-long-passphrase"
    )
    with pytest.raises(ConfigurationError):
        secret_value(
            "APP_LOGIN_PASSWORD",
            {"APP_LOGIN_PASSWORD_FILE": str(path), "APP_LOGIN_PASSWORD": "ambiguous"},
        )
    with pytest.raises(ConfigurationError, match="Cannot read"):
        secret_value("APP_LOGIN_PASSWORD", {"APP_LOGIN_PASSWORD_FILE": str(path / "missing")})


def test_metadata_identifies_source_and_package_without_environment_leak():
    result = metadata({"PACKAGE_REVISION": "a" * 40, "OPENAI_API_KEY": "never-output"})
    assert result["input_source_revision"] == SOURCE_REVISION
    assert result["packaging_revision"] == "a" * 40
    assert result["mode"] == "provider-backed" and "never-output" not in str(result)
    assert (
        metadata({"PACKAGE_REVISION": "b" * 40}, smoke_test=True)["mode"]
        == "deterministic-test-only"
    )
    with pytest.raises(ConfigurationError):
        metadata({})
