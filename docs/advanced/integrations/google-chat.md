---
title: Google Chat
description: Run Hermes as a Google Chat bot over a Cloud Pub/Sub pull subscription.
---

| Required secret | Overlay |
| --- | --- |
| Model provider key (`OPENAI_API_KEY` in the example) and a service-account JSON Secret | `values-google-chat.yaml` |

## When to use it

Use it when your team talks to Hermes in Google Chat. Events arrive over a Cloud Pub/Sub **pull** subscription, so the pod only makes outbound connections to Google APIs. It needs no inbound Service, Ingress or public endpoint, and the example keeps every listener disabled.

Requires `v2026.9.14` or newer. From that release the official image ships the Google Chat dependencies, so a fresh pod does not install anything on first boot.

## Prerequisites in Google Cloud

Follow the upstream [Google Chat setup guide](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/google_chat) for the Workspace side. The IAM bindings are the part people most often get wrong, and they go on two different resources:

- On the **topic**: `chat-api-push@system.gserviceaccount.com` needs `Pub/Sub Publisher`. Without it Google Chat can never deliver an event.
- On the **subscription**: your own service account needs `Pub/Sub Subscriber` and `Pub/Sub Viewer`. Hermes checks the subscription at startup.

Do not grant project-level Pub/Sub roles. The Chat app itself is configured with **Cloud Pub/Sub** as its connection setting and pointed at the topic.

## Install

Put the service-account JSON into a Secret first. The overlay mounts it read-only and points `GOOGLE_CHAT_SERVICE_ACCOUNT_JSON` at the file:

```bash
kubectl create secret generic google-chat-sa \
  --namespace hermes-agent \
  --from-file=sa.json=/path/to/key.json

helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-google-chat.yaml \
  --set-string env.OPENAI_API_KEY='<real-value>' --wait
```

The Secret volume's default mode (`0644`) lets the Hermes runtime user (uid `10000`) read the key. If you tighten `defaultMode` to `0440`, also set `podSecurityContext.fsGroup: 10000`.

## Adapt before deploying

Replace the project ID, the full subscription name and the allowlisted emails in `extraEnv`. Keep `GOOGLE_CHAT_ALLOWED_USERS` narrow: whoever is on it can make the agent run commands inside the pod. `GOOGLE_CHAT_HOME_CHANNEL` is optional and only sets where cron output goes.

Plain text messaging works with this overlay alone. Native file attachments need a separate per-user OAuth setup (`/setup-files` in chat, Step 10 of the upstream guide) that this example does not configure.

## What was checked

The overlay is rendered in CI with every other `values-*.yaml`. Against the pinned image, the Google Chat adapter was confirmed to start and read the service-account file from the mounted path. A real Google Workspace message round trip needs a Workspace tenant and was not part of that check.

[Open Raw YAML](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-google-chat.yaml)

## Complete overlay

```yaml title="charts/hermes-agent/values-google-chat.yaml"
--8<-- "charts/hermes-agent/values-google-chat.yaml"
```
