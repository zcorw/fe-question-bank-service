# Project Summary

FE Question Bank Service 是一个独立题库服务，用于把 `fe_siken_questions.sqlite` 的读取、题目详情抽取、图片缓存和格式保真校验从 FE-Test 与当前维护项目中抽离出来。MVP 重点是 Runtime 只读 API、Admin 维护 API、现有 SQLite 兼容、FE-Test HTTP Provider 迁移路径。

## Source Documents Reviewed

- `D:\Workspace\AI\FE-Test\docs\QUESTION_DB_RUNTIME_USAGE.md`：说明 FE-Test 对题库的只读调用链、路径配置、查询函数和运行时边界。
- `D:\Workspace\AI\FE-QuestionBank-Service\docs\01_project_overview.md`：项目目标、用户、MVP 和非目标。
- `D:\Workspace\AI\FE-QuestionBank-Service\docs\02_architecture.md`：Runtime/Admin 服务边界与模块结构。
- `D:\Workspace\AI\FE-QuestionBank-Service\docs\03_api_spec.md`：API endpoint、请求响应和错误码。
- `D:\Workspace\AI\FE-QuestionBank-Service\docs\04_data_model.md`：现有 SQLite 表结构和关联策略。
- `D:\Workspace\AI\FE-QuestionBank-Service\docs\05_security_deployment.md`：权限、部署和写操作控制。
- `D:\Workspace\AI\FE-QuestionBank-Service\docs\06_integration_migration.md`：FE-Test 与当前维护项目迁移路径。
- `D:\Workspace\AI\FE-QuestionBank-Service\docs\07_testing_operations.md`：测试、性能和发布检查。
- `D:\Workspace\AI\FE-QuestionBank-Service\docs\08_technical_stack.md`：推荐技术栈与约束。
- `D:\Workspace\AI\FE-QuestionBank-Service\docs\09_deliverables.md`：最终代码和文档交付物，包含 FE-Test 与当前维护项目的改造说明文档要求。

## Key Requirements

- Runtime API 必须只读读取 `fe_siken_questions.sqlite`。
- Runtime API 必须支持关键词、候选题、单题详情和批量详情查询。
- Admin API 必须支持刷新单题、补齐缺失详情和缓存校验。
- API 对外必须暴露 `questionId`，内部继续兼容 URL 关联。
- FE-Test 必须可以通过 Provider 抽象在 SQLite 和 HTTP 之间切换。
- 当前维护项目应逐步从直接 SQLite/脚本调用迁移到服务 API。
- 格式保真必须覆盖指数、上下标、overline 和嵌套 span。
- 最终必须输出 FE-Test 改造说明文档和当前维护项目改造说明文档。

## Questions / Assumptions

- 假设 MVP 使用 Python FastAPI。
- 假设现有 SQLite 表结构暂不强制迁移。
- 假设生产 Runtime 默认关闭 Admin API。
- 待确认：是否需要 Admin 服务独立部署，还是同一镜像通过环境变量控制。
- 待确认：题库 DB 发布流程采用文件替换还是服务内增量刷新。

## Development TodoList

- [x] T001 [P0] 初始化 Python 服务项目
  Goal: 创建可运行的 FastAPI 项目骨架。
  Notes: 使用 `src/question_bank_service` 包结构，配置 `pyproject.toml`、pytest、ruff 或等价工具。
  Likely files/modules: `pyproject.toml`, `src/question_bank_service/app.py`, `tests/`.
  Depends on: None.
  Verify: `python -m pytest` 可执行且至少有健康检查测试。

- [x] T002 [P0] 实现配置加载
  Goal: 从环境变量读取数据库路径、资产目录、只读模式和 Admin 开关。
  Notes: 配置缺失时给出明确错误；Runtime 模式默认只读。
  Likely files/modules: `src/question_bank_service/config.py`.
  Depends on: T001.
  Verify: 覆盖默认值、缺失 DB 路径、Admin token 配置测试。

- [x] T003 [P0] 实现 SQLite repository
  Goal: 封装关键词、候选题、详情、ID/URL 关联查询。
  Notes: 兼容 `questions.url = question_details.question_url`；解析 `choices_json` 和 `images_json`。
  Likely files/modules: `src/question_bank_service/db/sqlite.py`, `src/question_bank_service/db/repositories.py`.
  Depends on: T002.
  Verify: 使用 fixture SQLite 测试所有查询。

- [x] T004 [P0] 实现 Runtime API
  Goal: 提供 `/health`、`/keywords`、候选题查询、单题详情、批量详情接口。
  Notes: `includeAnswer=false` 时不能返回答案和解析；batch 返回顺序应与请求 URL 顺序一致。
  Likely files/modules: `src/question_bank_service/runtime/router.py`, `runtime/service.py`, `runtime/schemas.py`.
  Depends on: T003.
  Verify: API 集成测试覆盖所有 Runtime endpoint。

