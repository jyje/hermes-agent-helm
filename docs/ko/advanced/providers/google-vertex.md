---
title: Google Vertex AI
description: GCP 서비스 계정으로 Vertex AI Gemini에 연결하는 구성
---

| 필수 Secret | 오버레이 |
| --- | --- |
| `GCP service-account Secret` | `values-google-vertex.yaml` |

## 언제 사용하나요?

GCP 프로젝트에서 Vertex AI API를 활성화하세요. 이 예제는 Vertex AI User
역할이 있는 GCP 서비스 계정의 JSON 파일을 마운트합니다.

이 예제는 글로벌 엔드포인트에서 `google/gemini-3.8-flash`를 사용합니다.
[Vertex에서 지원이 종료된 Gemini 2.5 Flash](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/model-versions)를 대체합니다.
리전이나 모델을 바꾸기 전에 [모델 및 리전 지원 범위](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/3-8-flash)를 확인하세요.
이 예제는 Gemini Developer API를 사용하지 않습니다.

## 설치

```bash
kubectl create namespace hermes-agent
kubectl create secret generic vertex-sa --namespace hermes-agent \
  --from-file=sa.json=/path/to/sa.json

helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-google-vertex.yaml \
  --set-string config.vertex.project_id='<your-gcp-project>' --wait
```

네임스페이스나 Secret이 이미 있으면 기존 리소스를 사용하세요. JSON 키는
Helm 값에 넣거나 커밋하지 마세요. 이 예제는 API 키 대신 파일을 마운트합니다.

## 배포 전 조정

기존 릴리스에서는 기본값인 `bootstrap.overwrite: false`가 PVC의
`config.yaml`을 보존합니다. Hermes에서 모델을 바꾸거나 해당 파일을 수정하세요.
오버레이만 업그레이드하면 저장된 모델은 바뀌지 않습니다.

[원본 YAML 열기](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-google-vertex.yaml)

## 전체 오버레이

```yaml title="charts/hermes-agent/values-google-vertex.yaml"
--8<-- "charts/hermes-agent/values-google-vertex.yaml"
```
