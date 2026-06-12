# FE Question Bank Service 项目概览

## 背景

`fe_siken_questions.sqlite` 当前被两个方向使用：

- FE-Test：运行时只读题库，用于候选题选择、题目详情读取、答案校验和关键词加载。
- 当前维护项目：负责抓取 FE 过去问原站、解析题干和选项、缓存图片、修复格式保真问题，并生成每日练习文档。

直接让多个项目读写同一个 SQLite 文件会带来耦合：运行时服务需要稳定只读能力，维护流程需要抓取、解析、校验和写库能力。两类职责应拆开。

## 项目目标

- 提供独立的题库读取服务，供 FE-Test 和每日练习生成流程调用。
- 封装题目抽取、详情刷新、缺失详情补齐和校验流程，减少 Codex 或人工直接操作 SQLite 的频率。
- 保持现有 `fe_siken_questions.sqlite` 数据结构兼容，避免为了服务化先做大规模迁移。
- 对外暴露 `questionId`、`questionUrl`、`sourcePageUrl`，改善人工查询体验。

## 目标用户

- FE-Test Web/Bot 运行时。
- 当前项目的每日练习生成流程。
- 维护者和 Codex，用于刷新题目详情、修复解析问题和校验缓存。

## MVP 范围

- Python FastAPI 服务。
- Runtime API：只读查询候选题、关键词、题目详情、批量详情。
- Admin API：刷新单题、刷新缺失详情、校验缓存。
- SQLite 数据源兼容现有表结构。
- FE-Test 可通过 HTTP Provider 替代直接 SQLite 查询。

## 非目标

- 不在 MVP 中重建 FE-Test 的业务数据库。
- 不在 MVP 中改造所有历史数据结构。
- 不在 MVP 中提供复杂管理后台 UI。
- 不把题目抓取逻辑重写为 Node.js。

## 关键假设

- `questions.url = question_details.question_url` 仍作为内部稳定关联键。
- Runtime API 在生产默认只读。
- Admin API 仅限本地或受保护网络使用，需要 token。
- 图片资产继续使用现有 `/assets/fe-siken/...` 路径规则。

## 待确认事项

- 生产环境是否需要单独部署 Admin 服务，还是同一镜像通过环境变量关闭 Admin API。
- FE-Test 是否需要长期保留 SQLite Provider 作为降级路径。
- 题库 DB 的发布流程是文件替换、增量刷新，还是服务内部定期同步。

## 补充开发目标

最终开发目标不仅包含服务代码和接口能力，还必须输出两个项目的改造说明文档：

- FE-Test 改造说明文档：说明从直接读取 SQLite 迁移到题库服务 HTTP Provider 的改造范围、配置变化、调用链变化、验证方式和回滚步骤。
- 当前维护项目改造说明文档：说明每日练习生成、题目详情刷新、格式保真校验如何改为调用 Runtime/Admin API，以及保留哪些本地脚本作为回退。

这两份文档属于项目完成定义的一部分，不能作为可选交付物。
