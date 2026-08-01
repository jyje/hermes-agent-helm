---
title: "OpenAI"
description: "values-openai.yaml for Hermes Agent."
sidebar:
  label: "OpenAI"
  order: 160
---

<div class="raw-document-actions" data-raw-path="/hermes-agent-helm/source/charts/hermes-agent/values-openai.yaml">
  <a href="/hermes-agent-helm/source/charts/hermes-agent/values-openai.yaml">Open raw YAML</a>
  <button type="button" data-copy-source>Copy source</button>
</div>

```yaml title="charts/hermes-agent/values-openai.yaml"
# values-openai.yaml
#
# Hermes Agent using OpenAI (api.openai.com) as the model provider.
# Dummy key — override at install time.
#
#   helm upgrade --install hermes-agent ./charts/hermes-agent \
#     --namespace hermes-agent --create-namespace \
#     -f charts/hermes-agent/values-openai.yaml \
#     --set-string env.OPENAI_API_KEY='sk-<real>' --wait

config:
  model:
    # NOTE: the built-in key is `openai-api` (api.openai.com).
    # `openai` is NOT valid here — it aliases to OpenRouter.
    provider: openai-api
    default: gpt-4o-mini
  terminal:
    backend: local

env:
  OPENAI_API_KEY: "sk-DUMMY_replace_me_000000000000000000000000"

```