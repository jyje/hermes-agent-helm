---
"@jyje/hermes-agent-helm": patch
---

Fix(chart): give the Helm test Job 1Gi of memory

Raise the test Job's default memory limit from 512Mi to 1Gi. `hermes doctor` was killed with `OOMKilled` at the old limit, so `helm test` failed on a fresh install.
