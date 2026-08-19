---
title: Egress 제한 NetworkPolicy
description: 에이전트 Pod를 격리하고 클라우드 metadata endpoint를 차단
---

| 필수 Secret | 오버레이 |
| --- | --- |
| `OPENAI_API_KEY` | `values-networkpolicy-litellm.yaml` |

## 언제 사용하나요?

에이전트는 자기 자신의 Pod 안에서 shell/코드 실행을 수행합니다 — Pod 자체가
샌드박스입니다. NetworkPolicy가 없으면 이 샌드박스에는 네트워크 경계가
없습니다: 다른 in-cluster Service로의 lateral movement, 그리고 대부분의
managed 클러스터에서 노드 IAM credential을 내주는 클라우드 metadata
endpoint(`169.254.169.254` / IPv6 등가인 `fd00::/8` 대역)로의 접근이 모두
가능합니다. 클러스터의 CNI가 `NetworkPolicy`를 실제로 강제하는 경우 사용하세요
(대부분의 managed Kubernetes는 지원하지만, kind 기본 CNI 등 일부 로컬 개발용
CNI는 지원하지 않습니다).

## 설치

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-networkpolicy-litellm.yaml \
  --set-string env.OPENAI_API_KEY='sk-<your-litellm-proxy-key>' --wait
```

## 배포 전 조정

기본값은 `networkPolicy.enabled: false`라 opt-in 하기 전까지 기존 설치에는
영향이 없습니다. 활성화하면:

- **Ingress는 기본적으로 전부 차단됩니다.** `hermes gateway run`은
  outbound-only이므로 listener(dashboard, `apiServer`, `webhook`, `a2a` 등)를
  노출하지 않는 한 이 Pod로 들어올 트래픽이 필요 없습니다 — 노출한다면
  `extraIngress`에 해당 규칙을 추가하세요.
- **DNS는 불변 namespace-name 라벨로 `kube-system`에 한정됩니다.** DNS가 다른
  곳에서 도는 배포판이라면 `networkPolicy.dns.namespaceSelector`/`podSelector`를
  오버라이드하세요.
- **`blockPrivateEgress: true`**는 RFC1918과 metadata endpoint를 차단하면서
  공인 인터넷 egress는 그대로 허용합니다. in-cluster 프록시에 접근해야 할 때도
  이 값을 `false`로 넓히기보다는, 이 예제처럼 정확한
  `namespaceSelector`/`podSelector`로 `extraEgress`를 쓰는 편을 우선하세요.
- `policyTypes`는 `[Ingress, Egress]`로 고정되어 있고 설정할 수 없습니다 — 이
  차트의 정책은 항상 양방향을 격리합니다.

[원본 YAML 열기](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-networkpolicy-litellm.yaml)

## 전체 오버레이

```yaml title="charts/hermes-agent/values-networkpolicy-litellm.yaml"
--8<-- "charts/hermes-agent/values-networkpolicy-litellm.yaml"
```
