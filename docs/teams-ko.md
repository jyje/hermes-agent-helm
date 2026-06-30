# Hermes 팀: 스케일 *업*, 그리고 그룹

[English](teams.md) · [한국어](teams-ko.md)

> 한 줄 요약 — **Hermes 파드를 스케일 아웃하지 마세요. 잘 관리된 단일 인스턴스를
> 여러 개 띄우고, 하나의 gateway 채널을 공유하는 팀으로 묶으세요.**

## Hermes가 단일 인스턴스인 이유

Hermes Agent는 **개인용 에이전트**입니다: 하나의 `HERMES_HOME`, 하나의
[gateway 프로세스](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/),
하나의 메모리/정체성(`SOUL`, skills, `auth.json`, self-improvement 상태). gateway는
공식 문서에서 명시하듯 "설정된 모든 플랫폼에 연결되어 세션을 처리하고 cron을 실행하며
메시지를 전달하는 단일 백그라운드 프로세스"입니다 — 하나의 에이전트가 거치는 *유일한*
허브죠.

그래서 단일 인스턴스는 **단일 writer 워크로드**가 되고, 이 차트가 `replicaCount: 1`을
고정하며 스케일 아웃을 지양하는 이유입니다([차트 README](../charts/hermes-agent/README.md)의
`replicaCount` 설명 참고):

- `controller.type=deployment` → 추가 레플리카는 `Pending`에 걸립니다
  (동일한 `ReadWriteOnce` PVC를 마운트할 수 없음).
- `controller.type=statefulset` → 추가 레플리카는 각자의 PVC/정체성을 가진
  **별개의, 단절된 에이전트**가 됩니다 — 같은 에이전트의 더 큰 버전이 아닙니다.

따라서 `replicaCount`를 올려도 "같은 Hermes가 더 많아지는" 일은 없습니다. 설계상
지원되는 멀티 레플리카 모드는 없습니다.

## 모델: 경량부터 프로덕션까지

홈랩 장난감에서 프로덕션 배포로 가는 길은 **스케일 '업'하고, 그다음 그룹 만들기**입니다 — 단일
에이전트를 스케일 아웃하는 게 아닙니다:

1. **단일 인스턴스의 스팩을 키웁니다.** `resources`를 늘리고, `persistence.size`를 키우고,
   실제 `storageClass`·probe·제대로 된 시크릿 관리(SealedSecret / external-secrets)를
   붙이세요. 하나의 인스턴스를, 잘.
2. **여러 인스턴스를 팀으로 묶습니다.** 한 에이전트로 부족할 때(사람이 늘고, 역할이
   늘고, 병렬 작업이 늘 때) *여러* 단일 인스턴스를 — 각각 독립 릴리즈로 — 배포하고,
   **하나의 공유 gateway 채널**에 합류시켜 에이전트와 팀이 공통 컨텍스트 버스를
   공유하게 합니다.

이 문서는 2번에 대한 이야기입니다.

## 팀이 컨텍스트를 공유하는 방식

각 Hermes 인스턴스는 자신의 gateway를 **같은 채널**(예: 하나의 Discord 채널)에
연결합니다. 그 공유 채널이 팀의 컨텍스트 버스가 됩니다:

- 각 에이전트가 채널에서 메시지를 읽고 쓰므로, **대화 자체가** 사람이든 에이전트든
  모든 구성원이 보는 **공유 컨텍스트**가 됩니다.
- 그 채널은 동시에 **home 채널**(`*_HOME_CHANNEL`) 역할을 합니다 — 각 에이전트가
  cron 결과와 능동적 알림을 전달하는 곳이며,
  [messaging gateway 문서](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/)에
  설명돼 있습니다.
