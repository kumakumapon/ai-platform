# AI Platform Repository

## 概要

`ai-platform` は、TypeScript / Python プロジェクトで共通に使うコーディングエージェント向けのルール、タスクプロンプト、GitHub テンプレート、CI 失敗サマリーを一元管理する正本です。各プロジェクトに同じルールを複製して保守するのではなく、共通部分はこのリポジトリで管理し、個別リポジトリにはそのプロジェクトにだけ必要な情報を置きます。

| 管理場所 | 管理する内容 |
| --- | --- |
| `ai-platform` | 安全・品質の共通ルール、Issue/PR/CI 用のプロンプト、GitHub テンプレート、再利用可能な Workflow |
| 各プロジェクト | 使用技術、アーキテクチャ、検証コマンド、変更禁止領域、DB/API・デプロイ固有の制約 |

このリポジトリはアプリケーション本体や各プロジェクトの業務仕様を持ちません。共通ルールを参照・同期しつつ、実装判断は必ず対象プロジェクトのコード、テスト、`AGENTS.md`、Issue/PR を根拠に行います。

## 使い方（最短手順）

新しいプロジェクトには、まず次の3点を導入します。

1. `templates/AGENTS.project-template.md` を対象プロジェクトの `AGENTS.md` としてコピーし、固有情報を記入します。
2. 必要な GitHub テンプレートを PR 経由で追加します。Issue Form は `.github/ISSUE_TEMPLATE/ai-platform.yml`、PR テンプレートは `.github/pull_request_template.md` に配置します。
3. 使用するエージェントに合わせて渡し方を選びます。
   - ChatGPT Work: 対象タスクに対応する `prompts/` のファイル、プロジェクトの `AGENTS.md`、Issue/PR、関連する CI ログを一緒に渡します。
   - Claude Code / Cloud Agent: `templates/CLAUDE.bridge.md` を `CLAUDE.md` として配置し、`prompts/` を `.claude/commands/` に配置します。詳細は「[Claude Code / Cloud Agent での利用](#claude-code--cloud-agent-での利用)」を参照してください。

既存の `AGENTS.md` やテンプレートがあるプロジェクトでは、上書きせず差分をレビューして統合してください。以後の更新も、同期用 Pull Request または各プロジェクト側の Pull Request で反映します。

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
| `templates/CLAUDE.bridge.md` | `AGENTS.md` を取り込む Claude Code 用 `CLAUDE.md` の雛形 |
| `templates/issue-form.yml` | 実装条件を明確にする Issue Form |
| `templates/pull-request-template.md` | PR の変更・検証・リスクを記録する雛形 |
| `templates/ci-summary-caller.yml` | CI ログを reusable workflow に渡す呼び出し雛形 |
| `scripts/prepare-agent-context.py` | Issue / PR 情報をエージェント向け Markdown に整形 |
| `scripts/summarize-ci.py` | 失敗ログから秘匿情報を伏せた短い Markdown サマリーを生成 |
| `.github/workflows/reusable-ci-summary.yml` | 他リポジトリから呼び出せる CI サマリー workflow |
| `.github/workflows/sync-agent-rules.yml` | 対象プロジェクトへ同期用 PR を作る手動 workflow |
| `.github/sync-targets.json` | 同期の対象・対象ファイル・opt-in 状態を管理する設定 |

## クイック依頼（ChatGPT Work）

長い依頼文を毎回書かずに済むよう、ChatGPT Project に共通指示を一度だけ登録しておけば、
以後は対象と作業種別を1行で指定できます。ChatGPT Project は、Project instructions と Sources を
複数のチャットで共有できるため、この用途に向いています。[OpenAI Docs: Projects and chats](https://learn.chatgpt.com/docs/projects)

### 初回設定（1回だけ）

1. ChatGPT Work で開発用の Project を作成する。
2. `templates/CHATGPT-WORK.project-instructions.md` の本文を Project instructions に貼り付ける。
3. Project の Sources に `prompts/quick-request.md` と `prompts/coding-agent-typescript-python.md` を追加する。
4. 対象プロジェクトの `AGENTS.md` / `CLAUDE.md` はリポジトリから確認させるか、固有ルールを確実に共有したい場合は Sources に追加する。

Project instructions と Sources はプロジェクト内の全チャットで共有されます。作業ごとに新しいチャットを
開始すると、依頼は短くしつつ、過去の作業と混ざらずに進められます。

### 以後の依頼

次の4形式だけを使います。 `PR作成` を付けた場合だけ、作業ブランチからドラフト PR まで作成します。

| 目的 | そのまま送る依頼 |
| --- | --- |
| Issue を実装して PR を作る | `実装 sj55576/MiniStr #96 PR作成` |
| CI を直して PR を作る | `CI sj55576/MiniStr https://github.com/sj55576/MiniStr/actions/runs/123456 修正 PR作成` |
| PR をレビューする | `レビュー sj55576/MiniStr #42` |
| Issue を調査するだけ | `調査 sj55576/MiniStr #97` |

エージェントは、対象リポジトリ、Issue/PR、`AGENTS.md` / `CLAUDE.md`、関連コード、既存テストを
確認してから作業します。実装を左右する重大な不明点だけを質問し、Issue/PR に書かれている内容を
再入力させません。認証・認可・DB・公開 API・デプロイの変更など、根拠が必要な判断は確認してから進めます。

Claude Code / Cloud Agent では、同じ `prompts/quick-request.md` を
`.claude/commands/quick-request.md` に置くと、`/quick-request 実装 owner/repo #番号 PR作成`
のように利用できます。

## タスクプロンプトの使い分け

用途に応じて、以下のプロンプトを選びます。対象 Issue / PR と関連ログを渡し、プロジェクト固有の `AGENTS.md` にある制約を優先させます。プロンプト本文はエージェント非依存です。

| 作業 | 使用するプロンプト | 期待する結果 |
| --- | --- | --- |
| Issue を実装する | `prompts/implement-issue.md` | 調査、最小実装、検証、PR 用の報告 |
| CI を直す | `prompts/fix-ci.md` | 失敗原因、最小修正、再現・検証結果 |
| PR をレビューする | `prompts/review-pr.md` | 品質・セキュリティ・互換性の指摘 |
| 変更せずに調査する | `prompts/investigate-issue.md` | 原因、選択肢、推奨対応 |

各プロンプトの冒頭には YAML フロントマター（`description`、`argument-hint`、`disable-model-invocation`）があります。Claude Code ではスラッシュコマンドの定義として使われ、それ以外のエージェントでは無視される短いヘッダーです。

### ChatGPT Work での利用

Issue/PR の情報を `prepare-agent-context.py` で整形し、失敗ログを `summarize-ci.py` で要約してから渡すと、必要な制約と根拠を短く共有できます。

```bash
python scripts/prepare-agent-context.py --input issue.json --kind issue --ci-summary ci-summary.md > agent-context.md
python scripts/summarize-ci.py --input failed-ci.log --workflow-name CI --run-url "https://github.com/OWNER/REPO/actions/runs/123" > ci-summary.md
```

生成した `agent-context.md`、対応するタスクプロンプト、対象プロジェクトの `AGENTS.md` を ChatGPT Work に添付し、「このコンテキストに従って実装・検証・報告して」と依頼します。どちらのスクリプトも標準ライブラリのみを使用します。詳細な入力形式とオプションは各スクリプトの `--help` を参照してください。

### Claude Code / Cloud Agent での利用

Claude Code が読み込むのは `CLAUDE.md` であり、`AGENTS.md` は読み込みません。そのため、`AGENTS.md` を取り込む `CLAUDE.md` を対象プロジェクトに配置します。以下は同期で配置できるファイルです。

| 配置元 | 配置先 | 役割 |
| --- | --- | --- |
| `templates/CLAUDE.bridge.md` | `CLAUDE.md` | `@AGENTS.md` の取り込みと Claude Code 固有の運用 |
| `prompts/coding-agent-typescript-python.md` | `.claude/rules/ai-platform-common.md` | 共通ルールの全文をセッション開始時に読み込む |
| `prompts/implement-issue.md` | `.claude/commands/implement-issue.md` | `/implement-issue` |
| `prompts/fix-ci.md` | `.claude/commands/fix-ci.md` | `/fix-ci` |
| `prompts/review-pr.md` | `.claude/commands/review-pr.md` | `/review-pr` |
| `prompts/investigate-issue.md` | `.claude/commands/investigate-issue.md` | `/investigate-issue` |

`CLAUDE.md` の同期はファイル全体を置き換えます。プロジェクト固有の Claude Code 用記述を `CLAUDE.md` に追加した場合は、この項目を `enabled: false` に戻し、固有の記述は `AGENTS.md` 側で管理してください。Claude Code 固有の記述が不要なら、`CLAUDE.md` を `AGENTS.md` へのシンボリックリンクにする方法もあります（Windows では管理者権限または開発者モードが必要です）。

`.claude/rules/ai-platform-common.md` を配置すると共通ルールの全文が毎回読み込まれるため、`AGENTS.md` のマーカー区間は他のエージェント向けの要約として残せます。

#### クラウドセッションでの前提

Claude Code のクラウドセッションは、毎回新しい VM でリポジトリを clone して開始します。リポジトリにコミットされたもの（`CLAUDE.md`、`.claude/rules/`、`.claude/commands/`、`.claude/settings.json`、`.mcp.json`）だけが届き、各自のマシンにあるユーザー設定は届きません。共有したい設定はリポジトリにコミットしてください。

検証コマンドを実行するには依存関係の導入が必要です。プロジェクト側でこれを自動化する場合は、`.claude/settings.json` に SessionStart hook を設定します。この設定はローカルとクラウドの両方で実行されるため、クラウドに限定するには `CLAUDE_CODE_REMOTE` を確認します。

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|resume",
        "hooks": [
          { "type": "command", "command": "bash \"$CLAUDE_PROJECT_DIR\"/scripts/install-deps.sh" }
        ]
      }
    ]
  }
}
```

```bash
#!/bin/bash
# scripts/install-deps.sh
[ "$CLAUDE_CODE_REMOTE" = "true" ] || exit 0
npm ci
pip install -r requirements.txt
exit 0
```

`.claude/settings.json` はプロジェクトごとに内容が異なるため、同期対象にしていません。上記を各プロジェクトの設定に統合してください。

#### 運用上の制約

- クラウドセッションからの `git push` は、そのセッションの作業ブランチだけに制限されます。他リポジトリへ書き込む同期は、引き続き **Sync AI Platform templates** workflow で実行します。
- `gh` CLI はクラウドセッションに導入されていません。Issue / PR / Actions の参照は組み込みの GitHub ツールを使用します。`prompts/fix-ci.md` の手順はそのまま適用できます。
- ネットワークは既定で「Trusted」（主要なパッケージレジストリと GitHub のみ）です。社内レジストリなどが必要な場合は、環境設定で許可ドメインを追加します。
- クラウド環境の環境変数は、その環境を使う全員が参照できます。専用の Secret ストアはないため、認証情報を設定しないでください。
- `reusable-ci-summary.yml` が PR に投稿する要約は、そのままエージェントの入力になります。CI 失敗を PR 上で追跡する運用と組み合わせると、失敗ログを手動で渡す必要がなくなります。

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
```

