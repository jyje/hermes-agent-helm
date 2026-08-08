---
title: Hermes Agent 설치
description: 제공자 키로 차트를 설치한 뒤, 렌더링된 워크로드를 검증합니다.
---

## Helm 저장소에서 설치

```bash
helm repo add hermes-agent https://jyje.github.io/hermes-agent-helm
helm repo update
helm upgrade --install hermes-agent hermes-agent/hermes-agent \
  --namespace hermes-agent --create-namespace \
  --set-string env.OPENAI_API_KEY='sk-...' --wait
```

## 또는 OCI 아티팩트로 설치

```bash
helm upgrade --install hermes-agent \
  oci://ghcr.io/jyje/hermes-agent-helm/hermes-agent \
  --version <chart-version> --namespace hermes-agent --create-namespace \
  --set-string env.OPENAI_API_KEY='sk-...' --wait
```

## 검증

```bash
helm test hermes-agent --namespace hermes-agent
kubectl get pods --namespace hermes-agent
```

Helm 테스트는 차트의 doctor 스타일 점검을 수행합니다. 기본 OpenAI 설정이 목표와
다르다면, 다음으로 제공자 오버레이를 선택하세요.
