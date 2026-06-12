# 最终交付物

## 代码交付物

- Python FastAPI 题库服务。
- Runtime 只读 API。
- Admin 维护 API。
- SQLite repository 与 DTO 映射。
- 题目详情解析、图片缓存和格式保真校验模块。
- 测试 fixture 与自动化测试。
- Docker 或等价部署配置。

## 文档交付物

### 服务自身文档

- README。
- API 使用说明。
- 环境变量说明。
- 部署说明。
- 测试与校验说明。

### FE-Test 改造说明

文件名建议：

```text
docs/FE_TEST_MIGRATION_GUIDE.md
```

必须说明：

- 改造背景和目标。
- 涉及文件清单。
- Provider 接口设计。
- SQLite Provider 和 HTTP Provider 的差异。
- 环境变量配置。
- Bot 创建测试、Web 加载测试、提交答案的调用链变化。
- 本地测试步骤。
- 生产切换步骤。
- 回滚步骤。

### 当前维护项目改造说明

文件名建议：

```text
docs/CURRENT_PROJECT_MIGRATION_GUIDE.md
```

必须说明：

- 改造背景和目标。
- 直接 SQLite 调用的替换范围。
- 题目详情刷新流程的替换范围。
- 每日练习文档生成的新调用链。
- Admin API 的使用边界。
- 本地脚本保留范围。
- 验证步骤。
- 降级和回滚步骤。

## 完成定义

项目不能只以服务代码完成作为结束。只有当以下内容同时完成，才视为开发目标完成：

- 服务代码通过测试。
- FE-Test 可通过 HTTP Provider 使用题库服务。
- 当前维护项目可通过服务生成每日练习文档。
- `FE_TEST_MIGRATION_GUIDE.md` 已输出并覆盖实际改造。
- `CURRENT_PROJECT_MIGRATION_GUIDE.md` 已输出并覆盖实际改造。
