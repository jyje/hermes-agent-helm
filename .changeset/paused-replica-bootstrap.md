---
"@jyje/hermes-agent-helm": minor
---

Feature(values): Allow paused GitOps bootstrap

Allow `replicaCount: 0` to prepare chart resources before scaling the single-agent workload to one replica.
