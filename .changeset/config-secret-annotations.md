---
"@jyje/hermes-agent-helm": minor
---

Feature(values): ConfigMap, Secret and ExternalSecret annotations

Set `configMapAnnotations` to add annotations to every ConfigMap the chart renders (config, device login script, team skill), `secretAnnotations` for the env Secret, and `externalSecret.annotations` for the ExternalSecret, for example Argo CD sync waves so these objects exist before the workload. All three default to `{}` and take string values, so existing installs render the same objects. With `externalSecret.enabled` the Secret is created by the External Secrets Operator, so use `externalSecret.annotations` there.
