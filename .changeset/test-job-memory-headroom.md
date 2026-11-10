---
"@jyje/hermes-agent-helm": patch
---

Fix(chart): Give the Helm test Job more memory headroom

Raise the test Job's default memory limit from 1Gi to 1536Mi. On the current Hermes image `hermes doctor` peaked between about 640 and 780 MiB, which left less than 1.5 times headroom under 1Gi. The request stays at 128Mi.
