---
title: Anthropic + Discord
description: Claude provider와 Discord bot을 한 릴리스에 결합한 구성
---

| 필수 Secret | 오버레이 |
| --- | --- |
| `ANTHROPIC_API_KEY, DISCORD_BOT_TOKEN` | `values-anthropic-and-discord.yaml` |

## 언제 사용하나요?

Anthropic API key, Discord bot token, 채널 ID가 필요합니다.

## 설치

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-anthropic-and-discord.yaml \
  --set-string env.ANTHROPIC_API_KEY='<real-value>' --wait
```

둘 이상의 자격 증명이 필요한 예제에서는 모든 값을 `--set-string`으로 전달하거나 `extraEnvFrom`으로 기존 Secret을 참조하세요.

## 배포 전 조정

모델과 messenger 설정을 함께 검증할 때 사용합니다.

[원본 YAML 열기](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-anthropic-and-discord.yaml)

## 전체 오버레이

```yaml title="charts/hermes-agent/values-anthropic-and-discord.yaml"
--8<-- "charts/hermes-agent/values-anthropic-and-discord.yaml"
```