# AI Platform Repository

`ai-platform` は、TypeScript / Python プロジェクトで共通に使うコーディングエージェント向けのルール、タスクプロンプト、GitHub テンプレート、CI 失敗サマリーを一元管理する正本です。各プロジェクトには技術構成・アーキテクチャ・DB/API・デプロイなどの固有情報だけを保持し、共通方針はここから参照または同期します。

## 構成

| パス | 役割 |
| --- | --- |
| `prompts/coding-agent-typescript-python.md` | TypeScript / Python 向けの共通安全・品質ルール |
| `prompts/implement-issue.md` | Issue 実装から PR 作成までのプロンプト |
| `prompts/fix-ci.md` | CI 失敗を最小差分で修正するプロンプト |
| `prompts/review-pr.md` | 品質・セキュリティ・互換性の PR レビュープロンプト |
| `prompts/investigate-issue.md` | コードを変更せず調査するプロンプト |
| `templates/AGENTS.project-template.md` | プロジェクト固有ルールを記入する `AGENTS.md` の雛形 |
| `templates/AGENTS.common-rules.md` | 同期対象に埋め込む、マーカー付きの短い共通ルール |
| `templates/issue-form.yml` | 実装条件を明確にする Issue Form |
| `templates/pull-request-template.md` | PR の変更・検証・リスクを記録する雛形 |
| `templates/ci-summary-caller.yml` | CI ログを reusable workflow に渡す呼び出し雛形 |
| `scripts/prepare-agent-context.py` | Issue / PR 情報を ChatGPT Work 用 Markdown に整形 |
| `scripts/summarize-ci.py` | 失敗ログから秘匿情報を伏せた短い Markdown サマリーを生成 |
| `.github/workflows/reusable-ci-summary.yml` | 他リポジトリから呼び出せる CI サマリー workflow |
| `.github/workflows/sync-agent-rules.yml` | 対象プロジェクトへ同期用 PR を作る手動 workflow |
| `.github/sync-targets.json` | 同期の対象・対象ファイル・opt-in 状態を管理する設定 |

## 新しいプロジェクトへの導入

1. `templates/AGENTS.project-template.md` を対象プロジェクトの `AGENTS.md` にコピーし、使用技術・検証コマンド・変更禁止領域などを埋めます。
2. 必要なら `templates/issue-form.yml` を `.github/ISSUE_TEMPLATE/ai-platform.yml`、`templates/pull-request-template.md` を `.github/pull_request_template.md` に導入します。既存テンプレートがあれば内容を比較して PR で統合してください。
3. CI の失敗ログをファイルに保存するジョブを用意し、下記の reusable workflow を `uses` で呼び出します。
4. ChatGPT Work に渡す際は、共通プロンプトとプロジェクトの `AGENTS.md` を併用します。Issue / PR の情報は `prepare-agent-context.py` で Markdown にすると扱いやすくなります。
5. 導入・更新ともに対象プロジェクトのブランチで行い、レビュー可能な Pull Request を作成してからマージします。

## ChatGPT Work での利用

Issue 実装では `prompts/implement-issue.md` を、CI 修正では `prompts/fix-ci.md` を、レビューでは `prompts/review-pr.md` を使います。対象 Issue / PR と関連ログを渡し、プロジェクト固有の `AGENTS.md` にある制約を優先させます。

```bash
python scripts/prepare-agent-context.py --input issue.json --kind issue --ci-summary ci-summary.md > agent-context.md
python scripts/summarize-ci.py --input failed-ci.log --workflow-name CI --run-url "https://github.com/OWNER/REPO/actions/runs/123" > ci-summary.md
```

どちらのスクリプトも標準ライブラリのみを使用します。詳細な入力形式とオプションは各スクリプトの `--help` を参照してください。

## Reusable Workflow の呼び出し例

