---
"@jyje/hermes-agent-helm": patch
---

Documentation(values): Larger context window for OpenAI Codex

Explain in `values-openai-codex.yaml` how to opt in to Hermes' `-900k` model variant (for example `gpt-6-luna-900k`) and why `compression.threshold_tokens` must be raised with it. The comments say the suffix is a Hermes alias, not an OpenAI model name, that it uses subscription quota faster, and that upstream is still refining it.
