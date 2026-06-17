# FE Question Bank Service Guide

## Purpose

FE Question Bank Service is the HTTP service layer for the Fundamental
Information Technology Engineer Examination (FE) question bank.

The project owns the shared question-bank runtime contract so consumer
applications do not read `fe_siken_questions.sqlite` directly. It provides:

- Read-only Runtime APIs for question selection, details, keyword taxonomy, and
  static assets.
- Maintenance-only Admin APIs for refreshing and validating question details.
- Docker Compose deployment for local, VPS, and shared-network integration.
- Generated keyword taxonomy and question topic mappings for precise study
  topic search.
- Optional learning explanation fields stored in SQLite and returned by detail
  endpoints when present.

## Main Consumers

- FE-Test web/bot runtime.
- Daily practice generation tools.
- Other FE study applications that need question candidates, details, answers,
  explanations, or image assets through HTTP.

Consumer applications should call the Runtime API. They should not mount or read
the SQLite database directly.

## Runtime Data

The runtime data set is made of:

```text
data/fe_siken_questions.sqlite
data/question_keyword_taxonomy.json
data/question_topic_mappings.json
public/assets/fe-siken/
```

`data/question_keyword_search_fixtures.json` is for contract tests and
integration verification. It is not required by the Runtime service at request
time.

The following local/generated artifacts are not required for deployment unless a
future feature explicitly reads them:

```text
data/question_search_index.json
docs/question-search-index.md
```

## Runtime API Summary

Base URL in Docker shared network:

```text
http://question-bank-runtime:8000
```

Base URL from the host-published port:

```text
http://127.0.0.1:${QUESTION_BANK_RUNTIME_PORT}
```

Common endpoints:

```text
GET  /health
GET  /keywords
GET  /questions/candidates
POST /questions/candidates/search
GET  /questions/by-url?url=<question-url>
GET  /questions/{questionId}
POST /questions/details/batch
GET  /assets/fe-siken/<asset-path>
```

`GET /keywords` returns the searchable taxonomy from
`data/question_keyword_taxonomy.json`.

`POST /questions/candidates/search` supports:

- `keywords`
- `topicTags`
- `knowledgePoints`
- `syllabusArea`
- `examPart`
- `limit`
- `offset`

Unknown or underfilled searches return a `shortage` object and do not silently
fall back to unrelated default questions.

Question detail responses may include:

- `learningExplanation`
- `explanationJa`
- `distractorExplanationsJa`
- `knowledgePointJa`
- `examPointJa`
- `commonTrapJa`
- `primaryTag`
- `topicTags`
- `knowledgePoints`
- `syllabusArea`

Full endpoint schemas and examples are maintained in
[`docs/03_api_spec.md`](03_api_spec.md).

## Local Docker Deployment

For local Windows development, keep `.env` host paths relative to the repository:

```env
QUESTION_BANK_RUNTIME_HOST=127.0.0.1
QUESTION_BANK_RUNTIME_PORT=18010
QUESTION_ASSET_ROOT=/app/public/assets/fe-siken
HOST_DATA_DIR=./data
HOST_ASSET_DIR=./public/assets/fe-siken
```

Create the shared Docker network once:

```powershell
docker network inspect fe-shared
docker network create fe-shared
```

Start the Runtime service:

```powershell
docker compose up -d --build question-bank-runtime
curl.exe -fsS http://127.0.0.1:18010/health
```

If the service starts but question endpoints fail with `unable to open database
file`, check that `HOST_DATA_DIR` points to a host directory containing
`fe_siken_questions.sqlite` and the keyword JSON files.

## VPS Docker Deployment

On the VPS, `.env` usually uses absolute host paths:

```env
QUESTION_BANK_RUNTIME_HOST=127.0.0.1
QUESTION_BANK_RUNTIME_PORT=8000
QUESTION_ASSET_ROOT=/app/public/assets/fe-siken
HOST_DATA_DIR=/opt/fe-question-bank/data
HOST_ASSET_DIR=/opt/fe-question-bank/public/assets/fe-siken
```