`reusable-ci-summary.yml` は呼び出し側のリポジトリを読み取り専用で checkout し、AI Platform の `summarize-ci.py` を別途 checkout して Job Summary を生成します。AI Platform は public のため、通常は追加トークンを渡す必要がありません。外部 fork の PR では platform checkout、コメントジョブ、渡された Secret のいずれも実行・参照しません。コメントには識別マーカーを付け、既存コメントを更新するため重複投稿を避けます。

## 更新と同期の運用

同期は `.github/sync-targets.json` の `enabled: true` にした対象だけに、手動の **Sync AI Platform templates** workflow から実行します。初期設定の例は無効であり、意図せず他リポジトリを変更しません。`dry_run: true` で差分を確認してから `false` に切り替えてください。

同期は対象リポジトリの既定ブランチを直接変更しません。`chore/sync-ai-platform-rules` ブランチに変更を作り、同じ同期 PR を更新します。対象リポジトリを限定した fine-grained PAT を `SYNC_REPOSITORIES_TOKEN` として設定する必要があります。AGENTS 共通部分の同期は `<!-- AI-PLATFORM:START -->` / `<!-- AI-PLATFORM:END -->` の両マーカーがある場合だけ実行されるため、プロジェクト固有部分を上書きしません。

テンプレートや共通ルールを更新したら、このリポジトリでレビュー済み PR をマージし、各プロジェクトでは dry run と同期 PR のレビューを実施します。個別プロジェクトの固有ルールに変更が必要なら、まずそのプロジェクトで変更し、共通化できるかを別途検討してください。

