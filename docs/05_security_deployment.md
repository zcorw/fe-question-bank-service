# 安全与部署

## 权限模型

| 能力 | Runtime API | Admin API |
|---|---|---|
| 查询关键词 | 允许 | 允许 |
| 查询候选题 | 允许 | 允许 |
| 查询题目详情 | 允许 | 允许 |
| 返回答案解析 | 按参数控制 | 允许 |
| 抓取原站 | 禁止 | 允许 |
| 写 SQLite | 禁止 | 允许 |
| 刷新图片缓存 | 禁止 | 允许 |

## 认证

- Runtime API 可在内网无 token 部署，也可使用服务间 token。
- Admin API 必须要求 `Authorization: Bearer <token>`。
- Admin token 通过环境变量注入，不写入仓库。

## 部署模式

### 推荐生产模式

```text
question-bank-runtime
  QUESTION_BANK_READ_ONLY=true
  ENABLE_ADMIN_API=false
  QUESTION_DB_PATH=/app/data/fe_siken_questions.sqlite
```

挂载：

```text
/opt/fe-question-bank/data:/app/data:ro
/opt/fe-question-bank/public/assets/fe-siken:/app/public/assets/fe-siken:ro
```

### 维护模式

```text
question-bank-admin
  QUESTION_BANK_READ_ONLY=false
  ENABLE_ADMIN_API=true
  QUESTION_DB_PATH=/app/data/fe_siken_questions.sqlite
```

挂载：

```text
/opt/fe-question-bank/data:/app/data:rw
/opt/fe-question-bank/public/assets/fe-siken:/app/public/assets/fe-siken:rw
```

## 写操作控制

- Admin 写库接口需要进程内锁。
- SQLite 写入必须使用事务。
- 批量刷新失败时记录失败 URL，不应中断已成功写入的题目。
- Runtime 连接使用只读模式。

## 日志

必须记录：

- 请求 ID。
- 刷新 URL。
- 抓取结果。
- 解析错误。
- 写库结果。
- 校验失败类型。

不记录：

- Admin token。
- 不必要的完整 HTML 大文本，除非本地调试模式开启。

## 备份

Admin 写库前应支持手动或自动备份：

```text
fe_siken_questions.sqlite.YYYYMMDDHHMMSS.bak
```

图片资产目录必须与 SQLite 一起备份和恢复：

```text
/opt/fe-question-bank/data/fe_siken_questions.sqlite
/opt/fe-question-bank/public/assets/fe-siken/
```

SQLite 中只保存图片路径和元数据。缺少资产目录会导致题目仍能读取，
但 `/assets/fe-siken/...` 图片请求返回 404。

MVP 可以先提供 CLI 备份脚本，后续再集成到 Admin API。
