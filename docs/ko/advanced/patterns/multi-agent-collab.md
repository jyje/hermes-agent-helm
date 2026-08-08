---
title: Collaborating pair
description: 같은 Discord channel에서 @mention으로 협업하는 planner 구성
---

| 필수 Secret | 오버레이 |
| --- | --- |
| `NVIDIA_API_KEY, DISCORD_BOT_TOKEN` | `values-multi-agent-collab.yaml` |

## 언제 사용하나요?

두 bot identity, 공통 channel, 서로의 Discord user ID가 필요합니다.

## 설치

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-multi-agent-collab.yaml \
  --set-string env.NVIDIA_API_KEY='<real-value>' --wait
```

둘 이상의 자격 증명이 필요한 예제에서는 모든 값을 `--set-string`으로 전달하거나 `extraEnvFrom`으로 기존 Secret을 참조하세요.

## 배포 전 조정

이 파일은 planner 절반입니다. builder용 별도 release와 loop-brake 설정을 함께 배포합니다.

[원본 YAML 열기](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-multi-agent-collab.yaml)

## 전체 오버레이

```yaml title="charts/hermes-agent/values-multi-agent-collab.yaml"
--8<-- "charts/hermes-agent/values-multi-agent-collab.yaml"
```