- 팀 전체가 공유해야 할 지식(기술 스택, 컨벤션, 우선순위)은 **컨텍스트 파일**
  (`SOUL.md`, `AGENTS.md`)로 고정합니다 — 매 세션의 시스템 프롬프트에 주입되며,
  [Team Telegram Assistant 가이드](https://hermes-agent.nousresearch.com/docs/guides/team-telegram-assistant)에
  나옵니다.
- **공유 영속적 지식** (벡터 인덱스, 대화 내역, 또는 공유 config 파일)을 위해, 모든
  에이전트가 `persistence.existingClaim` 필드를 사용하여 **같은 ReadWriteMany (RWX)
  PVC**를 마운트할 수 있습니다. 이렇게 하면 에이전트들이 공통 지식 베이스에 읽기/쓰기를
  할 수 있습니다. 완전한 예는
  [`values-shared-knowledge.yaml`](../charts/hermes-agent/values-shared-knowledge.yaml)을
  참조하세요. **주의:** PVC는 `ReadWriteMany` 액세스 모드를 지원하는 StorageClass를
  사용해야 합니다(예: NFS, CephFS, Longhorn); 대부분의 클라우드 제공자의 기본
  StorageClass는 `ReadWriteOnce`이므로 다중 작성자는 동작하지 않습니다.

> **솔직한 현황(업스트림).** 하나의 그룹 안에서 에이전트끼리 직접 인지하는 기능은
> Hermes 자체에서 아직 발전 중입니다(업스트림 이슈
> [#10965](https://github.com/NousResearch/hermes-agent/issues/10965),
> [#14853](https://github.com/NousResearch/hermes-agent/issues/14853) 참고). 현재
> 신뢰할 수 있는 팀 패턴은 **공유 채널에 사람 + 역할별 에이전트 한둘**을 두고 각
> 에이전트를 `@mention`으로 부르는 것입니다. 채널을 단일 진실 공급원으로 삼으세요;
> 더 풍부한 에이전트 간 컨텍스트 주입은 업스트림 로드맵에 있습니다.

## Discord로 Hermes 팀 만들기

하나의 Discord 채널에 두 에이전트로 구성한 구체적 예시입니다.

### 1. 에이전트마다 봇 1개, 공유 채널 1개

원하는 에이전트마다
[Discord Developer Portal](https://discord.com/developers/applications)에서 봇을
만들고 **Message Content Intent**를 켠 뒤, **모두**를 **같은 서버·같은 채널**에
초대하세요. 그 채널 ID를 메모해 두면 공유 `DISCORD_HOME_CHANNEL`이 되고, 팀원들의
Discord 사용자 ID를 모아 `DISCORD_ALLOWED_USERS`로 씁니다.

### 2. 봇마다 인스턴스 1개, 같은 채널로

각 에이전트를 **독립 릴리즈**로 배포하되, **각자의 `DISCORD_BOT_TOKEN`**을 쓰고
**`DISCORD_HOME_CHANNEL`과 `DISCORD_ALLOWED_USERS`는 동일하게** 둡니다. 순수 Helm으로는
두 설치를 나란히 실행합니다:

```bash
# 에이전트 A — "planner"
helm upgrade --install hermes-planner ./charts/hermes-agent \
  --namespace hermes-team --create-namespace \
  -f charts/hermes-agent/values-anthropic-and-discord.yaml \
  --set-string env.ANTHROPIC_API_KEY='sk-ant-...' \
  --set-string env.DISCORD_BOT_TOKEN='<planner-bot-token>' \
  --set-string extraEnv[0].name=DISCORD_HOME_CHANNEL \
  --set-string extraEnv[0].value='<shared-channel-id>' --wait

# 에이전트 B — "builder" (같은 채널, 다른 봇 토큰)
helm upgrade --install hermes-builder ./charts/hermes-agent \
  --namespace hermes-team --create-namespace \
  -f charts/hermes-agent/values-anthropic-and-discord.yaml \
  --set-string env.ANTHROPIC_API_KEY='sk-ant-...' \
  --set-string env.DISCORD_BOT_TOKEN='<builder-bot-token>' \
  --set-string extraEnv[0].name=DISCORD_HOME_CHANNEL \
  --set-string extraEnv[0].value='<shared-channel-id>' --wait
```

릴리즈 이름을 다르게(`hermes-planner`, `hermes-builder`) 두면 모든 리소스가 분리됩니다 —
각 에이전트가 자신의 파드·PVC·정체성을 가지므로, 채널만 공유할 뿐 진짜로 독립적인 단일
인스턴스들이 됩니다.

### 3. 또는 ArgoCD ApplicationSet으로 팀을 생성하기 (권장)

1~2단계는 멤버가 몇 명을 넘어가면 확장되지 않습니다 — 에이전트마다 Application/설치를
하나씩 두면, 명부가 바뀔 때마다 파일을 손으로 고쳐야 합니다.
[ApplicationSet](https://argo-cd.readthedocs.io/en/stable/operator-manual/applicationset/)은
명부를 **데이터**로, 에이전트당 Application을 **템플릿**으로 바꿉니다:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: hermes-team
  namespace: argocd
spec:
  generators:
    - list:
        elements:
          - name: planner
            botTokenSecret: hermes-planner-discord-secrets
          - name: builder
            botTokenSecret: hermes-builder-discord-secrets
          # 팀원 추가 = 리스트 항목 추가
  template:
    metadata:
      name: 'hermes-{{name}}'
    spec:
      project: default
      source:
        repoURL: ghcr.io/jyje/hermes-agent-helm
        chart: hermes-agent
        targetRevision: '*'   # 릴리즈된 차트 버전으로 고정
        helm:
          releaseName: 'hermes-{{name}}'
          valuesObject:
            env:
              ANTHROPIC_API_KEY: sk-ant-REPLACE_ME
            extraEnvFrom:
              - secretRef:
                  name: '{{botTokenSecret}}'   # 멤버별 시크릿, 별도 생성
            extraEnv:
              - name: DISCORD_HOME_CHANNEL     # 팀 전체 공유
                value: "<shared-channel-id>"
              - name: DISCORD_ALLOWED_USERS    # 팀 전체 공유
                value: "<comma-separated-ids>"
      destination:
        server: https://kubernetes.default.svc
        namespace: hermes-team
      syncPolicy:
        syncOptions:
          - CreateNamespace=true
```

이렇게 하면 [examples/argocd/](../examples/argocd/)와
["Multiple instances in the same namespace"](../examples/argocd/README.md#multiple-instances-in-the-same-namespace)
섹션의 `fullname` 유일성 규칙을 그대로 따르면서, 다음을 거의 공짜로 얻습니다:

- **명부가 한 곳**(`generators[0].list.elements`)**에 존재** — N개의 Application
  파일이 아니라. 팀원 추가는 한 줄짜리 diff입니다.
- **공유 필드**(`DISCORD_HOME_CHANNEL`, `DISCORD_ALLOWED_USERS`)는 `template`에
  한 번만 두고, **멤버별 필드**(이름, 시크릿 참조, 역할)는 리스트에서 옵니다 —
  차트 자체의 공유/인스턴스별 분리(`env`/`extraEnvFrom`은 릴리즈별, `extraEnv`는
  template으로 공유)와 같은 모양입니다.
- **멤버별 유일한 `fullname`**은 `releaseName`의 `{{name}}` 치환에서 자동으로
  나옵니다.

렌더링된 형태를 명시적으로 보고 싶다면(예: 리뷰용, 또는 ApplicationSet 없이),
[examples/argocd/](../examples/argocd/)에 제공자/예제별로 손으로 작성한 Application이
하나씩 있습니다 — 팀원마다 복사해서 쓸 수 있고, 위 ApplicationSet은 같은 모양을
생성하는 것뿐입니다.

### 4. (선택) 각 에이전트에 역할 부여

각 인스턴스는 자신의 `config`와 personality를 가지므로, 한 에이전트를 복제하기보다
상호 보완적인 역할(예: planner vs. builder)로 범위를 나누세요. 모두가 공유해야 할
팀 지식은 각 인스턴스의 `HERMES_HOME`에 심는 컨텍스트 파일(`SOUL.md` / `AGENTS.md`)에
둡니다.

> **다음 단계(탐색적).** 위 ApplicationSet은 팀의 릴리즈를 선언적으로
> **템플릿화**하는 부분을 커버하며, 이게 "팀"에 필요한 것의 대부분입니다.
> 전용 오퍼레이터(`Agent` / `AgentTeam` CRD, 별도 레포)는 이 템플릿 전용 모델이
> 실제로 부족해질 때만 가치가 있습니다 — 예를 들어:
>
> - **팀 전체 상태를 보여주는 단일 오브젝트**(`kubectl get agentteam my-team` →
>   "3/4 멤버 healthy")가 필요한데, ApplicationSet은 이를 집계해주지 않을 때;
> - **팀 단위 불변식의 admission-time 검증**(예: "모든 멤버는 동일한
>   `DISCORD_HOME_CHANNEL`을 공유해야 한다")이 필요한데, 템플릿으로는 강제할 수
>   없을 때;
> - **능동적 reconcile/상태 기계**(예: 멤버 장애 시 역할 재배정)가 필요한데,
>   템플릿이 표현할 수 있는 범위를 넘어설 때.
>
> 이 중 하나가 실제로, 관찰된 필요가 되기 전까지는 위 ApplicationSet 패턴이
> 권장 접근입니다. [로드맵](roadmap-ko.md)과
> [`charts/hermes-operator/`](../charts/hermes-operator/) 플레이스홀더를
> 참고하세요.

## 함께 보기

- [collaboration-ko.md](collaboration-ko.md) — 다음 단계: 묶인 에이전트들이
  `@mention`으로 핸드오프하고 무한루프를 멈추게 하기(봇 대 봇 레시피).
- [차트 README](../charts/hermes-agent/README.md) — 전체 값 테이블,
  `replicaCount` 단일 writer 근거, Discord/Telegram 환경변수.
- [로드맵](roadmap-ko.md) — ApplicationSet 기반 팀 패턴, 그리고
  `hermes-operator`(`Agent` / `AgentTeam` CRD)가 정당화되는 조건.
- [examples/argocd/](../examples/argocd/) — 에이전트당 Application 1개, 네임스페이스당
  다중 인스턴스, SealedSecret 시크릿 연결.
- Hermes 공식 문서:
  [Messaging gateway](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/)
  ·
  [Team Telegram Assistant](https://hermes-agent.nousresearch.com/docs/guides/team-telegram-assistant)
