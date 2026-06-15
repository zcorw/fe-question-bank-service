# Question Keyword Taxonomy

## Purpose

This taxonomy lets the FE Question Bank Runtime expose stable searchable learning topics to consumer applications. Japanese question text, choices, explanations, and existing category/topic values are kept in Japanese and are not translated back into source data.

## Three-Level Model

| Level | Purpose | Source |
| --- | --- | --- |
| `syllabusArea` | Coarse filtering by exam syllabus area | Rule mapping from existing `questions.category` |
| `topicTag` | Main searchable topic used by daily practice plans | Existing `questions.category` |
| `knowledgePoint` | Specific review point for a question | Existing `questions.topic` |

## Naming Rules

- IDs are stable lowercase identifiers.
- `syllabusArea` uses fixed readable IDs such as `database` and `security`.
- `topicTag` and `knowledgePoint` use stable SHA-1 based IDs because the source labels are Japanese.
- Japanese source labels are preserved in `displayNameJa` and `aliasesJa`.
- English abbreviations such as SQL, ACID, TLS, and MTBF are stored in `aliasesEn` when detectable.

## Syllabus Areas

| syllabusArea | displayNameJa | questionCount |
| --- | --- | ---: |
| `computer_system` | コンピュータシステム | 792 |
| `software_design` | ソフトウェア・開発 | 606 |
| `strategy` | ストラテジ系 | 497 |
| `security` | 情報セキュリティ | 286 |
| `mathematics` | 基礎理論・数学 | 276 |
| `network` | ネットワーク | 259 |
| `database` | データベース | 223 |
| `management` | マネジメント系 | 147 |
| `project_management` | プロジェクトマネジメント | 135 |
| `service_management` | サービスマネジメント | 109 |
| `business_law` | 法務・標準化 | 108 |

## Top TopicTags

| id | displayNameJa | syllabusArea | questionCount |
| --- | --- | --- | ---: |
| `topic_9363758fab` | 離散数学 | `mathematics` | 152 |
| `security` | 情報セキュリティ | `security` | 145 |
| `topic_7091d9394b` | 業務分析・データ利活用 | `strategy` | 135 |
| `topic_ce95d85630` | オペレーティングシステム | `computer_system` | 133 |
| `topic_cef6886818` | メモリ | `computer_system` | 100 |
| `topic_8c08ee8201` | プロセッサ | `computer_system` | 99 |
| `algorithm` | アルゴリズム | `software_design` | 98 |
| `availability` | システムの評価指標 | `computer_system` | 95 |
| `topic_87ec27f1df` | システムの構成 | `computer_system` | 92 |
| `network` | 通信プロトコル | `network` | 80 |
| `topic_69b33aedc0` | データ通信と制御 | `network` | 78 |
| `topic_06e225ea87` | ハードウェア | `computer_system` | 76 |
| `topic_b1c63a08ad` | ソフトウェア方式設計・詳細設計 | `software_design` | 75 |
| `topic_15311538fb` | システム監査 | `management` | 72 |
| `sql` | データ操作 | `database` | 70 |
| `transaction` | トランザクション処理 | `database` | 68 |
| `topic_659da24ff9` | データ構造 | `software_design` | 66 |
| `topic_019937bca7` | 情報セキュリティ対策 | `security` | 62 |
| `topic_e45fa28034` | 入出力装置 | `computer_system` | 62 |
| `topic_1cb4907abe` | 応用数学 | `mathematics` | 59 |
| `topic_00b1c61d43` | データベース設計 | `database` | 56 |
| `topic_85a53f142e` | プロジェクトの時間 | `project_management` | 55 |
| `topic_0ca193e39c` | 会計・財務 | `strategy` | 55 |
| `topic_e261626099` | 情報に関する理論 | `mathematics` | 54 |
| `topic_1a08962c97` | ソフトウェア構築 | `software_design` | 53 |
| `topic_035a6076bb` | ネットワーク方式 | `network` | 48 |
| `topic_74fcb36447` | 開発プロセス・手法 | `software_design` | 45 |
| `topic_78a7433d07` | サービスの運用 | `service_management` | 44 |
| `topic_49b75da8d2` | 開発ツール | `software_design` | 42 |
| `topic_504b088fb1` | 情報システム戦略 | `strategy` | 42 |
| `topic_42853199a9` | 経営戦略手法 | `strategy` | 41 |
| `topic_4c34cec601` | セキュリティ実装技術 | `security` | 40 |
| `topic_d989df8b90` | ソフトウェア要件定義 | `software_design` | 39 |
| `topic_fa62f09735` | e-ビジネス | `strategy` | 38 |
| `topic_dc2392fa49` | 知的財産権 | `business_law` | 35 |
| `topic_5c1087e9e4` | 情報セキュリティ管理 | `security` | 32 |
| `topic_82d19001cd` | 経営・組織論 | `strategy` | 31 |
| `topic_f60cdcfbd3` | 労働関連・取引関連法規 | `business_law` | 31 |
| `topic_8ca9b58e83` | ファイルシステム | `computer_system` | 31 |
| `topic_06f8363d1a` | プロジェクトのコスト | `project_management` | 31 |
| `topic_6e19cebd10` | ネットワーク応用 | `network` | 30 |
| `topic_1039524fb1` | マーケティング | `strategy` | 30 |
| `topic_b7663003a2` | マルチメディア技術 | `computer_system` | 30 |
| `topic_6d51e85487` | システム活用促進・評価 | `management` | 27 |
| `topic_a063da1b9c` | プログラミング | `software_design` | 26 |
| `topic_587c0f683d` | サービスの設計・移行 | `service_management` | 25 |
| `topic_f495c9904c` | 入出力デバイス | `computer_system` | 25 |
| `topic_9f5feee139` | UX/UIデザイン | `software_design` | 24 |
| `topic_7bc3177164` | ソリューションビジネス | `strategy` | 23 |
| `topic_c5bdc7b5e7` | プログラム言語 | `software_design` | 23 |

## Runtime Search Example

```json
{
  "examPart": "科目A",
  "topicTags": ["transaction"],
  "limit": 5
}
```

Runtime should resolve `topicTags`, `knowledgePoints`, and `syllabusArea` through `data/question_topic_mappings.json` and return only matched question URLs. Unknown keywords must return an explicit shortage response, not default ordered questions.

## Maintenance Rules

1. Regenerate the JSON files after updating `questions.category` or `questions.topic`.
2. Review low-confidence mappings listed in `docs/question-keyword-generation-report.md`.
3. Keep original Japanese question content unchanged.
4. Keep browser image paths as public paths only; do not expose host filesystem paths to consumers.
