---
"@jyje/hermes-agent-helm": patch
---

Documentation(dashboard): Show how the chart exposes the dashboard instead of a screenshot gallery

Replace the six web dashboard screenshots in the chart and repository READMEs with one architecture diagram: Browser, Ingress or HTTPRoute, a Service on port 9119, and the dashboard process running next to `hermes gateway run` in one pod, both sharing the `HERMES_HOME` volume, with the required auth gate and the values that drive each piece. The introduction now states that the dashboard is upstream Hermes' own and the chart only enables and exposes it. The diagram is also added to the English and Korean dashboard guides.
