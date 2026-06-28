<div align="center">

# jyje/hermes-agent-helm

<p>
  <img height="96" src="https://helm.sh/img/boat.svg" alt="Helm"/>
  &nbsp;&nbsp;<sup><b> ➕ </b></sup>&nbsp;&nbsp;
  <img height="96" src="https://hermes-agent.nousresearch.com/docs/img/logo.png" alt="Hermes Agent"/>
</p>

👩🏻‍💻 A Helm chart to run **Hermes Agent** on Kubernetes, community-powered, lightweight

[![GitHub Repo stars](https://img.shields.io/github/stars/jyje/hermes-agent-helm?style=social)](https://github.com/jyje/hermes-agent-helm)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Helm](https://img.shields.io/badge/Helm-3%2B-0F1689?logo=helm&logoColor=white)](https://helm.sh)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?logo=kubernetes&logoColor=white)](https://kubernetes.io)
[![Artifact Hub](https://img.shields.io/endpoint?url=https://artifacthub.io/badge/repository/hermes-agent)](https://artifacthub.io/packages/search?repo=hermes-agent)

[English](README.md) · [한국어](README-ko.md) · [Chart docs](charts/hermes-agent/README-ko.md) · [팀](docs/teams-ko.md) · [협업 가이드](docs/collaboration-ko.md) · [CONTRIBUTING](CONTRIBUTING.md) · [AGENTS](AGENTS.md)

---

**이 프로젝트가 도움이 되셨나요? 별(⭐)을 눌러주세요 — 다른 분들이 찾는 데 도움이 됩니다.**

</div>

## TL;DR

| 할 수 있는 것 | 방법 |
|---|---|
| **단일 에이전트** — 어떤 LLM 제공자든, 하나의 Hermes 인스턴스 | `helm install` — [시작하기](#시작하기) 참고 |
| **에이전트 팀** — `@mention`으로 대화를 넘기는 다중 인스턴스 | 릴리즈 여러 개 배포 후 연결 — [팀 구성](docs/teams-ko.md) + [협업 가이드](docs/collaboration-ko.md) 참고 |

## 요약

[Hermes Agent](https://github.com/NousResearch/hermes-agent)를 Kubernetes에서
`helm install` 한 번으로 실행하세요 — Hermes가 지원하는 모든 LLM 제공자에서 동작하고,
단일 소형 노드로 확장되며, 실제로 동작하는지 검증된(단순 렌더만 아님)
**커뮤니티 기반** 차트입니다. Nous Research 공식 릴리즈가 아닙니다.

## 시작하기

Helm 레포지토리(GitHub Pages에 배포됨)를 추가하고 설치하세요:

```bash
helm repo add hermes-agent https://jyje.github.io/hermes-agent-helm
helm repo update
helm install hermes-agent hermes-agent/hermes-agent \
  --namespace hermes-agent --create-namespace \
  --set-string env.OPENAI_API_KEY='sk-...' \
  --wait
```

각 릴리즈는 OCI 아티팩트로도 배포되므로, `helm repo add` 없이
레지스트리에서 바로 설치할 수도 있습니다:

```bash
helm install hermes-agent oci://ghcr.io/jyje/hermes-agent-helm/hermes-agent \
  --namespace hermes-agent --create-namespace \
  --set-string env.OPENAI_API_KEY='sk-...' \
  --wait
```

필요하면 latest 대신 특정 [릴리즈된 차트 버전](https://github.com/jyje/hermes-agent-helm/releases)으로 `--version`을 고정할 수 있습니다.

이 리포지토리 소스에서 설치하려면(예: 미릴리즈 변경사항 시도),
아래 [빠른 시작](#빠른-시작)을 참고하세요.

## 이 차트의 장점

- **Hermes가 지원하는 모든 제공자를 `values.yaml`로.** `openai-api`, `anthropic`,
  `gemini`, `openrouter`, `nvidia`, `deepseek`, 또는
  [LiteLLM](https://github.com/BerriAI/litellm) 같은 OpenAI 호환 엔드포인트는
  이미 Hermes 자체가 환경변수로 지원하는 기능입니다 — 이 차트는 그 설정을
  `values.yaml`로 편하게 노출하고, 제공자별 즉시 사용 가능한 예제를 제공할 뿐,
  템플릿에 특정 제공자를 하드코딩하지 않습니다.
- **경량 → 프로덕션.** 기본값은 홈랩/싱글노드/엣지 클러스터용(단일 레플리카, 적당한
  요청, 작은 PVC)이면서, 스케일 아웃이 아니라 스케일 업으로 키워 프로덕션까지 갑니다. Hermes는
  단일 인스턴스 개인용 에이전트(하나의 `HERMES_HOME`·gateway·메모리)이므로 파드를
  복제하지 않고, 잘 관리된 인스턴스를 여러 개 띄워 공통 gateway 채널로 컨텍스트를
  공유하는 **팀**으로 묶습니다. [Hermes 팀](docs/teams-ko.md)을 참고하세요.
- **엔드-투-엔드 검증.** CI가 임시 **kind** 클러스터에 차트를 설치하고
  번들된 테스트 Job(`hermes doctor`)과 실제 NVIDIA NIM 계정에 대한
  **live `hermes chat` 라운드트립**을 실행 — 목(mock)이 아님.
  🔜 Telegram/Discord 라운드트립 검증은 아직 준비 중.

자세한 리소스 구조, 설정 모델, 제공자별 설치 예제(메신저 통합 포함)는
[charts/hermes-agent/README-ko.md](charts/hermes-agent/README-ko.md)를 참고하세요.

## 리포지토리 구조

```
charts/hermes-agent/                     # Helm 차트 (전체 값 테이블은 README 참고)
charts/hermes-agent/values-*.yaml        # 즉시 사용 가능한 예제: 제공자별, Discord/Telegram, LiteLLM (차트 README "More examples" 참고)
examples/helm/                           # Git 및 OCI(ghcr.io)에서 설치 + 배포 가이드
examples/argocd/                         # ArgoCD Application 예제 (values-*.yaml별 1개) + GitOps/SealedSecret 패턴
charts/hermes-operator/                  # ⏸️ 장기·미착수: Agent/AgentTeam CRD 오퍼레이터의 가능한 설치용 차트 — 플레이스홀더, TBA (로드맵 참고)
docs/                                    # 심화 가이드: teams-ko.md (인스턴스를 팀으로 묶기), collaboration-ko.md (@mention으로 핸드오프시키기), roadmap-ko.md
.github/workflows/                       # ci (lint + docs-drift + kind에서 실제 라운드트립) 및 release (버전 범프 -> 태그 -> ghcr OCI)
CONTRIBUTING.md                          # 브랜치 모델 (dev/main + tags) + 버전 범프 기반 릴리즈
AGENTS.md                                # 기여자용 설계 원칙 & 워크플로우
Makefile                                 # docs / lint / template / install / test / package / push
```

## 빠른 시작

```bash
# 렌더링 & 린트
make template
make lint

# 제네릭 기본값으로 설치 (제공자 키 설정)
# 릴리즈 이름 == 차트 이름으로 리소스명이 깔끔함 (hermes-agent-hermes-agent-0 아니라 hermes-agent-0)
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

전체 값 테이블, "More examples" 표(모든 지원 제공자 + Discord/Telegram + LiteLLM용
`values-*.yaml`), 그리고 [ArgoCD 예제](examples/argocd/)는
[charts/hermes-agent/README-ko.md](charts/hermes-agent/README-ko.md)를 참고하세요.

## 개발

브랜치 모델, 릴리즈 프로세스, 로컬 체크(`make lint` / `make docs` / `make test`)는
[CONTRIBUTING.md](CONTRIBUTING.md)에 설명되어 있고,
차트 설계 원칙은 [AGENTS.md](AGENTS.md)를 참고하세요.

## CI/CD

- **모든 PR과 `dev`/`main`로의 push**는 [validate-chart.yaml](.github/workflows/validate-chart.yaml)을 실행합니다:
  `helm lint`, `helm template`, 차트-docs 드리프트 체크, 그리고 임시 **kind** 클러스터에서의
  완전한 설치 + 테스트 (NVIDIA_API_KEY 시크릿이 있을 때는 실제 `hermes chat` 라운드트립).
- **릴리즈는 버전 범프 기반**이며, 태그 푸시 기반이 아닙니다. [propose-release.yaml](.github/workflows/propose-release.yaml)을 실행합니다
  (Actions → "📋 propose-release"): main과 마지막 릴리즈 태그를 비교해서
  체인지로그를 **결정적으로** 생성하고(git-cliff), **NVIDIA NIM**에게 semver 범프 추천을 요청하고
  (키 없으면 transparent한 휴리스틱으로 폴백), 모든 커밋과 PR 작성자를 크레딧한 단일
  **릴리즈 PR**을 생성/업데이트합니다. 버전이 마음에 안 들면 조정한 후 머지하세요.
  (또는 제안을 건너뛰고 `Chart.yaml`을 직접 범프하거나 `/version vX.Y.Z`를 코멘트하세요.)
  PR이 `main`으로 머지되면 [release-chart.yaml](.github/workflows/release-chart.yaml)이
  `vX.Y.Z` 태그를 생성하고, GitHub Release를 작성하고, 차트를 `oci://ghcr.io/<owner>/hermes-agent-helm/hermes-agent`에 배포합니다.

즉: lint + test가 모든 변경사항을 게이트합니다; *릴리즈* 자체는 단순한
리뷰된 PR (버전 범프) — AI는 조언만 하고, 머지가 배포합니다.
전체 릴리즈 플레이북은 [CONTRIBUTING.md](CONTRIBUTING.md)를 참고하세요.

## 로드맵

이 차트는 **하나**의 에이전트를 잘 배포·관리하며, 오늘은 ArgoCD ApplicationSet
기반 팀으로 확장하고, CRD 기반 오퍼레이터는 일정 없는 장기 후보입니다. 자세한
내용은 [docs/roadmap-ko.md](docs/roadmap-ko.md)를 참고하세요.

---

> 배너 © [Nous Research](https://github.com/NousResearch/hermes-agent) (MIT).
