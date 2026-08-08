---
title: CI 가이드
description: 지속적인 검증과 릴리즈 체크입니다.
---

# CI / 지속적 검증

이 저장소에는 세 개의 GitHub Actions workflow가 있어, PR부터 서명된
게시 아티팩트까지 변경사항을 함께 검증합니다.

| Workflow | 트리거 | 역할 |
|---|---|---|
| [validate-chart.yaml](../../../.github/workflows/validate-chart.yaml) | `charts/hermes-agent/**`를 건드리는 PR과 `dev`/`main`로의 push | 무엇이든 머지되기 전에 lint + 격리된 **kind** 설치/테스트 |
| [release-chart.yaml](../../../.github/workflows/release-chart.yaml) | `charts/hermes-agent/Chart.yaml`을 바꾸는 `main`로의 push | `vX.Y.Z` 태그를 만들고, OCI 아티팩트 + Helm 저장소를 배포하고, cosign으로 서명. [CONTRIBUTING.md](../../../CONTRIBUTING.md#how-to-cut-a-release) 참고 |
| [verify-release.yaml](../../../.github/workflows/verify-release.yaml) | `release-chart` 성공 이후 | **게시되어 서명된** 아티팩트를 처음부터 끝까지 다시 검증 |

## validate-chart

기능적 변경마다 job 두 개가 실행됩니다:

### `lint`

`helm lint`, `helm template`, 그리고 **helm-docs 드리프트 체크** - `charts/hermes-agent/README.md`가
`README.md.gotmpl` 대비 오래됐으면 job이 실패합니다. `values.yaml`을 수정한
뒤에는 항상 `make docs`를 실행하고 결과를 커밋하세요.

### `test`

시나리오 두 개가 **매트릭스**로 실행되며, 각각 **독립된 임시 kind
클러스터**(별도 러너)에서 돕니다 - 완전히 격리되어 있고, 하나로 뭉친 로그
대신 job별로 고유한 상태·타임아웃·실패 진단을 갖습니다. PR 체크 목록에는
`test (message)`와 `test (existing-claim)`으로 따로 표시됩니다. 시나리오
로직은 workflow에 인라인으로 있지 않고
[.github/scripts](../../../.github/scripts)(`lib.sh` + 시나리오별 스크립트)에
있습니다.

`changes` job은 버전 범프만 있는(차트 동작이 바뀌지 않는) 커밋에는 `test`
자체를 건너뜁니다.

#### message 시나리오: [scenario-message.sh](../../../.github/scripts/scenario-message.sh)

1. 차트가 관리하는 스토리지로 설치.
2. 차트의 `hermes doctor` 테스트 훅을 실행(`helm test`와 같은 Job이지만,
   hook watch에서 멈추지 않도록 직접 호출).
3. **신뢰된 실행에서만**(`NVIDIA_API_KEY` 시크릿이 있을 때): PVC에 skill을
   주입한 뒤, NVIDIA NIM을 통한 `hermes chat` 라운드트립을 한 번 실행.

`CI_MODELS` 풀은 **failover 전용**입니다 - 라운드트립은 모든 모델이 아니라
먼저 응답한 모델에서 통과합니다. chat 호출은 차트 자체의 테스트 훅을
그대로 반영합니다: `hermes chat -m <model> --provider nvidia -q <prompt> --max-turns N`.

라이브 Discord 알림 단계(workflow 레벨, 시나리오 스크립트 이후)는 이
시나리오에서만 실행됩니다 - Discord가 켜져 있는 유일한 시나리오이기
때문입니다.

#### existingClaim 시나리오: [scenario-existing-claim.sh](../../../.github/scripts/scenario-existing-claim.sh)

`persistence.existingClaim`(차트가 만드는 대신 이미 존재하는 PVC를 마운트하는
기능 - [PR #37](https://github.com/jyje/hermes-agent-helm/pull/37))을
검증합니다:

1. 차트 **바깥에서** `ci-shared-pvc` PVC 생성.
2. `--set persistence.existingClaim=ci-shared-pvc`로 설치.
3. `hermes doctor` 테스트 훅 통과 확인.
4. 파드에 exec로 들어가 `${HERMES_HOME}/ci-claim-probe.txt`를 쓰고 읽기.
5. `hermes doctor` 재실행.

이건 **스모크 테스트**입니다: 차트가 미리 만들어진 PVC에 바인딩되어 깨끗하게
시작함을 증명합니다. 재시작/업그레이드 사이의 영속성은 후속 과제로
남아 있습니다.

별도의 `team` 시나리오는 `hermes-team-knowledge`를 RWX로 준비해 리더에는
읽기/쓰기로, 멤버에는 읽기 전용으로 마운트하고, 리더가 프로브를 쓰고
멤버가 이를 교차로 읽은 뒤, 멤버의 쓰기가 거부되는지 확인합니다. 이렇게
멀티 인스턴스 공유 지식의 경계를 검증하되, 이 볼륨을 작업 핸드오프
경로로 취급하지는 않습니다.

### Fork PR

Fork PR은 저장소 시크릿을 받지 못하므로, chat 라운드트립(그리고 라이브
Discord 체크)은 건너뛰고 **doctor 전용**으로 폴백합니다 - 안전하면서도
여전히 의미 있는 검증입니다.

## verify-release

릴리즈가 게시된 뒤, 이 workflow는 사용자가 실제로 pull하는 아티팩트를
기준으로 전체 공급망을 증명합니다(네임스페이스 `verify-hermes-chart`):

1. 이 저장소의 Actions OIDC 아이덴티티로 OCI 아티팩트를 **cosign verify**.
2. (로컬 소스가 아니라) **OCI 레지스트리에서** `helm install`.
3. `validate-chart`와 같은 `hermes doctor` + chat 라운드트립 실행.

여기서 실패하면 게시된 아티팩트나 서명이 깨졌다는 뜻입니다.

## 로컬에서 동등한 작업 실행하기

```bash
make lint        # helm lint
make template    # 매니페스트 렌더링
make docs        # 차트 README 재생성(helm-docs) - 결과를 커밋하세요
make test        # 설치 + helm test(클러스터/kind 필요)
```

로컬 kind 클러스터 준비와 Discord + NVIDIA 개발 루프는
[로컬 개발 가이드](local-development.md)를 참고하세요.
