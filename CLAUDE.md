# CLAUDE.md — ai-platform

このリポジトリは、TypeScript / Python プロジェクト向けのコーディングエージェント用ルール、タスクプロンプト、GitHub テンプレート、CI サマリー機構の正本です。アプリケーション本体は含みません。詳細は `README.md` を参照してください。

## 変更時の原則

- `prompts/`、`templates/`、`agents/` は、複数のプロジェクトで手動適用できる共通資産です。特定プロジェクトの事情に依存する記述を追加しません。
- `prompts/` のタスクプロンプトは、対象プロジェクトの `.claude/commands/` へ配置できます。YAML フロントマター（`description`、`argument-hint`、`disable-model-invocation`）を壊さないでください。`argument-hint` は `<owner/repo>` で始めます。
- タスクプロンプトは次の構成に統一します。`依頼形式` → （任意で `入力情報`）→ `手順` → `完了基準` → （任意でプロンプト固有の節）→ `禁止事項` → `報告形式`。`報告形式` は散文ではなく ```md フェンス内の Markdown テンプレートにします。出力が構造化されていないと、複数プロジェクト・複数ツール間で結果を比較できなくなります。`quick-request.md`（複合入口）と `coding-agent-typescript-python.md`（ルール文書）はこの構成の対象外です。
- プロンプトを追加・変更したら `tests/test_prompt_structure.py` を実行します。構成、フロントマター、特定プロジェクト名の混入、`templates/CLAUDE.bridge.md` のコマンド表との対応を検証します。プロンプトを1件追加したら、同テンプレートのコマンド表にも1行追加してください。
- `agents/` のサブエージェント定義は、対象プロジェクトの `.claude/agents/` へ配置できます。`name` フロントマターを変更すると `templates/CLAUDE.bridge.md` のオーケストレーション手順との対応が壊れるため、変更する場合は両方を同時に更新してください。
- 実装系プロンプト（`implement-issue.md` 等）が要求する2つのレビューゲート（計画レビュー: Critical/High 解消まで着手しない、差分レビュー: Critical/High 解消までPR作成しない）は、ツール中立な自己レビューとしてプロンプト本文に実装してください。`agents/` のサブエージェント委任は、そのゲートを独立したコンテキストで実行する Claude Code 向けの追加手段であり、代替ではありません。両者の基準がずれないようにしてください。
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
