---
title: 公开监听器清单
description: 各版本的 HTTP 监听器、身份验证和 Kubernetes 路由配置。
translation_source:
  path: docs/advanced/integrations/listeners.md
  commit: 9864b4e468af6282319822029794dea65eb340c0
---

<a id="public-listener-inventory"></a>

# 公开监听器清单

每行内容均按链接中的 Hermes 标签核对。下表是**启用监听器时的默认值**，
并非 Chart 默认安装时开放的端口。网关默认主动连接消息平台，访问用 Service 和
HTTP 路由均需显式启用。StatefulSet 的无头 Service 仅提供 DNS。如果上游适配器
默认使用双栈，绑定所有接口时会同时包含 IPv4 和 IPv6。

| 监听器及标签源码 | 默认绑定地址 / 端口 | 消息或数据请求的身份验证 | Chart 配置 |
| --- | --- | --- | --- |
| [管理仪表板](https://github.com/NousResearch/hermes-agent/tree/v0.22.2/hermes_cli/dashboard_auth) | 镜像中绑定所有接口，9119 | 通过 basic/OAuth/OIDC 建立会话；非回环绑定必须配置认证提供商。应将登录权限视为等同于 Shell 访问权限。 | `dashboard.enabled`、Service 和 Ingress/HTTPRoute。不受限制的公开访问应使用 OAuth/OIDC；basic 仅用于受信任网络或 VPN。 |
| [Webapp](https://github.com/NousResearch/hermes-agent/blob/v0.23.0/gateway/webapp_listener.py) | 回环地址，9120 | 非回环绑定或使用外部来源时，必须通过仪表板的登录验证。 | `config.webapp` 和显式的 `service.ports`；参见 `values-webapp.yaml`。 |
| [OpenAI 兼容 API](https://github.com/NousResearch/hermes-agent/blob/v0.22.2/gateway/platforms/api_server.py) | 上游为回环地址，8642；Chart 启用后设置为 `0.0.0.0`。 | 即使从回环地址访问，也需要 Bearer 密钥 `API_SERVER_KEY`。 | `apiServer.enabled`、显式的 `service.ports` 和路由。 |
| [通用 Webhook](https://github.com/NousResearch/hermes-agent/blob/v0.22.2/gateway/platforms/webhook.py) | 所有接口，8644 | 全局或逐路由配置签名密钥，并根据来源验证签名。 | `webhook.enabled`；路由位于 `/webhooks/<route>`，支持带配置档案前缀的路由。显式指定 Service 端口。 |
| [A2A](https://github.com/NousResearch/hermes-agent/blob/v0.23.0/plugins/platforms/a2a/security.py) | 回环地址，9900；远程绑定需要令牌。 | 每个对等方的 `A2A_PEER_TOKENS`（具名身份）或共享 `A2A_BEARER_TOKEN`（身份为 `ip:<source-ip>`）。分派时须与 `A2A_TRUSTED_PEERS` 中的身份匹配。 | 自由配置 `config.gateway.platforms.a2a`、主机与端口环境变量及显式 Service；参见 `values-a2a.yaml`。 |
| [Telegram 原生 Webhook](https://github.com/NousResearch/hermes-agent/blob/v0.22.2/plugins/platforms/telegram/adapter.py) | 所有接口，8443；未指定 Webhook URL 时使用轮询。 | 必须设置 `TELEGRAM_WEBHOOK_SECRET`，接收端会验证传入的密钥令牌请求头。 | 环境变量或配置、显式 Service 和路由；参见 `values-telegram-webhook.yaml`。 |
| [WhatsApp Cloud](https://github.com/NousResearch/hermes-agent/blob/v0.22.2/gateway/platforms/whatsapp_cloud.py) | 所有接口，8090 | GET 验证请求使用验证令牌，POST 使用应用密钥验证 HMAC。 | 环境变量或配置、显式端口以及 `/whatsapp/webhook` 路由。 |
| [SMS / Twilio](https://github.com/NousResearch/hermes-agent/blob/v0.22.2/plugins/platforms/sms/adapter.py) | 回环地址，8080 | 使用 `TWILIO_AUTH_TOKEN` 验证 `X-Twilio-Signature`。`SMS_WEBHOOK_URL` 必须与公开 URL 一致。 | 使用 Service 时设置 `SMS_WEBHOOK_HOST=0.0.0.0`，再显式开放 `/webhooks/twilio`。 |
| [WeCom 回调](https://github.com/NousResearch/hermes-agent/blob/v0.22.2/plugins/platforms/wecom/callback_adapter.py) | 所有接口，8645 | 回调令牌、消息签名和编码用 AES 密钥。 | 环境变量或配置、显式端口以及 `/wecom/callback` 路由。与出站的 WeCom WebSocket 模式不同。 |
| [BlueBubbles 回调](https://github.com/NousResearch/hermes-agent/blob/v0.22.2/gateway/platforms/bluebubbles.py) | 回环地址，8645 | 通过受支持的查询参数或请求头提供配置的密码。 | 使用 Service 时设置 `BLUEBUBBLES_WEBHOOK_HOST=0.0.0.0`，再显式路由 `/bluebubbles-webhook`。不要在日志中输出凭据。 |
| [Microsoft Graph Webhook](https://github.com/NousResearch/hermes-agent/blob/v0.22.2/gateway/platforms/msgraph_webhook.py) | 所有接口，8646 | `client_state`；非回环绑定还必须配置 `allowed_source_cidrs`。 | 环境变量或配置、显式端口以及 `/msgraph/webhook` 路由。链接中的标签源码强制执行 CIDR 要求。 |

开放监听器之前，请确认适配器或插件可用并配置凭据。默认绑定地址和验证条件
以所链接的标签源码为准。上游环境变量参考可能落后于源码变更。此表记录的是
源码核查结果，不代表每个消息平台都已通过实际运行验证。

<a id="choose-the-ports-explicitly"></a>

## 显式选择端口

Chart 现有的通用 `service.ports` 和路由字段已经支持消息平台的原生接收端。
Chart 不为每个平台单独增加配置块。启用上游监听器不会自动创建 Kubernetes 路由。

- 非空的 `service.ports` 列表会**替换**原有的仪表板端口。请列出要开放的每个监听器，
  并将各主机和路径路由到对应端口。
- WeCom 回调与 BlueBubbles 默认均使用 8645。如果在同一 Pod 中运行两者，请同时
  修改其中一个适配器的监听端口及其 Service 和路由端口。
- 仅绑定回环地址的监听器无法接收 Service 流量。请先配置必需的身份验证，再有意扩大绑定范围。
- 启用 NetworkPolicy 后，只允许实际的 Ingress 控制器对等方访问所选端口。
  不要为了解决无关 Webhook 的问题而扩大仪表板的访问范围。
- 保留签名验证所用的 Webhook 路径和外部 HTTPS URL。不要为适配代理路径重写而关闭签名验证。

<a id="webapp-on-a-trusted-cluster"></a>

## 在受信任集群中使用 Webapp

使用 Hermes v0.23.0 并创建新 release。先创建命名空间和外部 Secret
`hermes-agent-webapp-secrets`，其中包含 `OPENAI_API_KEY`、
`HERMES_DASHBOARD_BASIC_AUTH_USERNAME`、`HERMES_DASHBOARD_BASIC_AUTH_PASSWORD`
和 `HERMES_DASHBOARD_BASIC_AUTH_SECRET`。请使用强密码和单独生成的随机会话签名密钥。

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent \
  -f charts/hermes-agent/values-webapp.yaml --wait
kubectl --namespace hermes-agent port-forward --address 127.0.0.1 \
  service/hermes-agent 9120:9120
```

打开 `http://127.0.0.1:9120` 并登录。Webapp 监听器使用内置密码认证提供商，
与端口 9119 上的管理仪表板相互独立。无法打开页面时，请查看网关日志中的监听器
或认证启动错误。Helm 的等待机制不会检查 Webapp 监听器是否就绪。

仅在受信任的网络中使用此密码认证示例。不需要共享 URL 时，请使用本地端口转发。
登录后可访问智能体的工作区和工具。对于设置了 `bootstrap.overwrite: false` 的
现有 release，请明确更新持久卷中的 `config.yaml` 并重启 Pod。
仅修改 Helm values 不会替换现有文件。

<a id="webapp-behind-an-https-ingress"></a>

### 通过 HTTPS Ingress 访问 Webapp

在受信任的网络或 VPN 中，继续使用同一个外部 Secret，并将以下 values 叠加在
`values-webapp.yaml` 之上。请替换主机名、Ingress 类、TLS Secret 名称及代理地址。
TLS Secret 必须和 release 位于同一命名空间，且证书必须覆盖 Webapp 主机名。

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

- 将浏览器访问的外部来源设置在 `config.webapp.public_url`。
  `config.dashboard.public_url` 只用于管理仪表板。
- 即使管理仪表板未启用，Hermes 也会从 `config.dashboard.trusted_proxies` 读取可信代理。
  仅列出实际连接的代理 IP，或代理专用的 CIDR。不要信任共享 Pod CIDR，否则其中的其他
  工作负载可能伪造转发的客户端 IP。在共享集群中，请使用 [NetworkPolicy](networkpolicy.md)
  将 Webapp 的 9120 端口限制为仅允许 Ingress 控制器对等方访问。
  TLS 在代理终止时，如果没有可信对等方，即使登录成功，Cookie 也不会标记为 `Secure`。
- 保留公开主机名，在 TLS 终止处设置 `X-Forwarded-Proto: https`。不要原样转发客户端
  提供的转发请求头。转发 `/api/ws` 上的 WebSocket 升级请求，不要重写其路径。
- 共享 URL 前，确认未登录的访问会被拒绝、会话 Cookie 带有 `Secure` 和 `HttpOnly`，
  并且登录后可以连接 WebSocket。不要将此密码认证示例直接暴露到公共互联网。

此路由已在 kind 中使用 Hermes v0.23.0、测试 TLS 证书和 Ingress 控制器验证。
公开 DNS、证书签发和 HTTPRoute 未包含在验证范围内。

<a id="telegram-webhook-example"></a>

## Telegram Webhook 示例

在所选命名空间中准备外部 Secret `hermes-agent-telegram-webhook-secrets`，并设置
`OPENAI_API_KEY`、`TELEGRAM_BOT_TOKEN`、`TELEGRAM_WEBHOOK_SECRET` 和
`TELEGRAM_ALLOWED_USERS`。生成足够长的随机验证密钥，只允许预期用户访问。
请勿提交真实凭据。

根据环境调整主机名、Ingress 类及 TLS Secret，或 cert-manager 的 issuer 注解，
然后安装：

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-telegram-webhook.yaml --wait
```

公开 URL 使用 HTTPS 端口 443。Ingress 将 `/telegram` 转发到 Service 的 8443
端口，再到 Pod 中的接收端。`TELEGRAM_WEBHOOK_SECRET` 保留在外部 Secret 中。
此覆盖配置不会启用仪表板或通用 Webhook 监听器。若使用轮询，请省略 Webhook URL
及这些需要显式启用的网络资源。

```yaml title="charts/hermes-agent/values-telegram-webhook.yaml"
--8<-- "charts/hermes-agent/values-telegram-webhook.yaml"
```

其他监听器也使用同样的显式端口配置，确保绑定地址、身份验证和路径与适配器匹配。
集群专用路由配置可参见[仪表板登录](dashboard.md)、[Ingress](ingress.md)、
[HTTPRoute](httproute.md) 和 [NetworkPolicy](networkpolicy.md)。
