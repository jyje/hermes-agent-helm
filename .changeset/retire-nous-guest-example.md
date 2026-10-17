---
"@jyje/hermes-agent-helm": patch
---

Documentation(providers): Retire the removed Nous guest-onboarding example

Remove the zero-key Nous gateway overlay and its provider/environment/example listings. Hermes v0.22 restricts free onboarding to desktop and removes HERMES_GUEST_ONBOARDING. Use a supported provider overlay with your own credentials, and follow the upgrade note when replacing an existing values-nous.yaml override.
