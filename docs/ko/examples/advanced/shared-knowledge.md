---
title: Shared knowledge PVC
description: 여러 agent가 RWX PVC를 공용 지식 저장소로 mount하는 구성
---

<div class="example-meta">
  <div><strong>필수 Secret</strong>Provider key</div>
  <div><strong>오버레이</strong>values-shared-knowledge.yaml</div>
</div>

## 언제 사용하나요?

미리 생성한 RWX PVC와 uid/gid 10000이 쓸 수 있는 권한이 필요합니다.

## 설치

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-shared-knowledge.yaml \
  --set-string env.Provider_key='<real-value>' --wait
```

둘 이상의 자격 증명이 필요한 예제에서는 모든 값을 `--set-string`으로 전달하거나 `extraEnvFrom`으로 기존 Secret을 참조하세요.

## 배포 전 조정

각 agent의 HERMES_HOME은 private PVC로 유지하면서 knowledge claim만 공유합니다.

[원본 YAML 열기](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-shared-knowledge.yaml)

## 전체 오버레이

```yaml title="charts/hermes-agent/values-shared-knowledge.yaml"
--8<-- "charts/hermes-agent/values-shared-knowledge.yaml"
```