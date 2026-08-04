---
title: Mixture of Agents
description: 여러 reference model과 aggregator model을 결합하는 구성
---

<div class="example-meta">
  <div><strong>필수 Secret</strong>OPENROUTER_API_KEY</div>
  <div><strong>오버레이</strong>values-moa.yaml</div>
</div>

## 언제 사용하나요?

Hermes image v2026.7.1 이상과 각 preset provider의 key가 필요합니다.

## 설치

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-moa.yaml \
  --set-string env.OPENROUTER_API_KEY='<real-value>' --wait
```

둘 이상의 자격 증명이 필요한 예제에서는 모든 값을 `--set-string`으로 전달하거나 `extraEnvFrom`으로 기존 Secret을 참조하세요.

## 배포 전 조정

preset의 reference·aggregator model을 워크로드에 맞게 교체합니다.

[원본 YAML 열기](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-moa.yaml)

## 전체 오버레이

```yaml title="charts/hermes-agent/values-moa.yaml"
--8<-- "charts/hermes-agent/values-moa.yaml"
```