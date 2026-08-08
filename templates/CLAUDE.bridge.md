# CLAUDE.md

@AGENTS.md

## このファイルの役割

Claude Code が読み込むのは `CLAUDE.md` だけで、`AGENTS.md` は読み込みません。冒頭の import で `AGENTS.md` を取り込むことで、他のコーディングエージェントと同じルールを共有します。

プロジェクト固有の指示は `AGENTS.md` 側に書きます。このテンプレートを使って `CLAUDE.md` を更新する場合は、Claude Code 固有の指示を対象プロジェクト側で手動統合してください。Claude Code 固有の記載が不要な場合は、`CLAUDE.md` を `AGENTS.md` へのシンボリックリンクにしても同じ結果になります（Windows では管理者権限または開発者モードが必要なため、import 方式を推奨します）。

## タスク別コマンド

`.claude/commands/` に必要なコマンドを配置した場合、次のコマンドを使用できます。引数には対象の URL または番号を渡します。

| コマンド | 用途 |
| --- | --- |
| `/implement-issue` | Issue の調査、最小差分の実装、検証、報告 |
| `/fix-ci` | CI 失敗の原因特定、最小修正、再検証 |
| `/review-pr` | 品質・セキュリティ・互換性のレビュー（コードは変更しない） |
| `/investigate-issue` | コードを変更しない原因調査と対応案の比較 |
| `/audit-repository` | リポジトリの課題・改善点を診断し、必要に応じて重複のないGitHub Issueを作成 |
| `/propose-features` | アプリの目的・実装・拡張性を確認し、追加実装候補を必要に応じてGitHub Issueとして作成 |

## サブエージェントによるオーケストレーション

`agents/` を `.claude/agents/` に配置した場合、`ai-platform-planner` / `ai-platform-implementer` / `ai-platform-reviewer` の3サブエージェントが使えます。次のコマンドを実行するときは、常にこの順で委任します。

対象: `/implement-issue`、`/fix-ci`、`/improve-tests`、`/refactor-repository`、`/update-dependencies`、および `/quick-request` の `実装` / `CI` / `テスト` / `リファクタ` / `依存更新`。

コードを変更しない `/review-pr`、`/investigate-issue`、`/audit-repository`、`/propose-features`、`/security-review` や、`Issue作成` を伴わない診断・企画には適用しません。

1. `ai-platform-planner` に、対象の Issue/PR/CI失敗ログと完了条件を渡して調査を委任し、変更範囲・実装方針・リスクを整理させる。
2. 調査結果に基づいて実装する（`ai-platform-implementer` に委任するか、自身で実装する）。
3. 実装後、差分とテスト結果を `ai-platform-reviewer` に渡してレビューを委任する。
4. **レビューで Critical または High の指摘がある場合、PR を作成せず、指摘に対応してから再度レビューする。** これは省略できない必須ゲート。Medium 以下の指摘は、対応するか対応しない理由を報告に残す。
5. レビューで Critical/High の指摘がなくなってから PR を作成する。

<!-- サブエージェントへの委任は Claude Code 固有の機能です。この節は AGENTS.md 側には反映しません。 -->

## 検証コマンドの実行

`AGENTS.md` の「検証コマンド」を実行する前に、依存関係が導入済みかを確認します。クラウドセッションは毎回新しい VM でリポジトリを clone するため、ローカルにだけ導入した依存やツールは存在しません。導入が必要な場合は、未導入であることを報告に含めます。

<!-- 依存導入を自動化する場合は、リポジトリの .claude/settings.json に SessionStart hook を設定します。設定例は AI Platform Repository の README を参照してください。 -->

## 報告とコミット

- 実行していない検証を成功として報告しません。実行できなかった検証は、理由とともに明示します。
- コミットとプッシュは、依頼された場合にのみ行います。クラウドセッションからプッシュできるのは、そのセッションの作業ブランチだけです。
- PR を作成する場合は、`.github/pull_request_template.md` の項目を埋めます。

<!--
このテンプレートを `CLAUDE.md` に適用する場合は、ファイル全体が置き換わります。
プロジェクト固有の指示は AGENTS.md に記載してください。
Claude Code 固有の指示（plan mode を使う範囲、レビューが必須のディレクトリ、
優先して使うサブエージェントなど）は、適用前に対象プロジェクト側で手動統合してください。
-->
