---
"@jyje/hermes-agent-helm": patch
---

Documentation(docs): say how the Vertex example is checked

Add a Verification section to the Google Vertex AI guide and a line to the README's end-to-end bullet. CI now checks the Vertex example offline against a local mock, so a change to the overlay or the Hermes image that breaks the request route or model is caught before it ships. The check does not cover IAM or live inference.
