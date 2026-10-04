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

## Dashboard behind an Ingress

Turning the policy on silently cuts an Ingress off from the dashboard: the pod
stays Ready (the kubelet probe is not affected) but the controller cannot reach
it. Add a rule for port 9119 to `networkPolicy.extraIngress`. What to allow depends
on how the controller reaches the pod. Measured on MicroK8s with Calico (VXLAN) and
a host-network ingress-nginx with one controller per node, the dashboard pod on one
of them:

| Rule | Controller on the same node | Controller on another node |
| --- | --- | --- |
| None | Allowed | Blocked |
| Pod and namespace selector of the ingress | Allowed | Blocked |
| `ipBlock` of the node network only | Allowed | Blocked |
| `ipBlock` of the node network and the pod network | Allowed | Allowed |

A host-network controller is not a pod as far as the policy is concerned, so a
selector never matches it, and Calico always admitted traffic from the pod's own node
in this test. Traffic from another node reaches the dashboard from that node's tunnel
address, which lies inside the pod network. Allow both networks and set the same two
CIDRs in `dashboard.trustedProxies`; otherwise sign-in works but the session cookies
lose `Secure` depending on which node the request enters. A controller that runs as
an ordinary pod can be matched with a namespace and pod selector instead, which is
narrower; that variant was not measured. Use bounded CIDRs rather than a pod IP,
which changes when the controller pod is recreated.

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-networkpolicy-dashboard.yaml --wait
```

```yaml title="charts/hermes-agent/values-networkpolicy-dashboard.yaml"
--8<-- "charts/hermes-agent/values-networkpolicy-dashboard.yaml"
```
