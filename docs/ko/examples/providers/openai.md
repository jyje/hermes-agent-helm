---
title: OpenAI
description: OpenAI API로 가장 빠르게 시작하는 기본 provider 구성
---

| 필수 Secret | 오버레이 |
| --- | --- |
| `OPENAI_API_KEY` | `values-openai.yaml` |

## 언제 사용하나요?

OpenAI 계정과 API key가 필요합니다. 처음 설치하거나 범용 기준 구성이 필요할 때 선택합니다.

## 설치

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-openai.yaml \
  --set-string env.OPENAI_API_KEY='<real-value>' --wait
```

둘 이상의 자격 증명이 필요한 예제에서는 모든 값을 `--set-string`으로 전달하거나 `extraEnvFrom`으로 기존 Secret을 참조하세요.

## 배포 전 조정

OpenAI 모델 ID와 key만 실제 값으로 바꾸면 됩니다.

[원본 YAML 열기](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-openai.yaml)

## 전체 오버레이

```yaml title="charts/hermes-agent/values-openai.yaml"
--8<-- "charts/hermes-agent/values-openai.yaml"
```