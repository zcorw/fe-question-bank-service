from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI(title="FE Question Bank Service")

    @app.get("/health")
    def health() -> dict[str, bool | str]:
        return {
            "ok": True,
            "database": "not_configured",
            "readOnly": True,
        }

    return app


app = create_app()