別ジョブで収集した失敗ログは、artifact として渡します（GitHub Actions のジョブ間で通常のファイルは共有されません）。`failure()` となったジョブ内でログを保存・upload し、失敗時にも実行される別ジョブから呼び出します。PR コメントを有効にする場合だけ `pull-requests: write` を付与します。

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: set -o pipefail; npm test 2>&1 | tee failed-ci.log
      - if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: failed-ci-log
          path: failed-ci.log
          if-no-files-found: error

  summarize-failure:
    if: failure()
    needs: [test]
    permissions:
      contents: read
      pull-requests: write # comment_on_pr: true の場合だけ
    uses: sj55576/ai-platform/.github/workflows/reusable-ci-summary.yml@main
    with:
      log_file: .ai-platform-failure-log/failed-ci.log
      log_artifact_name: failed-ci-log
      workflow_name: CI
      run_url: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}
      reproduce_command: npm test
      comment_on_pr: true
    secrets:
      # private な AI Platform を使う same-repository 実行時だけ渡す
      platform_read_token: ${{ secrets.AI_PLATFORM_READ_TOKEN }}
```

`reusable-ci-summary.yml` は呼び出し側のリポジトリを読み取り専用で checkout し、AI Platform の `summarize-ci.py` を別途 checkout して Job Summary を生成します。`sj55576/ai-platform` を private 運用にする場合は、呼び出し側が read-only の `platform_read_token` を明示的に渡せます。資格情報は永続化せず、トークンがない・取得できない場合は Secret を要求せずに要約を安全にスキップして理由だけを Job Summary に残します。外部 fork の PR では platform checkout、コメントジョブ、渡された Secret のいずれも実行・参照しません。コメントには識別マーカーを付け、既存コメントを更新するため重複投稿を避けます。

## 更新と同期の運用

同期は `.github/sync-targets.json` の `enabled: true` にした対象だけに、手動の **Sync AI Platform templates** workflow から実行します。初期設定の例は無効であり、意図せず他リポジトリを変更しません。`dry_run: true` で差分を確認してから `false` に切り替えてください。

同期は対象リポジトリの既定ブランチを直接変更しません。`chore/sync-ai-platform-rules` ブランチに変更を作り、同じ同期 PR を更新します。対象リポジトリを限定した fine-grained PAT を `SYNC_REPOSITORIES_TOKEN` として設定する必要があります。AGENTS 共通部分の同期は `<!-- AI-PLATFORM:START -->` / `<!-- AI-PLATFORM:END -->` の両マーカーがある場合だけ実行されるため、プロジェクト固有部分を上書きしません。

テンプレートや共通ルールを更新したら、このリポジトリでレビュー済み PR をマージし、各プロジェクトでは dry run と同期 PR のレビューを実施します。個別プロジェクトの固有ルールに変更が必要なら、まずそのプロジェクトで変更し、共通化できるかを別途検討してください。

## セキュリティ上の注意

- Secret、アクセストークン、個人情報、ログに含まれる認証情報をプロンプト・Issue・PR・Job Summary に掲載しません。`summarize-ci.py` は Secret らしい値をマスクしますが、入力ログの公開範囲も確認してください。
- 認証・認可、DB スキーマ、公開 API、デプロイ設定は根拠とプロジェクト固有レビューなしに変更しません。
- reusable workflow は通常 `contents: read` のみです。PR コメントは same-repository PR の明示的 opt-in 時だけ、コメントジョブに限定して `pull-requests: write` を使います。
- 同期用トークンは fine-grained PAT とし、対象リポジトリだけに Contents: Read/Write と Pull requests: Read/Write を与えます。外部 fork でこの同期 workflow は実行されません。

## 今後の拡張候補

- 言語・フレームワーク別の検証コマンドセット
- CodeQL / 依存関係更新 / SBOM の共通テンプレート
- Issue・PR・CI 情報を GitHub API から取得するコンテキスト生成アダプタ
- 同期 PR の状態を集約するダッシュボード
- ルール・テンプレートのバージョン固定と互換性ポリシー
