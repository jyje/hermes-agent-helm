---
title: Public listener inventory
description: Version-specific HTTP listeners, authentication, and explicit Kubernetes routing.
---

# Public listener inventory

Checked against the tagged **Hermes v0.22.2** source. These are the defaults
**when a listener is enabled**, not open ports in a default chart installation.
The default gateway uses outbound messenger connections; access Services and
HTTP routing are opt-in. A StatefulSet's headless Service provides DNS only.
An all-interface bind below includes IPv4 and IPv6 where the upstream adapter
uses its dual-stack default.

| Listener and tagged source | Default bind / port | Authentication for message/data requests | Chart wiring |
| --- | --- | --- | --- |
| [Management dashboard](https://github.com/NousResearch/hermes-agent/tree/v0.22.2/hermes_cli/dashboard_auth) | All interfaces, 9119 in the image | Session through basic/OAuth/OIDC; non-loopback requires a provider. Treat sign-in as shell access. | `dashboard.enabled`, Service and Ingress/HTTPRoute. Use OAuth/OIDC for unrestricted public exposure; basic is for a trusted network/VPN. |
| [OpenAI-compatible API](https://github.com/NousResearch/hermes-agent/blob/v0.22.2/gateway/platforms/api_server.py) | Upstream loopback, 8642; chart sets 0.0.0.0 when enabled | Bearer `API_SERVER_KEY`, required even on loopback | `apiServer.enabled` plus explicit `service.ports` and routing |
| [Generic webhook](https://github.com/NousResearch/hermes-agent/blob/v0.22.2/gateway/platforms/webhook.py) | All interfaces, 8644 | Global/per-route signing secret and source-specific signature validation | `webhook.enabled`; routes under `/webhooks/<route>`, including profile-prefixed routes. Explicit Service port. |
| [A2A](https://github.com/NousResearch/hermes-agent/blob/v0.22.2/plugins/platforms/a2a/adapter.py) | Loopback, 9900; remote bind requires configured transport auth | `A2A_BEARER_TOKEN` or per-peer `A2A_PEER_TOKENS` | Freeform `config.gateway.platforms.a2a`, host/port env, explicit Service; see `values-a2a.yaml` |
| [Telegram native webhook](https://github.com/NousResearch/hermes-agent/blob/v0.22.2/plugins/platforms/telegram/adapter.py) | All interfaces, 8443; polling is used without a webhook URL | Mandatory `TELEGRAM_WEBHOOK_SECRET`; the receiver verifies the incoming secret-token header | Env/config plus explicit Service/routing; `values-telegram-webhook.yaml` |
| [WhatsApp Cloud](https://github.com/NousResearch/hermes-agent/blob/v0.22.2/gateway/platforms/whatsapp_cloud.py) | All interfaces, 8090 | Verification token for GET challenge; app-secret HMAC for POST | Env/config; explicit port and `/whatsapp/webhook` routing |
| [SMS / Twilio](https://github.com/NousResearch/hermes-agent/blob/v0.22.2/plugins/platforms/sms/adapter.py) | Loopback, 8080 | `X-Twilio-Signature` with `TWILIO_AUTH_TOKEN`; `SMS_WEBHOOK_URL` must match the public URL | Set `SMS_WEBHOOK_HOST=0.0.0.0` for a Service, then expose `/webhooks/twilio` explicitly |
| [WeCom callback](https://github.com/NousResearch/hermes-agent/blob/v0.22.2/plugins/platforms/wecom/callback_adapter.py) | All interfaces, 8645 | Callback token, message signature and encoding AES key | Env/config; explicit port and `/wecom/callback` routing. The outbound WeCom WebSocket mode is separate. |
| [BlueBubbles callback](https://github.com/NousResearch/hermes-agent/blob/v0.22.2/gateway/platforms/bluebubbles.py) | Loopback, 8645 | Configured password via supported callback query/header fields | Set `BLUEBUBBLES_WEBHOOK_HOST=0.0.0.0` for a Service; explicitly route `/bluebubbles-webhook`. Keep credentials out of logs. |
| [Microsoft Graph webhook](https://github.com/NousResearch/hermes-agent/blob/v0.22.2/gateway/platforms/msgraph_webhook.py) | All interfaces, 8646 | `client_state`; non-loopback additionally requires `allowed_source_cidrs` | Env/config; explicit port and `/msgraph/webhook` routing. Tagged source enforces the CIDR requirement. |

Adapter/plugin availability and credentials must be configured before exposing
the listener. Bind defaults and validation come from the tagged source links;
the moving upstream environment reference can lag source changes. This table
records source inspection, not live verification of every messenger.

## Choose the ports explicitly

The chart's generic `service.ports` and routing fields already support native
messenger receivers. This chart does not add a separate value block for every
platform. Enabling an upstream listener does not create Kubernetes routing.

- A nonempty `service.ports` list **replaces** the legacy dashboard port. Include
  every listener you intend to expose and route each host/path to its own port.
- WeCom callback and BlueBubbles both default to 8645. If both run in one Pod,
  change one adapter's listener port **and** its Service/routing port.
- A loopback-only listener cannot receive Service traffic. Widen its bind
  deliberately and configure its required authentication first.
- With NetworkPolicy enabled, allow the selected port from the actual ingress
  controller peers. Never broaden dashboard access to fix an unrelated webhook.
- Preserve provider webhook paths and the external HTTPS URL used by signature
  validation. Do not turn off signatures to accommodate a proxy rewrite.

## Telegram webhook example

Prepare an external Secret named `hermes-agent-telegram-webhook-secrets` with
`OPENAI_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_WEBHOOK_SECRET` and
`TELEGRAM_ALLOWED_USERS` in the chosen namespace. Generate a long random
verification secret and allow only intended users. Do not commit the credentials.

Adapt the hostname, Ingress class and TLS Secret (or cert-manager issuer
annotation), then install:

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-telegram-webhook.yaml --wait
```

The public URL uses HTTPS port 443; the Ingress forwards `/telegram` to Service
port 8443 and the Pod's receiver. `TELEGRAM_WEBHOOK_SECRET` remains in the external
Secret; no dashboard or generic webhook listener is enabled by this overlay.
For polling, omit the webhook URL and these opt-in networking resources.

```yaml title="charts/hermes-agent/values-telegram-webhook.yaml"
--8<-- "charts/hermes-agent/values-telegram-webhook.yaml"
```

For other listeners, use the same explicit-port pattern with the matching
adapter bind, authentication and path. See [dashboard sign-in](dashboard.md),
[Ingress](ingress.md), [HTTPRoute](httproute.md) and
[NetworkPolicy](networkpolicy.md) for cluster-specific routing.
