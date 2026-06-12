# Question Asset Service Migration TodoList

## Project Summary

Move FE question images from consuming applications into FE Question Bank Service. The question bank service will own asset storage and serve stable asset paths. FE-Test will continue to render question Markdown and image metadata, but browser-facing image requests will be proxied through FE-Test so the internal question bank runtime does not need to be exposed publicly.

## Source Documents Reviewed

- `README.md`
- `docker-compose.yml`
- `docs/03_api_spec.md`
- `docs/06_integration_migration.md`
- Current architecture decision from deployment discussion: FE-Test and the question bank service share the `fe-shared` Docker network; FE-Test can call `http://question-bank-runtime:8000`, but browsers cannot resolve Docker-internal hostnames.

## Key Requirements

- The question bank service must serve image files from `QUESTION_ASSET_ROOT`.
- Runtime API responses must keep stable image references under `/assets/fe-siken/...`.
- FE-Test must not read question image files directly from its own project after migration.
- FE-Test must proxy browser image requests to the question bank runtime instead of exposing the runtime service publicly.
- Docker deployment must mount the asset directory on the question bank service side.
- Backup and operations documentation must treat SQLite and image assets as one restore unit.

## Questions / Assumptions

- Assumption: public image paths remain `/assets/fe-siken/...`.
- Assumption: FE-Test is the only public web entrypoint for rendered quiz pages.
- Assumption: `question-bank-runtime` remains bound to the VPS/private network, not directly public.
- Assumption: existing SQLite `images_json` and Markdown question content may contain either camelCase or snake_case image fields; the service should normalize its API output where needed.

## Development TodoList

- [x] A001 [P0] Add static asset serving to FE Question Bank Service
  Goal: Serve cached question images from `QUESTION_ASSET_ROOT` at `/assets/fe-siken/...`.
  Notes: Mount FastAPI `StaticFiles` only for the configured asset root. Missing files should return normal 404 responses. Runtime and Admin containers already mount the asset directory with different read/write modes.
  Likely files/modules: `src/question_bank_service/app.py`, `src/question_bank_service/config.py`, `tests/`.
  Depends on: None.
  Verify: Add a fixture image under a temporary asset root and assert `GET /assets/fe-siken/<file>` returns the image bytes; assert a missing image returns 404. Run `python -m pytest`.

- [x] A002 [P0] Normalize runtime image metadata in API responses
  Goal: Make Runtime API responses expose stable image paths that clients can consume without knowing local filesystem layout.
  Notes: Preserve existing `questionText` Markdown. Normalize `images_json` entries so clients can rely on `publicPath` under `/assets/fe-siken/...`; do not expose host filesystem paths. If legacy DB rows contain `public_path` or `local_path`, map them to the API schema consistently.
  Likely files/modules: `src/question_bank_service/db/repositories.py`, `src/question_bank_service/runtime/schemas.py`, `src/question_bank_service/runtime/service.py`, `tests/`.
  Depends on: A001.
  Verify: Repository/API tests cover camelCase and snake_case image metadata, rows without images, and Markdown image references. Run `python -m pytest`.

- [x] A003 [P1] Document service-owned asset storage and backup rules
  Goal: Make operators understand that image assets belong to FE Question Bank Service and must be backed up with SQLite.
  Notes: Document that `QUESTION_ASSET_ROOT` is container-internal, `HOST_ASSET_DIR` is the VPS host directory, and both SQLite and assets are required for a complete restore.
  Likely files/modules: `README.md`, `.env.vps.example`, `docs/05_security_deployment.md`, `docs/07_testing_operations.md`.
  Depends on: A001.
  Verify: Documentation includes local and VPS path examples and backup/restore checklist.

- [ ] A004 [P0] Add FE-Test browser-facing asset proxy
  Goal: Let browsers load `/assets/fe-siken/...` from the FE-Test domain while FE-Test fetches the real file from `QUESTION_BANK_SERVICE_URL`.
  Notes: The proxy must reject paths outside `/assets/fe-siken/`, preserve image content type where possible, and return upstream 404s clearly. It must not require Telegram credentials.
  Likely files/modules: FE-Test `src/app/assets/fe-siken/[...path]/route.ts` or equivalent route handler, FE-Test config/env modules, tests.
  Depends on: A001.
  Verify: With `QUESTION_BANK_SERVICE_URL=http://question-bank-runtime:8000` or a local service URL, a request to FE-Test `/assets/fe-siken/<file>` returns the image bytes. Run FE-Test `pnpm typecheck`, `pnpm lint`, `pnpm test`.

