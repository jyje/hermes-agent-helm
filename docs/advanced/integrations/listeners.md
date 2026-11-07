---
title: Public listener inventory
description: Version-specific HTTP listeners, authentication, and explicit Kubernetes routing.
---

# Public listener inventory

Checked against the Hermes tag linked in each row. These are the defaults
**when a listener is enabled**, not open ports in a default chart installation.
The default gateway uses outbound messenger connections; access Services and
HTTP routing are opt-in. A StatefulSet's headless Service provides DNS only.
An all-interface bind below includes IPv4 and IPv6 where the upstream adapter
uses its dual-stack default.

| Listener and tagged source | Default bind / port | Authentication for message/data requests | Chart wiring |
| --- | --- | --- | --- |
| [Management dashboard](https://github.com/NousResearch/hermes-agent/tree/v0.22.2/hermes_cli/dashboard_auth) | All interfaces, 9119 in the image | Session through basic/OAuth/OIDC; non-loopback requires a provider. Treat sign-in as shell access. | `dashboard.enabled`, Service and Ingress/HTTPRoute. Use OAuth/OIDC for unrestricted public exposure; basic is for a trusted network/VPN. |
| [Webapp](https://github.com/NousResearch/hermes-agent/blob/v0.23.0/gateway/webapp_listener.py) | Loopback, 9120 | Dashboard sign-in gate for a non-loopback bind or external origin | `config.webapp` and explicit `service.ports`; see `values-webapp.yaml` |
| [OpenAI-compatible API](https://github.com/NousResearch/hermes-agent/blob/v0.22.2/gateway/platforms/api_server.py) | Upstream loopback, 8642; chart sets 0.0.0.0 when enabled | Bearer `API_SERVER_KEY`, required even on loopback | `apiServer.enabled` plus explicit `service.ports` and routing |
| [Generic webhook](https://github.com/NousResearch/hermes-agent/blob/v0.22.2/gateway/platforms/webhook.py) | All interfaces, 8644 | Global/per-route signing secret and source-specific signature validation | `webhook.enabled`; routes under `/webhooks/<route>`, including profile-prefixed routes. Explicit Service port. |
| [A2A](https://github.com/NousResearch/hermes-agent/blob/v0.23.0/plugins/platforms/a2a/security.py) | Loopback, 9900; remote bind requires a token | Per-peer `A2A_PEER_TOKENS` (named identity) or shared `A2A_BEARER_TOKEN` (`ip:<source-ip>` identity). Match that identity in `A2A_TRUSTED_PEERS` for dispatch. | Freeform `config.gateway.platforms.a2a`, host/port env, explicit Service; see `values-a2a.yaml` |
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

## Webapp on a trusted cluster

Use Hermes v0.23.0 and a fresh release. Create the namespace and an external
Secret named `hermes-agent-webapp-secrets` with `OPENAI_API_KEY`,
`HERMES_DASHBOARD_BASIC_AUTH_USERNAME`, `HERMES_DASHBOARD_BASIC_AUTH_PASSWORD`
and `HERMES_DASHBOARD_BASIC_AUTH_SECRET`. Use a strong password and a separate
random session signing secret.

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent \
  -f charts/hermes-agent/values-webapp.yaml --wait
kubectl --namespace hermes-agent port-forward --address 127.0.0.1 \
  service/hermes-agent 9120:9120
```

Open `http://127.0.0.1:9120` and sign in. The Webapp listener uses the bundled
password provider and is separate from the management dashboard on port 9119.
If the page is unreachable, inspect the gateway logs for listener or sign-in
startup errors: Helm's wait does not check the Webapp listener.

Keep this password example on a trusted network. Use local port forwarding
when you do not need a shared URL. Signing in gives access to the agent's
workspace and tools.
For an existing release with `bootstrap.overwrite: false`, update its
persisted `config.yaml` deliberately and restart the Pod; a new Helm value
does not replace the existing file.

### Webapp behind an HTTPS Ingress

For a trusted network or VPN, keep the same external Secret and layer the
following values over `values-webapp.yaml`. Replace the hostname, Ingress
class, TLS Secret name, and proxy address. The TLS Secret must be in the
release namespace and cover the Webapp hostname.

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

- Set the browser-facing origin in `config.webapp.public_url`, not
  `config.dashboard.public_url`. The latter is for the management dashboard.
- Hermes reads trusted proxy peers from `config.dashboard.trusted_proxies`
  even with the management dashboard disabled. List the actual proxy IPs or
  a CIDR dedicated to those proxies. Do not trust a shared Pod CIDR: other
  workloads in it could spoof forwarded client IPs. In a shared cluster,
  use [NetworkPolicy](networkpolicy.md) to allow traffic to Webapp port 9120
  only from the Ingress controller peers. Without a trusted peer, login can
  succeed but the cookies are not marked `Secure` when TLS terminates at
  the proxy.
- Preserve the public host and set `X-Forwarded-Proto: https` at TLS
  termination. Do not pass client-supplied forwarding headers through
  unchanged. Forward WebSocket upgrades on `/api/ws` without rewriting
  the path.
- Before sharing the URL, check that signed-out access is denied, the signed-in
  session cookie is `Secure` and `HttpOnly`, and the WebSocket connects after
  sign-in. Keep this password example off the public internet.

This route was checked in kind with Hermes v0.23.0, a test TLS certificate, and
an Ingress controller. Public DNS, certificate issuance, and HTTPRoute were
not part of that check.

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
