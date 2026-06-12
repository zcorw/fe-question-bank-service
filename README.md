# FE Question Bank Service

FastAPI service for reading and maintaining the FE question bank SQLite database.

## Docker On VPS

1. Copy `.env.vps.example` to `.env` on the VPS and adjust paths and ports.
2. Put `fe_siken_questions.sqlite` under `${HOST_DATA_DIR}`.
3. Put cached assets under `${HOST_ASSET_DIR}` when image assets are available.
4. Start runtime:

`QUESTION_DB_PATH` is optional. By default the service reads
`/app/data/fe_siken_questions.sqlite` inside the container. The VPS host
directory `${HOST_DATA_DIR}` is mounted to `/app/data`, so the matching host file
is `${HOST_DATA_DIR}/fe_siken_questions.sqlite`. Override `QUESTION_DB_PATH`
only when the SQLite file should use a different container-internal path.

`QUESTION_BANK_RUNTIME_HOST` and `QUESTION_BANK_ADMIN_HOST` control the VPS host
IP address used by Docker port publishing. Keep them at `127.0.0.1` when the
service should only be reachable from the VPS or an internal reverse proxy. Set
one to `0.0.0.0` only when that service should bind to all host interfaces.
Inside the container, Uvicorn still listens on `0.0.0.0:8000`.

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
