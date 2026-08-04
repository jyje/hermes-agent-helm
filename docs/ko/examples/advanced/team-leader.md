---
title: Team leader
description: Discord thread 기반 leader-orchestrated team의 leader 구성
---

| 필수 Secret | 오버레이 |
| --- | --- |
| `NVIDIA_API_KEY, DISCORD_BOT_TOKEN` | `values-team-leader.yaml` |

## 언제 사용하나요?

RWX knowledge claim, leader bot, member bot IDs가 필요합니다.

## 설치

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-team-leader.yaml \
  --set-string env.NVIDIA_API_KEY='<real-value>' --wait
```

둘 이상의 자격 증명이 필요한 예제에서는 모든 값을 `--set-string`으로 전달하거나 `extraEnvFrom`으로 기존 Secret을 참조하세요.

## 배포 전 조정

leader는 shared knowledge를 read-write로 mount하고 member에게 명시적으로 작업을 handoff합니다.

[원본 YAML 열기](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-team-leader.yaml)

## 전체 오버레이

```yaml title="charts/hermes-agent/values-team-leader.yaml"
--8<-- "charts/hermes-agent/values-team-leader.yaml"
```