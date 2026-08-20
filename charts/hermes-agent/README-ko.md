<div align="center" markdown="1">

# hermes-agent-helm/hermes-agent

<img height="240" src="https://raw.githubusercontent.com/jyje/hermes-agent-helm/main/docs/images/hermes-agent-helm.png" alt="Kubernetes × Hermes Agent"/>

</div>

👩🏻‍💻 Kubernetes에서 실행하는 Hermes Agent - Codex/Copilot 계정으로 로그인하고, 에이전트 팀을 운영하며, 가볍게 유지됩니다.

[Hermes Agent](https://github.com/NousResearch/hermes-agent) - 멀티 제공자 LLM 에이전트 프레임워크 - 를 Kubernetes에서 실행하세요. Hermes가 지원하는 모든 제공자(OpenAI, Anthropic, Gemini, OpenRouter, NVIDIA, 또는 LiteLLM/vLLM 같은 OpenAI 호환 프록시)를 `values.yaml`만으로 설정할 수 있고, 내장된 `helm test` 헬스체크도 함께 제공됩니다.

[![GitHub](https://img.shields.io/badge/GitHub-jyje%2Fhermes--agent--helm-181717?logo=github)](https://github.com/jyje/hermes-agent-helm) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/jyje/hermes-agent-helm/blob/main/LICENSE) ![Version: 0.4.0](https://img.shields.io/badge/Version-0.4.0-informational?style=flat) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat) ![AppVersion: v2026.6.19](https://img.shields.io/badge/AppVersion-v2026.6.19-informational?style=flat)

[English](README.md) · [한국어](README-ko.md)

## TL;DR

```bash
# OCI (권장)
helm upgrade --install hermes-agent \
  oci://ghcr.io/jyje/hermes-agent-helm/hermes-agent --version 0.4.0 \
  --namespace hermes-agent --create-namespace \
  --set-string env.OPENAI_API_KEY='sk-...' --wait
```

```bash
# Helm Repository
helm repo add hermes-agent https://jyje.github.io/hermes-agent-helm
helm repo update
helm upgrade --install hermes-agent hermes-agent/hermes-agent \
  --namespace hermes-agent --create-namespace \
  --set-string env.OPENAI_API_KEY='sk-...' --wait
```

- **ArgoCD**: 제공자/메신저 조합별로 바로 적용 가능한 `Application` 매니페스트:
  [`examples/argocd/`](../../examples/argocd/).
- **실제 시크릿을 커밋하지 않는 GitOps**: SealedSecret + `extraEnvFrom` 가이드:
  [`examples/argocd/` § SealedSecret](../../examples/argocd/#sealedsecret-walkthrough-nvidia-nim--discord).
- **에이전트 팀**: 여러 인스턴스를 Discord 채널에서 `@mention`으로 대화를 넘기도록 연결:
  [`examples/argocd/hermes-collab-pair.yaml`](../../examples/argocd/hermes-collab-pair.yaml),
  [팀 구성](../../docs/ko/advanced/teams/reference.md) + [협업 가이드](../../docs/ko/advanced/teams/collaboration.md) 참고.

## 제공자 설정

`config.model.provider`를 내장 키로 설정하고, 해당 키를 `env` 아래에 제공하세요:

| 제공자 | `config.model.provider` | 키 env var | 예제 |
| --- | --- | --- | --- |
| OpenAI | `openai-api` | `OPENAI_API_KEY` | [`values-openai.yaml`](values-openai.yaml) |
| Anthropic (Claude) | `anthropic` | `ANTHROPIC_API_KEY` | [`values-anthropic.yaml`](values-anthropic.yaml) |
| Google Gemini | `gemini` | `GOOGLE_API_KEY` | [`values-gemini.yaml`](values-gemini.yaml) |
| Google Vertex AI | `vertex` | 없음: 마운트된 서비스 계정 JSON(또는 ADC)에서 OAuth2 토큰 자동 발급 | [`values-google-vertex.yaml`](values-google-vertex.yaml) |
| OpenRouter | `openrouter` | `OPENROUTER_API_KEY` | [`values-openrouter.yaml`](values-openrouter.yaml) |
| NVIDIA NIM | `nvidia` | `NVIDIA_API_KEY` | [`values-nvidia-nim-and-discord.yaml`](values-nvidia-nim-and-discord.yaml) |
| Fireworks AI | `fireworks` | `FIREWORKS_API_KEY` | [`values-fireworks.yaml`](values-fireworks.yaml) |
| DeepInfra | `deepinfra` | `DEEPINFRA_API_KEY` | [`values-deepinfra.yaml`](values-deepinfra.yaml) |
| Upstage Solar | `upstage` | `UPSTAGE_API_KEY` | [`values-upstage.yaml`](values-upstage.yaml) |
| GitHub Copilot | `copilot` | `COPILOT_GITHUB_TOKEN` (OAuth 디바이스 플로우: API 키 불필요) | [`values-github-copilot.yaml`](values-github-copilot.yaml) |
| OpenAI Codex | `openai-codex` | ChatGPT/Codex 디바이스 로그인(API 키 불필요) | [`values-openai-codex.yaml`](values-openai-codex.yaml) |
| Mixture-of-Agents (MoA) | `moa` | 프리셋의 reference/aggregator 모델에 따라 다름 | [`values-moa.yaml`](values-moa.yaml) |
| 커스텀 (LiteLLM / vLLM / LM Studio) | `config.providers` 아래 직접 정의한 id | 프록시마다 다름 | [`values-litellm.yaml`](values-litellm.yaml) |

> `openai`(접미사 없음)는 **유효하지 않은** 제공자 키입니다 - OpenRouter의
> 별칭으로 처리됩니다. `openai-api`를 사용하세요.

제공자별 전체 `--set` 예시와 메신저(Discord/Telegram) 설정 가이드는 아래
[제공자 & 메신저 설정](#제공자--메신저-설정)을 참고하세요.

## 테스트

```bash
helm test hermes-agent -n hermes-agent
kubectl logs -n hermes-agent -l app.kubernetes.io/component=test --tail=-1
```

설치 후 `hermes doctor` 스타일 헬스체크 Job을 실행합니다. 실제 제공자
라운드트립까지 검증하려면 아래 [고급 테스트](#고급-테스트)를 참고하세요.

## 개요

Kubernetes에서 [Hermes Agent](https://github.com/NousResearch/hermes-agent)를 실행합니다.
다음 리소스를 배포합니다:

- 영속 `HERMES_HOME`을 가진 단일 레플리카의 **Deployment**(기본) 또는
  **StatefulSet**(`controller.type`) - 이미지의 s6-supervised gateway를 실행
- 부분 `config.yaml`과 선택적 `SOUL.md`를 담는 **ConfigMap**
- `.env`를 담는 **Secret**(`envFrom`으로 주입)
- `controller.type=statefulset`인 경우: DNS/거버넌스용 헤드리스 Service(인바운드
  포트 없음 - gateway는 아웃바운드); `deployment`인 경우: 대신 독립 PVC. 둘 다
  선택한 dashboard, API server, webhook 리스너 포트용 **선택적** ClusterIP
  Service와 **선택적** Ingress 또는 Gateway API HTTPRoute(`ingress.enabled` 또는
  `httpRoute.enabled`)를 가질 수 있습니다
- `hermes doctor` 스타일 체크를 실행하는 **Helm test** Job(`helm test`)

에이전트의 명령 실행은 **`local` 백엔드**를 사용합니다(명령이 파드 내부에서
실행되며, 파드 자체가 샌드박스입니다). `docker` 백엔드는 의도적으로 **클러스터
내에서 지원하지 않습니다** - Docker 데몬/소켓이 필요한데, containerd 클러스터
(MicroK8s / Raspberry Pi)에는 없고, 마운트하는 것 자체가 보안 위험입니다.

> 이미지 태그는 **날짜 기반**입니다(예: `v2026.6.5` == Hermes v0.16.0); 이미지는
> 멀티 아키텍처(amd64 + arm64)이므로 Raspberry Pi 클러스터에서도 실행됩니다.

> **스케일링 참고.** Hermes는 단일 인스턴스 개인용 에이전트이므로, 이 차트는
> `replicaCount: 1`을 고정하며 멀티 레플리카 모드가 없습니다([값 테이블](#values)의
> `replicaCount` 설명 참고). 키우려면 스케일 *업*(더 큰 `resources`, 더 큰
> `persistence.size`)을 하고 - 한 에이전트로 부족해지면 여러 인스턴스를 띄워
> 하나의 gateway 채널을 공유하는 **팀**으로 묶으세요. [Hermes 팀](../../docs/ko/advanced/teams/reference.md)을
> 참고하세요.

## 제공자 & 메신저 설정

로컬 차트 체크아웃으로 설치하는 경우(예: 아직 릴리즈되지 않은 변경 시도):

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  --set-string env.OPENAI_API_KEY='sk-...' --wait
```

이 차트는 플레이스홀더 `OPENAI_API_KEY`를 기본으로 포함합니다; 설치/업그레이드
시점에 사용하는 제공자에 맞게(그리고 `config.model`도) 덮어쓰거나, values
파일을 제공하세요.

> 팁: 릴리즈 이름을 차트 이름(`hermes-agent`)과 같게 하면 리소스 이름이
> `hermes-agent-hermes-agent-0`처럼 접두사가 중복되는 대신
> `hermes-agent-0`처럼 깔끔하게 유지됩니다. 또는 `fullnameOverride`를
> 설정하세요.

### 설치 옵션: LLM 제공자

설치 시점에 설정하는 가장 중요한 항목입니다 - Hermes가 *어떤* LLM 백엔드와
대화할지를 정합니다. (채팅 플랫폼 설정은 아래
[메신저 통합](#messenger-integrations-telegram--discord)을 참고하세요.)

- **내장 제공자**: `config.model.provider`를 Hermes의 내장 키(`openai-api`,
  `anthropic`, `gemini`, `openrouter`, `nvidia`, `deepseek`, `lmstudio`, …)
  중 하나로 설정하고, `config.model.default`를 해당 제공자의 모델 id로
  설정하세요. 그에 맞는 키를 `env` 아래에 제공하세요(`OPENAI_API_KEY`,
  `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`, `NVIDIA_API_KEY`, …).

  ```bash
  # OpenAI
  helm upgrade --install hermes-agent ./charts/hermes-agent -n hermes-agent --create-namespace \
    --set-string config.model.provider=openai-api \
    --set-string config.model.default=gpt-4o-mini \
    --set-string env.OPENAI_API_KEY='sk-...' --wait

  # Gemini
  helm upgrade --install hermes-agent ./charts/hermes-agent -n hermes-agent --create-namespace \
    --set-string config.model.provider=gemini \
    --set-string config.model.default=gemini-2.5-flash \
    --set-string env.GOOGLE_API_KEY='<your-key>' \
    --set-string env.OPENAI_API_KEY=unused --wait

  # NVIDIA NIM (CI가 엔드-투-엔드로 검증하는 제공자)
  helm upgrade --install hermes-agent ./charts/hermes-agent -n hermes-agent --create-namespace \
    --set-string config.model.provider=nvidia \
    --set-string config.model.default=nvidia/nemotron-3-nano-omni-30b-a3b-reasoning \
    --set-string env.NVIDIA_API_KEY='nvapi-...' \
    --set-string env.OPENAI_API_KEY=unused --wait
  ```

- **커스텀 OpenAI 호환 제공자**(LiteLLM, vLLM, LM Studio, …): `config.providers.<id>`
  (`base_url`, `key_env`) 아래 등록하고 `config.model.provider`가 해당 `<id>`를
  가리키게 하세요. ["More examples"](#more-examples)의 `values-litellm.yaml`
  (원격 프록시) 또는 `values-litellm-k8s.yaml`(클러스터 내)을 참고하세요.

### 메신저 통합 (Telegram / Discord)

`hermes gateway run`(워크로드의 실행 커맨드)은 **자격 증명**을 찾을 수 있는
모든 채팅 플랫폼에 연결합니다 - 따라서 메신저를 연결하는 것은 단순히 봇
토큰을 제공하는 문제입니다. 토큰은 민감하므로 `.Values.env`(Secret으로
렌더링됨) 아래에 두고, 민감하지 않은 설정(허용된 사용자, 홈 채널)은
`.Values.extraEnv`(평문 env) 아래 둘 수 있습니다. 토큰을 설정하는 것만으로
해당 플랫폼이 **자동으로 활성화**됩니다 - `config.yaml` 변경은 필요 없습니다.

> **검증 상태:** 차트는 올바른 Secret/env를 렌더링하고 에이전트가 해당
> 플랫폼을 인식합니다. `DISCORD_BOT_TOKEN`과 `DISCORD_HOME_CHANNEL` 시크릿이
> 설정된 신뢰된 CI 실행에서는, CI가 완전한 라이브 라운드트립을 수행합니다.
> 해당 채널에 `hermes send`를 보내고, Discord API로 채널을 다시 읽어 메시지가
> 도착했는지 확인하며 - **검증할 수 없으면 실패합니다**(봇에는 *View Channel*
> + *Read Message History* 권한이 필요합니다). 포크 PR은 시크릿이 노출되지
> 않으므로 이 단계를 건너뜁니다. Telegram은 아직 플레이스홀더만 있습니다.
> 실제 봇 토큰을 제공하면 본인 클러스터에서 둘 다 시도해볼 수 있습니다.

- **Discord**: [Discord Developer Portal](https://discord.com/developers/applications)에서
  봇을 생성하고, **Message Content Intent**를 활성화한 후 서버에 초대하세요.

  ```bash
  helm upgrade --install hermes-agent ./charts/hermes-agent -n hermes-agent --create-namespace \
    --set-string config.model.provider=nvidia \
    --set-string config.model.default=nvidia/nemotron-3-nano-omni-30b-a3b-reasoning \
    --set-string env.NVIDIA_API_KEY='nvapi-...' \
    --set-string env.OPENAI_API_KEY=unused \
    --set-string env.DISCORD_BOT_TOKEN='<bot-token>' --wait
  ```

  선택적인 민감하지 않은 설정(`extraEnv` 또는 `--set`을 통해):

  | env var | 의미 |
  | --- | --- |
  | `DISCORD_ALLOWED_USERS` | 봇과 대화할 수 있는 사용자 ID 목록(쉼표 구분) |
  | `DISCORD_ALLOW_ALL_USERS` | `true`로 설정하면 누구나 허용(개발용) |
  | `DISCORD_HOME_CHANNEL` | cron / 알림 전달용 채널 ID |
  | `DISCORD_HOME_CHANNEL_NAME` | 해당 홈 채널의 표시 이름 |

- **Telegram**: [@BotFather](https://t.me/BotFather)로 봇을 생성하고
  `env.TELEGRAM_BOT_TOKEN`을 설정하세요(선택적으로 `TELEGRAM_HOME_CHANNEL`,
  `TELEGRAM_ALLOWED_USERS`를 `extraEnv`로).

복사해서 바로 쓸 수 있는 메신저 설정 블록은 ["More examples"](#more-examples)의
`values-anthropic-and-discord.yaml` / `values-openai-and-telegram.yaml`을
참고하세요.

## Device flow 로그인(GitHub Copilot과 OpenAI Codex)

`auth.deviceFlow.enabled=true`로 **`auth-device-login` init container**를
추가할 수 있습니다. 이 컨테이너는 검증 URL과 일회용 코드를 Discord 홈 채널
(또는 로그)로 보내고, 사용자의 승인을 기다린 뒤 자격증명을 `HERMES_HOME`
볼륨에 저장합니다.

- `github-copilot`은 GitHub OAuth 2.0 device grant를 수행하고
  `COPILOT_GITHUB_TOKEN`을 `.env`에 저장합니다.
- `openai-codex`는 차트에 고정된 Hermes 버전의 device-code flow를 따르고,
  Hermes native helper로 refresh-token chain을 포함한 `auth.json`을 원자적으로
  갱신합니다. 이는 ChatGPT/Codex 계정 인증이며 API key 방식인 `openai-api`와
  별개입니다.

`auth.deviceFlow.provider`에서 `github-copilot` 또는 `openai-codex`를 선택하세요.

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent -n hermes-agent --create-namespace \
  -f charts/hermes-agent/values-openai-codex.yaml \
  --set-string env.DISCORD_BOT_TOKEN='<bot-token>' --wait
# Discord에 게시된 요청을 승인하거나 init container 로그를 확인하세요.
kubectl logs deploy/hermes-agent -n hermes-agent -c auth-device-login -f
```

참고 사항:

- **`persistence.enabled=true`가 필요합니다.** 영속 볼륨이 없으면 재시작할
  때 자격증명이 사라져 매번 다시 승인해야 합니다.
- **`notify`**는 `discord`(`DISCORD_BOT_TOKEN`과
  `DISCORD_HOME_CHANNEL` 재사용) 또는 `logs`(init container 로그에만 표시)입니다.
- init container는 스토리지 클래스와 관계없이 쓸 수 있도록 **root**로 실행한
  뒤, 자격증명 파일의 소유자를 `auth.deviceFlow.tokenOwner`(기본 uid/gid
  `10000`)로 변경합니다.
- Copilot client id는 Hermes upstream이 사용하는 shared client와 같습니다.
  OpenAI protocol 상수와 저장 로직은 차트가 별도로 소유하지 않고 pinned Hermes
  이미지에서 가져옵니다.

## 에이전트 팀

Hermes는 **단일 인스턴스 개인용 에이전트**입니다 - 수평 확장(스케일 아웃)이 아닙니다.
대신 잘 관리된 인스턴스를 여러 개 띄우고, **하나의 Discord 채널**을 컨텍스트 버스로
공유해 팀을 구성하세요. 각 에이전트는 고유한 봇 토큰, 파드, 사설 `HERMES_HOME`
PVC, 아이덴티티를 가집니다. 과제 조정은 Discord 채널에서만 공유하며, 팀 전용 지식
볼륨은 별도로 마운트합니다.

### `@mention`으로 대화 넘기기

모든 인스턴스가 같은 `DISCORD_HOME_CHANNEL`을 가리키도록 설정하고(각각 다른
`DISCORD_BOT_TOKEN`), Discord 메시지 **본문**에 `<@BOT_USER_ID>`를 직접 삽입해
대화를 넘깁니다 - 답장 참조(reply reference)가 아닌 본문 mention이어야 합니다.
무한 핑퐁을 막기 위해 아래 네 가지 환경변수를 설정하세요:

| 환경변수 | 권장값 | 이유 |
| --- | --- | --- |
| `DISCORD_ALLOW_BOTS` | `mentions` | 다른 봇이 `@mention`할 때만 반응합니다. |
| `DISCORD_THREAD_REQUIRE_MENTION` | `true` | 공유 스레드에서도 명시적 mention이 있어야만 반응합니다. |
| `DISCORD_REPLY_TO_MODE` | `off` | 답장 참조를 붙이지 않습니다: 답장은 자동 ping을 발생시켜 루프를 재시작합니다. |
| `DISCORD_ALLOW_MENTION_REPLIED_USER` | `false` | 자동 reply-ping을 실제 mention으로 처리하지 않습니다. |

이 환경변수들은 `env` / `extraEnv` 아래에 설정하세요(`config` 블록이 아닙니다.
Discord 어댑터가 `os.getenv`로 직접 읽습니다).

또한 `config.group_sessions_per_user: false`를 설정하고
`config.discord.history_backfill: true`를 유지하세요. 그렇지 않으면 Hermes가 같은
스레드의 사람과 각 봇 발신자를 서로 다른 세션으로 분리합니다. Backfill은 봇이
멘션되지 않았던 동안 도착한 보이는 메시지를 문맥으로 보충합니다.

### 빠른 시작: 에이전트 2개, 채널 1개

```bash
helm upgrade --install hermes-planner ./charts/hermes-agent \
  --namespace hermes-team --create-namespace \
  -f charts/hermes-agent/values-multi-agent-collab.yaml \
  --set-string env.DISCORD_BOT_TOKEN='<planner-bot-token>' --wait

helm upgrade --install hermes-builder ./charts/hermes-agent \
  --namespace hermes-team \
  -f charts/hermes-agent/values-multi-agent-collab.yaml \
  --set-string env.DISCORD_BOT_TOKEN='<builder-bot-token>' --wait
```

에이전트가 3명 이상이거나 GitOps로 관리하려면 **ArgoCD ApplicationSet**을 사용하세요.
팀원 추가가 한 줄 diff로 해결됩니다.
[`examples/argocd/hermes-collab-pair.yaml`](../../examples/argocd/hermes-collab-pair.yaml)과
[팀 구성](../../docs/ko/advanced/teams/reference.md) + [협업 가이드](../../docs/ko/advanced/teams/collaboration.md)를
참고하세요.

리더와 여러 멤버로 구성하려면
[`values-team-leader.yaml`](values-team-leader.yaml)과
[`values-team-member.yaml`](values-team-member.yaml)을 사용하세요. 이 기준
프로토콜은 한 번에 하나의 명시적 봇 멘션만 직렬로 처리하고 모든 과제·결과·리뷰를
Discord 스레드에 남깁니다. 별도로 미리 준비한 RWX PVC에는 영속 공유 지식만 두며,
과제·상태·결과 핸드오프에는 사용하지 않습니다. 팀 레시피는 이 claim을 필수로 하며
리더는 읽기/쓰기, 멤버는 읽기 전용으로 마운트합니다.
`file`과 `memory` toolset은 각 에이전트의 자체 작업에 계속 사용할 수 있으며,
파일·메모리·hook·백그라운드 작업을 통한 에이전트 간 핸드오프만 금지합니다.

> Upstream은 현재 Hermes 봇 대 봇 Discord 대화를 내장 circuit breaker가 없는
> 미지원 토폴로지로 문서화합니다. 이 예시는 실험적입니다. 전용 신뢰 채널과 수동
> 중지 경로를 준비하고, 고정한 이미지 조합으로 실제 실증한 뒤 사용하세요.

기준 시퀀스는 kind의 `v2026.7.20`에서 실제로 완주했습니다. 타임스탬프가 있는
[팀 증거](../../docs/ko/advanced/teams/reference.md#리더-주도-팀-leader-orchestrated-teams)를 참고하세요.

> **대안: 파드 하나, 프로필 여러 개.** 여러 봇이 채널 하나를 공유하는 게 아니라,
> **봇 토큰 하나**로 서로 다른 Discord 길드/채널/스레드를 서로 다른 에이전트
> *프로필*로 라우팅하는 게 실제로 필요한 것이라면, `config.gateway.multiplex_profiles:
> true`를 설정하세요(환경변수 오버라이드: `GATEWAY_MULTIPLEX_PROFILES=1`). 이러면
> 팀원마다 파드 하나가 아니라 파드 하나로 끝납니다 - 위의 핸드오프 패턴과는 다른
> 문제(협업이 아니라 라우팅)를 푸는 것이니, 실제 필요한 형태에 맞춰 고르세요.

## 고급 테스트

[`helm test`](#테스트) Job(훅 `helm.sh/hook: test`)은 `hermes --version`을
실행하고, 시드된 `config.yaml`을 검증하며, docker 가용성을 확인하고(백엔드가
`local`이므로 정보 제공용), `hermes doctor`를 실행합니다. `--set
tests.enabled=false`로 끄거나, `--set tests.doctorStrict=true`로 doctor
실패를 치명적 오류로 만들 수 있습니다.

### 제공자 엔드-투-엔드 검증 (`tests.chat.enabled`)

`tests.chat.enabled=true`는 5번째 체크를 추가합니다: 릴리즈가 설치될 때 사용된
**동일한 `config`/`env`**로 실제 `hermes chat` 라운드트립을 수행하고(테스트
Job이 메인 워크로드와 같은 ConfigMap·Secret을 마운트하므로 별도의 제공자
키가 필요 없습니다), **전체 대화(프롬프트 + 응답)를 테스트 Job의 로그에
출력**합니다. `helm test`는 `--set`을 받지 않으므로, `helm upgrade --reuse-values`로
플래그를 켠 다음 테스트를 실행하세요:

```bash
helm upgrade hermes-agent ./charts/hermes-agent -n hermes-agent \
  --reuse-values --set tests.chat.enabled=true --wait

helm test hermes-agent -n hermes-agent
kubectl logs -n hermes-agent -l app.kubernetes.io/component=test --tail=-1
```

출력 예시(NVIDIA NIM, 기본 프롬프트 `tests.chat.prompt` "Just say hi."):

```
[5/5] hermes chat round-trip
--- prompt ---
Just say hi.
--- model: (config default) (timeout 180s) ---
Query: Just say hi.
Initializing agent...
────────────────────────────────────────

╭─ ⚕ Hermes ───────────────────────────────────────────────────────────────────╮
    Hi.
╰──────────────────────────────────────────────────────────────────────────────╯

--- end response ---
```

기본적으로 실패하거나 빈 라운드트립은 **치명적이지 않습니다**(로그만 남김);
`tests.chat.failOnError=true`로 설정하면 테스트 Job을 실패시킵니다(`NVIDIA_API_KEY`
시크릿이 있을 때 CI가 이렇게 동작합니다).

단일 모델이 불안정/과부하될 수 있는 무료 등급 제공자의 경우, `tests.chat.models`에
`provider/model` id 목록을 설정하세요 - 테스트 Job이 각각을 순서대로
`hermes chat -m <id> --provider <config.model.provider>`로 시도하고(시도마다
자체 `tests.chat.timeout` 적용) 하나라도 성공하면 통과합니다. CI가 바로 이
방식을 사용합니다(소수의 무료 NVIDIA NIM 모델 풀).

## 설정 모델

Hermes는 `$HERMES_HOME/config.yaml`과 환경의 시크릿을 버전별 내장 기본값 위에
적용되는 **부분 오버라이드**로 읽습니다(우선순위: CLI > `config.yaml` >
`.env` > 내장 기본값). 이 차트도 같은 모델을 따릅니다 - 바꾸고 싶은 값만
설정하면 되고, 업스트림 전체 설정을 차트에 복제하지 않습니다(그러면 Hermes
버전이 바뀔 때마다 어긋나게 됩니다).

> **패스스루 원칙.** `.Values.config`는 **그대로** `config.yaml`로
> 렌더링됩니다 - 모든 레벨에서 임의의 추가 키를 허용합니다(`values.schema.json`
> 참고). 즉 Hermes 자체의
> [설정 가이드](https://hermes-agent.nousresearch.com/docs/user-guide/configuration)나
> [환경변수 레퍼런스](https://hermes-agent.nousresearch.com/docs/reference/environment-variables)에
> 문서화된 **어떤 키든** `config.<경로>` 또는 `env`/`extraEnv`로 **차트 변경
> 없이** 이미 설정 가능합니다. 이 README는 설치 시점에 대부분의 사람이 건드리는
> 소수의 설정(제공자, 메신저, 팀 토폴로지)만 엄선해 다루며, 의도적으로
> 업스트림 문서 전체를 복제하지 않습니다. 조회 방법은 아래 [FAQ](#faq)를
> 참고하세요.

- **`config.yaml`**: `.Values.config` 아래 오버라이드할 키만 설정하세요.
  ConfigMap으로 렌더링되어 init 컨테이너에 의해 **`HERMES_HOME`에 시드**됩니다
  (영속 볼륨), Hermes가 런타임에도 자신의 home에 쓰기 때문입니다(skills,
  `auth.json`, self-improvement). `bootstrap.overwrite=true`(기본값)는 매
  배포마다 다시 시드하고, `false`로 설정하면 없을 때만 시드합니다(런타임
  수정 보존).
- **`SOUL.md` 정체성**: `.Values.soul.text`를 설정하면 영속 에이전트 정체성을
  `HERMES_HOME/SOUL.md`에 시드합니다. 비워 두면 Hermes가 첫 실행에서 자체
  시작 파일을 만듭니다. `config.yaml`과는 독립적으로 처리하므로
  `bootstrap.overwrite=false`에서는 기존 정체성을 보존하고, `true`에서는 매
  배포마다 차트 내용으로 교체합니다. ConfigMap 기반 값에는 시크릿을 넣지
  마세요. 정체성 내용과 범위는 공식
  [SOUL.md 가이드](https://hermes-agent.nousresearch.com/docs/guides/use-soul-with-hermes)를
  참고하세요.
- **시크릿 / API 키**: `.Values.env` 아래 설정하세요. Secret으로 렌더링되어
  `envFrom`을 통해 환경변수로 주입됩니다(env가 `config.yaml`보다 우선).

### 시크릿 공급 전략

배포마다 하나를 고르세요 - 조합도 가능합니다(제공자 키는 SealedSecret, 나머지는
Bitwarden 등):

| 전략 | 언제 쓰나 | 참고 |
| --- | --- | --- |
| 평문 `.Values.env` | 로컬/개발용, 또는 실제 값을 절대 커밋하지 않는 values 파일 | 이 README의 제공자 예제 |
| SealedSecret + `extraEnvFrom` | GitOps: 실제 시크릿을 암호화해서 커밋 가능하게 | [`examples/argocd/`](../../examples/argocd/) |
| Bitwarden Secrets Manager | N개 제공자 키를 회전 가능한 부트스트랩 토큰 하나로 중앙화 | [`values-bitwarden.yaml`](values-bitwarden.yaml) |
| 1Password | 이 차트는 아직 다루지 않습니다: 해당 시크릿 소스는 시작 시 이미지/PATH에 `op` CLI가 있어야 하는데, 이는 values 예제 하나로 해결할 범위를 넘어섭니다. 업스트림 쪽 작업이 먼저 필요합니다. |: |

GitOps 환경에서는 실제 키를 `env`에 커밋하지 말고 - 대신 `extraResources`를
통해 `SealedSecret`(또는 유사한 것)을 배포하고, 거기서 생성된 Secret을
`extraEnvFrom`으로 참조하세요(차트 자체 Secret 다음에 적용되므로 우선
적용됩니다). 완전한 SealedSecret + `extraEnvFrom` GitOps 예제는
[`examples/argocd/`](../../examples/argocd/)를 참고하세요.

Bitwarden Secrets Manager는 `config.secrets.bitwarden`으로 시작 시 제공자
키를 가져옵니다. 부트스트랩 자격증명인 `BWS_ACCESS_TOKEN`만 외부에서 관리하는
Kubernetes Secret에 넣고 `extraEnvFrom`으로 참조하세요.
[`values-bitwarden.yaml`](values-bitwarden.yaml) 예제를 참고하세요. 첫 시작
시 checksum 검증된 `bws` CLI를 `HERMES_HOME`에 내려받으므로, Pod에는
Bitwarden과 GitHub Releases로의 egress가 필요합니다.

- **대시보드 라우팅**: 관리 대시보드(`service.port`, 기본값 9119)는
  `127.0.0.1` 너머로 바인딩하려면 `--insecure`가 필요한데, 업스트림은 이것이
  **네트워크에 API 키를 노출**한다고 경고합니다. 인증(예: oauth2-proxy/basic-auth
  Ingress annotation) 뒤에서나 사설 네트워크에서만 라우팅하세요.

### API server와 webhook 리스너

`apiServer.enabled`는 Hermes의 OpenAI 호환 API server를 시작합니다. Kubernetes
Service가 연결할 수 있도록 차트의 기본 host는 업스트림 loopback 기본값과 달리
`0.0.0.0`입니다. loopback 전용 server라도 `API_SERVER_KEY`가 필요하므로 `env`
또는 권장 방식인 `extraEnvFrom`으로 참조하는 외부 관리 Secret을 통해 설정하세요.
`apiServer.corsOrigins`는 명시적이고 좁은 browser origin 허용 목록에만 사용하세요.
공식 [API server 가이드](https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server)를
참고하세요.

`webhook.enabled`는 하나의 범용 webhook receiver를 시작합니다. Telegram,
Discord, Slack 등은 별도 리스너가 아니라 이 리스너 뒤의 route입니다.
`WEBHOOK_SECRET` 또는 route별 secret을 `env`나 `extraEnvFrom`으로 설정하세요.
공식 [webhook 가이드](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/webhooks)를
참고하세요.

두 런타임 설정 모두 포트를 자동 노출하지 않습니다. 기존 dashboard만 노출하는
Service를 유지하려면 `service.ports: []`를 두고, API server나 webhook을 노출할
때는 필요한 Service port를 모두 명시하세요. 바로 사용할 수 있는
[`values-api-server-and-webhook.yaml`](values-api-server-and-webhook.yaml)은 API
server와 webhook 포트를 노출하고 필요한 자격증명은 외부 Secret으로 참조합니다.

### A2A(Agent-to-Agent) 리스너

위 두 리스너와 달리 A2A는 전용 chart 값이나 env var 스위치가 없습니다 —
업스트림의 유일한 스위치는 `config.yaml`의 `gateway.platforms.a2a` 블록이라,
차트가 이미 갖고 있는 free-form `config:` passthrough로 직접 켭니다:

```yaml
config:
  gateway:
    platforms:
      a2a:
        enabled: true
        extra:
          port: 9900
extraEnv:
  - name: A2A_HOST      # 업스트림 기본값은 127.0.0.1 - Service를 위해 넓힘
    value: "0.0.0.0"
  - name: A2A_PORT
    value: "9900"
```

`A2A_BEARER_TOKEN`(공유) 또는 `A2A_PEER_TOKENS`(피어별, 권장)를 `env`나
`extraEnvFrom`으로 설정하세요 — 업스트림은 이 토큰이 설정돼야만 loopback
너머로 바인딩을 넓힙니다. 공식
[A2A 가이드](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/a2a)를
참고하세요. 바로 사용할 수 있는 [`values-a2a.yaml`](values-a2a.yaml)은 명시적
Service port로 이 포트를 노출하고 필요한 토큰은 외부 Secret으로 참조합니다.

### HTTP 라우팅: Ingress 또는 HTTPRoute

두 라우팅 리소스는 기본으로 꺼져 있습니다. 설치된 Ingress controller가 있으면
`ingress`를 사용하세요. 클러스터에 Gateway API CRD와 `parentRefs`로 참조할
Gateway가 이미 있으면 `httpRoute`를 사용하세요. 같은 host와 path에 두 리소스를
함께 켜기보다 클러스터가 운영하는 라우팅 API 하나를 선택하세요.

각 Ingress path는 `service`와 `port`를 덮어쓸 수 있습니다. Service 이름을 생략하면
이 차트의 Service를 대상으로 하므로 `service.enabled: true`가 필요합니다. 외부
Service 이름을 명시하면 차트 Service 없이도 됩니다. HTTPRoute도 각
`backendRefs` 항목에 같은 기본 규칙을 적용합니다. 암시적 chart-Service backend가
존재하지 않는 Service를 가리키면 차트가 일찍 실패합니다.

[`values-ingress-listeners.yaml`](values-ingress-listeners.yaml)은 `/v1` API와
webhook 트래픽을 서로 다른 Ingress host와 Service port로 라우팅합니다.
[`values-httproute.yaml`](values-httproute.yaml)은 Gateway API 시작점입니다. 하나의
HTTPRoute에서 hostname은 모든 rule에 적용되므로, 리스너 rule을 host 단위로
분리해야 하면 별도의 HTTPRoute를 만드세요.

### Pod Security Standards 하드닝

`podSecurityContext`/`securityContext`는 어떤 클러스터에서도 동작하도록
기본값이 비어 있지만, non-root와 read-only rootfs 둘 다 pinned 이미지 기준으로
CI 검증됐습니다: s6-overlay가 스스로 non-root uid로 내려가고, `/run`과 `/tmp`가
쓰기 가능한 실행형(execable) tmpfs이기만 하면 read-only 상태로도 정상
부팅합니다(`/run`엔 s6 자신의 init 바이너리가 있고, 시작할 때 그걸 exec합니다).
직접 만들지 말고 [`values-hardened.yaml`](values-hardened.yaml)을 쓰세요 -
Pod Security Standards `restricted`를 만족하는 오버레이이고,
`pod-security.kubernetes.io/enforce=restricted`가 설정된 namespace에 설치하면
됩니다.

init container 2개는 pod/메인 컨테이너와 별도로 자기만의 securityContext가
필요합니다: `auth.deviceFlow.securityContext`(기본값 비어 있음, login 이미지의
기본 유저를 그대로 씀)는 대상 uid가 토큰 저장 경로를 이미 소유하고 있으면
non-root로도 동작합니다 - `values-hardened.yaml`이 `tokenOwner`와 맞춘 오버라이드
예시를 보여줍니다. `team.sharedVolume.permissions`의 소유권 준비 컨테이너는
임의의 storage backend에 `chown`하려면 root가 필요해서 non-root 옵션이
없습니다 - `restricted` 아래에서는 `permissions.enabled`를 꺼두고, storage
backend가 fsGroup을 지원한다면 `podSecurityContext.fsGroup`에 맡기세요.

## 무인(unattended) 승인

Gateway 파드에는 **TTY가 없습니다** - 위험한 `terminal`/`execute_code` 명령에
대한 Hermes의 인터랙티브 승인 프롬프트에 답할 사람이 없어서, 그 자리에서
실행이 멈출 수 있습니다. `config.approvals` 아래에서 조정하세요:

```yaml
config:
  approvals:
    mode: manual        # 기본값 "manual"은 프롬프트를 띄움 - gateway엔 답할 사람이 없음
    deny:                # 이 패턴에 매칭되는 명령은 승인/yolo 로직이 보기도 전에
      - "rm -rf /"       # 무조건 거부됩니다: yolo 모드에서도 안전하게 유지
      - "curl.*\\|.*sh"
    cron_mode: deny       # 무인 cron 실행: "deny"(기본값) 또는 "approve"
    discord_prompt_timeout: 120  # Discord 버튼 프롬프트 유지 시간(초)
                                 # (업스트림에서 clamp됨; 기본값 300초/5분)
```

`approvals.deny`는 전체 정책이 아니라 "거부 목록"입니다 - 다른 승인 모드가
무엇이든 상관없이 특정 위험 패턴을 무조건 막기 위해 존재합니다. 이것만으로
gateway가 비대화형이 되지는 않으니, 감수할 위험 수준에 맞는
HERMES_YOLO_MODE/승인 모드 설정과 함께 사용하세요(전체 내용은 [설정
가이드](https://hermes-agent.nousresearch.com/docs/user-guide/configuration)
참고 - 승인 정책 전체를 여기서 다시 다루지는 않습니다).

## 환경변수

이 차트는 시작에 필요한 [제공자](#install-options-llm-provider) 및
[메신저](#messenger-integrations-telegram--discord) 변수만 다룹니다 - Hermes
자체는 환경에서 훨씬 많은 변수를 읽습니다. 이들 모두 위와 같은 방식으로
설정할 수 있습니다: 시크릿은 `.Values.env`(Secret) 아래, 민감하지 않은 설정은
`.Values.extraEnv`(평문 env) 아래, 또는 외부에서 관리되는 시크릿은
`extraEnvFrom`을 통해([설정 모델](#configuration-model) 참고).

전체 레퍼런스(각 Hermes 릴리즈에 맞춰 최신 상태 유지):
**[Environment Variables - Hermes Agent docs](https://hermes-agent.nousresearch.com/docs/reference/environment-variables)**.

이미지 `v2026.7.1` 기준으로 자주 쓰이는 몇 가지를 더 소개합니다:

| 변수 | 용도 |
| --- | --- |
| `DEEPSEEK_API_KEY` | DeepSeek 제공자 |
| `FIREWORKS_API_KEY` | Fireworks AI 제공자 |
| `DEEPINFRA_API_KEY` / `DEEPINFRA_BASE_URL` | DeepInfra 제공자 및 선택적 엔드포인트 오버라이드 |
| `UPSTAGE_API_KEY` / `UPSTAGE_BASE_URL` | Upstage Solar 제공자 및 선택적 엔드포인트 오버라이드 |
| `ZAI_API_KEY` | Z.AI / GLM 제공자 (내장 키 `zai`; `GLM_BASE_URL`로 Global/중국/Coding Plan 엔드포인트 선택) |
| `AWS_REGION` / `AWS_PROFILE` | Amazon Bedrock 제공자 |
| `AZURE_FOUNDRY_API_KEY` | Microsoft Foundry / Azure OpenAI 제공자 |
| `NOUS_INFERENCE_BASE_URL` | Nous OAuth 추론 엔드포인트 오버라이드 |
| `HERMES_WRITE_SAFE_ROOT` | `write_file`/`patch`를 이 루트 디렉터리들로 제한 (여러 개는 OS 경로 구분자로) |
| `SLACK_BOT_TOKEN` / `SLACK_APP_TOKEN` | Slack 봇 (Socket Mode) |
| `MATRIX_HOMESERVER` / `MATRIX_ACCESS_TOKEN` | Matrix 홈서버 통합 |
| `WHATSAPP_CLOUD_PHONE_NUMBER_ID` / `WHATSAPP_CLOUD_ACCESS_TOKEN` | WhatsApp Cloud API |
| `HERMES_MAX_ITERATIONS` | 도구 호출 루프 제한 (기본값: 90) |
| `HERMES_AGENT_TIMEOUT` | Gateway 비활성 타임아웃 (기본값: 1800초 / 30분) |
| `SESSION_IDLE_MINUTES` | 유휴 세션 초기화 주기 (기본값: 1440) |
| `HERMES_TIMEZONE` | IANA 타임존 오버라이드 |

> **환경변수로 설정 불가:** 컨텍스트 압축, 폴백 제공자, 제공자 라우팅은
> `config.yaml`(`.Values.config` 아래)에만 존재하며, 대응하는 환경변수가
> 없습니다.

## FAQ

**이 README에 없는 Hermes 설정을 하고 싶어요 - 어떻게 하나요?**

이 README는 설치 시점의 기본 사항(제공자, 메신저, 팀 토폴로지)만 다룹니다.
그 외의 것은:

1. 공식 [설정 가이드](https://hermes-agent.nousresearch.com/docs/user-guide/configuration)
   (`config.yaml` 키용) 또는
   [환경변수 레퍼런스](https://hermes-agent.nousresearch.com/docs/reference/environment-variables)
   (환경변수용)에서 바꾸고 싶은 항목을 찾아보세요.
2. `config.yaml` 키(예: `foo.bar: baz`)를 찾았다면? values 파일의
   `.Values.config.foo.bar`에 설정하세요(또는
   `--set-string config.foo.bar=baz`). 환경변수(예: `SOME_TOKEN`)를
   찾았다면? `.Values.env.SOME_TOKEN`(시크릿) 또는 `.Values.extraEnv`
   (평문)에 설정하세요.
3. `helm upgrade` 후 `kubectl exec <pod> -- hermes doctor` 또는 `helm test`로
   확인하세요.

Hermes 자체가 이미 지원하는 설정이라면 차트 변경은 전혀 필요 없습니다 - 위의
[패스스루 원칙](#설정-모델)을 참고하세요. 이 차트의 `values.yaml`/예제
파일들은 시작 템플릿을 가질 만한 가치가 있는 설정(새 제공자의 전체 블록,
메신저의 루프 브레이크 env var, 팀 토폴로지)에 대해서만 존재하며, Hermes
자체 레퍼런스 문서를 다시 복제한 것이 아닙니다.

**업스트림 릴리즈 노트가 왜 새 `values.yaml` 키로 이어지지 않았나요?**

"config X 추가" 형태의 업스트림 요청 대부분은 위 패스스루로 차트 변경 없이
이미 도달 가능한 것으로 판명됩니다 - 최근 사례:
[#45](https://github.com/jyje/hermes-agent-helm/issues/45),
[#46](https://github.com/jyje/hermes-agent-helm/issues/46),
[#48](https://github.com/jyje/hermes-agent-helm/issues/48). 새
`values-*.yaml` 예제 파일은 설정이 복사해서 바로 쓸 시작점을 가질 만큼
복잡할 때만(새 제공자, 새 시크릿 소스) 추가되며, 업스트림이 출시하는
개별 키마다 추가되지는 않습니다.

## 더 많은 예제

소규모/홈 클러스터(예: Raspberry Pi / arm64 k3s 클러스터)를 대상으로 한,
바로 적용 가능한 `-f` 오버레이입니다. 이 파일의 자격증명은 **더미 플레이스홀더
또는 외부 Secret 참조**입니다. 플레이스홀더는 설치 시점에 `--set-string`으로
덮어쓰거나(각 파일 헤더 주석의 커맨드 참고), 위의 SealedSecret +
`extraEnvFrom` 패턴을 사용하세요.

| 파일 | 모델 제공자 | 추가 사항 |
| --- | --- | --- |
| [`values-nvidia-nim-and-discord.yaml`](values-nvidia-nim-and-discord.yaml) | NVIDIA NIM | **Discord 봇** 연결됨 |
| [`values-nvidia-nim-and-buzz.yaml`](values-nvidia-nim-and-buzz.yaml) | NVIDIA NIM | **Buzz 봇** 연결됨 (Block의 Nostr 기반 사람+에이전트 플랫폼) |
| [`values-github-copilot.yaml`](values-github-copilot.yaml) | GitHub Copilot (`copilot`) | **OAuth device-flow 로그인** + Discord 봇 |
| [`values-openai-codex.yaml`](values-openai-codex.yaml) | OpenAI Codex (`openai-codex`) | **ChatGPT/Codex device 로그인** + Discord 봇 |
| [`values-anthropic-and-discord.yaml`](values-anthropic-and-discord.yaml) | Anthropic (Claude) | **Discord 봇** 연결됨 |
| [`values-openai-and-telegram.yaml`](values-openai-and-telegram.yaml) | OpenAI (`openai-api`) | **Telegram 봇** 연결됨 |
| [`values-openai.yaml`](values-openai.yaml) | OpenAI (`openai-api`) |: |
| [`values-anthropic.yaml`](values-anthropic.yaml) | Anthropic (Claude) |: |
| [`values-gemini.yaml`](values-gemini.yaml) | Google Gemini |: |
| [`values-google-vertex.yaml`](values-google-vertex.yaml) | Google Vertex AI (`vertex`) | **서비스 계정 JSON 마운트** (`extraVolumes`, 정적 API 키 없음) |
| [`values-openrouter.yaml`](values-openrouter.yaml) | OpenRouter |: |
| [`values-fireworks.yaml`](values-fireworks.yaml) | Fireworks AI | Fireworks 고유 모델 ID |
| [`values-deepinfra.yaml`](values-deepinfra.yaml) | DeepInfra | `DEEPINFRA_BASE_URL`로 엔드포인트 오버라이드 |
| [`values-upstage.yaml`](values-upstage.yaml) | Upstage Solar | `UPSTAGE_BASE_URL`로 엔드포인트 오버라이드 |
| [`values-moa.yaml`](values-moa.yaml) | Mixture-of-Agents (`moa`) | reference 모델들이 병렬로 실행되고, aggregator 모델이 결과를 종합 |
| [`values-bitwarden.yaml`](values-bitwarden.yaml) | any | **Bitwarden Secrets Manager**가 시작 시 제공자 키 제공 |
| [`values-litellm.yaml`](values-litellm.yaml) | LiteLLM 프록시 (원격/Ingress) |: |
| [`values-litellm-k8s.yaml`](values-litellm-k8s.yaml) | LiteLLM 프록시 (클러스터 내 Service DNS) |: |
| [`values-ingress.yaml`](values-ingress.yaml) | OpenAI (`openai-api`) | **대시보드 Ingress** 연결됨 (basic-auth) |
| [`values-api-server-and-webhook.yaml`](values-api-server-and-webhook.yaml) | OpenAI (`openai-api`) | **API server + webhook**: 명시적 Service port와 외부 listener secret |
| [`values-a2a.yaml`](values-a2a.yaml) | OpenAI (`openai-api`) | **A2A (Agent-to-Agent)**: config.yaml passthrough + 명시적 Service port로 다른 A2A 에이전트가 발견·구동 가능 |
| [`values-ingress-listeners.yaml`](values-ingress-listeners.yaml) | OpenAI (`openai-api`) | **Ingress 리스너 라우팅**: `/v1` API와 webhook host가 별도 Service port 사용 |
| [`values-httproute.yaml`](values-httproute.yaml) | OpenAI (`openai-api`) | **Gateway API HTTPRoute**: 사전에 만든 Gateway를 통한 리스너 라우팅 |
| [`values-networkpolicy-litellm.yaml`](values-networkpolicy-litellm.yaml) | LiteLLM proxy (in-cluster) | **Egress 제한 NetworkPolicy**: RFC1918과 클라우드 metadata endpoint 차단, LiteLLM Service만 정확히 허용 |
| [`values-hardened.yaml`](values-hardened.yaml) | OpenAI (`openai-api`) | **Pod Security Standards `restricted`**: non-root, read-only rootfs, capability 전부 drop - `restricted`를 강제하는 namespace에서 CI 검증됨 |
| [`values-soul.yaml`](values-soul.yaml) | any | **영속 정체성**: 실용적인 엔지니어링 말투, 런타임 편집 보존 |
| [`values-multi-agent-collab.yaml`](values-multi-agent-collab.yaml) | any | **협업 페어**: 공유 Discord 채널에서 @mention으로 핸드오프하는 두 에이전트 |
| [`values-team-leader.yaml`](values-team-leader.yaml) + [`values-team-member.yaml`](values-team-member.yaml) | NVIDIA NIM (무엇이든 가능) | **리더 주도 팀**: 직렬 명시적 봇 @mention과 리더 쓰기/멤버 읽기 전용 RWX 지식 PVC; 파일 기반 과제 핸드오프는 사용하지 않음; [Teams](../../docs/ko/advanced/teams/reference.md) 참고 |
| [`values-shared-knowledge.yaml`](values-shared-knowledge.yaml) | Anthropic (Claude) | **공유 RWX PVC**: 동일한 지식 베이스에 읽기/쓰기하는 다수의 에이전트 |

순수 `helm`/`-f` 대신 ArgoCD로 배포하시나요? [`examples/argocd/`](../../examples/argocd/)를
참고하세요 - 위 예제마다 하나의 Application 매니페스트와 그에 맞는
`extraEnvFrom` 기반 시크릿 패턴이 준비되어 있습니다.

## 값 (Values)

> 아래 표는 `values.yaml`의 주석에서 [helm-docs](https://github.com/norwoodj/helm-docs)로
> 자동 생성되며, 단일 소스 유지를 위해 원문(영어) 그대로 둡니다 - 최신 내용은
> 언제나 [영어 표](README.md#values)와 동일합니다.

| Key | Type | Description | Default |
|-----|------|-------------|---------|
| affinity | object | Affinity rules for Pod scheduling. | `{}` |
| apiServer | object | ------------------------------------------------------------------------- | `{"corsOrigins":"","enabled":false,"host":"0.0.0.0","port":8642}` |
| apiServer.corsOrigins | string | Comma-separated browser origins allowed to call the API directly. Empty    disables browser CORS access. | `""` |
| apiServer.enabled | bool | Enable Hermes' OpenAI-compatible HTTP API server. | `false` |
| apiServer.host | string | Bind address. Upstream defaults to 127.0.0.1; a Kubernetes Service needs    a non-loopback address. API_SERVER_KEY is still required on loopback. | `"0.0.0.0"` |
| apiServer.port | int | API server port. | `8642` |
| args | list | Arguments passed through the image entrypoint. `gateway run` selects the    non-interactive outbound messaging service instead of the default TUI. | `["gateway","run"]` |
| auth | object | ------------------------------------------------------------------------- | `{"deviceFlow":{"enabled":false,"forceRelogin":false,"image":{"repository":"python","tag":"3.13-slim"},"notify":"discord","provider":"github-copilot","providers":{"github-copilot":{"authHost":"github.com","clientId":"Ov23li8tweQw6odWQebz","flow":"github","scope":"read:user","tokenEnv":"COPILOT_GITHUB_TOKEN","validateUrl":"https://api.github.com/copilot_internal/v2/token"},"openai-codex":{"flow":"openai-codex","issuer":"https://auth.openai.com"}},"resources":{},"timeoutSeconds":870,"tokenOwner":{"gid":10000,"uid":10000}}}` |
| auth.deviceFlow.enabled | bool | Bootstrap a provider credential via the OAuth device flow at startup.    When false, the agent uses the static key from `env`/`extraEnvFrom`. | `false` |
| auth.deviceFlow.forceRelogin | bool | Force a fresh login even if a token already exists on the volume. | `false` |
| auth.deviceFlow.image | object | Login image for GitHub-style profiles. OpenAI Codex uses the pinned    Hermes image so auth.json persistence and refresh stay version-aligned. | `{"repository":"python","tag":"3.13-slim"}` |
| auth.deviceFlow.notify | string | Where to deliver the verification URL + user code for human approval.    `discord` reuses the agent's bot creds (DISCORD_BOT_TOKEN +    DISCORD_HOME_CHANNEL from `env`/`extraEnvFrom`). The code is always    also printed to the init container logs as a fallback. | `"discord"` |
| auth.deviceFlow.provider | string | Which provider profile to authenticate. Must be a key under    `providers` below. Only one device-flow login runs at a time. | `"github-copilot"` |
| auth.deviceFlow.providers.github-copilot.authHost | string | Host serving the device-code + token endpoints (GitHub-style paths). | `"github.com"` |
| auth.deviceFlow.providers.github-copilot.clientId | string | OAuth client id for the device grant. The shared opencode/Copilot-CLI    client that Hermes upstream itself uses (hermes_cli/copilot_auth.py). | `"Ov23li8tweQw6odWQebz"` |
| auth.deviceFlow.providers.github-copilot.flow | string | Login protocol handler. | `"github"` |
| auth.deviceFlow.providers.github-copilot.scope | string | OAuth scope requested in the device grant. | `"read:user"` |
| auth.deviceFlow.providers.github-copilot.tokenEnv | string | .env key Hermes reads this provider's token from (resolution order    COPILOT_GITHUB_TOKEN > GH_TOKEN > GITHUB_TOKEN). | `"COPILOT_GITHUB_TOKEN"` |
| auth.deviceFlow.providers.github-copilot.validateUrl | string | Optional endpoint to verify an existing token is still live; on    401/403 the init container re-runs the login. Empty = skip the check. | `"https://api.github.com/copilot_internal/v2/token"` |
| auth.deviceFlow.providers.openai-codex.flow | string | Use the OpenAI Codex device-code flow bundled with the pinned    Hermes version and persist refreshable credentials in auth.json. | `"openai-codex"` |
| auth.deviceFlow.providers.openai-codex.issuer | string | OpenAI account issuer. Override only for a compatible test server. | `"https://auth.openai.com"` |
| auth.deviceFlow.resources | object | Resources for the login init container. | `{}` |
| auth.deviceFlow.securityContext | object | securityContext for the device-login init container. Empty by    default - inherits the image's own user (root for the Python image,    the pinned Hermes image otherwise). Overriding to a non-root uid only    works if that uid can already write the token's destination path;    see values-hardened.yaml for a verified non-root override (uid/gid    matching tokenOwner, so the chown above becomes a same-uid no-op). | `{}` |
| auth.deviceFlow.timeoutSeconds | int | Seconds to wait for the human to authorize before the init container    fails (and retries). Keep below the provider's device-code validity. | `870` |
| auth.deviceFlow.tokenOwner | object | uid/gid that should own the written token file. By default this init    container inherits the login image's own user (root for the Python    image below) so it can write to any storage class reliably, then    chowns the token to this owner. Set it to the Hermes runtime uid; the    upstream image's s6-overlay runs the agent as uid/gid 10000: so the    non-root agent can read the credential. | `{"gid":10000,"uid":10000}` |
| bootstrap.enabled | bool | Seed chart-managed files into HERMES_HOME via an init container. | `true` |
| bootstrap.overwrite | bool | true: overwrite config.yaml and configured SOUL.md with chart content on    every deploy (declarative). false: seed each file only if it does not    already exist (preserve runtime edits). | `true` |
| command | list | Container command override. Empty keeps the Hermes image entrypoint, which    starts the s6-supervised outbound messaging gateway and prepares volume    ownership before dropping privileges. Set only for explicit debugging. | `[]` |
| config | object | ------------------------------------------------------------------------- | `{"agent":{"gateway_timeout":1800,"max_turns":90},"model":{"default":"gpt-4o-mini","provider":"openai-api"},"providers":{},"terminal":{"backend":"local"}}` |
| controller | object | ------------------------------------------------------------------------- | `{"type":"deployment"}` |
| controller.type | string | Workload kind: "deployment" or "statefulset". | `"deployment"` |
| deploymentAnnotations | object | Annotations to add to the Deployment or StatefulSet object. | `{}` |
| env | object | ------------------------------------------------------------------------- | `{"OPENAI_API_KEY":"sk-REPLACE_ME"}` |
| extraContainers | list | Extra sidecar containers appended to the Pod's main `containers:` list.    Distinct from `extraInitContainers` (init phase only). Full container    spec; giving a sidecar its own resources and a PSS-compatible    securityContext is the operator's responsibility. | `[]` |
| extraEnv | list | Plain (non-secret) env vars injected directly on the container. | `[]` |
| extraEnvFrom | list | Extra envFrom sources (reference existing ConfigMaps/Secrets). | `[]` |
| extraInitContainers | list | Extra init containers, appended after the chart's own (seed-config,    device-flow login). Full container spec; combine with `extraVolumes` for    one-time preparation of a user-provided volume (for example, a shared    knowledge volume used independently of the Discord team handoff). | `[]` |
| extraResources | list | Extra raw manifests rendered as-is alongside this chart's resources.    Each entry is `tpl`-rendered, so `{{ .Release.Namespace }}` etc. work, and    may be either an object or a multiline string (see examples/argocd/).    Useful for things this chart doesn't model directly, e.g. a SealedSecret    that a sealed-secrets controller decrypts into a Secret referenced via    `extraEnvFrom` (see examples/argocd/). | `[]` |
| extraVolumeMounts | list | Extra volume mounts on the hermes-agent container (pairs with extraVolumes). | `[]` |
| extraVolumes | list | Extra volumes on the pod, for anything the agent needs as a FILE rather    than an env var: e.g. a Secret holding a service-account JSON    (see values-google-vertex.yaml). | `[]` |
| fullnameOverride | string | Fully override the generated resource name (release-name-chart). | `""` |
| httpRoute.enabled | bool | Create a Gateway API HTTPRoute. The cluster must already provide the    Gateway API CRD and a Gateway selected by `parentRefs`. | `false` |
| httpRoute.hostnames | list | HTTP hostnames accepted by this route. | `[]` |
| httpRoute.parentRefs | list | Gateway API parent references. | `[]` |
| httpRoute.rules | list | HTTPRoute rules. An empty backendRef name targets this chart's Service. | `[]` |
| image.pullPolicy | string | Image pull policy. | `"IfNotPresent"` |
| image.repository | string | Container image repository (multi-arch: amd64 + arm64). | `"nousresearch/hermes-agent"` |
| image.tag | string | Image tag. Upstream uses DATE-based tags (e.g. "v2026.6.5" == Hermes v0.16.0), plus `latest` / `main`. There is no semver tag. Empty defaults to `.Chart.AppVersion`. | `""` |
| imagePullSecrets | list | Image pull secrets for private registries. | `[]` |
| ingress.annotations | object | Annotations to add to the Ingress (e.g. auth, cert-manager, rewrite rules). | `{}` |
| ingress.className | string | IngressClass name (e.g. "nginx", "traefik"). Empty uses the cluster default. | `""` |
| ingress.enabled | bool | Create an Ingress resource. | `false` |
| ingress.hosts | list | Host/path rules. Each path defaults to this chart's Service and the    legacy dashboard port; override `service` and `port` per listener. | `[{"host":"hermes-agent.example.com","paths":[{"path":"/","pathType":"Prefix"}]}]` |
| ingress.tls | list | TLS configuration for the Ingress. | `[]` |
| nameOverride | string | Override the chart name used in resource names. | `""` |
| nodeSelector | object | Node selector for Pod scheduling. | `{}` |
| persistence | object | ------------------------------------------------------------------------- | `{"accessModes":["ReadWriteOnce"],"enabled":true,"existingClaim":"","mountPath":"/opt/data","size":"5Gi","storageClass":""}` |
| persistence.existingClaim | string | Use an existing PVC instead of creating a new one. When specified, the chart will use this PVC and skip creating its own. | `""` |
| persistence.storageClass | string | StorageClass for the volumeClaimTemplate. Empty = cluster default. | `""` |
| podAnnotations | object | Annotations to add to the Pod. | `{}` |
| podLabels | object | Labels to add to the Pod. | `{}` |
| podSecurityContext | object | Pod-level securityContext. Left empty by default to stay compatible with the image's s6-overlay init (which starts as root and drops privileges itself). Add hardening here once verified for your environment. | `{}` |
| probes | object | Health probes. Empty = none. The image's s6-overlay already supervises and auto-restarts the gateway in-container, so k8s probes are optional. Provide a full probe spec to enable, e.g. an exec check:   liveness:     exec: { command: ["hermes","gateway","status"] }     initialDelaySeconds: 30     periodSeconds: 30 | `{"liveness":{},"readiness":{},"startup":{}}` |
| probes.liveness | object | Liveness probe spec. Empty = no liveness probe. | `{}` |
| probes.readiness | object | Readiness probe spec. Empty = no readiness probe. | `{}` |
| probes.startup | object | Startup probe spec. Empty = no startup probe. Use this when first start takes longer than the liveness probe allows. | `{}` |
| replicaCount | int | Set to 0 to prepare GitOps resources (Secret, ConfigMap, PVC, ...)    without starting an agent Pod, then scale to 1 after credentials and    optional device login are ready. The gateway and device-login init    container do not run while paused. Hermes Agent is a single-writer    workload bound to one HERMES_HOME (ReadWriteOnce PVC), so values above 1    are unsupported: Deployment replicas contend for the same volume and    StatefulSet replicas are disconnected agent identities. | `1` |
| resources | object | Container resource requests/limits. Lightweight defaults aimed at small clusters (incl. Raspberry Pi / arm64). | `{"limits":{"cpu":"2","memory":"2Gi"},"requests":{"cpu":"100m","memory":"256Mi"}}` |
| runtimeClassName | string | RuntimeClass for the Pod. Set to a sandboxed runtime (gVisor: "gvisor",    Kata: "kata-containers") to add a kernel isolation boundary around the    agent's shell execution. Empty by default: the cluster's default runtime. | `""` |
| securityContext | object | Container-level securityContext. Same caveat as `podSecurityContext` above. | `{}` |
| service | object | ------------------------------------------------------------------------- | `{"annotations":{},"enabled":false,"port":9119,"type":"ClusterIP"}` |
| service.annotations | object | Annotations to add to the Service. | `{}` |
| service.enabled | bool | Create a ClusterIP Service for explicitly selected listeners. | `false` |
| service.port | int | Legacy dashboard Service port. Used only while `service.ports` is empty,    preserving the existing dashboard-only Service behaviour. | `9119` |
| service.ports | list | Explicit Service ports. A non-empty list replaces the legacy dashboard    port entirely. Enabling apiServer or webhook does not add a Service port    automatically. | `[]` |
| service.type | string | Service type. | `"ClusterIP"` |
| serviceAccount.annotations | object | Annotations to add to the ServiceAccount. | `{}` |
| serviceAccount.automountServiceAccountToken | bool | Mount the ServiceAccount token into the Pod. The agent does not call    the Kubernetes API, so this chart turns it off. Behaviour change on    upgrade: without this field, Kubernetes applies its own default of    true. Set to true if something inside the Pod deliberately calls the    API (e.g. kubectl-style tooling in an extraContainer). | `false` |
| serviceAccount.create | bool | Create a ServiceAccount for the pod. | `true` |
| serviceAccount.name | string | Name to use; generated from fullname when empty. | `""` |
| soul | object | Contents of SOUL.md, seeded into HERMES_HOME alongside config.yaml. It    defines the agent's persistent identity. Empty means the chart seeds    nothing, so Hermes writes its own starter file on first run. | `{"text":""}` |
| terminationGracePeriodSeconds | string | Pod termination grace period in seconds. Empty = Kubernetes default (30s). The gateway (image v2026.7.1+) defaults `agent.restart_drain_timeout` to 0: on stop it interrupts in-flight runs immediately, persists the transcript, and exits fast: the default grace period is plenty. If you opt into a drain window via `config.agent.restart_drain_timeout: <seconds>`, raise this WELL ABOVE that value or the kubelet SIGKILLs the gateway mid-drain (stale lock + crash loop: the same race upstream warns about with systemd's TimeoutStopSec). See "Gateway lifecycle" in the README. | `""` |
| tests | object | ------------------------------------------------------------------------- | `{"chat":{"enabled":false,"failOnError":false,"maxTurns":1,"models":[],"prompt":"Just say hi.","timeout":180},"doctorStrict":false,"doctorTimeout":120,"enabled":true,"image":{"pullPolicy":"","repository":"","tag":""},"resources":{"limits":{"cpu":"1","memory":"512Mi"},"requests":{"cpu":"100m","memory":"128Mi"}}}` |
| tests.chat | object | ------------------------------------------------------------------------- | `{"enabled":false,"failOnError":false,"maxTurns":1,"models":[],"prompt":"Just say hi.","timeout":180}` |
| tests.chat.enabled | bool | Run a `hermes chat` round-trip and log the conversation. | `false` |
| tests.chat.failOnError | bool | When true, a failed/empty round-trip fails the test job. | `false` |
| tests.chat.maxTurns | int | Max agent turns for the round-trip. | `1` |
| tests.chat.models | list | Optional pool of `provider/model` ids to try in order (via `hermes chat    -m <id> --provider config.model.provider`), each with its own `timeout`.    Passes as soon as one succeeds: useful for free-tier models that are    sometimes overloaded. Leave empty to use `config.model.default` as-is    (single attempt, no `-m`/`--provider` override). | `[]` |
| tests.chat.prompt | string | Prompt sent to the agent. | `"Just say hi."` |
| tests.chat.timeout | int | Seconds to allow each round-trip attempt to run before timing out. | `180` |
| tests.doctorStrict | bool | When true, `hermes doctor` issues fail the test. When false, doctor runs    for visibility but only hard checks (hermes --version, seeded config) fail. | `false` |
| tests.doctorTimeout | int | Seconds to allow `hermes doctor` to run before timing out. | `120` |
| tests.enabled | bool | Render the chart test Job. | `true` |
| tests.image | object | Image used by the test Job. Empty fields fall back to the main `image.*` (so the hermes CLI + doctor are available and arch matches). | `{"pullPolicy":"","repository":"","tag":""}` |
| tests.resources | object | Resource requests/limits for the test Job's container. | `{"limits":{"cpu":"1","memory":"512Mi"},"requests":{"cpu":"100m","memory":"128Mi"}}` |
| tolerations | list | Tolerations for Pod scheduling. | `[]` |
| webhook.enabled | bool | Enable Hermes' generic inbound webhook receiver. Telegram, Discord,    Slack, and other sources are routes behind this single listener. | `false` |
| webhook.port | int | Webhook receiver port. | `8644` |

----------------------------------------------
Autogenerated from chart metadata using [helm-docs v1.14.2](https://github.com/norwoodj/helm-docs/releases/v1.14.2)
