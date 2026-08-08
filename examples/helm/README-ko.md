# Helm으로 설치하기

`hermes-agent`를 설치하는 두 가지 방법: **Git에서**(이 저장소) 그리고 **OCI
레지스트리에서**(GitHub Packages / `ghcr.io`, Artifact Hub가 인덱싱하는 형식).

어느 쪽이든 API 키는 매니페스트 밖에 두세요 - 설치 시점에 넘기거나, 미리 만든
Secret에서 주입하세요("Secret" 참고).

---

## 1. Git에서(로컬 체크아웃)

이 저장소의 클론에서 차트를 직접 씁니다. 개발할 때, 그리고 게시 전에 변경을
시도해볼 때 가장 좋습니다.

```bash
git clone https://github.com/jyje/hermes-agent-helm
cd hermes-agent-helm

# 제네릭 기본값(실제 OpenAI)
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  --set-string env.OPENAI_API_KEY='sk-...' --wait

# 환경별 설정(준비된 예제를 고르세요, 예: LiteLLM, Anthropic+Discord 등)
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-litellm-k8s.yaml \
  --set-string env.OPENAI_API_KEY='sk-<your-key>' --wait

helm test hermes-agent -n hermes-agent
```

> `values-*.yaml` 예제(제공자, Discord/Telegram, LiteLLM)의 전체 표는
> [`charts/hermes-agent/README.md`](../../charts/hermes-agent/README-ko.md#more-examples)를
> 참고하세요.

> 릴리즈 이름 `hermes-agent`(== 차트 이름)로 리소스가 깔끔해집니다
> (`hermes-agent-hermes-agent-0`가 아니라 `hermes-agent-0`).

---

## 2. OCI 레지스트리에서(GitHub Packages, `ghcr.io`)

차트가 게시된 뒤에는("배포" 참고) 클론이 필요 없습니다. Artifact Hub가
목록에 올리는 형식입니다.

```bash
# 공개 차트: pull에 로그인 불필요
helm upgrade --install hermes-agent \
  oci://ghcr.io/jyje/hermes-agent-helm/hermes-agent --version 1.2.0 \
  --namespace hermes-agent --create-namespace \
  --set-string env.OPENAI_API_KEY='sk-...' --wait

# 환경별 values 파일과 함께(다운로드하거나 직접 보유)
helm upgrade --install hermes-agent \
  oci://ghcr.io/jyje/hermes-agent-helm/hermes-agent --version 1.2.0 \
  --namespace hermes-agent --create-namespace \
  -f my-values.yaml --set-string env.OPENAI_API_KEY='sk-...' --wait
```

설치 전에 살펴보기:

```bash
helm show values oci://ghcr.io/jyje/hermes-agent-helm/hermes-agent --version 1.2.0
helm show readme oci://ghcr.io/jyje/hermes-agent-helm/hermes-agent --version 1.2.0
```

패키지가 비공개라면 먼저 로그인하세요:

```bash
echo "$GITHUB_TOKEN" | helm registry login ghcr.io -u jyje --password-stdin
```

---

## 차트 이름이 바뀌는 업그레이드

릴리즈가 설치된 차트를 바꾸는 경우(예: fork나 이름이 바뀐 로컬 복사본에서
이 차트로 옮길 때), 단순 `helm upgrade`는 실패하거나 더 나쁘게는 기존 것
옆에 **비어 있는 StatefulSet + PVC**를 새로 만들 수 있습니다. 두 가지가
차트 이름(`Chart.Name`)에서 파생되기 때문입니다:

1. **`fullname`**: 릴리즈 이름에 새 차트 이름이 이미 포함되어 있지 않으면,
   Helm은 기존 `<release>` 이름을 재사용하는 대신 `<release>-<chart>`(예:
   `myrelease-hermes-agent`)를 계산합니다 - 그래서 기존 리소스를 업그레이드
   하는 대신 (비어 있는 새 PVC를 포함한) 완전히 새로운 리소스를 만듭니다.
2. **`volumeClaimTemplates[].metadata.labels["helm.sh/chart"]`**: 이 레이블은
   차트 이름+버전을 담고 있고 StatefulSet의 **불변** `volumeClaimTemplates`의
   일부라서, 차트 이름이 바뀌는 순간 Kubernetes가 업그레이드 자체를
   거부합니다.

원래 이름을 고정하고 StatefulSet을 (삭제가 아니라) 다시 만들어 두 문제를
고치세요:

```bash
# 1) fullname/selector를 고정(YOUR 기존 릴리즈 이름으로 바꾸세요)
RELEASE=hermes-agent
NS=hermes-agent

# 2) StatefulSet 객체만 제거: Pod와 PVC(그리고 데이터)는 유지됨
kubectl delete sts "$RELEASE" -n "$NS" --cascade=orphan

# 3) 새 차트로 업그레이드하되, nameOverride를 기존 이름으로 고정
helm upgrade --install "$RELEASE" ./charts/hermes-agent -n "$NS" \
  -f charts/hermes-agent/values-litellm-k8s.yaml \
  --set nameOverride="$RELEASE" \
  --set-string env.OPENAI_API_KEY='sk-<your-key>'

# 4) Pod가 한 번 재시작합니다(새 차트의 StatefulSet이 기존 PVC를 인수함). 확인:
kubectl rollout status statefulset/"$RELEASE" -n "$NS"
helm test "$RELEASE" -n "$NS"
```

> 기존 릴리즈 이름/리소스를 보존할 필요가 없다면, `nameOverride`를 생략하고
> 그냥 `helm uninstall` 뒤 새 차트로 새로 설치하세요.

---

## Secret(두 방법 모두 공통)

키를 커밋되는 values 파일에 굽지 마세요. 설치 시점에 `--set-string`으로
넘기거나, Secret을 미리 만들어 `extraEnvFrom`으로 참조하세요(나중에 적용된
envFrom이 차트의 플레이스홀더보다 우선합니다):

```bash
kubectl create namespace hermes-agent
kubectl create secret generic hermes-agent-provider-key -n hermes-agent \
  --from-literal=OPENAI_API_KEY='sk-<your-key>'

helm upgrade --install hermes-agent oci://ghcr.io/jyje/hermes-agent-helm/hermes-agent \
  --version 1.2.0 -n hermes-agent --create-namespace \
  --set 'extraEnvFrom[0].secretRef.name=hermes-agent-provider-key'
```

---

## Artifact Hub를 위해 GitHub Packages(OCI)에 배포하기

> **`.tgz` 생명주기는 CI가 관리합니다.** `main`에서 `Chart.yaml`의
> `version`을 올리면 `.github/workflows/release-chart.yaml`이 트리거되어
> `vX.Y.Z` 태그를 만들고, 릴리즈 노트(Changesets)를 쓰고,
> `oci://ghcr.io/<owner>/hermes-agent-helm`에 푸시합니다 - 패키지는 절대
> 커밋되지 않습니다. 아래 명령들은 그와 동등한 수동/로컬 플로우입니다.

```bash
# 1) 패키징(Makefile 타겟을 통해 docs + lint도 함께 실행)
make package                      # -> dist/hermes-agent-1.2.0.tgz

# 2) ghcr에 로그인(PAT에는 write:packages 필요)
echo "$GITHUB_TOKEN" | helm registry login ghcr.io -u jyje --password-stdin

# 3) OCI 아티팩트로 푸시
helm push dist/hermes-agent-1.2.0.tgz oci://ghcr.io/jyje/hermes-agent-helm
#   -> ghcr.io/jyje/hermes-agent-helm/hermes-agent:1.2.0

# (Makefile 단축 명령)
make push
```

그다음 `ghcr.io` 패키지를 **공개**로 전환하세요(GitHub → Packages → 패키지
설정) - Artifact Hub와 사용자들이 익명으로 pull할 수 있도록.

### Artifact Hub에 등록하기

1. artifacthub.io → Control Panel → Add → **Helm charts** 저장소.
2. URL: `oci://ghcr.io/jyje/hermes-agent-helm/hermes-agent`
3. (권장) 소유권 확인: [`artifacthub-repo.yml`](../../artifacthub-repo.yml)
   (저장소 루트)을 같은 OCI 경로로 푸시하면 Artifact Hub가 저장소 소유를
   확인할 수 있습니다. `Chart.yaml`에 이미 있는 `artifacthub.io/*`
   어노테이션이 목록을 채웁니다.

> 차트 버전 vs 앱 버전: 차트가 바뀌면 `Chart.yaml`의 `version`을 올리고,
> `appVersion`은 Hermes 이미지 태그(날짜 기반, 예: `v2026.6.5`)를 따라갑니다.
