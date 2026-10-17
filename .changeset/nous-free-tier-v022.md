---
"@jyje/hermes-agent-helm": patch
---

Documentation(values): The Nous free-tier example does not work on Hermes v0.22

`values-nous.yaml` and the chart README (English, Korean, Japanese, Chinese) described a boot-time anonymous Nous identity enabled by `HERMES_GUEST_ONBOARDING=1`. Hermes `v0.22.0` and later, including this chart's default image, ignore that variable and create no identity at boot, so a headless pod answers "Hermes is not logged into Nous Portal". The provider table, the environment variable note, the examples table and the example's header now say so, name the images where it still applies, and point to `hermes model` for signing in.
