---
title: OpenRouter
description: 하나의 OpenRouter key로 다양한 upstream 모델을 선택하는 구성
---

| 필수 Secret | 오버레이 |
| --- | --- |
| `OPENROUTER_API_KEY` | `values-openrouter.yaml` |

## 언제 사용하나요?

OpenRouter API key와 선택할 모델 ID가 필요합니다.

## 설치

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-openrouter.yaml \
  --set-string env.OPENROUTER_API_KEY='<real-value>' --wait
```

둘 이상의 자격 증명이 필요한 예제에서는 모든 값을 `--set-string`으로 전달하거나 `extraEnvFrom`으로 기존 Secret을 참조하세요.

## 배포 전 조정

모델 이름은 OpenRouter 카탈로그에 있는 provider/model 형식으로 지정합니다.

[원본 YAML 열기](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-openrouter.yaml)

## 전체 오버레이

```yaml title="charts/hermes-agent/values-openrouter.yaml"
--8<-- "charts/hermes-agent/values-openrouter.yaml"
```