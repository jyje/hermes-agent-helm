---
"@jyje/hermes-agent-helm": patch
---

Fix(values): Validate annotation and label values as strings

The values schema now requires string values in `serviceAccount.annotations`, `service.annotations`, `ingress.annotations`, `httpRoute.annotations`, `podAnnotations`, `deploymentAnnotations` and `podLabels`. A number or boolean there, for example from `--set key=true`, is now rejected by `helm` with the offending path, instead of rendering and failing later when Kubernetes applies the object. Use `--set-string` or quote the value in a values file.
