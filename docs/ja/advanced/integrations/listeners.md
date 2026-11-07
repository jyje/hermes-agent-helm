---
title: 公開リスナー一覧
description: バージョン別の HTTP リスナー、認証、Kubernetes のルーティング設定。
translation_source:
  path: docs/advanced/integrations/listeners.md
  commit: 9864b4e468af6282319822029794dea65eb340c0
---

<a id="public-listener-inventory"></a>

# 公開リスナー一覧

各行のリンク先にある Hermes のタグで確認した内容です。ここで示すのは
**リスナーを有効にした場合のデフォルト**で、チャートの標準インストールで
開くポートではありません。標準のゲートウェイはメッセージングサービスに
外向きに接続します。アクセス用 Service と HTTP ルーティングはオプトインです。
StatefulSet のヘッドレス Service は DNS のみを提供します。上流のアダプターが
デュアルスタックを使う場合、全インターフェースへのバインドには IPv4 と IPv6 が含まれます。

| リスナーとタグ付きソース | デフォルトのバインド先 / ポート | メッセージ・データ要求の認証 | チャートの設定 |
| --- | --- | --- | --- |
| [管理ダッシュボード](https://github.com/NousResearch/hermes-agent/tree/v0.22.2/hermes_cli/dashboard_auth) | イメージでは全インターフェース、9119 | basic/OAuth/OIDC のセッション認証。ループバック以外にはプロバイダーが必要。サインインはシェルへのアクセスと同等に扱う。 | `dashboard.enabled`、Service と Ingress/HTTPRoute。一般公開には OAuth/OIDC を使用し、basic は信頼できるネットワークや VPN に限定する。 |
| [Webapp](https://github.com/NousResearch/hermes-agent/blob/v0.23.0/gateway/webapp_listener.py) | ループバック、9120 | ループバック以外へのバインド、または外部オリジンを使う場合はダッシュボードの認証が必要。 | `config.webapp` と明示的な `service.ports`。`values-webapp.yaml` を参照。 |
| [OpenAI 互換 API](https://github.com/NousResearch/hermes-agent/blob/v0.22.2/gateway/platforms/api_server.py) | 上流はループバック、8642。チャートは有効時に `0.0.0.0` を設定する。 | ループバックでも Bearer トークン `API_SERVER_KEY` が必要。 | `apiServer.enabled` と明示的な `service.ports`、ルーティング。 |
| [汎用 Webhook](https://github.com/NousResearch/hermes-agent/blob/v0.22.2/gateway/platforms/webhook.py) | 全インターフェース、8644 | 全体またはルート単位の署名用シークレットと、送信元に応じた署名検証。 | `webhook.enabled`。ルートは `/webhooks/<route>` 配下で、プロファイルの接頭辞付きルートも使用できる。Service ポートを明示する。 |
| [A2A](https://github.com/NousResearch/hermes-agent/blob/v0.23.0/plugins/platforms/a2a/security.py) | ループバック、9900。リモート接続にはトークンが必要。 | ピアごとの `A2A_PEER_TOKENS`（名前付きの識別子）または共有 `A2A_BEARER_TOKEN`（`ip:<source-ip>`）。配信するには `A2A_TRUSTED_PEERS` と識別子を一致させる。 | `config.gateway.platforms.a2a`、ホストとポートの環境変数、明示的な Service。`values-a2a.yaml` を参照。 |
| [Telegram ネイティブ Webhook](https://github.com/NousResearch/hermes-agent/blob/v0.22.2/plugins/platforms/telegram/adapter.py) | 全インターフェース、8443。Webhook URL を指定しない場合はポーリング。 | `TELEGRAM_WEBHOOK_SECRET` が必須。受信側でシークレットトークンのヘッダーを検証する。 | 環境変数や設定、明示的な Service とルーティング。`values-telegram-webhook.yaml` を参照。 |
| [WhatsApp Cloud](https://github.com/NousResearch/hermes-agent/blob/v0.22.2/gateway/platforms/whatsapp_cloud.py) | 全インターフェース、8090 | GET のチャレンジには検証トークン、POST にはアプリのシークレットを使った HMAC。 | 環境変数や設定、明示的なポートと `/whatsapp/webhook` へのルーティング。 |
| [SMS / Twilio](https://github.com/NousResearch/hermes-agent/blob/v0.22.2/plugins/platforms/sms/adapter.py) | ループバック、8080 | `TWILIO_AUTH_TOKEN` で `X-Twilio-Signature` を検証する。`SMS_WEBHOOK_URL` は公開 URL と一致させる。 | Service を使う場合は `SMS_WEBHOOK_HOST=0.0.0.0` を設定し、`/webhooks/twilio` を明示的に公開する。 |
| [WeCom コールバック](https://github.com/NousResearch/hermes-agent/blob/v0.22.2/gateway/platforms/wecom/callback_adapter.py) | 全インターフェース、8645 | コールバックトークン、メッセージ署名、エンコード用 AES キー。 | 環境変数や設定、明示的なポートと `/wecom/callback` へのルーティング。外向きの WeCom WebSocket モードとは別。 |
| [BlueBubbles コールバック](https://github.com/NousResearch/hermes-agent/blob/v0.22.2/gateway/platforms/bluebubbles.py) | ループバック、8645 | 対応するクエリパラメーターやヘッダーで設定済みのパスワードを渡す。 | Service を使う場合は `BLUEBUBBLES_WEBHOOK_HOST=0.0.0.0` を設定し、`/bluebubbles-webhook` を明示的に公開する。認証情報をログに出さない。 |
| [Microsoft Graph Webhook](https://github.com/NousResearch/hermes-agent/blob/v0.22.2/gateway/platforms/msgraph_webhook.py) | 全インターフェース、8646 | `client_state`。ループバック以外では `allowed_source_cidrs` も必須。 | 環境変数や設定、明示的なポートと `/msgraph/webhook` へのルーティング。リンク先のタグ付きソースで CIDR が強制される。 |

リスナーを公開する前に、アダプターやプラグインが利用できることを確認し、
認証情報を設定してください。バインドのデフォルトと検証条件は、リンク先の
タグ付きソースに基づいています。上流の環境変数リファレンスはソースの変更に
遅れることがあります。この表はソース調査の結果であり、すべてのメッセージング
サービスを実際に検証したものではありません。

<a id="choose-the-ports-explicitly"></a>

## ポートを明示する

チャートの汎用 `service.ports` とルーティング設定で、メッセージングサービスの
ネイティブ受信機能を構成できます。プラットフォームごとに個別の値ブロックは
用意していません。上流のリスナーを有効にしても、Kubernetes のルートは作成されません。

- 空でない `service.ports` リストは従来のダッシュボードポートを**置き換えます**。
  公開するすべてのリスナーを含め、各ホストとパスを対応するポートにルーティングしてください。
- WeCom コールバックと BlueBubbles はどちらもデフォルトが 8645 です。同じ Pod で
  有効にする場合は、片方のリスナーポートと Service・ルーティング側のポートを変更してください。
- ループバック専用のリスナーは Service のトラフィックを受けられません。
  必要な認証を先に構成し、意図的にバインド先を広げてください。
- NetworkPolicy を有効にしている場合は、実際の Ingress コントローラーのピアから
  対象ポートへのアクセスを許可してください。無関係な Webhook のために
  ダッシュボードのアクセス範囲を広げないでください。
- 署名検証に使う Webhook のパスと外部 HTTPS URL を維持してください。
  プロキシでパスを書き換えるために署名検証を無効にしないでください。

<a id="webapp-on-a-trusted-cluster"></a>

## 信頼できるクラスターでの Webapp

Hermes v0.23.0 を使い、新規リリースとしてインストールします。ネームスペースを作成し、
外部 Secret `hermes-agent-webapp-secrets` に `OPENAI_API_KEY`、
`HERMES_DASHBOARD_BASIC_AUTH_USERNAME`、`HERMES_DASHBOARD_BASIC_AUTH_PASSWORD`、
`HERMES_DASHBOARD_BASIC_AUTH_SECRET` を入れてください。強いパスワードと、
それとは別のランダムなセッション署名用シークレットを使います。

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent \
  -f charts/hermes-agent/values-webapp.yaml --wait
kubectl --namespace hermes-agent port-forward --address 127.0.0.1 \
  service/hermes-agent 9120:9120
```

`http://127.0.0.1:9120` を開いてサインインします。Webapp は組み込みのパスワード
認証を使い、ポート 9119 の管理ダッシュボードとは別に動作します。
ページにアクセスできない場合は、ゲートウェイのログでリスナーや認証の起動エラーを
確認してください。Helm の待機処理は Webapp リスナーの準備を確認しません。

このパスワード認証の例は信頼できるネットワークで使用してください。
URL を共有する必要がない場合は、ローカルのポートフォワードを使います。
サインインすると、エージェントのワークスペースとツールにアクセスできます。
既存のリリースで `bootstrap.overwrite: false` の場合は、永続化された
`config.yaml` を明示的に更新して Pod を再起動してください。Helm の値だけを変更しても
既存のファイルは置き換わりません。

<a id="webapp-behind-an-https-ingress"></a>

### HTTPS Ingress 経由の Webapp

信頼できるネットワークや VPN では、同じ外部 Secret を使い、以下の値を
`values-webapp.yaml` に重ねて適用できます。ホスト名、Ingress クラス、TLS Secret 名、
プロキシアドレスを置き換えてください。TLS Secret はリリースと同じネームスペースに
配置し、Webapp のホスト名をカバーする必要があります。

```yaml title="webapp-ingress.yaml"
config:
  webapp:
    public_url: https://webapp.example.com
  dashboard:
    trusted_proxies:
      - "192.0.2.10/32"

ingress:
  enabled: true
  className: your-ingress-class
  hosts:
    - host: webapp.example.com
      paths:
        - path: /
          pathType: Prefix
          port: 9120
  tls:
    - secretName: webapp-tls
      hosts:
        - webapp.example.com
```

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent \
  -f charts/hermes-agent/values-webapp.yaml -f webapp-ingress.yaml --wait
```

- ブラウザーからアクセスするオリジンは `config.webapp.public_url` に設定します。
  `config.dashboard.public_url` は管理ダッシュボード用です。
- 管理ダッシュボードを無効にしていても、Hermes は `config.dashboard.trusted_proxies`
  から信頼するプロキシを読み取ります。実際のプロキシ IP、またはプロキシ専用の CIDR
  だけを登録してください。共有 Pod CIDR を信頼すると、他のワークロードが転送ヘッダーの
  クライアント IP を偽装できます。共有クラスターでは [NetworkPolicy](networkpolicy.md)
  で、Webapp のポート 9120 への通信を Ingress コントローラーのピアに限定してください。
  TLS がプロキシで終端される場合、信頼するピアがないとサインインできても
  Cookie に `Secure` が付きません。
- 公開ホスト名を維持し、TLS 終端で `X-Forwarded-Proto: https` を設定します。
  クライアントから受け取った転送ヘッダーをそのまま渡さないでください。
  `/api/ws` のパスを書き換えずに WebSocket のアップグレードを転送します。
- URL を共有する前に、サインアウト中のアクセスが拒否されること、セッション Cookie に
  `Secure` と `HttpOnly` が付くこと、サインイン後に WebSocket が接続できることを
  確認してください。このパスワード認証の例はインターネットに直接公開しないでください。

この経路は、Hermes v0.23.0、テスト用 TLS 証明書、Ingress コントローラーを使って
kind で確認しました。公開 DNS、証明書の発行、HTTPRoute は検証対象外です。

<a id="telegram-webhook-example"></a>

## Telegram Webhook の例

選択したネームスペースに外部 Secret `hermes-agent-telegram-webhook-secrets` を用意し、
`OPENAI_API_KEY`、`TELEGRAM_BOT_TOKEN`、`TELEGRAM_WEBHOOK_SECRET`、
`TELEGRAM_ALLOWED_USERS` を設定します。長いランダムな検証用シークレットを生成し、
対象ユーザーだけを許可してください。認証情報をコミットしないでください。

ホスト名、Ingress クラス、TLS Secret または cert-manager の issuer アノテーションを
環境に合わせてからインストールします。

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-telegram-webhook.yaml --wait
```

公開 URL は HTTPS のポート 443 を使います。Ingress は `/telegram` を Service の
ポート 8443 に転送し、Pod の受信側に届けます。`TELEGRAM_WEBHOOK_SECRET` は外部 Secret
に保持されます。このオーバーレイは、ダッシュボードや汎用 Webhook リスナーを有効にしません。
ポーリングを使う場合は、Webhook URL とこれらのオプトインのネットワーク設定を省略します。

```yaml title="charts/hermes-agent/values-telegram-webhook.yaml"
--8<-- "charts/hermes-agent/values-telegram-webhook.yaml"
```

他のリスナーも同様に、アダプターのバインド先、認証、パスに合わせてポートを明示します。
クラスター固有のルーティングについては、[ダッシュボードのサインイン](dashboard.md)、
[Ingress](ingress.md)、[HTTPRoute](httproute.md)、[NetworkPolicy](networkpolicy.md)
を参照してください。
