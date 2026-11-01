---
"@jyje/hermes-agent-helm": minor
---

Feature(values): NetworkPolicy and test Job annotations

Set `networkPolicy.annotations` to add annotations to the NetworkPolicy, and `tests.annotations` to add annotations to the Helm test Job. The Job's own Helm and Argo CD hook annotations are always set, and a key in `tests.annotations` that repeats one of them is ignored. Both default to `{}` and take string values, so existing installs render the same objects.
