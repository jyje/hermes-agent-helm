---
"@jyje/hermes-agent-helm": patch
---

Documentation(docs): Replace em-dashes with colons or plain dashes

Convert every em-dash in the chart README, the values examples, the JSON
schema description, and the Helm and ArgoCD example manifests to a colon
or a plain dash, so the documentation stays easy to type, grep, and read
in a terminal. Wording and every configuration key are unchanged.
