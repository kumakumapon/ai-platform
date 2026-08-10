# AI Platform Repository

## 概要

`ai-platform` は、TypeScript / Python プロジェクトで共通に使うコーディングエージェント向けのルール、タスクプロンプト、GitHub テンプレート、CI 失敗サマリーを一元管理する正本です。各プロジェクトに同じルールを複製して保守するのではなく、共通部分はこのリポジトリで管理し、個別リポジトリにはそのプロジェクトにだけ必要な情報を置きます。

| 管理場所 | 管理する内容 |
| --- | --- |
| `ai-platform` | 安全・品質の共通ルール、Issue/PR/CI 用のプロンプト、GitHub テンプレート、再利用可能な Workflow |
| 各プロジェクト | 使用技術、アーキテクチャ、検証コマンド、変更禁止領域、DB/API・デプロイ固有の制約 |

このリポジトリはアプリケーション本体や各プロジェクトの業務仕様を持ちません。共通ルールを参照しつつ、実装判断は必ず対象プロジェクトのコード、テスト、`AGENTS.md`、Issue/PR を根拠に行います。

## 使い方（最短手順）

新しいプロジェクトには、まず次の3点を導入します。

1. `templates/AGENTS.project-template.md` を対象プロジェクトの `AGENTS.md` としてコピーし、固有情報を記入します。
2. 必要な GitHub テンプレートを PR 経由で追加します。Issue Form は `.github/ISSUE_TEMPLATE/ai-platform.yml`、PR テンプレートは `.github/pull_request_template.md` に配置します。
3. 使用するエージェントに合わせて渡し方を選びます。
   - ChatGPT Work: 対象タスクに対応する `prompts/` のファイル、プロジェクトの `AGENTS.md`、Issue/PR、関連する CI ログを一緒に渡します。
   - Claude Code / Cloud Agent: `templates/CLAUDE.bridge.md` を `CLAUDE.md` として配置し、`prompts/` を `.claude/commands/` に配置します。詳細は「[Claude Code / Cloud Agent での利用](#claude-code--cloud-agent-での利用)」を参照してください。

既存の `AGENTS.md` やテンプレートがあるプロジェクトでは、上書きせず差分をレビューして統合してください。以後の更新も、各プロジェクト側の Pull Request で反映します。

## 構成

| パス | 役割 |
| --- | --- |
| `prompts/coding-agent-typescript-python.md` | TypeScript / Python 向けの共通安全・品質ルール |
| `prompts/implement-issue.md` | Issue 実装から PR 作成までのプロンプト |
| `prompts/fix-ci.md` | CI 失敗を最小差分で修正するプロンプト |
| `prompts/review-pr.md` | 品質・セキュリティ・互換性の PR レビュープロンプト |
| `prompts/investigate-issue.md` | コードを変更せず調査するプロンプト |
| `prompts/audit-repository.md` | リポジトリの課題・改善点を根拠付きで診断し、必要に応じてIssue化するプロンプト |
| `prompts/propose-features.md` | アプリの目的・実装・拡張性から、価値のある追加実装候補をIssue化するプロンプト |
| `prompts/document-repository.md` | 構成・シーケンス・詳細仕様を人が保守できる技術ドキュメントにまとめるプロンプト |
| `prompts/prepare-release.md` | リリースを公開せず、変更履歴・検証・公開準備を整えるプロンプト |
| `prompts/update-dependencies.md` | 互換性・ライセンス・セキュリティを確認して依存関係を更新するプロンプト |
| `prompts/improve-tests.md` | 重要な未カバーフローに回帰テストを追加するプロンプト |
| `prompts/refactor-repository.md` | 振る舞いを変えずに保守性を改善するプロンプト |
| `prompts/security-review.md` | 公開情報を増やさずにセキュリティを調査するプロンプト |
| `templates/AGENTS.project-template.md` | プロジェクト固有ルールを記入する `AGENTS.md` の雛形 |
| `templates/AGENTS.common-rules.md` | プロジェクトへ手動で適用する範囲を示す、マーカー付きの短い共通ルール |
| `templates/CLAUDE.bridge.md` | `AGENTS.md` を取り込む Claude Code 用 `CLAUDE.md` の雛形 |
| `agents/planner.md` | 実装前の調査・計画整理を担当するサブエージェント（Claude Code 用） |
| `agents/implementer.md` | 計画に基づき最小差分を実装するサブエージェント（Claude Code 用） |
| `agents/reviewer.md` | 計画（着手前）と実装差分（PR作成前）をレビューする必須ゲートのサブエージェント（Claude Code 用） |
| `templates/issue-form.yml` | 実装条件を明確にする Issue Form |
| `templates/pull-request-template.md` | PR の変更・検証・リスクを記録する雛形 |
| `templates/ci-summary-caller.yml` | CI ログを reusable workflow に渡す呼び出し雛形 |
| `scripts/prepare-agent-context.py` | Issue / PR 情報をエージェント向け Markdown に整形 |
| `scripts/summarize-ci.py` | 失敗ログから秘匿情報を伏せた短い Markdown サマリーを生成 |
| `.github/workflows/reusable-ci-summary.yml` | 他リポジトリから呼び出せる CI サマリー workflow |

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

次の15形式を使います。`OWNER/REPOSITORY` は作業対象のリポジトリ名に置き換えます。`PR作成` を付けた場合だけ、作業ブランチからドラフト PR まで作成します。診断は `Issue作成` を付けた場合だけ、既存Issueを照合したうえで改善Issueを作成します。

| 目的 | そのまま送る依頼 |
| --- | --- |
| 指定した Issue を実装して PR を作る | `実装 OWNER/REPOSITORY #123 PR作成` |
| 実装候補を1件おまかせで選び、PRを作る | `実装 OWNER/REPOSITORY PR作成` |
| 関連する実装候補を最大3件おまかせで選び、PRを作る | `実装 OWNER/REPOSITORY おまかせ 3件 PR作成` |
| CI を直して PR を作る | `CI OWNER/REPOSITORY https://github.com/OWNER/REPOSITORY/actions/runs/RUN_ID 修正 PR作成` |
| PR をレビューする | `レビュー OWNER/REPOSITORY #42` |
| Issue を調査するだけ | `調査 OWNER/REPOSITORY #97` |
| リポジトリを診断し、改善Issueを作る | `診断 OWNER/REPOSITORY Issue作成` |
| アプリの追加実装候補をIssue化する | `企画 OWNER/REPOSITORY Issue作成` |
| 実装を読み解き、網羅ドキュメントとPRを作る | `文書化 OWNER/REPOSITORY PR作成` |
| AI Platform設定の更新を比較してPRにする | `同期 OWNER/REPOSITORY PR作成` |
| 公開前のリリース準備をする | `リリース OWNER/REPOSITORY PR作成` |
| セキュリティ更新を優先して依存関係を更新する | `依存更新 OWNER/REPOSITORY セキュリティ PR作成` |
| 重要な未カバーフローのテストを追加する | `テスト OWNER/REPOSITORY PR作成` |
| 振る舞いを変えずに安全なリファクタをする | `リファクタ OWNER/REPOSITORY おまかせ PR作成` |
| 公開せずにセキュリティを調査する | `セキュリティ OWNER/REPOSITORY 調査` |

実装で Issue 番号を省略すると、おまかせ選定になります。件数を省略した場合は1件、`2件` または `3件` を指定した場合は最大その件数を選びます。選定では未対応のOpen Issue、既存PR、依存関係、変更範囲、完了条件、リスクを照合し、同じPRで安全に扱える候補だけを組み合わせます。候補が足りない、または無関係・大規模・判断待ちでまとめられない場合は、件数を満たすために寄せ集めず、実装した件数と見送り理由を報告します。

エージェントは、対象リポジトリ、Issue/PR、`AGENTS.md` / `CLAUDE.md`、関連コード、既存テストを
確認してから作業します。実装を左右する重大な不明点だけを質問し、Issue/PR に書かれている内容を
再入力させません。認証・認可・DB・公開 API・デプロイの変更など、根拠が必要な判断は確認してから進めます。

Claude Code / Cloud Agent では、同じ `prompts/quick-request.md` を
`.claude/commands/quick-request.md` に置くと、`/quick-request 実装 owner/repo PR作成` や
`/quick-request 実装 owner/repo おまかせ 3件 PR作成`、`/quick-request 文書化 owner/repo PR作成`、`/quick-request セキュリティ owner/repo 調査`、`/quick-request 同期 owner/repo PR作成` のように利用できます。単体コマンドとしても `.claude/commands/sync-ai-platform.md` に配置すれば `/sync-ai-platform owner/repo PR作成` で同じ更新を実行できます。

## タスクプロンプトの使い分け

用途に応じて、以下のプロンプトを選びます。対象 Issue / PR と関連ログを渡し、プロジェクト固有の `AGENTS.md` にある制約を優先させます。プロンプト本文はエージェント非依存です。

| 作業 | 使用するプロンプト | 期待する結果 |
| --- | --- | --- |
| Issue を実装する | `prompts/implement-issue.md` | 調査、最小実装、検証、PR 用の報告 |
| CI を直す | `prompts/fix-ci.md` | 失敗原因、最小修正、再現・検証結果 |
| PR をレビューする | `prompts/review-pr.md` | 品質・セキュリティ・互換性の指摘 |
| 変更せずに調査する | `prompts/investigate-issue.md` | 原因、選択肢、推奨対応 |
| リポジトリの改善点をIssue化する | `prompts/audit-repository.md` | 根拠・優先度・完了条件を備えた改善Issue |
| アプリの追加実装候補をIssue化する | `prompts/propose-features.md` | ユーザー価値・実装状況・拡張性に基づく実装候補Issue |
| リポジトリを網羅的に文書化する | `prompts/document-repository.md` | 構成・処理フロー・実装仕様を根拠付きで説明するドキュメント |
| AI Platform 設定を更新する | `prompts/sync-ai-platform.md` | 固有設定を保護した更新差分とPR |
| リリース準備をする | `prompts/prepare-release.md` | 変更履歴・公開前検証・リリースノート |
| 依存関係を更新する | `prompts/update-dependencies.md` | 最小の互換・セキュリティ更新 |
| 重要フローのテストを強化する | `prompts/improve-tests.md` | 決定的な回帰テスト |
| 振る舞いを変えずリファクタする | `prompts/refactor-repository.md` | 限定的な保守性改善 |
| セキュリティを調査する | `prompts/security-review.md` | 非公開前提の読み取り専用調査 |

各プロンプトの冒頭には YAML フロントマター（`description`、`argument-hint`、`disable-model-invocation`）があります。Claude Code ではスラッシュコマンドの定義として使われ、それ以外のエージェントでは無視される短いヘッダーです。

### ChatGPT Work での利用

Issue/PR の情報を `prepare-agent-context.py` で整形し、失敗ログを `summarize-ci.py` で要約してから渡すと、必要な制約と根拠を短く共有できます。

```bash
python scripts/prepare-agent-context.py --input issue.json --kind issue --ci-summary ci-summary.md > agent-context.md
python scripts/summarize-ci.py --input failed-ci.log --workflow-name CI --run-url "https://github.com/OWNER/REPO/actions/runs/123" > ci-summary.md
```

生成した `agent-context.md`、対応するタスクプロンプト、対象プロジェクトの `AGENTS.md` を ChatGPT Work に添付し、「このコンテキストに従って実装・検証・報告して」と依頼します。どちらのスクリプトも標準ライブラリのみを使用します。詳細な入力形式とオプションは各スクリプトの `--help` を参照してください。

### Claude Code / Cloud Agent での利用

Claude Code が読み込むのは `CLAUDE.md` であり、`AGENTS.md` は読み込みません。そのため、`AGENTS.md` を取り込む `CLAUDE.md` を対象プロジェクトに配置します。以下は各プロジェクトへ必要に応じて配置できるファイルです。

| 配置元 | 配置先 | 役割 |
| --- | --- | --- |
| `templates/CLAUDE.bridge.md` | `CLAUDE.md` | `@AGENTS.md` の取り込みと Claude Code 固有の運用 |
| `prompts/coding-agent-typescript-python.md` | `.claude/rules/ai-platform-common.md` | 共通ルールの全文をセッション開始時に読み込む |
| `prompts/implement-issue.md` | `.claude/commands/implement-issue.md` | `/implement-issue` |
| `prompts/fix-ci.md` | `.claude/commands/fix-ci.md` | `/fix-ci` |
| `prompts/review-pr.md` | `.claude/commands/review-pr.md` | `/review-pr` |
| `prompts/investigate-issue.md` | `.claude/commands/investigate-issue.md` | `/investigate-issue` |
| `prompts/audit-repository.md` | `.claude/commands/audit-repository.md` | `/audit-repository owner/repo Issue作成` |
| `prompts/propose-features.md` | `.claude/commands/propose-features.md` | `/propose-features owner/repo Issue作成` |
| `prompts/document-repository.md` | `.claude/commands/document-repository.md` | `/document-repository owner/repo PR作成` |
| `prompts/sync-ai-platform.md` | `.claude/commands/sync-ai-platform.md` | `/sync-ai-platform owner/repo PR作成` |
| `prompts/prepare-release.md` | `.claude/commands/prepare-release.md` | `/prepare-release owner/repo PR作成` |
| `prompts/update-dependencies.md` | `.claude/commands/update-dependencies.md` | `/update-dependencies owner/repo セキュリティ PR作成` |
| `prompts/improve-tests.md` | `.claude/commands/improve-tests.md` | `/improve-tests owner/repo PR作成` |
| `prompts/refactor-repository.md` | `.claude/commands/refactor-repository.md` | `/refactor-repository owner/repo おまかせ PR作成` |
| `prompts/security-review.md` | `.claude/commands/security-review.md` | `/security-review owner/repo 調査` |
| `agents/planner.md` | `.claude/agents/planner.md` | サブエージェント `ai-platform-planner`（調査担当、コード変更なし） |
| `agents/implementer.md` | `.claude/agents/implementer.md` | サブエージェント `ai-platform-implementer`（実装担当） |
| `agents/reviewer.md` | `.claude/agents/reviewer.md` | サブエージェント `ai-platform-reviewer`（計画レビュー・差分レビューの両方を担当、コード変更なし） |

このテンプレートで `CLAUDE.md` を置き換える場合はファイル全体が対象になります。プロジェクト固有の Claude Code 用記述がある場合は、内容を比較して `AGENTS.md` 側へ移すか、対象リポジトリで手動統合してください。Claude Code 固有の記述が不要なら、`CLAUDE.md` を `AGENTS.md` へのシンボリックリンクにする方法もあります（Windows では管理者権限または開発者モードが必要です）。

`.claude/rules/ai-platform-common.md` を配置すると共通ルールの全文が毎回読み込まれるため、`AGENTS.md` のマーカー区間は他のエージェント向けの要約として残せます。

#### 調査・計画レビュー・実装・差分レビューの段階分け（全ツール共通）とサブエージェントへの委任（Claude Code 限定）

`prompts/implement-issue.md`、`fix-ci.md`、`improve-tests.md`、`refactor-repository.md`、`update-dependencies.md`、および `quick-request.md` の `実装` / `CI` / `テスト` / `リファクタ` / `依存更新` は、次の4段階をプロンプト本文（ツール中立）に含んでいます。単一のエージェントが1つの会話の中で自己レビューとして実行するもので、**ChatGPT Work を含むどのツールでも機能します**。

1. 調査（目的・完了条件・変更範囲・実装方針・リスクを整理する）
2. 計画レビュー（要求との整合性・見落とし・実現性を確認する必須ゲート。Critical/High 相当の懸念があれば着手前に解消する）
3. 実装
4. 差分レビュー（`review-pr.md` と同じ観点で確認する必須ゲート。Critical/High 相当の指摘があれば完了・PR作成前に解消する）

コードを変更しない `/review-pr`、`/investigate-issue`、`/audit-repository`、`/propose-features`、`/security-review` にはこの段階分けを適用しません（すでに単独で完結する設計です）。

Claude Code では、この4段階を独立したコンテキストのサブエージェントへ委任することで、権限分離とレビューの客観性を高められます。`agents/` を `.claude/agents/` に配置すると、次のサブエージェントが使えます。

| 段階 | サブエージェント | 権限 |
| --- | --- | --- |
| 1. 調査 | `ai-platform-planner` | 読み取りとテスト実行のみ。コード・設定・Issue・PR は変更しない |
| 2. 計画レビュー | `ai-platform-reviewer` | 読み取りとテスト実行のみ。実装着手前の必須ゲート |
| 3. 実装 | `ai-platform-implementer` | 通常の編集権限を継承 |
| 4. 差分レビュー | `ai-platform-reviewer` | 読み取りとテスト実行のみ。PR作成前の必須ゲート |

`ai-platform-reviewer` は計画レビューと差分レビューの両方で使い回します（同じ基準を独立したコンテキストで2回適用するもので、別のサブエージェントを用意する必要はありません）。サブエージェントは会話履歴を共有しないため、各段階への委任時には目的・完了条件・変更範囲などを明示的に渡す必要があります。1タスクあたりの実行回数が増えるため、レイテンシとコストは単一エージェントでの実行より増えます。`.claude/agents/` を配置していない場合は、プロンプト本文の指示どおり同じ会話の中で自己レビューとして実行され、ゲート自体は変わりません。

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

- クラウドセッションからの `git push` は、そのセッションの作業ブランチだけに制限されます。テンプレートの更新は、対象リポジトリで差分を確認してPRとして作成します。
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

## 更新の運用

テンプレートや共通ルールを更新したら、このリポジトリでレビュー済み PR をマージし、対象プロジェクトでは `同期 owner/repo PR作成` で差分を確認して個別の更新PRを作成します。`AGENTS.md` は `<!-- AI-PLATFORM:START -->` / `<!-- AI-PLATFORM:END -->` の範囲だけを候補にし、固有部分を上書きしません。個別プロジェクトの固有ルールに変更が必要なら、まずそのプロジェクトで変更し、共通化できるかを別途検討してください。

## セキュリティ上の注意

- Secret、アクセストークン、個人情報、ログに含まれる認証情報をプロンプト・Issue・PR・Job Summary に掲載しません。`summarize-ci.py` は Secret らしい値をマスクしますが、入力ログの公開範囲も確認してください。
- 認証・認可、DB スキーマ、公開 API、デプロイ設定は根拠とプロジェクト固有レビューなしに変更しません。
- reusable workflow は通常 `contents: read` のみです。PR コメントは same-repository PR の明示的 opt-in 時だけ、コメントジョブに限定して `pull-requests: write` を使います。
- Claude Code のクラウド環境に設定した環境変数は、その環境を使う全員が参照できます。専用の Secret ストアはないため、API キーやトークンを設定しません。

## 今後の拡張候補

- 言語・フレームワーク別の検証コマンドセット
- CodeQL / 依存関係更新 / SBOM の共通テンプレート
- Issue・PR・CI 情報を GitHub API から取得するコンテキスト生成アダプタ
- 複数リポジトリへのテンプレート適用状況を確認するチェックリスト
- ルール・テンプレートのバージョン固定と互換性ポリシー
