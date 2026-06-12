from pathlib import Path

from fastapi.testclient import TestClient

from question_bank_service.app import create_app
from question_bank_service.config import Settings


def test_serves_question_assets_from_configured_asset_root(tmp_path: Path) -> None:
    asset_root = tmp_path / "assets"
    nested_dir = asset_root / "r07_haru"
    nested_dir.mkdir(parents=True)
    image_bytes = b"\x89PNG\r\n\x1a\nfixture"
    (nested_dir / "q28.png").write_bytes(image_bytes)
    db_path = tmp_path / "questions.sqlite"
    db_path.write_bytes(b"")

    client = TestClient(create_app(settings=_settings(db_path, asset_root)))

    response = client.get("/assets/fe-siken/r07_haru/q28.png")

    assert response.status_code == 200
    assert response.content == image_bytes
    assert response.headers["content-type"] == "image/png"


def test_missing_question_asset_returns_404(tmp_path: Path) -> None:
    asset_root = tmp_path / "assets"
    asset_root.mkdir()
    db_path = tmp_path / "questions.sqlite"
    db_path.write_bytes(b"")

    client = TestClient(create_app(settings=_settings(db_path, asset_root)))

    response = client.get("/assets/fe-siken/missing.png")

    assert response.status_code == 404


def _settings(db_path: Path, asset_root: Path) -> Settings:
    return Settings(
        database_path=db_path,
        asset_root=asset_root,
        read_only=True,
        enable_admin_api=False,
        admin_api_token=None,
    )
