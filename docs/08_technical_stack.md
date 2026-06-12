# 技术栈

## 后端

推荐：

- Python 3.11+
- FastAPI
- Uvicorn
- Pydantic
- sqlite3 或 apsw
- BeautifulSoup4 / lxml
- httpx
- pytest

理由：

- 当前题目抓取和解析逻辑已经是 Python。
- HTML 解析细节复杂，重写为 Node.js 风险较高。
- FastAPI 适合快速提供稳定 JSON API 和 OpenAPI 文档。

## FE-Test 客户端

推荐：

- TypeScript interface 抽象 Provider。
- HTTP 客户端使用项目现有 fetch 能力或轻量封装。
- 测试使用 FE-Test 当前测试框架。

## 数据库

MVP：

- 继续使用现有 `fe_siken_questions.sqlite`。
- Runtime 只读连接。
- Admin 写操作使用事务。

后续：

- 可增加 `question_details.question_id`。
- 可增加迁移脚本，但不作为 MVP 前置。

## API 风格

- REST JSON。
- Batch endpoint 用 POST。
- Admin 接口统一 `/admin` 前缀。
- 错误响应统一 `{ code, message, detail }`。

## 配置

```text
QUESTION_DB_PATH
QUESTION_ASSET_ROOT
QUESTION_BANK_READ_ONLY
ENABLE_ADMIN_API
ADMIN_API_TOKEN
LOG_LEVEL
```

## 不建议自研的能力

- 不自研 HTTP 框架，使用 FastAPI。
- 不自研 HTML DOM 解析器，使用 BeautifulSoup4/lxml。
- 不自研测试运行器，使用 pytest。
- 不重写 FE-Test 业务数据逻辑。

## 代码仓库结构

```text
FE-QuestionBank-Service/
  docs/
  src/
    question_bank_service/
  tests/
  scripts/
  pyproject.toml
  README.md
```

## 风险

- 原站 HTML 结构变化会影响 Admin 抓取。
- 现有数据中可能存在已缓存的解析错误，需要 validator 扫描。
- Runtime 和 Admin 共用 SQLite 时需要避免写锁影响读取。
- FE-Test 切换 HTTP Provider 后需要关注网络失败和超时处理。
