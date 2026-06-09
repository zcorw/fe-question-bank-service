# FE Question Bank Service

FastAPI service for reading and maintaining the FE question bank SQLite database.

## Docker On VPS

1. Copy `.env.vps.example` to `.env` on the VPS and adjust paths and ports.
2. Put `fe_siken_questions.sqlite` under `${HOST_DATA_DIR}`.
3. Put cached assets under `${HOST_ASSET_DIR}` when image assets are available.
4. Start runtime:

```bash
docker compose up -d --build question-bank-runtime
curl -fsS http://127.0.0.1:${QUESTION_BANK_RUNTIME_PORT:-8000}/health
```

Start the Admin API only for maintenance windows:

```bash
docker compose --profile admin up -d --build question-bank-admin
```

Runtime mounts database and assets read-only. Admin mounts them read-write and requires
`ADMIN_API_TOKEN`.

## GitHub Actions Deployment

The workflow in `.github/workflows/deploy.yml` runs tests and lint, then deploys to the VPS over SSH.

Required repository secrets:

- `VPS_HOST`
- `VPS_USER`
- `VPS_SSH_KEY`
- `VPS_APP_DIR`

Optional repository variable:

- `QUESTION_BANK_RUNTIME_PORT`, default `8000`

The VPS app directory should already be a clone of this repository with a configured `.env`.
