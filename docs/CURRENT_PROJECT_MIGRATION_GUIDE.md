# Current Project Migration Guide

This guide explains how the current maintenance project should move daily
practice generation, question refresh, and question format validation from
direct SQLite/script access to the FE Question Bank Service.

## Scope

Use the service as the default integration boundary for runtime reads and
maintenance writes:

| Workflow | Previous approach | Service-based approach |
| --- | --- | --- |
| Daily practice generation | Read `data/fe_siken_questions.sqlite` directly in the consumer project. | Call the Runtime API, then render the returned question details. |
| Question refresh | Run scraper or ad hoc SQLite update scripts against the shared database. | Start the Admin API during a maintenance window and call `/admin/questions/refresh`. |
| Format validation | Inspect cached rows or HTML with local scripts. | Call `/admin/questions/validate-cache` for selected URLs, and run `scripts/validate_question_bank.py` for release checks. |
| Backup before maintenance | Copy the SQLite file manually. | Run `scripts/backup_db.py` before Admin API writes. |

The SQLite file remains the source of truth, but external projects should stop
opening it directly during normal runtime paths.

## Files To Replace Or Keep

Replace direct SQLite reads in downstream code with HTTP calls to the Runtime API:

- Code that opens `data/fe_siken_questions.sqlite`.
- Code that queries `questions` for candidate URLs, question text, choices,
  answer, or explanation.
- Code that expects the SQLite schema to be available inside the caller process.

Keep these scripts in this repository:

- `scripts/generate_daily_practice.py`: generates practice Markdown. Prefer
  `--base-url` for Runtime API mode. Use `--db-path` only as a local fallback.
- `scripts/backup_db.py`: creates a timestamped `.bak` copy before maintenance.
- `scripts/validate_question_bank.py`: validates persisted question details
  before release or after refresh.

Do not commit `data/fe_siken_questions.sqlite`, generated backup files, cache
images, or generated daily practice output unless a task explicitly requires it.

## Runtime API

Runtime mode is read-only and is the default for production consumers.

Start it locally:

```powershell
$env:PYTHONPATH = "src"
$env:QUESTION_DB_PATH = "data/fe_siken_questions.sqlite"
$env:QUESTION_BANK_READ_ONLY = "true"
$env:ENABLE_ADMIN_API = "false"
python -m uvicorn question_bank_service.app:app --host 127.0.0.1 --port 8000
```

Docker runtime mode:

```bash
docker compose up -d --build question-bank-runtime
curl -fsS http://127.0.0.1:8000/health
```

Primary Runtime API calls:

```bash
curl -fsS "http://127.0.0.1:8000/questions/candidates?category=management&limit=5"
```

```bash
curl -fsS -X POST "http://127.0.0.1:8000/questions/details/batch" \
  -H "content-type: application/json" \
  -d "{\"urls\":[\"https://example.test/question\"],\"includeAnswer\":false,\"includeExplanation\":false}"
```

Use `/questions/by-url?url=...` or `/questions/{question_id}` for single-detail
lookups. Set `includeAnswer=true` only for answer reveal, grading, or admin
checks.

## Daily Practice Generation

Recommended service-backed command:

```bash
python scripts/generate_daily_practice.py \
  --base-url http://127.0.0.1:8000 \
  --category management \
  --limit 5 \
  --title "Daily FE Practice" \
  --output tmp/daily-practice.md
```

Fallback command if the service is unavailable but the local SQLite file is
present:

```bash
python scripts/generate_daily_practice.py \
  --db-path data/fe_siken_questions.sqlite \
  --category management \
  --limit 5 \
  --title "Daily FE Practice" \
  --output tmp/daily-practice.md
```

Consumer projects should implement the same order:

1. Try the Runtime API.
2. Fail closed for user-facing flows that must not show stale or partial data.
3. For scheduled document generation, optionally fall back to the local SQLite
   path and mark the generated document as produced from fallback data.

## Admin API

Admin mode is writable and should run only during maintenance windows.

Start it locally:

```powershell
$env:PYTHONPATH = "src"
$env:QUESTION_DB_PATH = "data/fe_siken_questions.sqlite"
$env:QUESTION_BANK_READ_ONLY = "false"
$env:ENABLE_ADMIN_API = "true"
$env:ADMIN_API_TOKEN = "replace-with-a-secret"
python -m uvicorn question_bank_service.app:app --host 127.0.0.1 --port 8001
```

Docker admin mode:

```bash
ADMIN_API_TOKEN=replace-with-a-secret docker compose --profile admin up -d --build question-bank-admin
curl -fsS http://127.0.0.1:8001/health
```

Refresh a question:

```bash
curl -fsS -X POST "http://127.0.0.1:8001/admin/questions/refresh" \
  -H "authorization: Bearer replace-with-a-secret" \
  -H "content-type: application/json" \
  -d "{\"url\":\"https://example.test/question\",\"force\":true}"
```

Validate cached details for known URLs:

```bash
curl -fsS -X POST "http://127.0.0.1:8001/admin/questions/validate-cache" \
  -H "authorization: Bearer replace-with-a-secret" \
  -H "content-type: application/json" \
  -d "{\"urls\":[\"https://example.test/question\"]}"
```

The Admin API requires `ADMIN_API_TOKEN` when `ENABLE_ADMIN_API=true`. Runtime
containers mount data read-only; Admin containers mount data read-write.

## Maintenance Runbook

Before a refresh:

```bash
python scripts/backup_db.py \
  --db-path data/fe_siken_questions.sqlite \
  --backup-dir data/backups
```

During refresh:

1. Start Admin API.
2. Refresh the target URL with `/admin/questions/refresh`.
3. Validate the refreshed URL with `/admin/questions/validate-cache`.
4. Stop Admin API after the maintenance window.

After refresh:

```bash
python scripts/validate_question_bank.py --db-path data/fe_siken_questions.sqlite --json
python -m pytest
python -m ruff check .
python -m compileall -q src tests scripts
```

## Degradation And Rollback

If Runtime API is unavailable:

- Scheduled generators may retry, then fall back to `--db-path` when the local
  SQLite file is available and trusted.
- Interactive consumers should return a service-unavailable response instead of
  silently using stale data.
- Do not enable Admin API as a runtime fallback.

If an Admin refresh corrupts or removes expected details:

1. Stop Admin API.
2. Restore the newest known-good backup created by `scripts/backup_db.py`.
3. Run `scripts/validate_question_bank.py --json`.
4. Restart Runtime API and check `/health`.
5. Re-run the daily practice generation command with `--base-url`.

## Verification

Minimum migration verification:

```bash
python scripts/generate_daily_practice.py \
  --base-url http://127.0.0.1:8000 \
  --limit 1 \
  --title "Daily FE Practice Verification" \
  --output tmp/daily-practice-verification.md

python scripts/validate_question_bank.py --db-path data/fe_siken_questions.sqlite --json
python -m pytest
python -m ruff check .
python -m compileall -q src tests scripts
```

The generated Markdown should contain one question heading, question text, answer
choices, and a source URL.

## Existing VPS Asset Migration

Use this checklist when an existing VPS already has question images under an
application-owned directory such as `/opt/fe-quiz-bot/assets/fe-siken/`.
The goal is to copy those files into FE Question Bank Service storage without
deleting the original files until runtime verification passes.

Set paths for the current host:

```bash
OLD_ASSET_DIR=/opt/fe-quiz-bot/assets/fe-siken
HOST_ASSET_DIR=/opt/fe-question-bank/public/assets/fe-siken
```

Create the destination and compare file counts:

```bash
sudo mkdir -p "${HOST_ASSET_DIR}"
find "${OLD_ASSET_DIR}" -type f | wc -l
find "${HOST_ASSET_DIR}" -type f | wc -l
```

Preview the copy first:

```bash
rsync -a --dry-run "${OLD_ASSET_DIR}/" "${HOST_ASSET_DIR}/"
```

If the dry run looks correct, copy the files:

```bash
rsync -a "${OLD_ASSET_DIR}/" "${HOST_ASSET_DIR}/"
find "${OLD_ASSET_DIR}" -type f | wc -l
find "${HOST_ASSET_DIR}" -type f | wc -l
```

Restart or deploy FE Question Bank Service, then verify the runtime container
can serve a known image:

```bash
docker compose up -d --build question-bank-runtime
curl -fsS "http://127.0.0.1:${QUESTION_BANK_RUNTIME_PORT:-8000}/assets/fe-siken/<known-image-path>" --output /tmp/question-asset-check
```

If FE-Test is already connected to the shared Docker network, verify the public
browser path through FE-Test as well:

```bash
curl -fsS "https://<fe-test-domain>/assets/fe-siken/<known-image-path>" --output /tmp/fe-test-asset-check
```

Do not delete `${OLD_ASSET_DIR}` during the same maintenance window. Keep it as
a rollback source until:

1. `question-bank-runtime` serves `/assets/fe-siken/...`.
2. FE-Test renders a question with an image through its own `/assets/fe-siken/...`
   proxy path.
3. SQLite and `${HOST_ASSET_DIR}` have both been included in the backup plan.

Rollback is file-copy only: point FE-Test back to its previous image setup or
copy the old files from `${OLD_ASSET_DIR}` again. Do not expose
`question-bank-runtime` publicly just to make browser image loading work; use
the FE-Test proxy route instead.