## セキュリティ上の注意

- Secret、アクセストークン、個人情報、ログに含まれる認証情報をプロンプト・Issue・PR・Job Summary に掲載しません。`summarize-ci.py` は Secret らしい値をマスクしますが、入力ログの公開範囲も確認してください。
- 認証・認可、DB スキーマ、公開 API、デプロイ設定は根拠とプロジェクト固有レビューなしに変更しません。
- reusable workflow は通常 `contents: read` のみです。PR コメントは same-repository PR の明示的 opt-in 時だけ、コメントジョブに限定して `pull-requests: write` を使います。
- 同期用トークンは fine-grained PAT とし、対象リポジトリだけに Contents: Read/Write と Pull requests: Read/Write を与えます。外部 fork でこの同期 workflow は実行されません。
- Claude Code のクラウド環境に設定した環境変数は、その環境を使う全員が参照できます。専用の Secret ストアはないため、API キーやトークンを設定しません。

## 今後の拡張候補

- 言語・フレームワーク別の検証コマンドセット
- CodeQL / 依存関係更新 / SBOM の共通テンプレート
- Issue・PR・CI 情報を GitHub API から取得するコンテキスト生成アダプタ
- 同期 PR の状態を集約するダッシュボード
- ルール・テンプレートのバージョン固定と互換性ポリシー
