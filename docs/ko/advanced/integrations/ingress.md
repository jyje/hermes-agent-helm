---
title: Ingress 리스너 라우팅
description: 선택한 Hermes 리스너를 Ingress controller로 라우팅하는 구성
---

| 필수 Secret | 오버레이 |
| --- | --- |
| `OPENAI_API_KEY, API_SERVER_KEY, WEBHOOK_SECRET` | `values-ingress-listeners.yaml` |

## 언제 사용하나요?

클러스터에 Ingress controller가 있을 때 사용하세요. API key, listener secret,
선택한 host에 맞는 controller 설정이 필요합니다. dashboard를 라우팅한다면 민감한
API key가 노출될 수 있으므로 반드시 인증으로 보호하세요.

## 설치

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-ingress-listeners.yaml --wait
```

둘 이상의 자격 증명이 필요한 예제에서는 모든 값을 `--set-string`으로 전달하거나 `extraEnvFrom`으로 기존 Secret을 참조하세요.

## 배포 전 조정

외부 Service를 쓸 때만 `paths[].service`를 설정하세요. 생략하면 이 release의
Service가 기본값이며 path의 `port`는 `service.port`를 기본값으로 사용합니다.
`service.enabled: false`인데 암시적 chart-Service backend를 쓰면 차트가 실패합니다.

Gateway API 클러스터에서는 [HTTPRoute](httproute.md)를 사용하세요. 두 라우팅
리소스는 기본으로 꺼져 있으므로 같은 host와 path에 둘 다 켜지 말고 클러스터가
운영하는 API를 선택하세요.

[원본 YAML 열기](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-ingress-listeners.yaml)

## 전체 오버레이

```yaml title="charts/hermes-agent/values-ingress-listeners.yaml"
--8<-- "charts/hermes-agent/values-ingress-listeners.yaml"
```