- [x] T005 [P1] 迁入题目详情解析模块
  Goal: 将当前维护项目中的详情抓取和 HTML 解析逻辑整理为可 import 模块。
  Notes: 保留指数、上下标、overline、嵌套 span 的保真逻辑。
  Likely files/modules: `src/question_bank_service/scraper/html_parser.py`, `detail_fetcher.py`, `asset_cache.py`.
  Depends on: T001.
  Verify: 解析 fixture HTML，断言 `2^5`、`¬x`、`¬y` 等文本不丢失。

- [x] T006 [P1] 实现 Admin API
  Goal: 提供单题刷新、缺失详情补齐、缓存校验接口。
  Notes: Admin API 需要 token；写库使用事务；批量刷新返回成功和失败列表。
  Likely files/modules: `src/question_bank_service/admin/router.py`, `admin/service.py`, `admin/schemas.py`.
  Depends on: T003, T005.
  Verify: token 校验、单题刷新、校验失败响应测试。

- [x] T007 [P1] 增加格式保真 validator
  Goal: 自动发现候选解析问题。
  Notes: 至少覆盖选择项数量、HTML 标签平衡、指数/上下标/overline 标记保留。
  Likely files/modules: `src/question_bank_service/scraper/validators.py`.
  Depends on: T005.
  Verify: 构造错误 fixture，确保 validator 能报出明确错误类型。

- [ ] T008 [P1] 添加 FE-Test HTTP Provider 设计适配
  Goal: 在 FE-Test 中可通过 HTTP 调用新服务，保留 SQLite Provider。
  Notes: 先设计 Provider 接口和 DTO 映射，默认不切生产。
  Likely files/modules: FE-Test `src/db/question-bank/*`, `src/quiz/*`, `src/bot/*`.
  Depends on: T004.
  Verify: FE-Test 单元测试通过，HTTP mock 覆盖 quiz 创建、加载、提交。

- [ ] T009 [P1] 改造每日练习生成调用路径
  Goal: 当前维护项目通过 Runtime/Admin API 获取题目和刷新缺失详情。
  Notes: 保留直接 SQLite 脚本作为回退，文档生成流程优先调用服务。
  Likely files/modules: 当前维护项目 daily 生成脚本或提示文档。
  Depends on: T004, T006.
  Verify: 生成一份今日练习文档，题目选项与原题格式一致。

- [ ] T010 [P2] 编写 Docker 部署配置
  Goal: 支持 Runtime 只读部署和 Admin 维护部署。
  Notes: 通过环境变量控制 Admin API；Runtime 挂载 DB 和 assets 为只读。
  Likely files/modules: `Dockerfile`, `docker-compose.yml`, `README.md`.
  Depends on: T004, T006.
  Verify: 本地 compose 启动后 `/health` 正常。

- [ ] T011 [P2] 增加发布和备份脚本
  Goal: Admin 写库前支持备份，发布前支持校验。
  Notes: 备份文件命名包含时间戳；校验失败时阻止发布。
  Likely files/modules: `scripts/backup_db.py`, `scripts/validate_question_bank.py`.
  Depends on: T006, T007.
  Verify: 备份文件生成，校验命令能返回非零失败码。

- [ ] T012 [P1] 输出 FE-Test 改造说明文档
  Goal: 让维护者能清楚理解 FE-Test 从直接 SQLite 读取迁移到题库服务的改造范围和切换方式。
  Notes: 文档需包含涉及文件、Provider 设计、环境变量、三条调用链新旧对比、验证命令、生产切换和回滚步骤。
  Likely files/modules: FE-Test `docs/FE_TEST_MIGRATION_GUIDE.md`.
  Depends on: T008.
  Verify: 文档中的文件清单与实际 diff 一致，验证命令可执行。

- [ ] T013 [P1] 输出当前维护项目改造说明文档
  Goal: 让维护者能清楚理解每日练习生成、题目刷新和格式校验如何改为调用题库服务。
  Notes: 文档需包含直接 SQLite/脚本调用替换范围、Runtime API 使用、Admin API 使用、保留脚本、验证步骤和服务不可用时的降级方式。
  Likely files/modules: 当前维护项目 `docs/CURRENT_PROJECT_MIGRATION_GUIDE.md`.
  Depends on: T009.
  Verify: 文档中的流程可以实际生成一份今日练习文档。

## Acceptance Criteria

- Runtime API 可以在只读模式读取真实或 fixture SQLite。
- FE-Test 可通过 HTTP Provider 完成候选题选择、quiz 加载和答案校验。
- Admin API 可刷新单题并写入 `question_details`。
- 格式保真测试覆盖指数、上下标、overline 和嵌套 span。
- 生产配置默认不会暴露写库能力。
- 当前维护项目可通过服务 API 生成每日练习文档。
- FE-Test 改造说明文档已输出，且覆盖配置、调用链、验证和回滚。
- 当前维护项目改造说明文档已输出，且覆盖每日文档生成、详情刷新、校验和降级。

## Suggested Execution Order

1. Foundation: T001, T002, T003.
2. Runtime API: T004.
3. Scraper/Admin: T005, T006, T007.
4. Integrations: T008, T009.
5. Migration documentation: T012, T013.
6. Deployment and operations: T010, T011.
