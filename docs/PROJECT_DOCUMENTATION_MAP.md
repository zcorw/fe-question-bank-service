# Project Documentation Map

## Project Purpose And Product Scope

| Document | Covers |
|---|---|
| [README.md](../README.md) | Short project summary, Docker/VPS deployment entry points, GitHub Actions deployment prerequisites, and links to current operational docs. |
| [PROJECT_GUIDE.md](./PROJECT_GUIDE.md) | Current project purpose, product scope, runtime data set, API overview, local/VPS deployment, backup rules, and verification commands. |
| [01_project_overview.md](./01_project_overview.md) | Original project background, target users, MVP scope, assumptions, and non-goals. Some local terminals may display this legacy document with encoding artifacts. |
| [09_deliverables.md](./09_deliverables.md) | Expected project deliverables and completion artifacts. |
| [TODO.md](./TODO.md) | Historical implementation checklist and project completion tracking. |

## Architecture And Data

| Document | Covers |
|---|---|
| [02_architecture.md](./02_architecture.md) | Original service architecture, runtime/admin responsibilities, module boundaries, and integration direction. |
| [04_data_model.md](./04_data_model.md) | SQLite tables, question/detail relationships, and data model notes. |
| [08_technical_stack.md](./08_technical_stack.md) | Python/FastAPI, SQLite, Docker, testing, and tooling decisions. |
| [question-keyword-taxonomy.md](./question-keyword-taxonomy.md) | Runtime keyword taxonomy design, tag hierarchy, naming rules, and maintenance rules. |
| [question-keyword-generation-report.md](./question-keyword-generation-report.md) | Generated keyword JSON files, coverage counts, low-confidence mappings, canonical tag migration, and Runtime implementation status. |
| [question-search-index.md](./question-search-index.md) | Local/generated question search-index notes. This is not required for current Runtime deployment unless a future feature explicitly reads `data/question_search_index.json`. |

## API And Integration

| Document | Covers |
|---|---|
| [03_api_spec.md](./03_api_spec.md) | Runtime and Admin API endpoints, request/response examples, keyword search behavior, detail response fields, and error codes. |
| [CONSUMER_INTEGRATION_GUIDE.md](./CONSUMER_INTEGRATION_GUIDE.md) | How consuming applications connect through Docker or host networking, call Runtime APIs, proxy image paths, and verify integration. |
| [06_integration_migration.md](./06_integration_migration.md) | Original migration direction for replacing direct SQLite reads with service calls. |
| [CURRENT_PROJECT_MIGRATION_GUIDE.md](./CURRENT_PROJECT_MIGRATION_GUIDE.md) | Current migration notes for this project and existing VPS asset movement. |

## Deployment, Security, And Operations

| Document | Covers |
|---|---|
| [05_security_deployment.md](./05_security_deployment.md) | Original security and deployment model, Runtime/Admin permissions, token rules, backup expectations, and logging notes. Some local terminals may display this legacy document with encoding artifacts. |
| [07_testing_operations.md](./07_testing_operations.md) | Original testing and operations guidance. |
| [.github/workflows/deploy.yml](../.github/workflows/deploy.yml) | CI/CD workflow: tests, lint, SSH deployment to VPS, Docker Compose rebuild, and health check. |
| [PROJECT_GUIDE.md](./PROJECT_GUIDE.md#local-docker-deployment) | Current local Docker deployment steps and common local path issues. |
| [PROJECT_GUIDE.md](./PROJECT_GUIDE.md#vps-docker-deployment) | Current VPS Docker deployment steps, required data/assets paths, and Admin profile usage. |
| [PROJECT_GUIDE.md](./PROJECT_GUIDE.md#backup-and-restore) | Current backup and restore unit: SQLite, keyword JSON files, and image assets. |

## Task Lists And Migration Plans

| Document | Covers |
|---|---|
| [todolist/14_QUESTION_ASSET_SERVICE_MIGRATION.md](./todolist/14_QUESTION_ASSET_SERVICE_MIGRATION.md) | Asset-service migration checklist and completion status. |
| [TODO.md](./TODO.md) | Broader project task status and historical implementation tracking. |

