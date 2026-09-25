---
"@jyje/hermes-agent-helm": minor
---

Feature(examples): Add a Google Chat Pub/Sub example

Add `values-google-chat.yaml`, which runs Hermes as a Google Chat bot over a Cloud Pub/Sub pull subscription: outbound-only, no Service or Ingress, the Google Chat settings as plain env vars, an explicit `GOOGLE_CHAT_ALLOWED_USERS` allowlist, and the service-account JSON mounted read-only from an existing Secret. Its guide explains which IAM binding goes on the topic and which on the subscription, how the runtime user reads the key, and that native attachments need a separate per-user OAuth setup. Requires `v2026.9.14` or newer, whose image ships the Google Chat dependencies. English and Korean guides and every chart README's examples table are updated.
