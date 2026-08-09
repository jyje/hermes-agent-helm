---
title: OpenAI Codex
description: Discord로 전달한 device code를 이용해 ChatGPT/Codex 계정을 인증합니다.
---

| 필요한 secret | Overlay |
| --- | --- |
| `DISCORD_BOT_TOKEN` | `values-openai-codex.yaml` |

## 사용 시점

계정 기반 Codex access에는 이 provider를 사용하세요. `OPENAI_API_KEY`가 필요한
`openai-api`와는 별개입니다. 사용할 수 있는 모델은 인증한 계정의 ChatGPT plan과
live Codex catalog에 따라 달라집니다.

Hermes가 refresh 가능한 자격증명을 `HERMES_HOME/auth.json`에 저장하므로 영속
스토리지가 필요합니다.

## 설치

```bash
helm upgrade --install hermes-codex ./charts/hermes-agent \
  --namespace hermes-codex --create-namespace \
  -f charts/hermes-agent/values-openai-codex.yaml \
  --set-string env.DISCORD_BOT_TOKEN='<real-value>' --wait
```

Discord에 게시된 링크를 열고 일회용 코드를 입력해 OpenAI 로그인을 완료하세요.
이후 Pod 시작 시 init container가 Hermes에게 저장된 자격증명을 검증하거나 갱신하도록
요청하며, 계속 사용할 수 있으면 새 로그인을 건너뜁니다.

```bash
kubectl logs deploy/hermes-codex-hermes-agent -n hermes-codex \
  -c auth-device-login -f
```

[원본 YAML 열기](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-openai-codex.yaml)

## 전체 overlay

```yaml title="charts/hermes-agent/values-openai-codex.yaml"
--8<-- "charts/hermes-agent/values-openai-codex.yaml"
```
