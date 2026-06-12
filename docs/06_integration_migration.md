# 集成与迁移方案

## FE-Test 迁移

### 当前状态

FE-Test 直接通过 `better-sqlite3` 读取题库：

- `src/db/question-bank/client.ts`
- `src/db/question-bank/queries.ts`
- `src/bot/quiz-session-factory.ts`
- `src/quiz/quiz-service.ts`
- `src/quiz/submit-service.ts`

### 目标状态

新增统一 Provider 接口：

```ts
interface QuestionBankProvider {
  listKeywords(): Promise<QuestionBankKeywords>
  findCandidates(filters: QuestionCandidateFilters): Promise<QuestionCandidate[]>
  getDetailByUrl(url: string, options?: DetailOptions): Promise<QuestionDetail | null>
  getDetailsByUrls(urls: string[], options?: DetailOptions): Promise<QuestionDetail[]>
}
```

实现：

```text
SqliteQuestionBankProvider
HttpQuestionBankProvider
```

### 迁移步骤

1. 在 FE-Test 中抽出 Provider 接口。
2. 将现有 SQLite 查询包装成 `SqliteQuestionBankProvider`。
3. 增加 `HttpQuestionBankProvider`。
4. 配置 `QUESTION_BANK_MODE=sqlite|http`。
5. 在开发环境使用 HTTP Provider 验证。
6. 生产切换前保留 SQLite Provider 作为回退。

## 当前维护项目迁移

### 当前状态

当前项目通过 Python 脚本直接访问 SQLite 和原站：

- `scripts/scrape_fe_siken_questions.py`
- `scripts/fetch_fe_siken_question_detail.py`
- `scripts/fetch_missing_fe_siken_question_details.py`

每日练习文档生成也会直接读取 `data/fe_siken_questions.sqlite`。

### 目标状态

- 每日练习生成通过 Runtime API 读取题目。
- 缺失详情通过 Admin API 刷新。
- 格式保真校验通过 Admin API 或服务内 validator 执行。

### 迁移步骤

1. 把现有 Python 解析逻辑迁入服务 `scraper/` 模块。
2. 保留原脚本作为 CLI wrapper，内部调用服务模块。
3. 今日练习生成流程改为调用 Runtime API。
4. 发现缺失详情时调用 Admin API。
5. 逐步减少直接 SQL 查询。

## 兼容策略

- 服务内部继续用 URL 作为详情关联键。
- API 对外同时支持 URL 和 ID。
- 资产路径继续返回 `/assets/fe-siken/...`。
- FE-Test 的 session 内仍保存 question URL，不立即迁移。

## 回滚策略

- FE-Test 保留 SQLite Provider。
- 服务切换失败时恢复 `QUESTION_BANK_MODE=sqlite`。
- Admin API 写库前保留 DB 备份。

## 最终改造说明文档

### FE-Test 改造说明

FE-Test 改造完成后必须输出：

```text
docs/FE_TEST_MIGRATION_GUIDE.md
```

文档至少包括：

- 修改过的模块和职责变化。
- `SqliteQuestionBankProvider` 与 `HttpQuestionBankProvider` 的切换方式。
- 新增或变更的环境变量。
- Bot 创建测试、Web 加载测试、提交答案三条调用链的新旧对比。
- 本地验证命令和生产切换步骤。
- 回滚到 SQLite Provider 的步骤。

### 当前维护项目改造说明

当前维护项目改造完成后必须输出：

```text
docs/CURRENT_PROJECT_MIGRATION_GUIDE.md
```

文档至少包括：

- 直接 SQLite 查询和脚本调用被替换的位置。
- 每日练习生成流程如何调用 Runtime API。
- 缺失详情和格式修复如何调用 Admin API。
- 仍保留的本地脚本及其回退用途。
- 生成今日文档的验证步骤。
- 服务不可用时的降级处理。
