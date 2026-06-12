# 数据模型

## 现有 SQLite 表

MVP 继续兼容现有 `fe_siken_questions.sqlite`。

### questions

用途：题目候选元数据。

关键字段：

| 字段 | 含义 |
|---|---|
| id | 当前项目内的题目 ID |
| source_page_label | 来源页面标签 |
| source_page_url | 来源列表页 URL |
| exam_part | 考试部分，FE-Test 固定使用 `科目A` |
| question_no | 题号 |
| topic | 主题 |
| category | 分类 |
| url | 题目原站 URL |
| scraped_at | 抽取时间 |

### question_details

用途：题干、选项、答案、解析、图片元数据。

关键字段：

| 字段 | 含义 |
|---|---|
| question_url | 题目原站 URL |
| source_url | 当前通常等于 question_url |
| question_text | 题干文本 |
| choices_json | 选项 JSON |
| answer | 正确选项 label |
| explanation | 解析文本 |
| images_json | 图片元数据 JSON |
| has_images | 是否包含图片 |
| fetched_at | 抓取时间 |

### question_assets

用途：图片缓存记录。

关键字段：

| 字段 | 含义 |
|---|---|
| question_url | 题目原站 URL |
| original_url | 原站图片 URL |
| local_path | 本地缓存路径 |
| public_path | 对外访问路径 |

## 内部关联规则

当前内部关联继续使用：

```sql
questions.url = question_details.question_url
```

原因：

- 原站 URL 是跨抓取批次更稳定的自然键。
- 现有 FE-Test 和当前项目都已经围绕 URL 保存 session 或查询详情。
- 不需要先迁移历史数据即可服务化。

## 对外 DTO

服务对外应补充 `questionId`：

```json
{
  "questionId": 3125,
  "questionUrl": "https://www.fe-siken.com/kakomon/14_aki/q7.html",
  "sourcePageUrl": "https://www.fe-siken.com/kakomon/14_aki/",
  "questionText": "...",
  "choices": [
    { "label": "ア", "text": "x＋¬y" }
  ]
}
```

这样人工查询可以用 ID，FE-Test 仍可用 URL 维持兼容。

## 后续可选迁移

后续可增加：

```sql
ALTER TABLE question_details ADD COLUMN question_id INTEGER;
```

并回填：

```sql
UPDATE question_details
SET question_id = (
  SELECT id FROM questions WHERE questions.url = question_details.question_url
);
```

但该迁移不应阻塞 MVP。
