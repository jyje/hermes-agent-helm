---
title: Bitwarden Secrets Manager
description: Bitwarden에서 provider key를 시작 시 가져오는 구성
---

<div class="example-meta">
  <div><strong>필수 Secret</strong>BWS_ACCESS_TOKEN</div>
  <div><strong>오버레이</strong>values-bitwarden.yaml</div>
</div>

## 언제 사용하나요?

읽기 권한이 있는 Bitwarden machine account와 bootstrap Kubernetes Secret이 필요합니다.

## 설치

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-bitwarden.yaml \
  --set-string env.BWS_ACCESS_TOKEN='<real-value>' --wait
```

둘 이상의 자격 증명이 필요한 예제에서는 모든 값을 `--set-string`으로 전달하거나 `extraEnvFrom`으로 기존 Secret을 참조하세요.

## 배포 전 조정

provider key는 Git이나 Kubernetes Secret이 아닌 Bitwarden project에 보관합니다.

[원본 YAML 열기](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-bitwarden.yaml)

## 전체 오버레이

```yaml title="charts/hermes-agent/values-bitwarden.yaml"
--8<-- "charts/hermes-agent/values-bitwarden.yaml"
```