<div align="center" markdown="1">

# jyje/hermes-agent-helm

<img height="240" src="https://raw.githubusercontent.com/jyje/hermes-agent-helm/main/docs/images/hermes-agent-helm.png" alt="Kubernetes × Hermes Agent"/>

👩🏻‍💻 Kubernetes에서 실행하는 Hermes Agent - Codex/Copilot 계정으로 로그인하고, 에이전트 팀을 운영하며, 가볍게 유지됩니다.

[![GitHub Repo stars](https://img.shields.io/github/stars/jyje/hermes-agent-helm?style=social)](https://github.com/jyje/hermes-agent-helm)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Helm](https://img.shields.io/badge/Helm-3%2B-0F1689?logo=helm&logoColor=white)](https://helm.sh)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?logo=kubernetes&logoColor=white)](https://kubernetes.io)
[![Artifact Hub](https://img.shields.io/endpoint?url=https://artifacthub.io/badge/repository/hermes-agent)](https://artifacthub.io/packages/search?repo=hermes-agent)

[English](README.md) · [한국어](README-ko.md) · **🚀 [Hermes 팀](docs/ko/advanced/teams/index.md)** · [Chart docs](charts/hermes-agent/README-ko.md) · [CONTRIBUTING](CONTRIBUTING.md) · [SECURITY](SECURITY-ko.md) · [AGENTS](AGENTS.md)

---

**이 프로젝트가 도움이 되셨나요? 별(⭐)을 눌러주세요 - 다른 분들이 찾는 데 도움이 됩니다.**

</div>

## 요약

![Flow of Hermes Agent](https://raw.githubusercontent.com/jyje/hermes-agent-helm/main/docs/images/hermes-agent-helm-flow.png)

[Hermes Agent](https://github.com/NousResearch/hermes-agent)를 Kubernetes에서
`helm install` 한 번으로 실행하세요 - Hermes가 지원하는 모든 LLM 제공자에서 동작하고,
단일 소형 노드로 확장되며, 실제로 동작하는지 검증된(단순 렌더만 아님) 차트입니다.
같은 클러스터 위에서 여러 인스턴스를 묶어 완전한 [**Hermes 팀**](docs/ko/advanced/teams/index.md)을
만드는 것도 그만큼 쉽습니다. **커뮤니티 기반** 차트이며, Nous Research 공식
릴리즈가 아닙니다.

## 빠른 시작

1. **OCI (권장)** — `helm repo add` 없이 레지스트리에서 바로 설치합니다:

    ```bash
    helm install hermes-agent oci://ghcr.io/jyje/hermes-agent-helm/hermes-agent \
      --namespace hermes-agent --create-namespace \
      --set-string env.OPENAI_API_KEY='sk-...' \
      --wait
    ```

2. **Helm Repository** - 한 번 추가해두고 이름으로 설치하는 방식을 원하면, GitHub Pages에 배포된 Helm 저장소도 있습니다:

    ```bash
    helm repo add hermes-agent https://jyje.github.io/hermes-agent-helm
    helm repo update
    helm install hermes-agent hermes-agent/hermes-agent \
      --namespace hermes-agent --create-namespace \
      --set-string env.OPENAI_API_KEY='sk-...' \
      --wait
    ```

필요하면 latest 대신 특정 [릴리즈된 차트 버전](https://github.com/jyje/hermes-agent-helm/releases)으로 `--version`을 고정할 수 있습니다.

이 리포지토리 소스에서 설치하려면(예: 미릴리즈 변경사항 시도),
아래 [개발](#개발)을 참고하세요.

## 이 차트의 장점

- **Hermes가 지원하는 모든 제공자를 `values.yaml`로.** `openai-api`, `anthropic`,
  `gemini`, `openrouter`, `nvidia`, `deepseek`, 또는
  [LiteLLM](https://github.com/BerriAI/litellm) 같은 OpenAI 호환 엔드포인트는
  이미 Hermes 자체가 환경변수로 지원하는 기능입니다 - 이 차트는 그 설정을
  `values.yaml`로 편하게 노출하고, 제공자별 즉시 사용 가능한 예제를 제공할 뿐,
  템플릿에 특정 제공자를 하드코딩하지 않습니다.
- **채팅 우선 gateway와 계정 로그인.** Discord 또는 Telegram 봇 토큰을 넣으면
  차트가 Kubernetes 수명주기 안에서 Hermes의 outbound gateway를 실행합니다.
  **GitHub Copilot**과 **OpenAI Codex**는 선택 가능한 device-login bootstrap이
  Discord 홈 채널(또는 로그)로 일회용 링크와 코드를 전달하고, 갱신 가능한
  자격증명을 `HERMES_HOME`에 보존합니다. 한 번 승인하면 일반적인 Pod 재시작에는
  저장된 로그인을 재사용합니다.
- **경량 → 프로덕션.** 기본값은 홈랩/싱글노드/엣지 클러스터용(단일 레플리카, 적당한
  요청, 작은 PVC)이면서, 스케일 아웃이 아니라 스케일 업으로 키워 프로덕션까지 갑니다. Hermes는
  단일 인스턴스 개인용 에이전트(하나의 `HERMES_HOME`·gateway·메모리)이므로 파드를
  복제하지 않고, 잘 관리된 인스턴스를 여러 개 띄워 공통 gateway 채널로 컨텍스트를
  공유하는 **팀**으로 묶습니다. [Hermes 팀](docs/ko/advanced/teams/reference.md)을 참고하세요.
- **엔드-투-엔드 검증.** CI가 임시 **kind** 클러스터에 차트를 설치하고
  번들된 테스트 Job(`hermes doctor`)을 실행합니다. `NVIDIA_API_KEY` 리포지토리
  시크릿이 있으면 NVIDIA NIM에 대한 **live `hermes chat` 라운드트립**도 실행합니다
  - 목(mock)이 아닙니다.
  Discord 스레드 리더 팀도 사람 → 리더 → 멤버 둘 → 리더 라이브 라운드트립을
  완주했습니다. Telegram 팀 오케스트레이션은 별도 실증 대상입니다.

<div align="center">
  <img src="https://raw.githubusercontent.com/jyje/hermes-agent-helm/main/docs/images/demos/team-k9s-pods.png" alt="kind 클러스터에서 k9s로 본, 리더 주도 Hermes 팀(august, may, march)"/>
  <p><em>배포 증거: 리더 <code>august</code>와 멤버
  <code>may</code>/<code>march</code>가 kind에서 독립 릴리스로 실행 중.
  이 스크린샷만으로 멀티턴 멘션 루프가 증명되지는 않습니다. 현재 상태는
  <a href="docs/ko/advanced/teams/reference.md">Hermes 팀</a> 참고.</em></p>
</div>

자세한 리소스 구조, 설정 모델, 제공자별 설치 예제(메신저 통합 포함)는
[charts/hermes-agent/README-ko.md](charts/hermes-agent/README-ko.md)를 참고하세요.

## 프로덕션 체크리스트

아래 항목은 기본값으로 켜져 있지 않습니다 - 기본값은 앞서 설명한 대로 경량을
유지합니다. 각 행은 필요할 때 직접 켜는 옵션이고, 무엇이 그 주장을 실제로
뒷받침하는지 함께 적어 두었습니다. `production-ready` 라벨을 그냥 믿는 대신
직접 판단할 수 있게 하기 위해서입니다.

| 관심사 | 방법 | 검증 근거 |
|---|---|---|
| Pod Security Standards | `-f values-hardened.yaml` | hardened kind 시나리오 (PSS `restricted`) |
| Egress 제어 | `networkPolicy.enabled=true` | CI의 렌더링된 정책 assertion |
| 커널 격리 | `runtimeClassName: gvisor` (또는 다른 샌드박스 런타임) | 클러스터에 따라 다름 - 문서화만 되어 있음 |
| 시크릿 관리 | [Bitwarden](charts/hermes-agent/values-bitwarden.yaml) 또는 [SealedSecret](examples/argocd/#sealedsecret-walkthrough-nvidia-nim--discord) 예제 | CI의 values 예제 스모크 테스트에서 렌더링 확인 |
| 업그레이드 안전성 | `bootstrap.overwrite=false`가 런타임 수정 내용을 보존 | 문서화된 동작 - 아직 CI로 검증되지 않음 ([#235](https://github.com/jyje/hermes-agent-helm/issues/235)) |

## 전체 설치

### OCI (권장)

```bash
# 설치 전에 차트를 렌더링해 템플릿을 확인합니다
helm template hermes-agent oci://ghcr.io/jyje/hermes-agent-helm/hermes-agent \
  --set-string env.OPENAI_API_KEY='sk-...'

# 제네릭 기본값으로 설치 (제공자 키 설정)
# 릴리즈 이름 == 차트 이름으로 리소스명이 깔끔함 (hermes-agent-hermes-agent-0 아니라 hermes-agent-0)
helm upgrade --install hermes-agent oci://ghcr.io/jyje/hermes-agent-helm/hermes-agent \
  --namespace hermes-agent --create-namespace \
  --set-string env.OPENAI_API_KEY='sk-...' --wait

# 설치 테스트 실행 (doctor 스타일 Job)
helm test hermes-agent -n hermes-agent
kubectl logs -n hermes-agent -l app.kubernetes.io/component=test --tail=-1
```

### Helm Repository

```bash
# Helm Repository를 추가하고 최신 차트 인덱스를 가져옵니다
helm repo add hermes-agent https://jyje.github.io/hermes-agent-helm
helm repo update

# 설치 전에 차트를 렌더링해 템플릿을 확인합니다
helm template hermes-agent hermes-agent/hermes-agent \
  --set-string env.OPENAI_API_KEY='sk-...'

# 제네릭 기본값으로 설치 (제공자 키 설정)
helm upgrade --install hermes-agent hermes-agent/hermes-agent \
  --namespace hermes-agent --create-namespace \
  --set-string env.OPENAI_API_KEY='sk-...' --wait

# 설치 테스트 실행 (doctor 스타일 Job)
helm test hermes-agent -n hermes-agent
kubectl logs -n hermes-agent -l app.kubernetes.io/component=test --tail=-1
```

전체 값 테이블, "More examples" 표(모든 지원 제공자 + Discord/Telegram + LiteLLM용
`values-*.yaml` - raw YAML을 복사해 `-f`로 넘기세요), 그리고
[ArgoCD 예제](examples/argocd/)는
[charts/hermes-agent/README-ko.md](charts/hermes-agent/README-ko.md)를 참고하세요.

## 자동화

이 저장소의 자동화 중 차트 사용자에게 직접 영향을 주는 세 가지입니다.

- **Upstream 추적.** 예약된 작업이 6시간마다 새 Hermes 이미지를 확인하고
  `appVersion` 업데이트 pull request를 엽니다. 스스로 릴리즈를 게시하지는
  않습니다. 이 업데이트도 다른 차트 변경과 동일한 리뷰 및 Changesets 경로를
  거칩니다.
- **서명된 릴리즈.** 게시 시 Helm Repository 인덱스와 함께 cosign으로 서명된
  OCI 아티팩트를 만듭니다.
- **릴리즈 이후 검증.** 릴리즈마다 CI가 게시된 아티팩트를 OCI에서 설치하고,
  서명을 확인한 뒤, 차트 자체 테스트 스위트를 그 아티팩트에 대해 실행합니다.

각 workflow와 트리거, 그리고 서로 어떻게 연결되는지는
[CI 가이드](docs/ko/contributing/ci.md)에 정리되어 있습니다.

## 개발

레포지토리를 클론하고, 게시된 레지스트리가 아니라 로컬 차트 경로(상대경로)로
설치해서 PR을 올리기 전에 변경사항을 확인하세요:

```bash
git clone https://github.com/jyje/hermes-agent-helm.git
cd hermes-agent-helm

# 렌더링 & 린트
make template
make lint

# 로컬 차트 소스로 설치
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  --set-string env.OPENAI_API_KEY='sk-...' --wait

# 설치 테스트 실행 (doctor 스타일 Job)
helm test hermes-agent -n hermes-agent
kubectl logs -n hermes-agent -l app.kubernetes.io/component=test --tail=-1

# 또는 준비된 예제로 바로 시작 (제공자, Discord/Telegram, LiteLLM 등)
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-anthropic-and-discord.yaml \
  --set-string env.ANTHROPIC_API_KEY='sk-ant-...' \
  --set-string env.DISCORD_BOT_TOKEN='...' --wait
```

브랜치 모델, 릴리즈 프로세스, 추가 로컬 체크(`make docs` / `make test`)는
[CONTRIBUTING.md](CONTRIBUTING.md)에 설명되어 있고,
차트 설계 원칙은 [AGENTS.md](AGENTS.md)를 참고하세요.

## 로드맵

이 차트는 **하나**의 에이전트를 잘 배포·관리하며, 오늘은 ArgoCD ApplicationSet
기반 팀으로 확장하고, CRD 기반 오퍼레이터는 일정 없는 장기 후보입니다. 자세한
내용은 [docs/ko/about/roadmap.md](docs/ko/about/roadmap.md)를 참고하세요.

## 기여하기

이슈, PR, 아이디어 모두 환영합니다 - [CONTRIBUTING.md](CONTRIBUTING.md)
(브랜치 모델, 로컬 체크, 릴리즈 플로우)부터 시작하세요. 머지된 모든 기여는
체인지로그와 릴리즈 노트에 크레딧됩니다.

기여하고 스타를 눌러주신 모든 분들께 감사드립니다 ⭐

<a href="https://github.com/jyje/hermes-agent-helm/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=jyje/hermes-agent-helm" alt="Contributors" />
</a>

---

> 배너 © [Nous Research](https://github.com/NousResearch/hermes-agent) (MIT).
