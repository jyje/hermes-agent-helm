---
title: Google Vertex AI
description: GCP 서비스 계정으로 Vertex AI Gemini에 연결하는 구성
---

<div class="example-meta">
  <div><strong>필수 Secret</strong>GCP service-account Secret</div>
  <div><strong>오버레이</strong>values-google-vertex.yaml</div>
</div>

## 언제 사용하나요?

Vertex AI User 권한의 GCP 서비스 계정 JSON Secret과 project ID가 필요합니다.

## 설치

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-google-vertex.yaml \
  --set-string env.GCP_service-account_Secret='<real-value>' --wait
```

둘 이상의 자격 증명이 필요한 예제에서는 모든 값을 `--set-string`으로 전달하거나 `extraEnvFrom`으로 기존 Secret을 참조하세요.

## 배포 전 조정

정적 API key 대신 credential 파일을 mount하므로 Secret 생성 단계를 먼저 수행합니다.

[원본 YAML 열기](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-google-vertex.yaml)

## 전체 오버레이

```yaml title="charts/hermes-agent/values-google-vertex.yaml"
--8<-- "charts/hermes-agent/values-google-vertex.yaml"
```