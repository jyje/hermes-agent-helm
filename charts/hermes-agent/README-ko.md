<div align="center">

# hermes-agent-helm/hermes-agent

<img height="240" src="https://raw.githubusercontent.com/jyje/hermes-agent-helm/main/docs/images/hermes-agent-helm.png" alt="Kubernetes × Hermes Agent"/>

</div>

👩🏻‍💻 **Hermes Agent**를 Kubernetes에서 실행하는 Helm 차트, 커뮤니티 기반, 경량

[Hermes Agent](https://github.com/NousResearch/hermes-agent) — 멀티 제공자 LLM 에이전트 프레임워크 — 를 Kubernetes에서 실행하세요. Hermes가 지원하는 모든 제공자(OpenAI, Anthropic, Gemini, OpenRouter, NVIDIA, 또는 LiteLLM/vLLM 같은 OpenAI 호환 프록시)를 `values.yaml`만으로 설정할 수 있고, 내장된 `helm test` 헬스체크도 함께 제공됩니다.

![Version: 0.4.0](https://img.shields.io/badge/Version-0.4.0-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: v2026.6.19](https://img.shields.io/badge/AppVersion-v2026.6.19-informational?style=flat-square)

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
# 클래식 Helm 저장소
helm repo add hermes-agent https://jyje.github.io/hermes-agent-helm
helm repo update
helm upgrade --install hermes-agent hermes-agent/hermes-agent \
  --namespace hermes-agent --create-namespace \
  --set-string env.OPENAI_API_KEY='sk-...' --wait
```

- **ArgoCD** — 제공자/메신저 조합별로 바로 적용 가능한 `Application` 매니페스트:
  [`examples/argocd/`](../../examples/argocd/).
- **실제 시크릿을 커밋하지 않는 GitOps** — SealedSecret + `extraEnvFrom` 가이드:
  [`examples/argocd/` § SealedSecret](../../examples/argocd/#sealedsecret-walkthrough-nvidia-nim--discord).
- **에이전트 팀** — 여러 인스턴스를 Discord 채널에서 `@mention`으로 대화를 넘기도록 연결:
  [`examples/argocd/hermes-collab-pair.yaml`](../../examples/argocd/hermes-collab-pair.yaml),
  [팀 구성](../../docs/teams-ko.md) + [협업 가이드](../../docs/collaboration-ko.md) 참고.

## 제공자 설정

`config.model.provider`를 내장 키로 설정하고, 해당 키를 `env` 아래에 제공하세요:

| 제공자 | `config.model.provider` | 키 env var | 예제 |
| --- | --- | --- | --- |
| OpenAI | `openai-api` | `OPENAI_API_KEY` | [`values-openai.yaml`](values-openai.yaml) |
| Anthropic (Claude) | `anthropic` | `ANTHROPIC_API_KEY` | [`values-anthropic.yaml`](values-anthropic.yaml) |
| Google Gemini | `gemini` | `GOOGLE_API_KEY` | [`values-gemini.yaml`](values-gemini.yaml) |
| Google Vertex AI | `vertex` | 없음 — 마운트된 서비스 계정 JSON(또는 ADC)에서 OAuth2 토큰 자동 발급 | [`values-google-vertex.yaml`](values-google-vertex.yaml) |
| OpenRouter | `openrouter` | `OPENROUTER_API_KEY` | [`values-openrouter.yaml`](values-openrouter.yaml) |
| NVIDIA NIM | `nvidia` | `NVIDIA_API_KEY` | [`values-nvidia-nim-and-discord.yaml`](values-nvidia-nim-and-discord.yaml) |
| GitHub Copilot | `copilot` | `COPILOT_GITHUB_TOKEN` (OAuth 디바이스 플로우 — API 키 불필요) | [`values-github-copilot.yaml`](values-github-copilot.yaml) |
| Mixture-of-Agents (MoA) | `moa` | 프리셋의 reference/aggregator 모델에 따라 다름 | [`values-moa.yaml`](values-moa.yaml) |
| 커스텀 (LiteLLM / vLLM / LM Studio) | `config.providers` 아래 직접 정의한 id | 프록시마다 다름 | [`values-litellm.yaml`](values-litellm.yaml) |

> `openai`(접미사 없음)는 **유효하지 않은** 제공자 키입니다 — OpenRouter의
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
  **StatefulSet**(`controller.type`) — 이미지의 s6-supervised gateway를 실행
- 부분 `config.yaml`을 담는 **ConfigMap**
- `.env`를 담는 **Secret**(`envFrom`으로 주입)
- `controller.type=statefulset`인 경우: DNS/거버넌스용 헤드리스 Service(인바운드
  포트 없음 — gateway는 아웃바운드); `deployment`인 경우: 대신 독립 PVC. 둘 다
  대시보드용 **선택적** ClusterIP Service와 그 앞단의 **선택적** Ingress
  (`ingress.enabled`)를 가질 수 있습니다
- `hermes doctor` 스타일 체크를 실행하는 **Helm test** Job(`helm test`)

에이전트의 명령 실행은 **`local` 백엔드**를 사용합니다(명령이 파드 내부에서
실행되며, 파드 자체가 샌드박스입니다). `docker` 백엔드는 의도적으로 **클러스터
내에서 지원하지 않습니다** — Docker 데몬/소켓이 필요한데, containerd 클러스터
(MicroK8s / Raspberry Pi)에는 없고, 마운트하는 것 자체가 보안 위험입니다.

> 이미지 태그는 **날짜 기반**입니다(예: `v2026.6.5` == Hermes v0.16.0); 이미지는
> 멀티 아키텍처(amd64 + arm64)이므로 Raspberry Pi 클러스터에서도 실행됩니다.

> **스케일링 참고.** Hermes는 단일 인스턴스 개인용 에이전트이므로, 이 차트는
> `replicaCount: 1`을 고정하며 멀티 레플리카 모드가 없습니다([값 테이블](#values)의
> `replicaCount` 설명 참고). 키우려면 스케일 *업*(더 큰 `resources`, 더 큰
> `persistence.size`)을 하고 — 한 에이전트로 부족해지면 여러 인스턴스를 띄워
> 하나의 gateway 채널을 공유하는 **팀**으로 묶으세요. [Hermes 팀](../../docs/teams-ko.md)을
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

설치 시점에 설정하는 가장 중요한 항목입니다 — Hermes가 *어떤* LLM 백엔드와
대화할지를 정합니다. (채팅 플랫폼 설정은 아래
[메신저 통합](#messenger-integrations-telegram--discord)을 참고하세요.)

- **내장 제공자** — `config.model.provider`를 Hermes의 내장 키(`openai-api`,
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

- **커스텀 OpenAI 호환 제공자**(LiteLLM, vLLM, LM Studio, …) — `config.providers.<id>`
  (`base_url`, `key_env`) 아래 등록하고 `config.model.provider`가 해당 `<id>`를
  가리키게 하세요. ["More examples"](#more-examples)의 `values-litellm.yaml`
  (원격 프록시) 또는 `values-litellm-k8s.yaml`(클러스터 내)을 참고하세요.

### 메신저 통합 (Telegram / Discord)

`hermes gateway run`(워크로드의 실행 커맨드)은 **자격 증명**을 찾을 수 있는
모든 채팅 플랫폼에 연결합니다 — 따라서 메신저를 연결하는 것은 단순히 봇
토큰을 제공하는 문제입니다. 토큰은 민감하므로 `.Values.env`(Secret으로
렌더링됨) 아래에 두고, 민감하지 않은 설정(허용된 사용자, 홈 채널)은
`.Values.extraEnv`(평문 env) 아래 둘 수 있습니다. 토큰을 설정하는 것만으로
해당 플랫폼이 **자동으로 활성화**됩니다 — `config.yaml` 변경은 필요 없습니다.

> **검증 상태:** 차트는 올바른 Secret/env를 렌더링하고 에이전트가 해당
> 플랫폼을 인식합니다. `DISCORD_BOT_TOKEN`과 `DISCORD_HOME_CHANNEL` 시크릿이
> 설정된 신뢰된 CI 실행에서는, CI가 완전한 라이브 라운드트립을 수행합니다 —
> 해당 채널에 `hermes send`를 보내고, Discord API로 채널을 다시 읽어 메시지가
> 도착했는지 확인하며 — **검증할 수 없으면 실패합니다**(봇에는 *View Channel*
> + *Read Message History* 권한이 필요합니다). 포크 PR은 시크릿이 노출되지
> 않으므로 이 단계를 건너뜁니다. Telegram은 아직 플레이스홀더만 있습니다.
> 실제 봇 토큰을 제공하면 본인 클러스터에서 둘 다 시도해볼 수 있습니다.

- **Discord** — [Discord Developer Portal](https://discord.com/developers/applications)에서
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

- **Telegram** — [@BotFather](https://t.me/BotFather)로 봇을 생성하고
  `env.TELEGRAM_BOT_TOKEN`을 설정하세요(선택적으로 `TELEGRAM_HOME_CHANNEL`,
  `TELEGRAM_ALLOWED_USERS`를 `extraEnv`로).

복사해서 바로 쓸 수 있는 메신저 설정 블록은 ["More examples"](#more-examples)의
`values-anthropic-and-discord.yaml` / `values-openai-and-telegram.yaml`을
참고하세요.

## 에이전트 팀

Hermes는 **단일 인스턴스 개인용 에이전트**입니다 — 수평 확장(스케일 아웃)이 아닙니다.
대신 잘 관리된 인스턴스를 여러 개 띄우고, **하나의 Discord 채널**을 컨텍스트 버스로
공유해 팀을 구성하세요. 각 에이전트는 고유한 봇 토큰, 파드, PVC, 아이덴티티를 가지며,
공유 채널만 공통으로 사용합니다.

### `@mention`으로 대화 넘기기

모든 인스턴스가 같은 `DISCORD_HOME_CHANNEL`을 가리키도록 설정하고(각각 다른
`DISCORD_BOT_TOKEN`), Discord 메시지 **본문**에 `<@BOT_USER_ID>`를 직접 삽입해
대화를 넘깁니다 — 답장 참조(reply reference)가 아닌 본문 mention이어야 합니다.
무한 핑퐁을 막기 위해 아래 네 가지 환경변수를 설정하세요:

| 환경변수 | 권장값 | 이유 |
| --- | --- | --- |
| `DISCORD_ALLOW_BOTS` | `mentions` | 다른 봇이 `@mention`할 때만 반응합니다. |
| `DISCORD_THREAD_REQUIRE_MENTION` | `true` | 공유 스레드에서도 명시적 mention이 있어야만 반응합니다. |
| `DISCORD_REPLY_TO_MODE` | `off` | 답장 참조를 붙이지 않습니다 — 답장은 자동 ping을 발생시켜 루프를 재시작합니다. |
| `DISCORD_ALLOW_MENTION_REPLIED_USER` | `false` | 자동 reply-ping을 실제 mention으로 처리하지 않습니다. |

이 환경변수들은 `env` / `extraEnv` 아래에 설정하세요(`config` 블록이 아닙니다
— Discord 어댑터가 `os.getenv`로 직접 읽습니다).

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

에이전트가 3명 이상이거나 GitOps로 관리하려면 **ArgoCD ApplicationSet**을 사용하세요
— 팀원 추가가 한 줄 diff로 해결됩니다.
[`examples/argocd/hermes-collab-pair.yaml`](../../examples/argocd/hermes-collab-pair.yaml)과
[팀 구성](../../docs/teams-ko.md) + [협업 가이드](../../docs/collaboration-ko.md)를
참고하세요.

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
`provider/model` id 목록을 설정하세요 — 테스트 Job이 각각을 순서대로
`hermes chat -m <id> --provider <config.model.provider>`로 시도하고(시도마다
자체 `tests.chat.timeout` 적용) 하나라도 성공하면 통과합니다. CI가 바로 이
방식을 사용합니다(소수의 무료 NVIDIA NIM 모델 풀).

## 설정 모델

Hermes는 `$HERMES_HOME/config.yaml`과 환경의 시크릿을 버전별 내장 기본값 위에
적용되는 **부분 오버라이드**로 읽습니다(우선순위: CLI > `config.yaml` >
`.env` > 내장 기본값). 이 차트도 같은 모델을 따릅니다 — 바꾸고 싶은 값만
설정하면 되고, 업스트림 전체 설정을 차트에 복제하지 않습니다(그러면 Hermes
버전이 바뀔 때마다 어긋나게 됩니다).

- **`config.yaml`** — `.Values.config` 아래 오버라이드할 키만 설정하세요.
  ConfigMap으로 렌더링되어 init 컨테이너에 의해 **`HERMES_HOME`에 시드**됩니다
  (영속 볼륨), Hermes가 런타임에도 자신의 home에 쓰기 때문입니다(skills,
  `auth.json`, self-improvement). `bootstrap.overwrite=true`(기본값)는 매
  배포마다 다시 시드하고, `false`로 설정하면 없을 때만 시드합니다(런타임
  수정 보존).
- **시크릿 / API 키** — `.Values.env` 아래 설정하세요. Secret으로 렌더링되어
  `envFrom`을 통해 환경변수로 주입됩니다(env가 `config.yaml`보다 우선).
  GitOps 환경에서는 실제 키를 `env`에 커밋하지 말고 — 대신 `extraResources`를
  통해 `SealedSecret`(또는 유사한 것)을 배포하고, 거기서 생성된 Secret을
  `extraEnvFrom`으로 참조하세요(차트 자체 Secret 다음에 적용되므로 우선
  적용됩니다). 완전한 SealedSecret + `extraEnvFrom` GitOps 예제는
  [`examples/argocd/`](../../examples/argocd/)를 참고하세요.
- **대시보드 Ingress** — 관리 대시보드(`service.port`, 기본값 9119)는
  `127.0.0.1` 너머로 바인딩하려면 `--insecure`가 필요한데, 업스트림은 이것이
  **네트워크에 API 키를 노출**한다고 경고합니다. `service.enabled: true`와
  `ingress.enabled: true`는 인증(예: oauth2-proxy/basic-auth Ingress
  annotation) 뒤에서나 사설 네트워크에서만 설정하세요 — `values.yaml`의
  `ingress.hosts` / `ingress.tls`를 참고하세요.

## 환경변수

이 차트는 시작에 필요한 [제공자](#install-options-llm-provider) 및
[메신저](#messenger-integrations-telegram--discord) 변수만 다룹니다 — Hermes
자체는 환경에서 훨씬 많은 변수를 읽습니다. 이들 모두 위와 같은 방식으로
설정할 수 있습니다: 시크릿은 `.Values.env`(Secret) 아래, 민감하지 않은 설정은
`.Values.extraEnv`(평문 env) 아래, 또는 외부에서 관리되는 시크릿은
`extraEnvFrom`을 통해([설정 모델](#configuration-model) 참고).

전체 레퍼런스(각 Hermes 릴리즈에 맞춰 최신 상태 유지):
**[Environment Variables — Hermes Agent docs](https://hermes-agent.nousresearch.com/docs/reference/environment-variables)**.

이미지 `v2026.7.1` 기준으로 자주 쓰이는 몇 가지를 더 소개합니다:

| 변수 | 용도 |
| --- | --- |
| `DEEPSEEK_API_KEY` | DeepSeek 제공자 |
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

## 더 많은 예제

소규모/홈 클러스터(예: Raspberry Pi / arm64 k3s 클러스터)를 대상으로 한,
바로 적용 가능한 `-f` 오버레이입니다. 이 파일들의 모든 시크릿은 **더미
플레이스홀더**입니다 — 설치 시점에 `--set-string`으로 덮어쓰거나(각 파일
헤더 주석의 커맨드 참고), 위의 SealedSecret + `extraEnvFrom` 패턴을 사용하세요.

| 파일 | 모델 제공자 | 추가 사항 |
| --- | --- | --- |
| [`values-nvidia-nim-and-discord.yaml`](values-nvidia-nim-and-discord.yaml) | NVIDIA NIM | **Discord 봇** 연결됨 |
| [`values-anthropic-and-discord.yaml`](values-anthropic-and-discord.yaml) | Anthropic (Claude) | **Discord 봇** 연결됨 |
| [`values-openai-and-telegram.yaml`](values-openai-and-telegram.yaml) | OpenAI (`openai-api`) | **Telegram 봇** 연결됨 |
| [`values-openai.yaml`](values-openai.yaml) | OpenAI (`openai-api`) | — |
| [`values-anthropic.yaml`](values-anthropic.yaml) | Anthropic (Claude) | — |
| [`values-gemini.yaml`](values-gemini.yaml) | Google Gemini | — |
| [`values-google-vertex.yaml`](values-google-vertex.yaml) | Google Vertex AI (`vertex`) | **서비스 계정 JSON 마운트** (`extraVolumes`, 정적 API 키 없음) |
| [`values-openrouter.yaml`](values-openrouter.yaml) | OpenRouter | — |
| [`values-litellm.yaml`](values-litellm.yaml) | LiteLLM 프록시 (원격/Ingress) | — |
| [`values-litellm-k8s.yaml`](values-litellm-k8s.yaml) | LiteLLM 프록시 (클러스터 내 Service DNS) | — |
| [`values-ingress.yaml`](values-ingress.yaml) | OpenAI (`openai-api`) | **대시보드 Ingress** 연결됨 (basic-auth) |
| [`values-multi-agent-collab.yaml`](values-multi-agent-collab.yaml) | any | **협업 페어** — 공유 Discord 채널에서 @mention으로 핸드오프하는 두 에이전트 |
| [`values-team-leader.yaml`](values-team-leader.yaml) + [`values-team-member.yaml`](values-team-member.yaml) | NVIDIA NIM (무엇이든 가능) | **리더 주도 팀** — 리더가 @mention으로 위임하고(스타 토폴로지) 멤버들이 RWX 워크스페이스를 공유; [Teams](../../docs/teams-ko.md) 참고 |
| [`values-shared-knowledge.yaml`](values-shared-knowledge.yaml) | Anthropic (Claude) | **공유 RWX PVC** — 동일한 지식 베이스에 읽기/쓰기하는 다수의 에이전트 |

순수 `helm`/`-f` 대신 ArgoCD로 배포하시나요? [`examples/argocd/`](../../examples/argocd/)를
참고하세요 — 위 예제마다 하나의 Application 매니페스트와 그에 맞는
`extraEnvFrom` 기반 시크릿 패턴이 준비되어 있습니다.

## 값 (Values)

> 아래 표는 `values.yaml`의 주석에서 [helm-docs](https://github.com/norwoodj/helm-docs)로
> 자동 생성되며, 단일 소스 유지를 위해 원문(영어) 그대로 둡니다 — 최신 내용은
> 언제나 [영어 표](README.md#values)와 동일합니다.

| Key | Type | Description | Default |
|-----|------|-------------|---------|
| affinity | object | Affinity rules for Pod scheduling. | `{}` |
| args | list | Arguments appended to `command`. | `["gateway","run"]` |
| bootstrap.enabled | bool | Seed the rendered config.yaml into HERMES_HOME via an init container. | `true` |
| bootstrap.overwrite | bool | true: overwrite HERMES_HOME/config.yaml with chart content on every    deploy (declarative). false: seed only if it does not already exist    (preserve runtime edits). | `true` |
| command | list | Container entrypoint. The image's DEFAULT CMD is the interactive `hermes` chat, which exits immediately in a pod (no TTY -> EOF -> "Goodbye"), causing a restart loop. So run the long-lived gateway explicitly; inside the s6-overlay image `gateway run` is auto-redirected to the SUPERVISED s6 service (auto-restart on crash). Append `--no-supervise` only if you want to bypass s6. | `["hermes"]` |
| config | object | ------------------------------------------------------------------------- | `{"agent":{"gateway_timeout":1800,"max_turns":90},"model":{"default":"gpt-4o-mini","provider":"openai-api"},"providers":{},"terminal":{"backend":"local"}}` |
| controller | object | ------------------------------------------------------------------------- | `{"type":"deployment"}` |
| controller.type | string | Workload kind: "deployment" or "statefulset". | `"deployment"` |
| env | object | ------------------------------------------------------------------------- | `{"OPENAI_API_KEY":"sk-REPLACE_ME"}` |
| extraEnv | list | Plain (non-secret) env vars injected directly on the container. | `[]` |
| extraEnvFrom | list | Extra envFrom sources (reference existing ConfigMaps/Secrets). | `[]` |
| extraResources | list | Extra raw manifests rendered as-is alongside this chart's resources.    Each entry is `tpl`-rendered, so `{{ .Release.Namespace }}` etc. work, and    may be either an object or a multiline string (see examples/argocd/).    Useful for things this chart doesn't model directly, e.g. a SealedSecret    that a sealed-secrets controller decrypts into a Secret referenced via    `extraEnvFrom` (see examples/argocd/). | `[]` |
| fullnameOverride | string | Fully override the generated resource name (release-name-chart). | `""` |
| image.pullPolicy | string | Image pull policy. | `"IfNotPresent"` |
| image.repository | string | Container image repository (multi-arch: amd64 + arm64). | `"nousresearch/hermes-agent"` |
| image.tag | string | Image tag. Upstream uses DATE-based tags (e.g. "v2026.6.5" == Hermes v0.16.0), plus `latest` / `main`. There is no semver tag. Empty defaults to `.Chart.AppVersion`. | `""` |
| imagePullSecrets | list | Image pull secrets for private registries. | `[]` |
| ingress.annotations | object | Annotations to add to the Ingress (e.g. auth, cert-manager, rewrite rules). | `{}` |
| ingress.className | string | IngressClass name (e.g. "nginx", "traefik"). Empty uses the cluster default. | `""` |
| ingress.enabled | bool | Create an Ingress resource. | `false` |
| ingress.hosts | list | Host/path rules, all routed to the Service port above. | `[{"host":"hermes-agent.example.com","paths":[{"path":"/","pathType":"Prefix"}]}]` |
| ingress.tls | list | TLS configuration for the Ingress. | `[]` |
| nameOverride | string | Override the chart name used in resource names. | `""` |
| nodeSelector | object | Node selector for Pod scheduling. | `{}` |
| persistence | object | ------------------------------------------------------------------------- | `{"accessModes":["ReadWriteOnce"],"enabled":true,"existingClaim":"","mountPath":"/opt/data","size":"5Gi","storageClass":""}` |
| persistence.existingClaim | string | Use an existing PVC instead of creating a new one. When specified, the chart will use this PVC and skip creating its own. | `""` |
| persistence.storageClass | string | StorageClass for the volumeClaimTemplate. Empty = cluster default. | `""` |
| podAnnotations | object | Annotations to add to the Pod. | `{}` |
| podLabels | object | Labels to add to the Pod. | `{}` |
| podSecurityContext | object | Pod-level securityContext. Left empty by default to stay compatible with the image's s6-overlay init (which starts as root and drops privileges itself). Add hardening here once verified for your environment. | `{}` |
| probes | object | Health probes. Empty = none. The image's s6-overlay already supervises and auto-restarts the gateway in-container, so k8s probes are optional. Provide a full probe spec to enable, e.g. an exec check:   liveness:     exec: { command: ["hermes","gateway","status"] }     initialDelaySeconds: 30     periodSeconds: 30 | `{"liveness":{},"readiness":{}}` |
| probes.liveness | object | Liveness probe spec. Empty = no liveness probe. | `{}` |
| probes.readiness | object | Readiness probe spec. Empty = no readiness probe. | `{}` |
| replicaCount | int | DO NOT change this. Hermes Agent is a single-writer workload bound to one HERMES_HOME (ReadWriteOnce PVC). Raising replicaCount does NOT scale it out — with controller.type=deployment extra replicas just hang Pending (can't mount the same RWO volume); with statefulset they become separate, disconnected agent instances with their own PVC/identity. There is no supported multi-replica mode for this chart. | `1` |
| resources | object | Container resource requests/limits. Lightweight defaults aimed at small clusters (incl. Raspberry Pi / arm64). | `{"limits":{"cpu":"2","memory":"2Gi"},"requests":{"cpu":"100m","memory":"256Mi"}}` |
| securityContext | object | Container-level securityContext. Same caveat as `podSecurityContext` above. | `{}` |
| service | object | ------------------------------------------------------------------------- | `{"annotations":{},"enabled":false,"port":9119,"type":"ClusterIP"}` |
| service.annotations | object | Annotations to add to the Service. | `{}` |
| service.enabled | bool | Create a ClusterIP Service (only useful if you expose the dashboard). | `false` |
| service.port | int | Service port (and the dashboard's container port). | `9119` |
| service.type | string | Service type. | `"ClusterIP"` |
| serviceAccount.annotations | object | Annotations to add to the ServiceAccount. | `{}` |
| serviceAccount.create | bool | Create a ServiceAccount for the pod. | `true` |
| serviceAccount.name | string | Name to use; generated from fullname when empty. | `""` |
| tests | object | ------------------------------------------------------------------------- | `{"chat":{"enabled":false,"failOnError":false,"maxTurns":1,"models":[],"prompt":"Just say hi.","timeout":180},"doctorStrict":false,"doctorTimeout":120,"enabled":true,"image":{"pullPolicy":"","repository":"","tag":""},"resources":{"limits":{"cpu":"1","memory":"512Mi"},"requests":{"cpu":"100m","memory":"128Mi"}}}` |
| tests.chat | object | ------------------------------------------------------------------------- | `{"enabled":false,"failOnError":false,"maxTurns":1,"models":[],"prompt":"Just say hi.","timeout":180}` |
| tests.chat.enabled | bool | Run a `hermes chat` round-trip and log the conversation. | `false` |
| tests.chat.failOnError | bool | When true, a failed/empty round-trip fails the test job. | `false` |
| tests.chat.maxTurns | int | Max agent turns for the round-trip. | `1` |
| tests.chat.models | list | Optional pool of `provider/model` ids to try in order (via `hermes chat    -m <id> --provider config.model.provider`), each with its own `timeout`.    Passes as soon as one succeeds — useful for free-tier models that are    sometimes overloaded. Leave empty to use `config.model.default` as-is    (single attempt, no `-m`/`--provider` override). | `[]` |
| tests.chat.prompt | string | Prompt sent to the agent. | `"Just say hi."` |
| tests.chat.timeout | int | Seconds to allow each round-trip attempt to run before timing out. | `180` |
| tests.doctorStrict | bool | When true, `hermes doctor` issues fail the test. When false, doctor runs    for visibility but only hard checks (hermes --version, seeded config) fail. | `false` |
| tests.doctorTimeout | int | Seconds to allow `hermes doctor` to run before timing out. | `120` |
| tests.enabled | bool | Render the chart test Job. | `true` |
| tests.image | object | Image used by the test Job. Empty fields fall back to the main `image.*` (so the hermes CLI + doctor are available and arch matches). | `{"pullPolicy":"","repository":"","tag":""}` |
| tests.resources | object | Resource requests/limits for the test Job's container. | `{"limits":{"cpu":"1","memory":"512Mi"},"requests":{"cpu":"100m","memory":"128Mi"}}` |
| tolerations | list | Tolerations for Pod scheduling. | `[]` |

----------------------------------------------
[helm-docs v1.14.2](https://github.com/norwoodj/helm-docs/releases/v1.14.2)로 차트 메타데이터에서 자동 생성됨 (값 테이블은 영어 원문 유지, 위 안내 참고)