Expected host files/directories:

```text
/opt/fe-question-bank/data/fe_siken_questions.sqlite
/opt/fe-question-bank/data/question_keyword_taxonomy.json
/opt/fe-question-bank/data/question_topic_mappings.json
/opt/fe-question-bank/public/assets/fe-siken/
```

Start or update the service:

```bash
docker network inspect fe-shared >/dev/null 2>&1 || docker network create fe-shared
docker compose up -d --build question-bank-runtime
curl -fsS http://127.0.0.1:${QUESTION_BANK_RUNTIME_PORT:-8000}/health
```

Use Admin only during maintenance windows:

```bash
docker compose --profile admin up -d --build question-bank-admin
```

Admin API requires `ADMIN_API_TOKEN` and mounts data read-write.

## GitHub Actions Deployment

Workflow:

```text
.github/workflows/deploy.yml
```

On push to `main`, the workflow:

1. Installs Python dependencies.
2. Runs `python -m pytest`.
3. Runs `python -m ruff check .`.
4. SSHes into the VPS.
5. Pulls `main`.
6. Runs `docker compose up -d --build --remove-orphans`.
7. Checks `/health`.

Required repository secrets:

- `VPS_HOST`
- `VPS_USER`
- `VPS_SSH_KEY`
- `VPS_APP_DIR`

Optional repository variable:

- `QUESTION_BANK_RUNTIME_PORT`

## Consumer Integration

Docker Compose consumers on the same VPS should call:

```text
http://question-bank-runtime:8000
```

Do not use `localhost` from another container. `localhost` points to the current
container.

Browser-facing applications should proxy image paths. The browser should request
the consumer app's public route, while the server-side proxy fetches from:

```text
http://question-bank-runtime:8000/assets/fe-siken/<asset-path>
```

Detailed consumer patterns are maintained in
[`docs/CONSUMER_INTEGRATION_GUIDE.md`](CONSUMER_INTEGRATION_GUIDE.md).

## Backup and Restore

SQLite and image assets are one operational restore unit:

```text
${HOST_DATA_DIR}/fe_siken_questions.sqlite
${HOST_DATA_DIR}/question_keyword_taxonomy.json
${HOST_DATA_DIR}/question_topic_mappings.json
${HOST_ASSET_DIR}/
```

Restoring only SQLite can leave valid question rows with broken image paths or
missing keyword mappings.

Before modifying SQLite locally, create a backup under:

```text
data/backups/
```

Backups and SQLite files are intentionally ignored by Git.

## Documentation Map

| Document | Purpose |
| --- | --- |
| [`README.md`](../README.md) | Short project entrypoint and deployment quick start |
| [`docs/PROJECT_GUIDE.md`](PROJECT_GUIDE.md) | Current project purpose, API, deployment, and operations guide |
| [`docs/03_api_spec.md`](03_api_spec.md) | Runtime/Admin API details |
| [`docs/CONSUMER_INTEGRATION_GUIDE.md`](CONSUMER_INTEGRATION_GUIDE.md) | How external applications integrate with the service |
| [`docs/question-keyword-taxonomy.md`](question-keyword-taxonomy.md) | Keyword taxonomy design |
| [`docs/question-keyword-generation-report.md`](question-keyword-generation-report.md) | Keyword generation report and coverage |
| [`docs/CURRENT_PROJECT_MIGRATION_GUIDE.md`](CURRENT_PROJECT_MIGRATION_GUIDE.md) | Existing project migration notes |

Some older documents may contain encoding artifacts in local terminals. Prefer
this guide and the API spec as the current operational reference.

## Verification Commands

```bash
python -m pytest
python -m ruff check src tests scripts/generate_question_keywords.py scripts/populate_learning_explanations.py
docker compose config
```

Runtime smoke tests:

```bash
curl -fsS http://127.0.0.1:${QUESTION_BANK_RUNTIME_PORT:-8000}/health
curl -fsS http://127.0.0.1:${QUESTION_BANK_RUNTIME_PORT:-8000}/keywords
```
