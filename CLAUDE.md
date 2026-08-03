# CLAUDE.md — ai-platform

このリポジトリは、TypeScript / Python プロジェクト向けのコーディングエージェント用ルール、タスクプロンプト、GitHub テンプレート、CI サマリー機構の正本です。アプリケーション本体は含みません。詳細は `README.md` を参照してください。

## 変更時の原則

- `prompts/` と `templates/` の内容は、複数のプロジェクトへ同期されます。特定プロジェクトの事情に依存する記述を追加しません。
- `prompts/` のタスクプロンプトは、対象プロジェクトの `.claude/commands/` へそのまま同期されます。YAML フロントマター（`description`、`argument-hint`、`disable-model-invocation`）を壊さないでください。
- `templates/AGENTS.common-rules.md` は `<!-- AI-PLATFORM:START -->` / `<!-- AI-PLATFORM:END -->` マーカーごと同期されます。マーカーを削除しないでください。
- 特定のエージェント製品に依存する表現は、`README.md` の製品別セクションに閉じ込めます。プロンプト本文はツール中立に保ちます。

## 検証コマンド

| 目的 | コマンド |
| --- | --- |
| unit test | `python -m unittest discover -s tests -v` |
| ワークフロー構文の確認 | `python -c "import yaml,sys;[yaml.safe_load(open(p)) for p in sys.argv[1:]]" .github/workflows/*.yml templates/*.yml` |
| 同期設定の確認 | `jq . .github/sync-targets.json` |

`scripts/` は標準ライブラリのみを使用します。依存パッケージを追加しないでください。

## 変更時に注意する領域

- `.github/workflows/reusable-ci-summary.yml`: 他リポジトリから呼ばれる公開インターフェースです。入力名の変更・削除は破壊的変更になります。fork PR で platform checkout とコメントジョブを実行しない条件を弱めないでください。
- `.github/workflows/sync-agent-rules.yml`: 対象リポジトリへ書き込みます。`enabled` の既定値、`dry_run` の既定値、パス検証（`safe_relative`）を緩めないでください。
- `.github/sync-targets.json`: 例として全項目が `enabled: false` です。既定で有効化しないでください。

## セキュリティ

Secret、アクセストークン、個人情報を、プロンプト、テンプレート、テストデータ、コミットに含めません。マスク処理（`mask_secrets`）を変更する場合は、対応するテストを追加してください。
