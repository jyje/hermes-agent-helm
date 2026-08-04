---
title: GitHub Copilot
description: Discord를 통해 GitHub OAuth device login을 완료하는 구성
---

<div class="example-meta">
  <div><strong>필수 Secret</strong>DISCORD_BOT_TOKEN</div>
  <div><strong>오버레이</strong>values-github-copilot.yaml</div>
</div>

## 언제 사용하나요?

Discord bot과 GitHub Copilot 권한이 필요합니다. 영속 볼륨도 활성화해야 로그인 토큰이 재사용됩니다.

## 설치

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-github-copilot.yaml \
  --set-string env.DISCORD_BOT_TOKEN='<real-value>' --wait
```

둘 이상의 자격 증명이 필요한 예제에서는 모든 값을 `--set-string`으로 전달하거나 `extraEnvFrom`으로 기존 Secret을 참조하세요.

## 배포 전 조정

초기 pod 로그 또는 Discord 안내에 나온 device code를 GitHub에서 승인합니다.

[원본 YAML 열기](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-github-copilot.yaml)

## 전체 오버레이

```yaml title="charts/hermes-agent/values-github-copilot.yaml"
--8<-- "charts/hermes-agent/values-github-copilot.yaml"
```