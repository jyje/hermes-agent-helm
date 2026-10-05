---
"@jyje/hermes-agent-helm": patch
---

Documentation(values): OpenAI Codex context window, login expiry, and shared accounts

Explain in `values-openai-codex.yaml` how to opt in to Hermes' `-900k` model variant (for example `gpt-6-luna-900k`) and why `compression.threshold_tokens` must be raised with it. The comments say the suffix is a Hermes alias, not an OpenAI model name, that it uses subscription quota faster, and that upstream is still refining it. The Codex docs page (English and Korean) also explains that a login code expires after about 15 minutes and is replaced automatically, and what to know when several releases log in to the same ChatGPT account.
