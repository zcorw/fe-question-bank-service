from pathlib import Path

import pytest

from question_bank_service.config import ConfigError, load_settings


def test_load_settings_uses_runtime_safe_defaults() -> None:
    settings = load_settings(
        {
            "QUESTION_DB_PATH": "data/fe_siken_questions.sqlite",
        }
    )

    assert settings.database_path == Path("data/fe_siken_questions.sqlite")
    assert settings.asset_root == Path("public/assets/fe-siken")
    assert settings.read_only is True
    assert settings.enable_admin_api is False
    assert settings.admin_api_token is None


def test_load_settings_requires_database_path() -> None:
    with pytest.raises(ConfigError, match="QUESTION_DB_PATH is required"):
        load_settings({})


def test_load_settings_requires_admin_token_when_admin_api_enabled() -> None:
    with pytest.raises(ConfigError, match="ADMIN_API_TOKEN is required"):
        load_settings(
            {
                "QUESTION_DB_PATH": "data/fe_siken_questions.sqlite",
                "ENABLE_ADMIN_API": "true",
            }
        )


def test_load_settings_allows_admin_mode_with_token_and_writable_database() -> None:
    settings = load_settings(
        {
            "QUESTION_DB_PATH": "data/fe_siken_questions.sqlite",
            "QUESTION_ASSET_ROOT": "assets",
            "QUESTION_BANK_READ_ONLY": "false",
            "ENABLE_ADMIN_API": "true",
            "ADMIN_API_TOKEN": "secret-token",
        }
    )

    assert settings.database_path == Path("data/fe_siken_questions.sqlite")
    assert settings.asset_root == Path("assets")
    assert settings.read_only is False
    assert settings.enable_admin_api is True
    assert settings.admin_api_token == "secret-token"
