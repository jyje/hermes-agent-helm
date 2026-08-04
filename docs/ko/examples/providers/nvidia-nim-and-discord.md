---
title: NVIDIA NIM + Discord
description: NVIDIA NIM 모델과 Discord bot을 함께 연결하는 구성
---

<div class="example-meta">
  <div><strong>필수 Secret</strong>NVIDIA_API_KEY, DISCORD_BOT_TOKEN</div>
  <div><strong>오버레이</strong>values-nvidia-nim-and-discord.yaml</div>
</div>

## 언제 사용하나요?

NVIDIA API key, Discord bot token, 채널 및 허용 사용자 ID가 필요합니다.

## 설치

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-nvidia-nim-and-discord.yaml \
  --set-string env.NVIDIA_API_KEY='<real-value>' --wait
```

둘 이상의 자격 증명이 필요한 예제에서는 모든 값을 `--set-string`으로 전달하거나 `extraEnvFrom`으로 기존 Secret을 참조하세요.

## 배포 전 조정

ARM64 클러스터에서도 사용할 수 있는 provider + messenger 조합입니다.

[원본 YAML 열기](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-nvidia-nim-and-discord.yaml)

## 전체 오버레이

```yaml title="charts/hermes-agent/values-nvidia-nim-and-discord.yaml"
--8<-- "charts/hermes-agent/values-nvidia-nim-and-discord.yaml"
```