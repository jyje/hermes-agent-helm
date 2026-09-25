---
title: Telegram 팀
description: 공유 Telegram assistant와 여러 봇으로 구성하는 Hermes 팀.
translation_source:
  path: docs/advanced/teams/telegram.md
  commit: 3f31940d96cad542c77efd776856ac6754c39bfd
---

# Telegram 팀

[English](../../../advanced/teams/telegram.md) · [한국어](telegram.md)

이 차트는 서로 다른 두 Telegram 구성을 지원합니다. 여러 사용자가 봇 하나를
공유하거나, 각 Hermes 정체성이 자기 봇을 갖는 여러 릴리스 팀입니다. 봇 하나만
사용한다면 [공유 assistant values](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-telegram-team-assistant.yaml),
여러 봇을 사용한다면 [leader](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-telegram-team-leader.yaml),
[member](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-telegram-team-member.yaml) values와
[ApplicationSet 예제](https://github.com/jyje/hermes-agent-helm/blob/main/examples/argocd/hermes-team-telegram.yaml)부터 살펴보세요.

## 여러 사람이 봇 하나를 공유하는 경우

공유 assistant 예제는 Telegram 봇 하나와 Helm 릴리스 하나를 사용합니다. DM과
그룹 접근은 서로 구분해 제한할 수 있습니다.

- `TELEGRAM_ALLOWED_USERS`는 DM과 그룹에서 사용할 수 있는 사용자 ID를 지정합니다.
- `TELEGRAM_GROUP_ALLOWED_USERS`는 그룹에서만 허용할 사용자 ID를 지정합니다.
- `TELEGRAM_GROUP_ALLOWED_CHATS`는 지정한 그룹이나 포럼의 모든 구성원을 허용합니다.
- pairing을 사용하면 봇에 먼저 DM을 보낸 사람을 승인할 수 있습니다. 승인은
  `HERMES_HOME`에 저장되므로 persistence가 켜져 있으면 파드 재시작 후에도 유지됩니다.

예제는 `telegram.require_mention`과 `group_sessions_per_user`를 설정합니다. 그룹에서는
봇을 멘션하거나, 봇 메시지에 답하거나, 봇을 지정한 명령을 보내야 합니다. 일반 그룹
대화는 실행을 시작하지 않습니다. 사용자마다 별도의 대화 세션을 가집니다. 운영 배포에서는
봇 토큰을 Secret에 저장하고 `extraEnvFrom`으로 주입하세요. 저장소의 values 파일에는
자리표시자만 있습니다.

## 그룹 하나에 봇 여러 개 배포하기

Hermes 정체성마다 별도의 릴리스 하나를 배포합니다. 각 릴리스는 자기 봇 토큰,
`HERMES_HOME` PVC, 모델 자격 증명, 팀 정체성을 가집니다. 모든 봇은 Telegram 그룹이나
포럼 주제를 공유합니다. 리더는 공유 roster skill과 읽기/쓰기 지식 PVC도 소유하고,
멤버는 이를 읽기 전용으로 마운트합니다. 영속 볼륨은 검토를 거친 재사용 지식을 보관하는
곳이지, 진행 중인 과제나 핸드오프 상태를 보관하는 곳이 아닙니다.

배포 전 BotFather에서 봇마다 다음을 설정하세요.

1. 봇을 각각 하나씩 만들고 Bot-to-Bot Communication을 켭니다.
2. 모든 봇을 동일한 그룹, supergroup 또는 포럼 주제에 추가합니다.
3. 봇을 그룹 관리자 권한으로 만들거나 Group Privacy를 끕니다. privacy를 변경한 뒤에는
   봇을 그룹에서 제거했다가 다시 추가해야 변경이 적용될 수 있습니다.
4. 릴리스마다 별도의 Secret과 `TELEGRAM_BOT_TOKEN`을 사용합니다. Telegram은 같은
   토큰을 여러 릴리스가 동시에 polling하는 것을 허용하지 않습니다.
5. 위의 사용자 및 그룹 allowlist로 사람의 접근을 제한합니다. 허용 사용자 ID는 각
   릴리스의 Secret이나 공유 라우팅 Secret에 넣습니다.

팀 모드는 roster에 적힌 공개 bot username으로 작업을 라우팅합니다.
`group_sessions_per_user=false`를 설정하고 `telegram.exclusive_bot_mentions=true`를
기본값으로 두며, 공유 `mention_patterns`를 비웁니다. 따라서 메시지에 이름이 나온 봇만
처리합니다. 또한 다음 컨테이너 환경변수를 강제합니다.

| 설정 | 값 | 목적 |
| --- | --- | --- |
| `TELEGRAM_ALLOW_BOTS` | `mentions` | 다른 봇이 명시적으로 이 봇을 부를 때만 허용합니다. |
| `TELEGRAM_BOTS_REQUIRE_MENTION` | `true` | 인용 답장만으로 봇 핸드오프가 시작되지 않게 합니다. |
| `TELEGRAM_REQUIRE_MENTION` | `true` | 그룹 메시지를 처리하려면 trigger가 필요합니다. |
| `TELEGRAM_REPLY_TO_MODE` | `off` | 다른 봇을 다시 깨울 수 있는 답장 참조를 붙이지 않습니다. |

roster 프로토콜은 작업을 순차화합니다. 리더는 한 번에 멤버 하나에게 위임하고 결과를
기다려 검토한 다음, 사람에게 멤버 멘션 없이 최종 답변을 합니다. 핸드오프 횟수에도
제한을 두고, 대화를 다시 시작할 후속 메시지 대신 멈추도록 지시합니다. Hermes의
대화별 bot-loop guard도 추가 안전장치로 계속 켜져 있습니다. 이 제어들은 우발적인
루프 가능성을 낮추지만, 실제 Telegram 대화를 관찰하는 일을 대신하지는 않습니다.

### 왜 `hermes peer`가 아니라 Telegram 봇 메시지를 쓰나요?

요구된 흐름은 Telegram 그룹에서 눈에 보여야 합니다. 사람이 리더를 부르고, 리더가
멤버를 부른 뒤, 최종 답변이 사람에게 돌아옵니다. `hermes peer`는 gateway 간 DM을
제공하는 유효한 플랫폼 중립 대안이지만, 접근 가능한 API server와 `API_SERVER_KEY`
자격 증명이 필요하고 핸드오프 메시지를 해당 그룹에 게시하지 않습니다. 따라서 이
예제를 그대로 대체할 수 있는 방식이 아니라 다른 상호작용 모델입니다. 내부 gateway
핸드오프가 더 적합하다면 업스트림 [`hermes peer` 가이드](https://hermes-agent.nousresearch.com/docs/user-guide/bot-mode#bot-initiated-dms-across-machines-hermes-peer)를
참고하세요.

## 검증 상태

values와 ApplicationSet 예제는 CI에서 렌더링 검사를 받습니다. 이는 차트 구성이
올바른지 확인하는 것이지 Telegram 전달 성공을 뜻하지 않습니다. 실제 봇 간 라우팅,
부정 사례, 스크린샷은 운영자가 Telegram 봇과 자격 증명을 제공한 라이브 배포에서
추가 확인해야 합니다. 이 예제는 라이브 검증이 완료되었다고 주장하지 않습니다.
