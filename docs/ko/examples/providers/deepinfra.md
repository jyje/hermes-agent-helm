---
title: DeepInfra
description: DeepInfra OpenAI-compatible endpoint에 연결하는 구성
---

<div class="example-meta">
  <div><strong>필수 Secret</strong>DEEPINFRA_API_KEY</div>
  <div><strong>오버레이</strong>values-deepinfra.yaml</div>
</div>

## 언제 사용하나요?

DeepInfra API key와 해당 endpoint에서 제공하는 모델 ID가 필요합니다.

## 설치

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-deepinfra.yaml \
  --set-string env.DEEPINFRA_API_KEY='<real-value>' --wait
```

둘 이상의 자격 증명이 필요한 예제에서는 모든 값을 `--set-string`으로 전달하거나 `extraEnvFrom`으로 기존 Secret을 참조하세요.

## 배포 전 조정

모델은 DeepInfra `/v1/openai/models` 목록에서 선택합니다.

[원본 YAML 열기](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-deepinfra.yaml)

## 전체 오버레이

```yaml title="charts/hermes-agent/values-deepinfra.yaml"
--8<-- "charts/hermes-agent/values-deepinfra.yaml"
```