# Example `values.yaml` files

Ready-to-adapt overrides for common setups, aimed at a small/home cluster
(e.g. a Raspberry Pi / arm64 k3s or MicroK8s cluster like
[`jyje/cluster`](https://github.com/jyje/cluster)). The upstream image is
multi-arch (amd64 + arm64), and the chart defaults (lightweight resources,
`ReadWriteOnce` single-writer volume, cluster-default StorageClass) already suit
arm64 nodes.

| File | Model provider | Extras |
| --- | --- | --- |
| [`values-nvidia-nim-and-discord.yaml`](values-nvidia-nim-and-discord.yaml) | NVIDIA NIM | **Discord bot** wired in |
| [`values-openai.yaml`](values-openai.yaml) | OpenAI (`openai-api`) | — |
| [`values-anthropic.yaml`](values-anthropic.yaml) | Anthropic (Claude) | — |
| [`values-gemini.yaml`](values-gemini.yaml) | Google Gemini | — |
| [`values-openrouter.yaml`](values-openrouter.yaml) | OpenRouter | — |

For a custom OpenAI-compatible proxy (LiteLLM / vLLM / LM Studio) and the
GitOps SealedSecret pattern, see
[`charts/hermes-agent/values.example.yaml`](../../charts/hermes-agent/values.example.yaml).

## All secret values are DUMMY

Every key in these files is a placeholder. **Do not commit real keys.** Provide
the real value in one of these ways:

- **At install time** (quick / interactive):

  ```bash
  helm upgrade --install hermes-agent ./charts/hermes-agent \
    --namespace hermes-agent --create-namespace \
    -f examples/values/values-nvidia-nim-and-discord.yaml \
    --set-string env.NVIDIA_API_KEY='nvapi-<real>' \
    --set-string env.DISCORD_BOT_TOKEN='<real-bot-token>' --wait
  ```

- **GitOps (recommended):** inject keys via a `SealedSecret` and point
  `extraEnvFrom` at the Secret it decrypts into — see the SealedSecret block in
  [`values.example.yaml`](../../charts/hermes-agent/values.example.yaml). Then
  the values file you commit can keep the dummy `env` values (or drop them),
  and `extraEnvFrom` overrides them at runtime.

## Notes

- Use the release name `hermes-agent` so resources are named `hermes-agent-*`
  (not `hermes-agent-hermes-agent-*`).
- `provider: openai-api` is the built-in key for `api.openai.com`. `openai` is
  **not** valid — it aliases to OpenRouter.
- Non-OpenAI examples set `env.OPENAI_API_KEY: "unused"` only to override the
  chart's default placeholder; that provider ignores it.
- Discord: only `DISCORD_BOT_TOKEN` is a secret (goes in `env` → Secret). The
  channel/allow-list knobs are non-secret and go in `extraEnv`.
