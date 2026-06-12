# API 规格

## 设计原则

- Runtime API 默认只读。
- Admin API 需要 `Authorization: Bearer <token>`。
- 批量读取优先，避免 FE-Test 每次加载 20 道题产生 20 次 HTTP 请求。
- 对外返回 `questionId`，但内部兼容 `question_url` 关联。
- 答案和解析按调用场景控制返回。

## Runtime API

### GET /health

返回服务状态、数据库是否可读。

```json
{
  "ok": true,
  "database": "ready",
  "readOnly": true
}
```

### GET /keywords

返回题库分类与主题。

```json
{
  "categories": ["基礎理論"],
  "topics": ["論理演算"]
}
```

### GET /questions/candidates

查询候选题。

Query 参数：

- `category`
- `topic`
- `url`
- `limit`
- `offset`

### POST /questions/candidates/search

支持多分类查询。

```json
{
  "categories": ["基礎理論", "アルゴリズム"],
  "topic": "論理演算",
  "limit": 100
}
```

### GET /questions/by-url

按 `questionUrl` 读取详情。

Query 参数：

- `url`
- `includeAnswer`，默认 `false`
- `includeExplanation`，默认跟随 `includeAnswer`

### GET /questions/{id}

按 `questions.id` 读取详情。服务内部通过 `questions.url = question_details.question_url` 关联。

### POST /questions/details/batch

批量读取详情。

```json
{
  "urls": [
    "https://www.fe-siken.com/kakomon/14_aki/q7.html"
  ],
  "includeAnswer": false,
  "includeExplanation": false
}
```

## Admin API

### POST /admin/questions/refresh

刷新单题详情。

```json
{
  "url": "https://www.fe-siken.com/kakomon/14_aki/q7.html",
  "force": true
}
```

### POST /admin/questions/refresh-missing

补齐缺失详情。

```json
{
  "limit": 100,
  "sourcePageLabel": "令和6年秋期"
}
```

### POST /admin/questions/validate-cache

校验题目缓存。

```json
{
  "urls": [
    "https://www.fe-siken.com/kakomon/14_aki/q7.html"
  ],
  "checks": ["choice_count", "html_balance", "notation_preservation"]
}
```

### POST /admin/questions/rebuild-index

重建 `questions` 索引表。该接口风险高，MVP 可只在本地启用。

## 错误码

| HTTP 状态 | code | 含义 |
|---|---|---|
| 400 | invalid_request | 参数无效 |
| 401 | unauthorized | Admin token 缺失或错误 |
| 404 | question_not_found | 题目不存在 |
| 409 | write_locked | 写操作正在执行 |
| 422 | parse_failed | 原站 HTML 解析失败 |
| 500 | database_error | SQLite 读取或写入失败 |
