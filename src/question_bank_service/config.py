import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path


class ConfigError(ValueError):
    """Raised when required runtime configuration is invalid."""


@dataclass(frozen=True)
class Settings:
    database_path: Path
    asset_root: Path
    read_only: bool
    enable_admin_api: bool
    admin_api_token: str | None
    keyword_taxonomy_path: Path = Path("data/question_keyword_taxonomy.json")
    question_topic_mappings_path: Path = Path("data/question_topic_mappings.json")


def load_settings(env: Mapping[str, str] | None = None) -> Settings:
    values = os.environ if env is None else env
    database_path = Path(
        _optional_non_empty(values.get("QUESTION_DB_PATH"))
        or "/app/data/fe_siken_questions.sqlite"
    )
    asset_root = Path(values.get("QUESTION_ASSET_ROOT", "public/assets/fe-siken"))
    read_only = _parse_bool(values.get("QUESTION_BANK_READ_ONLY"), default=True)
    enable_admin_api = _parse_bool(values.get("ENABLE_ADMIN_API"), default=False)
    admin_api_token = _optional_non_empty(values.get("ADMIN_API_TOKEN"))
    keyword_taxonomy_path = Path(
        values.get("QUESTION_KEYWORD_TAXONOMY_PATH", "data/question_keyword_taxonomy.json")
    )
    question_topic_mappings_path = Path(
        values.get("QUESTION_TOPIC_MAPPINGS_PATH", "data/question_topic_mappings.json")
    )

    if enable_admin_api and admin_api_token is None:
        raise ConfigError("ADMIN_API_TOKEN is required when ENABLE_ADMIN_API is true")

    return Settings(
        database_path=database_path,
        asset_root=asset_root,
        read_only=read_only,
        enable_admin_api=enable_admin_api,
        admin_api_token=admin_api_token,
        keyword_taxonomy_path=keyword_taxonomy_path,
        question_topic_mappings_path=question_topic_mappings_path,
    )


def _optional_non_empty(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def _parse_bool(value: str | None, *, default: bool) -> bool:
    if value is None or value.strip() == "":
        return default

    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False

    raise ConfigError(f"Invalid boolean value: {value}")
