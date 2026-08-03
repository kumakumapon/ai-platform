<!-- AI-PLATFORM:START -->
## AI Platform 共通ルール（同期管理）

- 変更前に関連実装・設定・テストを確認し、既存の設計と命名を尊重する。
- 必要最小限の差分を選び、外部入力を検証する。TypeScript は型安全性、Python は型ヒントと明確な例外処理を優先する。
- 不具合修正には回帰テストを追加し、lint・型チェック・テスト・ビルドを実行する。テスト削除やチェック無効化で問題を回避しない。
- Secret・個人情報を出力しない。認証、認可、DB、公開 API は根拠なく変更しない。
- 実行していない検証を成功と報告せず、PR には変更内容、テスト結果、リスク・未検証事項を記載する。

詳細: `sj55576/ai-platform` の `prompts/coding-agent-typescript-python.md`
<!-- AI-PLATFORM:END -->