- [ ] A005 [P1] Ensure FE-Test Markdown rendering uses proxied relative image paths
  Goal: Render question Markdown images through FE-Test's own `/assets/fe-siken/...` route instead of direct DB/app-local files or Docker-internal service URLs.
  Notes: Keep existing layout preservation behavior. If the service returns absolute internal URLs, rewrite them to relative asset paths before rendering. Prefer keeping question bank API output relative to avoid browser DNS problems.
  Likely files/modules: FE-Test Markdown rendering components, question DTO mapping, HTTP provider tests.
  Depends on: A002, A004.
  Verify: Unit/component test renders a Markdown image and asserts the final `img.src` points to `/assets/fe-siken/...`. Run relevant FE-Test Playwright test if the rendered question page is affected.

- [ ] A006 [P1] Update FE-Test deployment configuration for asset proxy mode
  Goal: Remove FE-Test's need to mount or manage question image cache files directly.
  Notes: Keep `QUESTION_BANK_SERVICE_URL` pointed at `http://question-bank-runtime:8000` inside Docker Compose. Document that image requests are browser-facing through FE-Test, service-facing through the shared Docker network.
  Likely files/modules: FE-Test `deploy/docker-compose.yml`, FE-Test `.env.example` or deployment docs.
  Depends on: A004, A005.
  Verify: `docker compose config` succeeds. FE-Test container can fetch the question bank runtime health endpoint and proxy one image.

- [ ] A007 [P1] Add end-to-end verification for a question with an image
  Goal: Prove a quiz question containing an image renders correctly without FE-Test reading local image files.
  Notes: Use a local fixture or a seeded test image. The test should assert the rendered question contains an image, the image request succeeds, and no direct SQLite/file image access is required by FE-Test.
  Likely files/modules: FE-Test Playwright tests, fixture setup, question bank service fixture data.
  Depends on: A004, A005.
  Verify: Run FE-Test `pnpm test:e2e` or the narrowed Playwright command for the quiz detail page.

- [ ] A008 [P2] Add operational migration checklist for existing VPS assets
  Goal: Provide a safe manual path to move existing image files from FE-Test or other app directories into FE Question Bank Service storage.
  Notes: Include commands to create the asset directory, copy files, verify counts, restart the service, and test one image through FE-Test. Do not delete old image files until verification passes.
  Likely files/modules: `docs/CURRENT_PROJECT_MIGRATION_GUIDE.md`, `README.md`, FE-Test migration docs.
  Depends on: A003, A006.
  Verify: Checklist includes rollback notes and does not require exposing question-bank-runtime publicly.

- [ ] A009 [P2] Add Docker Compose verification for assets
  Goal: Confirm the service can serve mounted assets in Docker with runtime read-only and admin read-write mounts.
  Notes: Use a fixture image under `HOST_ASSET_DIR` and request it from the runtime container or host-published runtime port. Keep database files out of git.
  Likely files/modules: `docker-compose.yml`, `README.md`, optional `scripts/validate_deploy_assets.*`.
  Depends on: A001, A003.
  Verify: `docker compose config`, `docker compose up -d --build question-bank-runtime`, `curl -fsS http://127.0.0.1:${QUESTION_BANK_RUNTIME_PORT:-8000}/assets/fe-siken/<fixture>` succeeds.

## Acceptance Criteria

- FE Question Bank Service serves `/assets/fe-siken/...` from `QUESTION_ASSET_ROOT`.
- Runtime API image metadata uses stable public paths and does not expose host filesystem paths.
- FE-Test loads question images through its own public route and proxies to the question bank runtime internally.
- FE-Test no longer requires a local question image cache mount for normal quiz rendering.
- VPS deployment docs explain `HOST_ASSET_DIR`, `QUESTION_ASSET_ROOT`, and SQLite-plus-assets backup requirements.
- `python -m pytest` passes in FE Question Bank Service.
- FE-Test `pnpm typecheck`, `pnpm lint`, `pnpm test`, and relevant Playwright verification pass after FE-Test items are implemented.
- Docker Compose verification proves the runtime container can serve a mounted image.

## Suggested Execution Order

1. Service asset serving: A001.
2. API metadata compatibility: A002.
3. Service docs and backup notes: A003.
4. FE-Test proxy and renderer migration: A004, A005.
5. FE-Test deployment update: A006.
6. E2E and Docker verification: A007, A009.
7. VPS migration checklist: A008.
