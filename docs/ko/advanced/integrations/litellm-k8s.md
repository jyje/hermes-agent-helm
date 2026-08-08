---
title: LiteLLM (in cluster)
description: 같은 Kubernetes 클러스터 안의 LiteLLM Service DNS를 사용하는 구성
---

| 필수 Secret | 오버레이 |
| --- | --- |
| `OPENAI_API_KEY` | `values-litellm-k8s.yaml` |

## 언제 사용하나요?

LiteLLM Service 이름·namespace·port와 proxy key가 필요합니다.

## 설치

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-litellm-k8s.yaml \
  --set-string env.OPENAI_API_KEY='<real-value>' --wait
```

둘 이상의 자격 증명이 필요한 예제에서는 모든 값을 `--set-string`으로 전달하거나 `extraEnvFrom`으로 기존 Secret을 참조하세요.

## 배포 전 조정

base URL을 Service FQDN으로 맞추면 Ingress와 TLS 없이 통신합니다.

[원본 YAML 열기](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-litellm-k8s.yaml)

## 전체 오버레이

```yaml title="charts/hermes-agent/values-litellm-k8s.yaml"
--8<-- "charts/hermes-agent/values-litellm-k8s.yaml"
```