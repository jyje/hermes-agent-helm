---
"@jyje/hermes-agent-helm": minor
---

Feature(values): Dashboard NetworkPolicy example and docs page

Add `values-networkpolicy-dashboard.yaml` for exposing the dashboard through an Ingress while `networkPolicy.enabled` is on (the policy otherwise cuts the Ingress off from the dashboard), with the rules measured on a host-network controller with Calico VXLAN. Add a "Dashboard sign-in and Ingress" docs page, a dashboard section on the NetworkPolicy page, and README guidance that on an overlay CNI the pod network must be listed as a trusted proxy as well as the node network.
