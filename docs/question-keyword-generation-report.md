# Question Keyword Generation Report

## Data Source

- SQLite: `data/fe_siken_questions.sqlite`
- Generated at: `2026-06-15T01:45:06.966590+00:00`
- Read model: `questions` LEFT JOIN `question_details`

## Tables and Fields Read

| Table | Fields |
| --- | --- |
| `questions` | `id`, `source_page_label`, `source_page_url`, `exam_part`, `question_no`, `topic`, `category`, `url`, `scraped_at` |
| `question_details` | `question_url`, `question_text`, `choices_json`, `answer`, `explanation`, `images_json`, `has_images`, `fetched_at` |
| `question_assets` | `question_url`, `section`, `choice_label`, `asset_type`, `url`, `alt`, `width`, `height`, `local_path`, `public_path` |

## Summary

| Metric | Count |
| --- | ---: |
| questions total | 3438 |
| question_details joined | 3400 |
| question_assets rows | 1892 |
| mappings generated | 3438 |
| tags generated | 2317 |
| low-confidence / review required mappings | 38 |
| missing detail rows | 38 |
| fallback categories | 0 |
| readable canonical topicTag IDs | 6 |
| hash-based topicTag IDs | 94 |

## Exam Part Counts

| examPart | Count |
| --- | ---: |
| 科目A | 3400 |
| 科目B | 38 |

## SyllabusArea Counts

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

## Top TopicTag Counts

| topicTag | displayNameJa | syllabusArea | questionCount |
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

## Human Review Samples

- `0.70` 科目B 問1 プログラムの基本要素 / 同じ値を返す関数 - https://www.fe-siken.com/kakomon/07_haru/b1.html
- `0.70` 科目B 問2 プログラムの基本要素 / 硬貨の組合せ数を求める関数 - https://www.fe-siken.com/kakomon/07_haru/b2.html
- `0.70` 科目B 問3 データ構造及びアルゴリズム / スタック構造のpush/popを行う関数 - https://www.fe-siken.com/kakomon/07_haru/b3.html
- `0.70` 科目B 問4 データ構造及びアルゴリズム / 配列から要素を探索する関数 - https://www.fe-siken.com/kakomon/07_haru/b4.html
- `0.70` 科目B 問5 プログラミングの諸分野への適用 / 理論度数を求める関数 - https://www.fe-siken.com/kakomon/07_haru/b5.html
- `0.70` 科目B 問6 情報セキュリティ / バックアップ管理 - https://www.fe-siken.com/kakomon/07_haru/b6.html
- `0.70` 科目B 問1 プログラムの基本要素 / 最大値を返すプログラム - https://www.fe-siken.com/kakomon/06_haru/b1.html
- `0.70` 科目B 問2 プログラムの基本要素 / 2進数文字列を10進数に変換するプログラム - https://www.fe-siken.com/kakomon/06_haru/b2.html
- `0.70` 科目B 問3 データ構造及びアルゴリズム / グラフの辺を隣接行列に変換するプログラム - https://www.fe-siken.com/kakomon/06_haru/b3.html
- `0.70` 科目B 問4 データ構造及びアルゴリズム / プログラム中の命令が実行される回数 - https://www.fe-siken.com/kakomon/06_haru/b4.html
- `0.70` 科目B 問5 プログラミングの諸分野への適用 / 商品注文の関連度を出力するプログラム - https://www.fe-siken.com/kakomon/06_haru/b5.html
- `0.70` 科目B 問6 情報セキュリティ / テレワーク環境のセキュリティ - https://www.fe-siken.com/kakomon/06_haru/b6.html
- `0.70` 科目B 問1 プログラムの基本要素 / 素数の合計を返すプログラム - https://www.fe-siken.com/kakomon/05_haru/b1.html
- `0.70` 科目B 問2 プログラムの基本要素 / サブルーチンを使用したプログラム - https://www.fe-siken.com/kakomon/05_haru/b2.html
- `0.70` 科目B 問3 データ構造及びアルゴリズム / 整列プログラム - https://www.fe-siken.com/kakomon/05_haru/b3.html
- `0.70` 科目B 問4 データ構造及びアルゴリズム / ハッシュ表の内容 - https://www.fe-siken.com/kakomon/05_haru/b4.html
- `0.70` 科目B 問5 プログラミングの諸分野への適用 / コサイン類似度 - https://www.fe-siken.com/kakomon/05_haru/b5.html
- `0.70` 科目B 問6 情報セキュリティ / 情報セキュリティ - https://www.fe-siken.com/kakomon/05_haru/b6.html
- `0.70` 科目B 問1 プログラムの基本要素 / 型，変数，代入のプログラム - https://www.fe-siken.com/kakomon/sample/b1.html
- `0.70` 科目B 問2 プログラムの基本要素 / 比較演算と選択処理のプログラム - https://www.fe-siken.com/kakomon/sample/b2.html
- `0.70` 科目B 問3 プログラムの基本要素 / 配列を処理するプログラム - https://www.fe-siken.com/kakomon/sample/b3.html
- `0.70` 科目B 問4 プログラムの基本要素 / 最大公約数を求めるプログラム - https://www.fe-siken.com/kakomon/sample/b4.html
- `0.70` 科目B 問5 プログラムの基本要素 / 斜辺の長さを求めるプログラム - https://www.fe-siken.com/kakomon/sample/b5.html
- `0.70` 科目B 問6 プログラムの基本要素 / 論理演算を用いたプログラム - https://www.fe-siken.com/kakomon/sample/b6.html
- `0.70` 科目B 問7 データ構造及びアルゴリズム / 再帰関数のプログラム - https://www.fe-siken.com/kakomon/sample/b7.html
- `0.70` 科目B 問8 データ構造及びアルゴリズム / 優先度付きキューを操作するプログラム - https://www.fe-siken.com/kakomon/sample/b8.html
- `0.70` 科目B 問9 データ構造及びアルゴリズム / 木構造を走査するプログラム - https://www.fe-siken.com/kakomon/sample/b9.html
- `0.70` 科目B 問10 データ構造及びアルゴリズム / リストの要素を削除するプログラム - https://www.fe-siken.com/kakomon/sample/b10.html
- `0.70` 科目B 問11 データ構造及びアルゴリズム / 整列プログラム - https://www.fe-siken.com/kakomon/sample/b11.html
- `0.70` 科目B 問12 プログラミングの諸分野への適用 / 文字列同士の類似度を求めるプログラム - https://www.fe-siken.com/kakomon/sample/b12.html

