# ArgoCD로 배포하기

이 Application 매니페스트들은 `hermes-agent`를 ArgoCD로 안전하게 배포하며,
**같은 네임스페이스에 여러 인스턴스를 충돌 없이** 둘 수도 있습니다.

각 파일은 대응하는
[`charts/hermes-agent/values-*.yaml`](../../charts/hermes-agent/README-ko.md#more-examples)
예제를 1:1로 그대로 옮긴 것이며, 시크릿은 단순 `--set` 대신 `extraEnvFrom`으로
연결합니다:

| Application 파일 | 대응하는 예제 | 필요한 Secret |
| --- | --- | --- |
| [`hermes-agent.yaml`](hermes-agent.yaml) | 차트 기본값(`values.yaml`) | `hermes-agent-secrets` (`OPENAI_API_KEY`) |
| [`hermes-agent-openai.yaml`](hermes-agent-openai.yaml) | `values-openai.yaml` | `hermes-agent-openai-secrets` (`OPENAI_API_KEY`) |
| [`hermes-agent-openai-sealedsecret.yaml`](hermes-agent-openai-sealedsecret.yaml) | `values-openai.yaml` + GitOps | **SealedSecret**을 통한 `hermes-agent-openai-sealedsecret-secrets` (`extraResources`) |
| [`hermes-agent-anthropic.yaml`](hermes-agent-anthropic.yaml) | `values-anthropic.yaml` | `hermes-agent-anthropic-secrets` (`ANTHROPIC_API_KEY`) |
| [`hermes-agent-gemini.yaml`](hermes-agent-gemini.yaml) | `values-gemini.yaml` | `hermes-agent-gemini-secrets` (`GOOGLE_API_KEY`) |
| [`hermes-agent-upstage.yaml`](hermes-agent-upstage.yaml) | `values-upstage.yaml`(모델을 **Solar Open 2**로 재정의) | `hermes-agent-upstage-secrets` (`UPSTAGE_API_KEY`) |
| [`hermes-agent-openrouter.yaml`](hermes-agent-openrouter.yaml) | `values-openrouter.yaml` | `hermes-agent-openrouter-secrets` (`OPENROUTER_API_KEY`) |
| [`hermes-agent-litellm.yaml`](hermes-agent-litellm.yaml) | `values-litellm.yaml` | `hermes-agent-litellm-secrets` (`OPENAI_API_KEY`, 프록시 키) |
| [`hermes-agent-litellm-k8s.yaml`](hermes-agent-litellm-k8s.yaml) | `values-litellm-k8s.yaml` | **SealedSecret**을 통한 `hermes-agent-litellm-k8s-secrets` (`extraResources`) |
| [`hermes-agent-anthropic-and-discord.yaml`](hermes-agent-anthropic-and-discord.yaml) | `values-anthropic-and-discord.yaml` | `hermes-agent-anthropic-discord-secrets` (`ANTHROPIC_API_KEY`, `DISCORD_BOT_TOKEN`) |
| [`hermes-agent-openai-and-telegram.yaml`](hermes-agent-openai-and-telegram.yaml) | `values-openai-and-telegram.yaml` | `hermes-agent-openai-telegram-secrets` (`OPENAI_API_KEY`, `TELEGRAM_BOT_TOKEN`) |
| [`hermes-agent-nvidia-nim-and-discord.yaml`](hermes-agent-nvidia-nim-and-discord.yaml) | `values-nvidia-nim-and-discord.yaml` | `hermes-agent-nim-discord-secrets` (`NVIDIA_API_KEY`, `DISCORD_BOT_TOKEN`) |
| [`hermes-agent-nvidia-nim-and-discord-sealedsecret.yaml`](hermes-agent-nvidia-nim-and-discord-sealedsecret.yaml) | `values-nvidia-nim-and-discord.yaml` + GitOps | **SealedSecret**을 통한 `hermes-agent-nim-discord-sealedsecret-secrets` (`extraResources`, `NVIDIA_API_KEY` + `DISCORD_BOT_TOKEN`) |
| [`hermes-agent-github-copilot.yaml`](hermes-agent-github-copilot.yaml) | `values-github-copilot.yaml` + GitOps | **SealedSecret**을 통한 `hermes-agent-copilot-secrets`(`DISCORD_BOT_TOKEN`만: Copilot 토큰은 **OAuth 기기 흐름**으로 런타임에 발급) |
| [`hermes-agent-ingress.yaml`](hermes-agent-ingress.yaml) | `values-ingress.yaml` | `hermes-agent-ingress-secrets` (`OPENAI_API_KEY`) + `hermes-agent-dashboard-auth`(nginx basic-auth) |
| [`hermes-collab-pair.yaml`](hermes-collab-pair.yaml) | `values-multi-agent-collab.yaml`(×2: planner+builder) | `hermes-planner-discord-secrets` + `hermes-builder-discord-secrets`: `@멘션`으로 핸드오프하는 **협업 페어**. [docs/reference/collaboration.md](../../docs/ko/reference/collaboration.md) 참고 |
| [`hermes-team.yaml`](hermes-team.yaml) | `values-team-leader.yaml` + `values-team-member.yaml` | `hermes-august-discord-secrets` + `hermes-may-discord-secrets` + `hermes-march-discord-secrets` + 미리 준비된 `hermes-team-knowledge` RWX PVC: **리더 주도 팀**(직렬화된 명시적 멘션, 리더 쓰기/멤버 읽기 전용 공유 지식, 파일 기반 작업 핸드오프 없음). [docs/reference/teams.md](../../docs/ko/reference/teams.md) 참고 |

`hermes-agent.yaml`은 최소한의 시작점입니다 - 순수 차트 기본값과 시크릿
연결뿐입니다. 이걸 복사하고 `valuesObject`를 추가해 커스터마이즈하세요.

`hermes-collab-pair.yaml`은 첫 번째 다중 Application 예제입니다: **두**
에이전트(LiteLLM 위의 `planner`와 Copilot 기기 흐름 위의 `builder`)가 하나의
Discord 채널을 공유하며 `@멘션`으로 핸드오프합니다. 핸드오프 프로토콜과 4개의
루프 브레이크 환경 변수는
[docs/reference/collaboration.md](../../docs/ko/reference/collaboration.md)를
참고하세요.

`hermes-team.yaml`은 그 패턴을 확장합니다: 팀 **리더**(`august`)용
Application 하나와, 멤버 명부(`may`, `march`)가 list-generator 항목인
**ApplicationSet** 하나로 구성됩니다 - 팀원 추가는 한 줄짜리 diff입니다.
에이전트들은 하나의 Discord 채널을 공유합니다(스타 토폴로지: 멘션은 리더 ↔
멤버 사이로만 흐릅니다). 스레드가 조정 버스이자 감사 로그입니다. 별도의 RWX
PVC가 지속적인 재사용 지식을 저장하지만(리더 읽기/쓰기, 멤버 읽기 전용), 작업,
상태, 중간 결과, 완료 신호는 절대 담지 않습니다.
[docs/reference/teams.md](../../docs/ko/reference/teams.md) → "리더 주도 팀"
참고.

모든 예제는 **OCI 레지스트리** 소스 형식(`ghcr.io`를 가리키는
`repoURL`/`chart`/`targetRevision`)을 씁니다. Git 저장소에 커밋된 차트를
추적하고 싶다면 Git 소스 형식(`repoURL`/`targetRevision`/`path`)도 동작합니다
- 둘을 자유롭게 바꿔 쓰세요.

`hermes-agent-litellm-k8s.yaml`이 가장 완전한 예제입니다: 전체 GitOps
패턴(`extraResources`를 통한 SealedSecret + `extraEnvFrom` + 기본값이 아닌
`persistence.storageClass`)을 보여줍니다. 나머지는 out-of-band로 생성한
평범한 Secret을 씁니다(정확한 `kubectl create secret` 명령은 각 파일의 헤더
주석 참고).

모든 Application은 `destination.namespace: hermes-agent`를 대상으로 하며
서로 다른 `releaseName`을 사용합니다 - 같은 네임스페이스에 함께 적용해도
충돌하지 않습니다(아래 참고).

## 유일한 규칙: 인스턴스마다 고유한 `fullname`

모든 차트 리소스는 Helm **fullname**(`{fullname}`, `{fullname}-0`,
`{fullname}-config`, `{fullname}-env`, `{fullname}-headless`,
`{fullname}-test`, `data-{fullname}-0`)으로 이름 지어집니다. 두 Application이
**같은 네임스페이스**에서 **같은 fullname**을 렌더링할 때만 충돌합니다.

그러니 각 Application에 서로 다른 `spec.source.helm.releaseName`을 주고:

> **`metadata.name` == `spec.source.helm.releaseName`으로 설정하세요.**

이렇게 하면 두 가지가 해결됩니다:
1. 인스턴스마다 fullname이 고유해집니다(이름 충돌 없음).
2. 차트의 `app.kubernetes.io/instance` 값이 Application과 같아집니다:
   직관적이고 일관됩니다.

## 여기서 추적 레이블이 충돌하지 않는 이유

ArgoCD는 `application.instanceLabelKey`로 설정된 키를 가진 레이블로 소유권을
추적합니다. 이 클러스터는 **`argocd.argoproj.io/instance`**(ArgoCD 전용
키)를 쓰는 반면, 차트는 자체 셀렉터에 **`app.kubernetes.io/instance`**를
씁니다. 키가 다르므로 → 기본 `label` 추적 방식이어도 **충돌하지
않습니다**. (만약 클러스터가 추적에 `app.kubernetes.io/instance`를 쓴다면,
`argocd-cm`에서 `application.resourceTrackingMethod: annotation`으로 바꿔
annotation 추적으로 전환하세요.)

## Secret(키를 커밋하지 마세요)

차트의 `env.<KEY>` 값은 플레이스홀더로 두고, 실제 키는 out-of-band로 생성한
Secret에서(또는 sealed-secrets / external-secrets를 통해) 주입하세요. 각
Application의 헤더 주석에 정확한 명령이 있습니다. 예:

```bash
kubectl create namespace hermes-agent
kubectl create secret generic hermes-agent-openai-secrets -n hermes-agent \
  --from-literal=OPENAI_API_KEY='sk-<your-key>'
```

`extraEnvFrom`이 그 Secret을 참조합니다. 차트 자체의 env Secret보다 나중에
적용되므로 이 값들이 우선합니다.

### SealedSecret 따라 하기(NVIDIA NIM + Discord)

[`hermes-agent-nvidia-nim-and-discord-sealedsecret.yaml`](hermes-agent-nvidia-nim-and-discord-sealedsecret.yaml)은
[`hermes-agent-nvidia-nim-and-discord.yaml`](hermes-agent-nvidia-nim-and-discord.yaml)의
GitOps 버전입니다: out-of-band로 평범한 Secret을 만드는 대신,
[bitnami **SealedSecret**](https://github.com/bitnami-labs/sealed-secrets)을
`extraResources`에 싣습니다. sealed-secrets 컨트롤러가 클러스터 안에서 이를
복호화해 일반 Secret(`hermes-agent-nim-discord-sealedsecret-secrets`)으로
만들고, `extraEnvFrom`이 이를 마운트합니다. 암호화된 blob은 Git에 커밋해도
안전합니다 - 컨트롤러의 개인 키(여러분의 클러스터가 보유)만 복호화할 수
있습니다.

이 가이드는 키 **두 개**(`NVIDIA_API_KEY`와 `DISCORD_BOT_TOKEN`)를 한 번에
봉인합니다. 키 하나만 봉인하는 더 간단한 `kubeseal --raw --from-file`
방식은 [`hermes-agent-openai-sealedsecret.yaml`](hermes-agent-openai-sealedsecret.yaml)을
참고하세요.

**사전 준비:**
- 대상 클러스터에
  [sealed-secrets 컨트롤러](https://github.com/bitnami-labs/sealed-secrets)가
  설치되어 있어야 합니다(예: `helm install sealed-secrets
  sealed-secrets/sealed-secrets -n kube-system`).
- 로컬에 `kubeseal` CLI가 설치되어 있고, 컨트롤러의 공개 인증서와 일치하거나
  가져올 수 있어야 합니다.

**1. 평문 Secret 매니페스트를 작성하되, 적용하지는 마세요:**

```bash
cat > /tmp/hermes-agent-nim-discord-secret.yaml <<'EOF'
apiVersion: v1
kind: Secret
metadata:
  name: hermes-agent-nim-discord-sealedsecret-secrets
  namespace: hermes-agent
type: Opaque
stringData:
  NVIDIA_API_KEY: "nvapi-<your-real-key>"
  DISCORD_BOT_TOKEN: "<your-real-bot-token>"
EOF
```

**2. 봉인합니다.** `kubeseal -o yaml`은 Secret 매니페스트를 읽어 그에
상응하는 SealedSecret을 출력하며, `data`/`stringData`의 모든 항목을
컨트롤러의 공개 키로 암호화합니다(클러스터에서 자동으로 가져오거나,
오프라인 인증서라면 `--cert <pub-cert.pem>`을 넘기세요):

```bash
kubeseal --scope namespace-wide \
  -o yaml < /tmp/hermes-agent-nim-discord-secret.yaml \
  > /tmp/hermes-agent-nim-discord-sealedsecret.yaml
```

이렇게 하면 `spec.encryptedData.NVIDIA_API_KEY`와
`spec.encryptedData.DISCORD_BOT_TOKEN`을 가진 `SealedSecret`이 만들어지며,
각각 긴 `AgB...` / `AgD...` base64 blob입니다. `--scope namespace-wide`는
재봉인 없이 `hermes-agent` 안에서 SealedSecret의 이름을 바꾸거나 옮길 수
있게 해줍니다 - 이 디렉터리의 다른 SealedSecret 예제들과 같은 관례입니다.

**3. `encryptedData` 값 두 개를**
`hermes-agent-nvidia-nim-and-discord-sealedsecret.yaml`의
`extraResources[0].spec.encryptedData`에 끼워 넣어,
`AgDUMMY_replace_with_kubeseal_output==` 플레이스홀더를 교체하세요:

```yaml
extraResources:
  - apiVersion: bitnami.com/v1alpha1
    kind: SealedSecret
    metadata:
      name: hermes-agent-nim-discord-sealedsecret-secrets
    spec:
      encryptedData:
        NVIDIA_API_KEY: AgB...      # <- 2단계에서
        DISCORD_BOT_TOKEN: AgD...   # <- 2단계에서
      template:
        metadata:
          name: hermes-agent-nim-discord-sealedsecret-secrets
        type: Opaque
```

`extraEnv[].value`(`DISCORD_HOME_CHANNEL`, `DISCORD_ALLOWED_USERS`)에도
실제 값을 채우고, 여러분의 계정으로 접근 가능한 NVIDIA NIM 모델을
고르세요.

**4. Application을 적용하고 확인합니다:**

```bash
kubectl apply -f examples/argocd/hermes-agent-nvidia-nim-and-discord-sealedsecret.yaml

# 컨트롤러가 SealedSecret을 복호화해 Secret으로 만들어야 합니다:
kubectl get sealedsecret,secret -n hermes-agent hermes-agent-nim-discord-sealedsecret-secrets

# 그리고 파드는 extraEnvFrom을 통해 두 키를 모두 받아야 합니다
# (fullnameOverride: hermes-agent가 리소스 이름을 짧게 유지합니다.
# 파일의 valuesObject 참고):
kubectl exec -n hermes-agent deploy/hermes-agent -- \
  env | grep -E '^(NVIDIA_API_KEY|DISCORD_BOT_TOKEN)='
```

`kubectl get secret`에 아무 Secret도 보이지 않으면 컨트롤러 로그를
확인하세요(`kubectl logs -n kube-system -l app.kubernetes.io/name=sealed-secrets`)
- 가장 흔한 원인은 잘못된 클러스터의 인증서로 봉인한 경우입니다.

## 적용

```bash
kubectl apply -f examples/argocd/hermes-agent-openai.yaml
```

(위 표의 다른 파일로 바꿔 쓰세요.)

## 같은 네임스페이스에 여러 인스턴스 두기

이름 == releaseName만 다르게 해서 Application을 복제하면 됩니다. 첫
인스턴스와 나란히, 둘 다 `hermes-agent`에 두는 두 번째 인스턴스 예:

```yaml
metadata:
  name: hermes-agent-staging      # 다른 이름
spec:
  source:
    helm:
      releaseName: hermes-agent-staging   # == metadata.name
  destination:
    namespace: hermes-agent       # 같은 네임스페이스도 괜찮음
```

리소스는 `hermes-agent-staging-*`로 렌더링되어(파드
`hermes-agent-staging-0`, `hermes-agent-staging-config`,
`data-hermes-agent-staging-0` 등) `hermes-agent-*` 집합과 겹치지 않습니다.
각각 자기 PVC를 갖기 때문에, 두 인스턴스는 지식 베이스를 공유하지
**않습니다**.
