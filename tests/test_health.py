from fastapi.testclient import TestClient

from question_bank_service.app import create_app


def test_health_endpoint_reports_ready_runtime() -> None:
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "ok": True,
        "database": "not_configured",
        "readOnly": True,
    }
