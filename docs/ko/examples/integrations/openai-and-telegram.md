---
title: OpenAI + Telegram
description: OpenAI provider와 Telegram bot을 결합한 구성
---

<div class="example-meta">
  <div><strong>필수 Secret</strong>OPENAI_API_KEY, TELEGRAM_BOT_TOKEN</div>
  <div><strong>오버레이</strong>values-openai-and-telegram.yaml</div>
</div>

## 언제 사용하나요?

OpenAI key와 Telegram bot token이 필요합니다.

## 설치

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-openai-and-telegram.yaml \
  --set-string env.OPENAI_API_KEY='<real-value>' --wait
```

둘 이상의 자격 증명이 필요한 예제에서는 모든 값을 `--set-string`으로 전달하거나 `extraEnvFrom`으로 기존 Secret을 참조하세요.

## 배포 전 조정

Telegram 대상 범위를 설정한 뒤 bot과 대화해 연결을 확인합니다.

[원본 YAML 열기](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-openai-and-telegram.yaml)

## 전체 오버레이

```yaml title="charts/hermes-agent/values-openai-and-telegram.yaml"
--8<-- "charts/hermes-agent/values-openai-and-telegram.yaml"
```