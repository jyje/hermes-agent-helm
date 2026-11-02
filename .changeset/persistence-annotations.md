---
"@jyje/hermes-agent-helm": minor
---

Feature(values): PVC annotations

Set `persistence.annotations` to add annotations to the PersistentVolumeClaim, or to the StatefulSet's volumeClaimTemplate, for example backup tool hints or `helm.sh/resource-policy: keep`. Set `team.sharedVolume.annotations` to do the same for the shared team volume; its `helm.sh/resource-policy: keep` annotation from `retain: true` is always kept. Both default to `{}`, so existing installs render the same objects. Kubernetes does not allow changing a StatefulSet's volumeClaimTemplates, so set the annotations at install time.
