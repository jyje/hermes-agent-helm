---
title: DevOps 로드맵
description: 운영 개선 로드맵입니다.
---

# DevOps 로드맵

이 문서는 `hermes-agent-helm`의 CI/CD 파이프라인 개선사항을 추적합니다.
항목들은 현재 `.github/workflows/` 설정에 대한 소스 컨트롤·DevOps 리뷰에서
도출됐습니다.

영역별로 묶고, 각 그룹 안에서는 우선순위순으로 정렬했습니다.

---

## 소스 컨트롤

### 🔴 높은 우선순위

- [ ] **`main`에 브랜치 보호 켜기**
  - 머지 전 최소 PR 1개 필수(`main`으로 직접 push 금지)
  - `validate-chart`를 필수 상태 체크로 추가
  - **오늘의 위험:** 깨진 커밋이 `main`에 그대로 올라가 CI 게이트 없이
    바로 `release-chart.yaml`을 트리거할 수 있음

- [ ] **`validate-chart` 트리거에 workflow 파일 변경도 포함**
  - 현재 경로 필터는 `charts/hermes-agent/**`와
    `.github/workflows/validate-chart.yaml`만 감시함
  - `cron-fetch-image.yaml`, `release-chart.yaml`, `propose-release.yaml`
    등의 변경은 검증 없이 `main`에 올라감
  - `paths:` 트리거에 `.github/workflows/**`를 추가(최소한 `actionlint`로
    YAML을 lint)

### 🟡 중간 우선순위

- [ ] **쓰이지 않는 `dev` 브랜치 전략 정리**
  - `validate-chart`는 `[dev, main]`에서 트리거되지만 실제 작업은 모두
    `main`으로 바로 감. `dev` 브랜치는 실무에서 쓰인 적이 없음
  - `dev → main` 머지 플로우를 채택하거나, 트리거 목록에서 `dev`를
    제거하고 `CONTRIBUTING.md`를 정리해 문서화된 전략을 실제와 맞추기

---

## 파이프라인 설계

### 🟡 중간 우선순위

- [ ] **`release-chart`를 독립된 OCI job과 gh-pages job으로 분리**
  - 지금은 하나의 job이 OCI push → gh-pages 배포를 순서대로 실행함
  - OCI push는 성공했는데 gh-pages가 실패하면, 재실행 시 전체가
    건너뛰어짐(태그 존재 여부 가드) - 자동 복구가 없는 부분 배포 상태
  - 두 job으로 나누면(태깅 단계에 공유 `needs:`를 걸어) 각각 독립적으로
    재실행 가능

- [ ] **"릴리즈 커밋은 테스트되지 않는다"는 공백 메우기**
  - Changesets 릴리즈 PR은 생성된 버전 메타데이터, `Chart.yaml`, 문서,
    `CHANGELOG.md`만 건드리므로 `functional=false` → kind 클러스터 테스트가
    건너뛰어짐
  - 배포 직전에 머지되는 마지막 커밋은 통합 테스트를 거치지 않음
  - 선택지: (a) 릴리즈 PR에 항상 도는 가벼운 스모크 테스트 추가, 또는
    (b) 앞선 기능 커밋이 테스트됐다는 전제로 이 공백을 알려진 트레이드
    오프로 문서화하고 받아들이기

### 🟢 낮은 우선순위

- [ ] **러너 레이블을 저장소 변수로 추상화**
  - 모든 workflow가 `ubuntu-26.04-arm`을 하드코딩함. 이 이미지가
    deprecated되거나 장애가 나면 모든 workflow가 동시에 실패함
  - `runs-on: ${{ vars.RUNNER_LABEL || 'ubuntu-latest' }}`를 써서 코드
    수정 없이 폴백을 바꿀 수 있게 하기
  - 아래 [러너 폴백 노트](#러너-폴백-노트) 참고

---

## 보안

### 🟢 낮은 우선순위

- [ ] **Helm 템플릿 보안 스캐닝 추가**
  - 지금은 렌더링된 템플릿에 `kubesec`, `trivy`, `checkov`, `kube-score`
    스캔이 전혀 없음
  - 제안하는 삽입 지점: `validate-chart / lint` job에 새 단계로
    `helm template | trivy config -` 또는 `kubesec scan -` 실행
  - Cosign 서명은 출처를 증명할 뿐, 서명된 내용 자체를 검증하지는 않음

- [ ] **각 릴리즈에 SBOM 생성·첨부**
  - `release-chart.yaml`은 OCI 아티팩트에 서명하지만 SBOM(Software Bill
    of Materials)은 만들지 않음
  - push 이후 단계로 `syft`나 `cosign attest --predicate`(CycloneDX/SPDX)를
    추가할 수 있음

---

## 운영

### 🟢 낮은 우선순위

- [ ] **gh-pages에서 오래된 차트 패키지 정리**
  - `release-chart.yaml`은 `keep_files: true`를 씀. 릴리즈마다
    `gh-pages` 브랜치에 `.tgz`가 무기한 쌓임
  - 최근 N개 버전(예: 10개)만 남기고 `index.yaml`을 재생성하기 전에
    오래된 `.tgz` 파일을 지우는 정리 단계 추가

- [ ] **`upstream-review`의 AI 어드바이저 폴백 강화**
  - NVIDIA NIM 엔드포인트가 다운되거나 quota가 소진되면
    `upstream-review` job이 조용히 실패하거나 GitHub 이슈를 만들지 않음
  - AI 호출이 실패했을 때 명시적으로 `continue-on-error: true`를 걸고
    폴백 댓글/이슈를 남기는 단계를 추가해 실패를 눈에 보이게 하기

---

## 참고

### 러너 폴백 노트

GitHub Actions는 "러너 A를 시도하고 안 되면 러너 B로"를 네이티브로
지원하지 않습니다. `runs-on: [label-a, label-b]` 배열 문법은 *먼저
가능한 것*이 아니라 *모든 레이블이 일치해야 함*을 뜻합니다. 저장소
변수 방식이 가장 오버헤드가 적은 우회책입니다 - 설정 하나만 바꾸면
모든 workflow에 즉시 전파됩니다.

### 기능 diff 필터 설계

`validate-chart`의 `changes` job은 릴리즈 전용 커밋(버전 범프 + 문서)에는
의도적으로 kind 클러스터 테스트를 건너뜁니다. 이건 의도된 비용/속도
트레이드오프입니다. 위의 "릴리즈 커밋은 테스트되지 않는다" 항목은 즉시
고쳐야 한다는 뜻이 아니라, 향후 검토를 위해 알려진 공백을 기록해 둔
것입니다.

---

*마지막 검토: 2026-06-29*
