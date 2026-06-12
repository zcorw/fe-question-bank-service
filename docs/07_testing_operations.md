# 测试与运维要求

## 单元测试

重点覆盖：

- SQLite repository 查询。
- `choices_json` 和 `images_json` 解析。
- URL 到 question ID 的关联。
- Runtime API 是否按 `includeAnswer` 隐藏答案和解析。
- Admin API token 校验。
- HTML 解析器格式保真。

格式保真用例至少包括：

- 指数：`2^5` 不应变成 `25`。
- 下标：变量下标不能丢失。
- overline：`¬x`、`¬y` 不能丢失。
- 嵌套 span 的选项提取不能截断。

## 集成测试

使用一份小型 fixture SQLite：

- 至少 3 道普通题。
- 至少 1 道带图片题。
- 至少 1 道包含指数/上下标题。
- 至少 1 道包含 overline 题。

验证：

- `/keywords`
- `/questions/candidates`
- `/questions/by-url`
- `/questions/{id}`
- `/questions/details/batch`
- `/admin/questions/validate-cache`

## FE-Test 兼容测试

在 FE-Test 中增加 HTTP Provider 测试：

- 创建 quiz session 时只读取候选题。
- 加载未提交 quiz 时不返回答案解析。
- 提交答案时能读取正确答案并校验选项 label。
- 批量读取 20 道题不会出现顺序错乱。

## 性能目标

- `/keywords` 可缓存，响应目标小于 100ms。
- `/questions/details/batch` 读取 20 道题目标小于 300ms。
- Admin 批量刷新不阻塞 Runtime API。

## 可观测性

基础日志字段：

- request_id
- route
- duration_ms
- question_url
- question_id
- result
- error_code

健康检查：

- 数据库文件存在。
- Runtime 连接可读。
- Admin 模式下资产目录可写。

## 发布检查

发布前必须确认：

- Runtime 模式不会写库。
- Admin API 在生产默认关闭。
- FE-Test 仍可回退 SQLite Provider。
- fixture 测试覆盖格式保真问题。
