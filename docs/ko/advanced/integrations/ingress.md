---
title: Dashboard Ingress
description: 민감한 management dashboard를 인증된 Ingress 뒤에 노출하는 구성
---

| 필수 Secret | 오버레이 |
| --- | --- |
| `OPENAI_API_KEY, basic-auth Secret` | `values-ingress.yaml` |

## 언제 사용하나요?

Ingress controller와 사전에 생성한 basic-auth Secret이 필요합니다.

## 설치

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-ingress.yaml \
  --set-string env.OPENAI_API_KEY='<real-value>' --wait
```

둘 이상의 자격 증명이 필요한 예제에서는 모든 값을 `--set-string`으로 전달하거나 `extraEnvFrom`으로 기존 Secret을 참조하세요.

## 배포 전 조정

dashboard는 API key를 노출할 수 있으므로 authentication과 private network 경계를 반드시 적용합니다.

[원본 YAML 열기](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-ingress.yaml)

## 전체 오버레이

```yaml title="charts/hermes-agent/values-ingress.yaml"
--8<-- "charts/hermes-agent/values-ingress.yaml"
```