## Data Quality Notes

- `question_details` is missing for 38 questions. These mappings are generated from existing category/topic only and require review.
- The generated topic and knowledge-point IDs are stable but hash-based. If these IDs become public API contracts, consider replacing high-traffic tags with curated human-readable IDs in a controlled migration.
- `question_assets` metadata exists, but this report does not verify that every referenced image file exists under `QUESTION_ASSET_ROOT`.

## High-Frequency Canonical ID Migration

| legacyId | canonicalId | source category |
| --- | --- | --- |
| `topic_10baec062e` | `transaction` | トランザクション処理 |
| `topic_593872b6fa` | `sql` | データ操作 |
| `topic_b32b4f2b76` | `security` | 情報セキュリティ |
| `topic_9ce7f8592a` | `network` | 通信プロトコル |
| `topic_72e3a51eec` | `algorithm` | アルゴリズム |
| `topic_a4b90d039a` | `availability` | システムの評価指標 |

## Runtime API Implementation Status

1. `GET /keywords` returns `version`, `language`, and `tags` from `data/question_keyword_taxonomy.json`.
2. `POST /questions/candidates/search` accepts `keywords`, `topicTags`, `knowledgePoints`, and `syllabusArea`, then filters through `data/question_topic_mappings.json`.
3. Unknown or underfilled searches return explicit `shortage.reason` instead of default ordered questions.
4. `POST /questions/details/batch` items include `primaryTag`, `topicTags`, `knowledgePoints`, and `syllabusArea` when mappings exist.

## Generated Files

- `docs/question-keyword-taxonomy.md`
- `docs/question-keyword-generation-report.md`
- `data/question_keyword_taxonomy.json`
- `data/question_topic_mappings.json`
- `data/question_keyword_search_fixtures.json`

## Verification Plan

- Parse all generated JSON files as UTF-8 JSON.
- Assert `questions` count equals `mappings` count.
- Assert transaction / sql / security / network / algorithm fixtures have expected URLs.
- After Runtime implementation, add contract tests for unknown keywords returning shortage without default questions.
