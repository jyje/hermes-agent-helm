<!-- translation_source: README.md @ 4c00dee9830393c8829109453d698bb1eb0ef3f3 -->

<div align="center" markdown="1">

# jyje/hermes-agent-helm

<img height="240" src="https://raw.githubusercontent.com/jyje/hermes-agent-helm/main/docs/images/hermes-agent-helm.png" alt="Kubernetes × Hermes Agent"/>

👩🏻‍💻 Kubernetes 上の Hermes Agent - Codex/Copilot でログインし、エージェントチームを軽量に運用できます。

[![GitHub Repo stars](https://img.shields.io/github/stars/jyje/hermes-agent-helm?style=social)](https://github.com/jyje/hermes-agent-helm)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Helm](https://img.shields.io/badge/Helm-3%2B-0F1689?logo=helm&logoColor=white)](https://helm.sh)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?logo=kubernetes&logoColor=white)](https://kubernetes.io)
[![Artifact Hub](https://img.shields.io/endpoint?url=https://artifacthub.io/badge/repository/hermes-agent)](https://artifacthub.io/packages/search?repo=hermes-agent)

[English](README.md) · [한국어](README-ko.md) · [日本語](README-ja.md) · [简体中文](README-zh.md) · **🚀 [Hermes チーム](docs/advanced/teams/index.md)** · [チャートのドキュメント](charts/hermes-agent/README-ja.md) · [CONTRIBUTING](CONTRIBUTING.md) · [SECURITY](SECURITY.md) · [AGENTS](AGENTS.md)

---

**役に立ったら ⭐ をお願いします。ほかの方がこのプロジェクトを見つける助けになります。**

</div>

## 概要

> 日本語版は入門ページを翻訳しています。未翻訳のセクションは英語で表示されます。日本語を母語とするメンテナーによる検証済みの翻訳ではありません。修正の提案を歓迎します。

![Flow of Hermes Agent](https://raw.githubusercontent.com/jyje/hermes-agent-helm/main/docs/images/hermes-agent-helm-flow.png)

[Hermes Agent](https://github.com/NousResearch/hermes-agent) を Kubernetes 上で、1 回の `helm install` で実行できます。Hermes が対応するすべての LLM プロバイダーを利用でき、小規模な単一ノードでも動作し、テンプレート生成だけでなく実際の稼働も検証しています。同じクラスターで複数のインスタンスを [**Hermes チーム**](docs/advanced/teams/reference.md) にまとめることもできます。これは **コミュニティが開発するチャート**であり、Nous Research の公式リリースではありません。

## クイックスタート

1. **OCI（推奨）**: レジストリから直接インストールします。`helm repo add` は不要です。

    ```bash
    helm install hermes-agent oci://ghcr.io/jyje/hermes-agent-helm/hermes-agent \
      --namespace hermes-agent --create-namespace \
      --set-string env.OPENAI_API_KEY='sk-...' \
      --wait
    ```

2. **Helm リポジトリ**: GitHub Pages にも Helm リポジトリを公開しています。一度登録すれば名前でインストールできます。

    ```bash
    helm repo add hermes-agent https://jyje.github.io/hermes-agent-helm
    helm repo update
    helm install hermes-agent hermes-agent/hermes-agent \
      --namespace hermes-agent --create-namespace \
      --set-string env.OPENAI_API_KEY='sk-...' \
      --wait
    ```

最新版ではなく特定の[リリース済みチャート](https://github.com/jyje/hermes-agent-helm/releases)を使う場合は、`--version` でバージョンを固定できます。

未リリースの変更を試すなど、リポジトリのソースからインストールする場合は、下の[開発](#開発)を参照してください。

## このチャートを使う理由

- **`values.yaml` で Hermes のプロバイダー設定を管理。** Hermes は環境変数で `openai-api`、`anthropic`、`gemini`、`openrouter`、`nvidia`、`deepseek`、および [LiteLLM](https://github.com/BerriAI/litellm) などの OpenAI 互換エンドポイントに対応しています。このチャートはその設定を `values.yaml` から渡し、プロバイダー別の編集可能なサンプルを提供します。テンプレートに特定のプロバイダーを固定しません。
- **チャット中心のゲートウェイとアカウントログイン。** Discord または Telegram のボットトークンを渡すと、Kubernetes がライフサイクルを管理する Hermes のアウトバウンドゲートウェイが起動します。**GitHub Copilot** と **OpenAI Codex** では、任意のデバイスログイン初期化機能が一度限りのリンクとコードを Discord のホームチャンネルまたはログに送り、更新可能な認証情報を `HERMES_HOME` に保存します。一度承認すると、通常の Pod 再起動では保存済みログインを再利用します。
- **軽量な構成から本番運用へ。** 初期設定はホームラボ、単一ノード、エッジクラスター向けです。レプリカ 1 個、控えめなリソース要求、小さな PVC から、リソースを増やして拡張できます。Hermes は単一インスタンスのパーソナルエージェントで、`HERMES_HOME`、ゲートウェイ、メモリをそれぞれ 1 つ持ちます。複数のエージェントが必要なら、個別に管理するインスタンスを**チーム**にまとめ、共通のゲートウェイチャンネルでコンテキストを共有します。[Hermes チーム](docs/advanced/teams/reference.md)を参照してください。
- **エンドツーエンドの検証。** CI は一時的な **kind** クラスターにチャートをインストールし、付属のテスト Job（`hermes doctor`）を実行します。リポジトリの `NVIDIA_API_KEY` シークレットが利用可能な場合は、NVIDIA NIM に対して実際の **`hermes chat` 往復通信**も行います。Discord スレッドのリーダーチームでは、人間 → リーダー → メンバー 2 体 → リーダーの実通信も完了しています。Telegram のチーム連携は別の検証対象です。

<div align="center">
  <img src="https://raw.githubusercontent.com/jyje/hermes-agent-helm/main/docs/images/demos/team-k9s-pods.png" alt="kind クラスター上の Hermes チーム august、may、march を k9s で表示"/>
  <p><em>デプロイの証拠: リーダー <code>august</code> とメンバー <code>may</code>/<code>march</code> が kind 上で独立したリリースとして稼働しています。この画像だけでは複数ターンのメンション連携を証明できません。最新の状況は <a href="docs/advanced/teams/reference.md">Hermes チーム</a>を参照してください。</em></p>
</div>

リソース構成、設定モデル、メッセンジャー連携を含むプロバイダー別のインストール例は、[チャートの README](charts/hermes-agent/README-ja.md) を参照してください。

## 本番運用のチェックリスト

以下の機能はデフォルトで有効になっていません。初期設定は軽量なままです。各項目は利用者が明示的に有効にするもので、検証方法も記載しています。実際の根拠を確認して運用への適合性を判断してください。

| 項目 | 方法 | 検証状況 |
|---|---|---|
| Pod Security Standards | `-f charts/hermes-agent/values-hardened.yaml` | kind の強化構成シナリオ（PSS `restricted`） |
| 外向き通信の制御 | `networkPolicy.enabled=true` | CI で生成済みポリシーを検査 |
| カーネルの分離 | `runtimeClassName: gvisor` などのサンドボックスランタイム | クラスター依存。文書化のみ |
| シークレット管理 | [Bitwarden の例](charts/hermes-agent/values-bitwarden.yaml)または [SealedSecret ガイド](examples/argocd/#sealedsecret-walkthrough-nvidia-nim--discord) | Bitwarden: CI の values サンプルのスモークテスト。SealedSecret: 文書化のみ |
| アップグレードの安全性 | `bootstrap.overwrite=false` で実行時の編集を保持 | 文書化済み。CI 検証は未完了（[#235](https://github.com/jyje/hermes-agent-helm/issues/235)） |

## インストールの詳細

### OCI（推奨）

```bash
# render the chart and check its templates before installing
helm template hermes-agent oci://ghcr.io/jyje/hermes-agent-helm/hermes-agent \
  --set-string env.OPENAI_API_KEY='sk-...'

# install with the generic defaults (set your provider key)
# release name == chart name keeps resources clean (hermes-agent-0, not hermes-agent-hermes-agent-0)
helm upgrade --install hermes-agent oci://ghcr.io/jyje/hermes-agent-helm/hermes-agent \
  --namespace hermes-agent --create-namespace \
  --set-string env.OPENAI_API_KEY='sk-...' --wait

# run the install test (doctor-style Job)
helm test hermes-agent -n hermes-agent
kubectl logs -n hermes-agent -l app.kubernetes.io/component=test --tail=-1
```

### Helm リポジトリ

```bash
# add the Helm Repository and fetch the latest chart index
helm repo add hermes-agent https://jyje.github.io/hermes-agent-helm
helm repo update

# render the chart and check its templates before installing
helm template hermes-agent hermes-agent/hermes-agent \
  --set-string env.OPENAI_API_KEY='sk-...'

# install with the generic defaults (set your provider key)
helm upgrade --install hermes-agent hermes-agent/hermes-agent \
  --namespace hermes-agent --create-namespace \
  --set-string env.OPENAI_API_KEY='sk-...' --wait

# run the install test (doctor-style Job)
helm test hermes-agent -n hermes-agent
kubectl logs -n hermes-agent -l app.kubernetes.io/component=test --tail=-1
```

完全な values 表、各プロバイダーと Discord/Telegram・LiteLLM の `values-*.yaml` をまとめた追加サンプル一覧は、[チャートの README](charts/hermes-agent/README-ja.md) を参照してください。YAML をコピーして `-f` で渡せます。[ArgoCD の例](examples/argocd/)もあります。

## 自動化

チャートの利用者に関係する自動化は次の 3 つです。

- **上流の追跡。** 定期ジョブが 6 時間ごとに新しい Hermes イメージを確認し、`appVersion` 更新のプルリクエストを作成します。自動でリリースすることはなく、ほかのチャート変更と同じレビューと Changesets の手順を通ります。
- **署名付きリリース。** 公開時に Helm リポジトリのインデックスと、cosign で署名した OCI アーティファクトを生成します。
- **リリース後の検証。** リリースのたびに CI が公開済み OCI アーティファクトをインストールし、署名を確認してチャートのテストを実行します。

各ワークフロー、トリガー、相互の関係は [CI ガイド](docs/contributing/ci.md)に記載しています。

## 開発

PR を作成する前に変更を確認するには、リポジトリを複製してローカルのチャートパスからインストールします。

```bash
git clone https://github.com/jyje/hermes-agent-helm.git
cd hermes-agent-helm

# render & lint
make template
make lint

# install from the local chart source
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  --set-string env.OPENAI_API_KEY='sk-...' --wait

# run the install test (doctor-style Job)
helm test hermes-agent -n hermes-agent
kubectl logs -n hermes-agent -l app.kubernetes.io/component=test --tail=-1

# or start from a ready-made example (provider, Discord/Telegram, LiteLLM, ...)
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-anthropic-and-discord.yaml \
  --set-string env.ANTHROPIC_API_KEY='sk-ant-...' \
  --set-string env.DISCORD_BOT_TOKEN='...' --wait
```

ブランチ運用、リリース手順、追加のローカル検証（`make docs` / `make test`）は [CONTRIBUTING.md](CONTRIBUTING.md)、チャートの設計原則は [AGENTS.md](AGENTS.md) を参照してください。

## ロードマップ

このチャートは **1 体**のエージェントのデプロイと管理を担います。現在は ArgoCD ApplicationSet によるチームで拡張でき、CRD ベースのオペレーターは未着手の長期候補です。[ロードマップ](docs/about/roadmap.md)を参照してください。

## コントリビューション

Issue、PR、アイデアを歓迎します。まず [CONTRIBUTING.md](CONTRIBUTING.md) でブランチ運用、ローカル検証、リリース手順を確認してください。マージされた貢献は変更履歴とリリースノートに記載されます。

貢献やスターで支えてくださった皆さま、ありがとうございます ⭐

<a href="https://github.com/jyje/hermes-agent-helm/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=jyje/hermes-agent-helm" alt="Contributors" />
</a>

---

> Banner © [Nous Research](https://github.com/NousResearch/hermes-agent) (MIT).
