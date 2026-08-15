---
title: HTTPRoute 리스너 라우팅
description: 선택한 Hermes 리스너를 Gateway API HTTPRoute로 라우팅하는 구성
---

| 필수 Secret | 오버레이 |
| --- | --- |
| `OPENAI_API_KEY, API_SERVER_KEY, WEBHOOK_SECRET` | `values-httproute.yaml` |

## 언제 사용하나요?

클러스터에 Gateway API CRD와 Gateway가 이미 있을 때 사용하세요.
`httpRoute.parentRefs`를 그 Gateway로 설정합니다. 이 차트는 Gateway API CRD를
설치하거나 Gateway를 만들지 않습니다.

## 설치

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-httproute.yaml --wait
```

## 배포 전 조정

비어 있는 `backendRefs[].name`은 이 release의 Service를 대상으로 하므로
`service.enabled: true`가 필요합니다. 외부 Service로 라우팅할 때는 이름을
명시하세요. 암시적 backend가 존재하지 않는 Service를 가리키면 차트가 일찍 실패합니다.

하나의 HTTPRoute에서 `hostnames`는 모든 rule에 적용됩니다. API와 webhook rule을
hostname 단위로 분리해야 하면 별도의 HTTPRoute를 만드세요.

Ingress controller로 운영하는 클러스터에서는 [Ingress](ingress.md)를 사용하세요.
두 라우팅 리소스는 기본으로 꺼져 있으므로 host와 path마다 하나를 선택하세요.

[원본 YAML 열기](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-httproute.yaml)

## 전체 오버레이

```yaml title="charts/hermes-agent/values-httproute.yaml"
--8<-- "charts/hermes-agent/values-httproute.yaml"
```
