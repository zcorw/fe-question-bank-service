from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_docker_deployment_files_define_runtime_and_admin_modes() -> None:
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")

    assert "uvicorn" in dockerfile
    assert "question_bank_service.app:app" in dockerfile
    assert "question-bank-runtime:" in compose
    assert "question-bank-admin:" in compose
    assert "ENABLE_ADMIN_API=false" in compose
    assert "QUESTION_BANK_READ_ONLY=true" in compose
    assert "ENABLE_ADMIN_API=true" in compose
    assert "QUESTION_BANK_READ_ONLY=false" in compose
    assert 'host_ip: "${QUESTION_BANK_RUNTIME_HOST:-127.0.0.1}"' in compose
    assert 'published: "${QUESTION_BANK_RUNTIME_PORT:-8000}"' in compose
    assert 'host_ip: "${QUESTION_BANK_ADMIN_HOST:-127.0.0.1}"' in compose
    assert 'published: "${QUESTION_BANK_ADMIN_PORT:-8001}"' in compose
    assert "${HOST_DATA_DIR:-./data}:/app/data:ro" in compose
    assert "${HOST_DATA_DIR:-./data}:/app/data:rw" in compose
    assert "fe-shared:" in compose
    assert "external: true" in compose
    assert "curl -fsS http://localhost:8000/health" in compose


def test_github_actions_workflow_tests_and_deploys_to_vps() -> None:
    workflow = (ROOT / ".github/workflows/deploy.yml").read_text(encoding="utf-8")

    assert "workflow_dispatch:" in workflow
    assert "python -m pytest" in workflow
    assert "python -m ruff check ." in workflow
    assert "VPS_HOST" in workflow
    assert "VPS_SSH_KEY" in workflow
    assert "docker compose up -d --build --remove-orphans" in workflow
    assert "curl -fsS http://127.0.0.1:${QUESTION_BANK_RUNTIME_PORT:-8000}/health" in workflow
