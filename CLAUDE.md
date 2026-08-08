# CLAUDE.md — ai-platform

このリポジトリは、TypeScript / Python プロジェクト向けのコーディングエージェント用ルール、タスクプロンプト、GitHub テンプレート、CI サマリー機構の正本です。アプリケーション本体は含みません。詳細は `README.md` を参照してください。

## 変更時の原則

- `prompts/`、`templates/`、`agents/` は、複数のプロジェクトで手動適用できる共通資産です。特定プロジェクトの事情に依存する記述を追加しません。
- `prompts/` のタスクプロンプトは、対象プロジェクトの `.claude/commands/` へ配置できます。YAML フロントマター（`description`、`argument-hint`、`disable-model-invocation`）を壊さないでください。
- `agents/` のサブエージェント定義は、対象プロジェクトの `.claude/agents/` へ配置できます。`name` フロントマターを変更すると `templates/CLAUDE.bridge.md` のオーケストレーション手順との対応が壊れるため、変更する場合は両方を同時に更新してください。
- `templates/AGENTS.common-rules.md` の `<!-- AI-PLATFORM:START -->` / `<!-- AI-PLATFORM:END -->` マーカーは、対象プロジェクトへ手動適用する範囲を示します。マーカーを削除しないでください。
- 特定のエージェント製品に依存する表現は、`README.md` の製品別セクションに閉じ込めます。プロンプト本文はツール中立に保ちます。

## 検証コマンド

| 目的 | コマンド |
| --- | --- |
| unit test | `python -m unittest discover -s tests -v` |
| ワークフロー構文の確認 | `python -c "import yaml,sys;[yaml.safe_load(open(p)) for p in sys.argv[1:]]" .github/workflows/*.yml templates/*.yml` |

`scripts/` は標準ライブラリのみを使用します。依存パッケージを追加しないでください。

## 変更時に注意する領域

- `.github/workflows/reusable-ci-summary.yml`: 他リポジトリから呼ばれる公開インターフェースです。入力名の変更・削除は破壊的変更になります。fork PR で platform checkout とコメントジョブを実行しない条件を弱めないでください。

## セキュリティ

Secret、アクセストークン、個人情報を、プロンプト、テンプレート、テストデータ、コミットに含めません。マスク処理（`mask_secrets`）を変更する場合は、対応するテストを追加してください。
