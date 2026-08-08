---
title: 설치
description: 이 Helm 저장소에서 Hermes Agent를 설치합니다.
---

## Helm 저장소에서 설치

```bash
helm repo add <repository-name> https://jyje.github.io/hermes-agent-helm
helm repo update
helm upgrade --install <release-name> <repository-name>/hermes-agent \
  --namespace <namespace> --create-namespace
```

배포 전에 차트의 [기본 values 레퍼런스](reference/values.md)를 확인하고
[values 오버레이](overlays/index.md)를 선택하세요.
