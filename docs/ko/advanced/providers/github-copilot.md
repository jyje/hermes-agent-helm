---
title: GitHub Copilot
description: Discord를 통해 GitHub OAuth device login을 완료하는 구성
---

| 필수 Secret | 오버레이 |
| --- | --- |
| `DISCORD_BOT_TOKEN` | `values-github-copilot.yaml` |

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

## 이후 시작

토큰은 영속 볼륨의 `HERMES_HOME/.env`에 저장됩니다. 이후 시작에서는 init container가
`https://api.github.com/user`로 토큰을 확인하고, 아직 동작하면 로그인을 건너뜁니다.
폐기된 토큰(HTTP 401)일 때만 새 device login을 시작합니다. 이 확인은 Copilot 플랜과
무관합니다. 1.18.0까지의 차트는 `copilot_internal/v2/token`을 확인했는데, Copilot Free
계정에서 유효한 토큰에도 403을 돌려줘서 재시작할 때마다 새 코드를 요구했습니다
([#349](https://github.com/jyje/hermes-agent-helm/issues/349)). `validateUrl`을 바꾼다면
폐기된 토큰에는 401, 그 외에는 200을 돌려주는 엔드포인트로 두세요.

## Discord 대신 Telegram

`auth.deviceFlow.notify: telegram`으로 설정하고, Discord 값 대신 Telegram 봇 토큰과 홈
채널(`TELEGRAM_BOT_TOKEN`, `TELEGRAM_HOME_CHANNEL`, `TELEGRAM_ALLOWED_USERS`)을
릴리스에 주세요. 그러면 코드가 Telegram 채팅으로 오고, `readyNotify.enabled: true`를 켜면
에이전트가 올라왔을 때 그곳에 한 줄이 옵니다. Copilot Free 계정에서 라이브로 확인했을 때
로그인이 끝났고 준비 알림이 왔으며 `gpt-4o`로 응답했습니다. 어떤 모델이 되는지는 GitHub
플랜에 따릅니다.

[원본 YAML 열기](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-github-copilot.yaml)

## 전체 오버레이

```yaml title="charts/hermes-agent/values-github-copilot.yaml"
--8<-- "charts/hermes-agent/values-github-copilot.yaml"
```