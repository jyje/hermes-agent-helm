---
"@jyje/hermes-agent-helm": minor
---

Feature(tests): Isolate optional Helm test diagnostics

Enable `tests.isolateDoctor` on Kubernetes 1.33 or later to keep a diagnostic container failure from ending the required Helm test checks.
