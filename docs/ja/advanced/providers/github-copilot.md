---
title: GitHub Copilot
description: Discord または Telegram を使って GitHub Copilot のデバイスログインを完了します。
translation_source:
  path: docs/advanced/providers/github-copilot.md
  commit: 8e2ddc80214e950127133e680a3534f8eea28dac
---

| 必要なシークレット | オーバーレイ |
| --- | --- |
| `DISCORD_BOT_TOKEN` | `values-github-copilot.yaml` |
| `TELEGRAM_BOT_TOKEN`（`auth.deviceFlow.notify: telegram` と併用） | `values-github-copilot.yaml` と下記の上書き設定 |

## 利用条件

Discord または Telegram のボットと、GitHub Copilot の利用権限が必要です。
ログイントークンを再利用するには、永続ストレージも必要です。

Hermes v0.23.0 で、`copilot` プロバイダーは
[GitHub Copilot Labs プラグイン](https://github.com/NousResearch/hermes-labs-plugins/pull/34)に移行しました。
Copilot を選択したプロファイルには、Hermes がプラグインを自動でインストールします。
外向き通信を制限している場合は、Copilot API に加え、初回起動時にプラグインカタログと
GitHub 上のプラグインのソースにアクセスできるようにしてください。

`config.model.provider: copilot` は変更しないでください。チャートのデバイスログインは
引き続き `COPILOT_GITHUB_TOKEN` を Hermes のボリュームに保存し、プラグインも同じキーを読み込みます。
別のマシンで GitHub または Copilot の CLI にログインしただけでは、プラグインはその認証情報を使えません。
その場合は、チャートのデバイスログインを使ってください。

## インストール

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-github-copilot.yaml \
  --set-string env.DISCORD_BOT_TOKEN='<real-value>' --wait
```

複数の認証情報が必要な例では、記載されているすべての値を `--set-string` で渡すか、
`extraEnvFrom` で既存の Secret を参照してください。

## デプロイ時の設定

初回起動時の Pod ログまたは Discord の通知に表示されるデバイスコードを、GitHub で承認します。

## 2 回目以降の起動

トークンは永続ボリューム上の `HERMES_HOME/.env` に保存されます。次回の起動時に、
初期化コンテナは `https://api.github.com/user` でトークンを確認し、有効であればログインを省略します。
確認先が HTTP 401 または 403 を返すと、初期化コンテナはデバイスログインをやり直します。
この確認は Copilot のプランに依存しません。チャート 1.18.0 までは
`copilot_internal/v2/token` で確認していました。このエンドポイントは Copilot Free の有効な
トークンにも 403 を返したため、再起動のたびに新しいコードが必要でした
（[#349](https://github.com/jyje/hermes-agent-helm/issues/349)）。`validateUrl` を上書きする場合は、
使用可能なトークンに 200 を返し、再ログインが必要な場合にのみ 401 または 403 を返すエンドポイントを使ってください。

## Discord の代わりに Telegram を使う

`auth.deviceFlow.notify: telegram` を設定し、Discord 用の値の代わりに
`TELEGRAM_BOT_TOKEN`、`TELEGRAM_HOME_CHANNEL`、`TELEGRAM_ALLOWED_USERS` を指定します。
デバイスコードは Telegram チャットに届きます。`readyNotify.enabled: true` にすると、
エージェントの起動時に同じチャットへ通知が届きます。Copilot Free アカウントでの実機確認では、
ログインが完了し、起動通知が届き、`gpt-4o` で応答できました。利用可能なモデルは GitHub のプランに従います。

[元の YAML を開く](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-github-copilot.yaml)

## オーバーレイ全体

```yaml title="charts/hermes-agent/values-github-copilot.yaml"
--8<-- "charts/hermes-agent/values-github-copilot.yaml"
```
