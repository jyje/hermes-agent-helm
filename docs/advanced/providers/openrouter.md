---
title: OpenRouter
description: Select models from multiple upstream providers with one OpenRouter key.
---

| Required secret | Overlay |
| --- | --- |
| `OPENROUTER_API_KEY` | `values-openrouter.yaml` |

## When to use it

An OpenRouter API key and a target model are required.

## Install

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-openrouter.yaml \
  --set-string env.OPENROUTER_API_KEY='<real-value>' --wait
```

When an example requires more than one credential, pass every listed value with `--set-string` or use `extraEnvFrom` to reference an existing Secret.

## Sign in with OpenRouter instead of pasting a key

Since `v2026.9.14`, Hermes can obtain an OpenRouter key through OpenRouter's own sign-in: `hermes auth add openrouter --type oauth`. This is an OAuth authorization-code flow with PKCE. You approve access in a browser and paste back a one-time code. It is not a device-code flow like GitHub Copilot or OpenAI Codex, so the chart's `auth.deviceFlow` cannot run it unattended at startup. Run it once, interactively, against the running pod.

1. Install without a static key. An empty value keeps the overlay's placeholder out of Hermes' credential pool:

    ```bash
    helm upgrade --install hermes-agent ./charts/hermes-agent \
      --namespace hermes-agent --create-namespace \
      -f charts/hermes-agent/values-openrouter.yaml \
      --set-string env.OPENROUTER_API_KEY= --wait
    ```

2. Sign in from an interactive terminal. `SSH_TTY` makes Hermes use OpenRouter's paste-the-code flow; without it, Hermes waits for a browser callback on a random port inside the pod, which your browser cannot reach:

    ```bash
    kubectl exec -it -n hermes-agent deploy/hermes-agent -c hermes-agent -- \
      env SSH_TTY=/dev/pts/0 hermes auth add openrouter --type oauth --priority 0
    ```

    Open the printed URL on any machine, approve access, and paste the code at the prompt. The code is single-use and expires after about ten minutes; if OpenRouter rejects it, run the command again.

3. Confirm the credential:

    ```bash
    kubectl exec -n hermes-agent deploy/hermes-agent -c hermes-agent -- hermes auth list
    ```

What you get is an ordinary OpenRouter API key with no refresh token. Hermes stores it in `auth.json` under `HERMES_HOME`, so it survives restarts as long as `persistence` is enabled; with persistence off it is lost with the pod. Chart upgrades do not touch `auth.json`. `--priority 0` puts it first if an `OPENROUTER_API_KEY` is also set. To rotate it, revoke the key in your OpenRouter settings, sign in again, and remove the old entry with `hermes auth remove openrouter <target>`.

Prefer the static `OPENROUTER_API_KEY` Secret for anything that must be reproducible from values alone, such as GitOps.

## Adapt before deploying

Use a provider/model name from the OpenRouter catalog.

[Open Raw YAML](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-openrouter.yaml)

## Complete overlay

```yaml title="charts/hermes-agent/values-openrouter.yaml"
--8<-- "charts/hermes-agent/values-openrouter.yaml"
```