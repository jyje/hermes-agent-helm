---
title: Egress-locked NetworkPolicy
description: Isolate the agent's Pod and block the cloud metadata endpoint.
---

| Required secret | Overlay |
| --- | --- |
| `OPENAI_API_KEY` | `values-networkpolicy-litellm.yaml` |

## When to use it

The agent runs its own shell/code execution inside its own Pod - the Pod
itself is the sandbox. Without a NetworkPolicy that sandbox has no network
boundary: lateral movement to other in-cluster Services, and reachability of
the cloud metadata endpoint (`169.254.169.254` / the IPv6 equivalent within
`fd00::/8`), which on most managed clusters hands out node IAM credentials.
Use this whenever the cluster's CNI enforces `NetworkPolicy` (most managed
Kubernetes offerings do; some local dev CNIs, notably kind's default, do not).

## Install

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-networkpolicy-litellm.yaml \
  --set-string env.OPENAI_API_KEY='sk-<your-litellm-proxy-key>' --wait
```

## Adapt before deploying

`networkPolicy.enabled: false` by default - existing installs are unaffected
until you opt in. Once enabled:

- **Ingress is denied entirely by default.** `hermes gateway run` is
  outbound-only, so nothing needs to reach this Pod unless a listener
  (dashboard, `apiServer`, `webhook`, `a2a`, ...) is exposed - add the
  matching rule to `extraIngress` in that case.
- **DNS is scoped to `kube-system`** via an immutable namespace-name label.
  Override `networkPolicy.dns.namespaceSelector`/`podSelector` for a
  distribution whose DNS runs elsewhere.
- **`blockPrivateEgress: true`** blocks RFC1918 and the metadata endpoint
  while still permitting public internet egress. Set it `false` only if the
  agent must reach an in-cluster proxy through a *broad* allowance; prefer
  `extraEgress` with a precise `namespaceSelector`/`podSelector` instead, as
  this example does for LiteLLM.
- `policyTypes` is fixed at `[Ingress, Egress]` and is not configurable - the
  chart's policy always isolates both directions.

[Open Raw YAML](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-networkpolicy-litellm.yaml)

## Complete overlay

```yaml title="charts/hermes-agent/values-networkpolicy-litellm.yaml"
--8<-- "charts/hermes-agent/values-networkpolicy-litellm.yaml"
```
