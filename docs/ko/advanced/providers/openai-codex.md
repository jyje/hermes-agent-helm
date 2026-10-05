---
title: OpenAI Codex
description: Discord로 전달한 device code를 이용해 ChatGPT/Codex 계정을 인증합니다.
---

| 필요한 secret | Overlay |
| --- | --- |
| `DISCORD_BOT_TOKEN` | `values-openai-codex.yaml` |

## 사용 시점

계정 기반 Codex access에는 이 provider를 사용하세요. `OPENAI_API_KEY`가 필요한
`openai-api`와는 별개입니다. 사용할 수 있는 모델은 인증한 계정의 ChatGPT plan과
live Codex catalog에 따라 달라집니다.

Hermes가 refresh 가능한 자격증명을 `HERMES_HOME/auth.json`에 저장하므로 영속
스토리지가 필요합니다.

## 설치

```bash
helm upgrade --install hermes-codex ./charts/hermes-agent \
  --namespace hermes-codex --create-namespace \
  -f charts/hermes-agent/values-openai-codex.yaml \
  --set-string env.DISCORD_BOT_TOKEN='<real-value>' --wait
```

Discord에 게시된 링크를 열고 일회용 코드를 입력해 OpenAI 로그인을 완료하세요.
이후 Pod 시작 시 init container가 Hermes에게 저장된 자격증명을 검증하거나 갱신하도록
요청하며, 계속 사용할 수 있으면 새 로그인을 건너뜁니다.

```bash
kubectl logs deploy/hermes-codex-hermes-agent -n hermes-codex \
  -c auth-device-login -f
```

## 로그인 코드 만료

코드는 약 15분 동안 유효합니다. 승인하기 전에 만료되면 init container가 타임아웃을
알리고 새 코드를 스스로 요청하므로, 가장 최근 코드를 입력하세요. 실제 실행에서도
첫 코드가 만료된 뒤 두 번째 코드가 오고, 그 코드를 승인해 로그인이 끝났습니다.

## 더 큰 컨텍스트 창

Codex 경로는 대부분의 모델에 272K를 광고합니다. Hermes는 `gpt-6-luna-900k`처럼
`-900k` 접미사로 옵트인하면 약 900K까지 쓸 수 있고, 이때 `compression.threshold_tokens`도
함께 올려야 합니다. 이 접미사는 Hermes의 별칭이지 OpenAI 모델명이 아니며, 창이 크면
구독 사용량을 더 빨리 씁니다. 자세한 내용은 아래 overlay의 주석을 참고하세요.

## 하나의 ChatGPT 계정에 릴리스 여러 개

각 릴리스는 독립적으로 로그인하고 자기 `auth.json`에 자격증명을 보관합니다. 업스트림
문서는 같은 OpenAI 계정으로 두 번 로그인하면 하나의 토큰 계열을 공유하고 OpenAI가 이전
로그인을 폐기한다고 설명합니다. 실제 확인에서는 릴리스 3개가 1분 안에 같은 Plus 계정으로
로그인했고, 각 릴리스에서 `hermes auth refresh openai-codex`를 실행해도 모두 성공해서
즉시 폐기되는 현상은 나타나지 않았습니다. 시간이 지난 뒤의 갱신은 확인하지 못했습니다.

- 팀에서는 릴리스마다 계정을 따로 쓰는 것을 권합니다.
- 어떤 릴리스가 갱신에 실패하기 시작하면, 각 릴리스에서
  `hermes auth refresh openai-codex`를 실행해 어느 로그인이 죽었는지 확인하고 그
  릴리스에서 다시 로그인하세요.
- 하나의 `auth.json`을 여러 릴리스에 복사하지 마세요. 리프레시 토큰은 일회용이라 복사본이
  모두 유효할 수 없습니다.

[원본 YAML 열기](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-openai-codex.yaml)

## 전체 overlay

```yaml title="charts/hermes-agent/values-openai-codex.yaml"
--8<-- "charts/hermes-agent/values-openai-codex.yaml"
```
