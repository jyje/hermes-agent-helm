---
title: "Fireworks AI"
description: "values-fireworks.yaml for Hermes Agent."
sidebar:
  label: "Fireworks AI"
  order: 50
---

<div class="raw-document-actions" data-raw-path="/hermes-agent-helm/source/charts/hermes-agent/values-fireworks.yaml">
  <a href="/hermes-agent-helm/source/charts/hermes-agent/values-fireworks.yaml">Open raw YAML</a>
  <button type="button" data-copy-source>Copy source</button>
</div>

```yaml title="charts/hermes-agent/values-fireworks.yaml"
# values-fireworks.yaml
#
# Hermes Agent using Fireworks AI's built-in OpenAI-compatible provider.
# Dummy key — override at install time.
#
#   helm upgrade --install hermes-agent ./charts/hermes-agent \
#     --namespace hermes-agent --create-namespace \
#     -f charts/hermes-agent/values-fireworks.yaml \
#     --set-string env.FIREWORKS_API_KEY='fw-<real>' --wait

config:
  model:
    provider: fireworks
    # Fireworks model IDs use its native accounts/fireworks/models/... form.
    default: accounts/fireworks/models/glm-5p2
  terminal:
    backend: local

env:
  FIREWORKS_API_KEY: "fw-DUMMY_replace_me_000000000000000000000000"
  # Unused by the fireworks provider; overrides the chart's OpenAI placeholder.
  OPENAI_API_KEY: "unused"

```