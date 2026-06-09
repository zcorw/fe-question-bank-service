from fastapi import FastAPI

from question_bank_service.config import ConfigError, Settings, load_settings
from question_bank_service.runtime.router import create_runtime_router


def create_app(settings: Settings | None = None) -> FastAPI:
    app = FastAPI(title="FE Question Bank Service")
    app.state.settings = settings

    @app.get("/health")
    def health() -> dict[str, bool | str]:
        if settings is None:
            return {
                "ok": True,
                "database": "not_configured",
                "readOnly": True,
            }

        database_status = "ready" if settings.database_path.exists() else "missing"
        return {
            "ok": database_status == "ready",
            "database": database_status,
            "readOnly": settings.read_only,
        }

    if settings is not None:
        app.include_router(create_runtime_router(settings))

    return app


def _load_settings_for_asgi() -> Settings | None:
    try:
        return load_settings()
    except ConfigError:
        return None


app = create_app(settings=_load_settings_for_asgi())
