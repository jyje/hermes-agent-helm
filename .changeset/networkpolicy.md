---
"@jyje/hermes-agent-helm": minor
---

Feature(values): Add an opt-in NetworkPolicy blocking the cloud metadata endpoint

Add `networkPolicy.*` rendering a NetworkPolicy that denies all ingress by
default, allows DNS to kube-system, and blocks RFC1918 plus the cloud
metadata endpoint (169.254.0.0/16 and its IPv6 equivalent) on egress while
still permitting public internet access. Off by default; existing installs
are unaffected. Ships with a values-networkpolicy-litellm.yaml example that
allowlists an in-cluster LiteLLM Service instead of opening all of RFC1918.
