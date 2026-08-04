---
title: Fireworks AI
description: Fireworks의 OpenAI-compatible provider를 사용하는 구성
---

| 필수 Secret | 오버레이 |
| --- | --- |
| `FIREWORKS_API_KEY` | `values-fireworks.yaml` |

## 언제 사용하나요?

Fireworks API key가 필요합니다.

## 설치

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-fireworks.yaml \
  --set-string env.FIREWORKS_API_KEY='<real-value>' --wait
```

둘 이상의 자격 증명이 필요한 예제에서는 모든 값을 `--set-string`으로 전달하거나 `extraEnvFrom`으로 기존 Secret을 참조하세요.

## 배포 전 조정

지원 모델 목록을 확인한 뒤 `config.model.default`를 바꿉니다.

[원본 YAML 열기](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-fireworks.yaml)

## 전체 오버레이

```yaml title="charts/hermes-agent/values-fireworks.yaml"
--8<-- "charts/hermes-agent/values-fireworks.yaml"
```