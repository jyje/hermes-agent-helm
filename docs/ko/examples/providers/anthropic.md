---
title: Anthropic
description: Claude를 Hermes Agent의 기본 모델로 사용하는 구성
---

<div class="example-meta">
  <div><strong>필수 Secret</strong>ANTHROPIC_API_KEY</div>
  <div><strong>오버레이</strong>values-anthropic.yaml</div>
</div>

## 언제 사용하나요?

Anthropic API key와 사용 가능한 Claude 모델이 필요합니다.

## 설치

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-anthropic.yaml \
  --set-string env.ANTHROPIC_API_KEY='<real-value>' --wait
```

둘 이상의 자격 증명이 필요한 예제에서는 모든 값을 `--set-string`으로 전달하거나 `extraEnvFrom`으로 기존 Secret을 참조하세요.

## 배포 전 조정

provider를 `anthropic`으로 두고 Anthropic key를 Secret으로 주입합니다.

[원본 YAML 열기](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-anthropic.yaml)

## 전체 오버레이

```yaml title="charts/hermes-agent/values-anthropic.yaml"
--8<-- "charts/hermes-agent/values-anthropic.yaml"
```