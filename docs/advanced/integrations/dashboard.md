---
title: Dashboard sign-in and Ingress
description: Expose the management dashboard through an Ingress with a password, Nous Portal OAuth, or your own OpenID Connect provider.
---

| Sign-in method | Required secret | Overlay |
| --- | --- | --- |
| Username and password | `OPENAI_API_KEY`, `HERMES_DASHBOARD_BASIC_AUTH_USERNAME`, `HERMES_DASHBOARD_BASIC_AUTH_PASSWORD` | `values-ingress.yaml` |
| Nous Portal OAuth | `OPENAI_API_KEY` (the client id is not a secret) | `values-ingress-oauth.yaml` |
| Your own OpenID Connect provider | `OPENAI_API_KEY` (the issuer and client id are not secrets) | `values-ingress-oidc.yaml` |

## When to use it

Use this when the management dashboard should be reachable at a URL. It shows API
keys to whoever is signed in, and a signed-in user can also edit the
configuration, create shell hooks (upstream documents that they run arbitrary
commands), and use the Chat tab, which is the agent itself with its tools
inside the pod. Treat sign-in as shell access to the pod, so choose the
method first. On a
non-loopback bind upstream's auth gate is mandatory: without a provider the
dashboard fails closed and never listens.

| Method | Use it for |
| --- | --- |
| Username and password | A trusted network or a VPN. Upstream does not recommend it for public internet exposure. |
| Nous Portal OAuth | A public host. Sign-in with a Nous account; a personal-account client limits sign-in to its owner. |
| Your own OpenID Connect provider | A public host with your own identity provider. The dashboard has no user allowlist: every identity the provider issues a token to for the client can sign in, so restrict the application at the provider. |

## Install

The `dashboard` values and these overlays are in chart releases after 1.16.0.
Pick one overlay.

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-ingress-oidc.yaml \
  --set-string env.OPENAI_API_KEY='sk-<real>' --wait
```

The password overlay also needs
`--set-string env.HERMES_DASHBOARD_BASIC_AUTH_PASSWORD='<strong password>'` and
`--set-string env.HERMES_DASHBOARD_BASIC_AUTH_SECRET="$(openssl rand -base64 32)"`.
`helm --wait` returns once the dashboard listens, because the chart renders a
readiness probe for it. The first start can take minutes while bundled skills sync
onto the volume.

## Adapt before deploying

- **Host and certificate.** Set `ingress.hosts[0].host`, the TLS block, and a
  cert-manager issuer annotation. `dashboard.publicUrl` is derived from the first
  host (`https` once `ingress.tls` is set); it must equal the origin registered
  with the identity provider.
- **Identity provider.** OAuth: in the Nous Portal register the dashboard and set
  **Base URL** to the external origin; the portal appends `/auth/callback`. OIDC:
  register a public PKCE client with the redirect URI `https://<host>/auth/callback`
  and put the issuer and client id under `config.dashboard.oauth.self_hosted`.
- **Trusted proxy.** List the address the dashboard sees as its peer in
  `dashboard.trustedProxies`, or the session cookies lose `Secure`. A controller on
  an overlay CNI can reach the pod from a node tunnel address inside the pod
  network, so list the pod network as well as the node network.
- **Changing it later.** `public_url` and `trusted_proxies` are seeded into
  `config.yaml` once. A later upgrade that changes them needs
  `--set bootstrap.overwrite=true` for that upgrade.
- **NetworkPolicy.** If `networkPolicy.enabled` is on, allow the controller to
  reach port 9119; see [Egress-locked NetworkPolicy](networkpolicy.md#dashboard-behind-an-ingress).

The README section
[Expose the dashboard](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/README.md#expose-the-dashboard)
has the complete steps and a symptom table.

## Check it

Without a session `GET /` redirects to the sign-in page and `/api/env` and
`/api/config` return 401. After signing in, `GET /api/auth/me` reports the provider
and the session cookies are `__Host-`, `Secure` and `HttpOnly`. A hostname under
`*.localhost` is treated as a development setup by upstream and never gets `Secure`
cookies, so do not test with one.

## Complete overlays

### Username and password

```yaml title="charts/hermes-agent/values-ingress.yaml"
--8<-- "charts/hermes-agent/values-ingress.yaml"
```

### Nous Portal OAuth

```yaml title="charts/hermes-agent/values-ingress-oauth.yaml"
--8<-- "charts/hermes-agent/values-ingress-oauth.yaml"
```

### Your own OpenID Connect provider

```yaml title="charts/hermes-agent/values-ingress-oidc.yaml"
--8<-- "charts/hermes-agent/values-ingress-oidc.yaml"
```
