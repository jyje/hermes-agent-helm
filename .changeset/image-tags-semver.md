---
"@jyje/hermes-agent-helm": patch
---

Documentation(image): Describe upstream's switch to semver image tags

Explain that upstream Hermes Agent images use semver tags (for example `v0.22.2`) since October 2026, while images up to `v2026.9.24` keep their date-based tags. Set `image.tag` to either form; the default still follows `appVersion`.
