# API Specification

## Runtime API

Runtime API is read-only by default. Consumers must call the HTTP API and must
not read the SQLite database directly.

### GET /health

Returns service and database readiness.

```json
{
  "ok": true,
  "database": "ready",
  "readOnly": true
}
```

### GET /keywords

Returns the searchable keyword taxonomy loaded from
`data/question_keyword_taxonomy.json`.

```json
{
  "version": 1,
  "language": "ja",
  "tags": [
    {
      "id": "transaction",
      "level": "topicTag",
      "displayNameJa": "トランザクション処理",
      "aliasesJa": ["トランザクション処理"],
      "aliasesEn": ["transaction", "lock", "acid"],
      "parentId": "database",
      "syllabusArea": "database"
    }
  ]
}
```

### GET /questions/candidates

Legacy candidate query endpoint.

Query parameters:

- `category`
- `topic`
- `url`
- `limit`
- `offset`

Responses include question metadata. If keyword mapping JSON is available,
items also include:

- `primaryTag`
- `topicTags`
- `knowledgePoints`
- `syllabusArea`

### POST /questions/candidates/search

Searches candidates through the generated keyword mapping JSON. This endpoint
does not fall back to default ordered questions when no keyword matches.

Request:

```json
{
  "examPart": "科目A",
  "keywords": ["トランザクション"],
  "topicTags": ["transaction"],
  "knowledgePoints": [],
  "syllabusArea": "database",
  "limit": 10,
  "offset": 0
}
```

Response:

```json
{
  "questions": [],
  "totalMatched": 0,
  "shortage": {
    "requested": 10,
    "returned": 0,
    "reason": "no_topic_matches"
  }
}
```

`shortage.reason` is:

- `no_topic_matches` when no question matches the requested keyword/tag.
- `not_enough_topic_matches` when fewer questions exist than requested.

Legacy fields `categories`, `topic`, and `url` are still accepted for older
callers, but new consumers should use `keywords`, `topicTags`,
`knowledgePoints`, and `syllabusArea`.

### GET /questions/by-url

Reads one question detail by URL.

Query parameters:

- `url`
- `includeAnswer`, default `false`
- `includeExplanation`, default follows `includeAnswer`

### GET /questions/{id}

Reads one question detail by internal `questions.id`.

### POST /questions/details/batch

Reads details for multiple question URLs while preserving request order.

```json
{
  "urls": [
    "https://www.fe-siken.com/kakomon/14_aki/q7.html"
  ],
  "includeAnswer": false,
  "includeExplanation": false
}
```

Each returned item includes keyword metadata when a mapping exists:

```json
{
  "questionUrl": "https://www.fe-siken.com/kakomon/14_aki/q7.html",
  "topicTags": ["transaction"],
  "knowledgePoints": ["transaction_atomicity"],
  "syllabusArea": "database",
  "primaryTag": "transaction_atomicity"
}
```

## Keyword Data Files

Runtime reads keyword data from:

- `QUESTION_KEYWORD_TAXONOMY_PATH`, default `data/question_keyword_taxonomy.json`
- `QUESTION_TOPIC_MAPPINGS_PATH`, default `data/question_topic_mappings.json`

In Docker Compose, the repository `data/` directory is mounted to `/app/data`.
Keep the generated JSON files together with `fe_siken_questions.sqlite` on the
host data directory.

## Admin API

Admin API is enabled only when `ENABLE_ADMIN_API=true` and requires
`Authorization: Bearer <ADMIN_API_TOKEN>`.

### POST /admin/questions/refresh

Refreshes one question detail.

```json
{
  "url": "https://www.fe-siken.com/kakomon/14_aki/q7.html",
  "force": true
}
```

### POST /admin/questions/refresh-missing

Backfills missing question details.

```json
{
  "limit": 100,
  "sourcePageLabel": "令和6年秋"
}
```

### POST /admin/questions/validate-cache

Validates cached question details.

```json
{
  "urls": [
    "https://www.fe-siken.com/kakomon/14_aki/q7.html"
  ],
  "checks": ["choice_count", "html_balance", "notation_preservation"]
}
```

## Error Codes

| HTTP | code | Meaning |
| --- | --- | --- |
| 400 | `invalid_request` | Invalid request |
| 401 | `unauthorized` | Missing or invalid Admin token |
| 404 | `question_not_found` | Question detail does not exist |
| 409 | `write_locked` | Write operation is locked |
| 422 | `parse_failed` | Source HTML parse failed |
| 500 | `database_error` | SQLite read/write failed |
