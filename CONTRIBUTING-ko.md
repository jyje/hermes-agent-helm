# 기여하기

## 브랜치 모델

| 브랜치 | 목적 | CI |
|---|---|---|
| `dev` | 메인테이너 실험용 / 통합용 | lint + docs-drift + template + kind `helm test` |
| `main` | 기본 브랜치이자 PR 대상, 안정 버전. 릴리즈는 여기서 잘라냅니다 | dev와 동일 |
| _태그_ `vX.Y.Z` | 릴리즈 그 자체: 차트 버전이 바뀌면 CI가 생성 | GitHub Packages(OCI)에 배포 |

장기 존속하는 `rc`/`release` 브랜치는 없습니다 - 릴리즈는 태그/이벤트입니다.

## 릴리즈를 잘라내는 방법

다음 SemVer 결정의 근거는 Changesets입니다. 사용자에게 보이는 차트 변경마다
[`.changeset/`](.changeset/) 아래에 Markdown 항목을 추가해, 이 비공개 릴리즈
manifest와 `patch`/`minor`/`major` 영향도를 명시합니다. 생성된 릴리즈 PR에서
이 manifest와 `charts/hermes-agent/Chart.yaml`은 항상 같은 결과 버전을
받습니다. manifest는 npm에 배포되지 않습니다.

### Changeset 추가하기(사용자에게 보이는 변경에는 필수)

새로운 `values-*.yaml` 예제, 새로운 ArgoCD 예제, `values.yaml` 기본값 변경,
템플릿/동작 변경, 사용자가 읽는 문서 등 사용자에게 보이는 차트 변경은 모두
Changeset이 필요합니다. 예제나 문서 파일처럼 "그냥" 보이는 추가도 포함됩니다
- 차트나 그 문서화된 예제에 실리면 사용자에게 보이는 것입니다. `pnpm changeset`을
실행해 `@jyje/hermes-agent-helm`을 선택하고, 차트의 SemVer 영향도를 고른 뒤
간결한 사용자 대상 요약을 작성하세요. 이 파일은 구현 PR과 함께 커밋합니다.
CI가 이를 강제하지 않으므로 PR을 열기 전에 스스로 diff를 검토하세요. 유일한
예외는 차트 사용자에게 아무것도 드러나지 않는 CI 전용/툴링/기타 미배포
유지보수 작업(workflow YAML, 스크립트, 이 기여 가이드 자체)입니다.

### 릴리즈 노트가 될 수 있는 항목 작성하기

YAML frontmatter는 Changesets 고유 데이터이므로 패키지 이름과
`major`/`minor`/`patch`로만 제한합니다. 그래서 카테고리는 Markdown 요약에
기록하며, 이 저장소는 heading과 상세 문단에 다음 규칙을 씁니다:

```md
Category(scope): Title

Concise user-facing detail.
```

`Category`에는 `Feature`, `Fix`, `Security`, `Dependency`, `Documentation`,
`Deprecated`, `Removed` 중 하나를, `scope`에는 `chart`, `values`, `docs`,
`image` 같은 짧은 영향 범위를 씁니다. `Feature`와 `Dependency`는 단수형
항목 카테고리이며, 릴리즈 노트 렌더러가 이를 **Features**와 **Dependencies**
아래로 묶을 수 있습니다. 예:

```md
---
"@jyje/hermes-agent-helm": minor
---

Feature(docs): Documentation portal

Add chart-scoped install, values overlay, example, and reference pages.
```

상세 문단은 명령형의 사용자 대상 언어로 쓰고, 요약에 `minor`/`major`/`patch`를
다시 적지 마세요. SemVer는 Changesets의 고유 frontmatter 데이터이고,
Category는 릴리즈 노트 관례일 뿐 SemVer에는 영향을 주지 않습니다. GitHub
기여자 표시는 Changesets 고유 데이터가 아니므로 요약에 사용자명을 중복해서
적지 마세요 - 커스텀 릴리즈 노트 렌더러가 커밋이나 PR에서 유도할 수 있습니다.
SemVer 선택과 fix 예제를 포함한 전체 가이드는
[`.changeset/README.md`](.changeset/README.md)를 참고하세요.

렌더링된 참조는 간결하게 유지합니다: 가능하면 구현 PR을
`[#101](https://github.com/jyje/hermes-agent-helm/pull/101) (minor) [@jyje](https://github.com/jyje)`
형식으로 쓰고, PR이 없으면 같은 자리에 링크된 짧은 커밋 해시를 씁니다.

대기 중인 Changeset들은 Actions 탭에서
[propose-release.yaml](.github/workflows/propose-release.yaml)을 수동
실행하기 전까지 `main`에 그대로 남습니다. 이 워크플로는 릴리즈 PR 하나를
열거나 갱신하며, 커스텀 버전 단계에서:

- 대기 중인 patch/minor/major 항목들을 하나의 SemVer 버전으로 합치고,
- 그에 맞는 `CHANGELOG.md` 섹션을 작성하고,
- `package.json`, `Chart.yaml`, Artifact Hub 변경사항, 차트 문서, 버전별
  설치 예제를 동기화합니다.

계산된 버전과 생성된 노트를 검토한 뒤 릴리즈 PR을 머지하세요. 릴리즈 영향도가
잘못됐다면 생성된 차트 버전을 직접 고치는 대신 대기 중인 Changeset을 수정하거나
추가한 뒤, 같은 릴리즈 PR을 갱신하기 위해 워크플로를 다시 수동 실행하세요.

변경 없이 로컬에서 미리 보려면 `make propose`를 실행하세요. 일회용 릴리즈
브랜치에서는 `make release-version`이 같은 버전 생성 단계를 적용합니다.

### 머지되면 일어나는 일

위 사항 중 하나가 `main`에 머지되면
[release-chart.yaml](.github/workflows/release-chart.yaml)이 새 버전을 감지하고,
`vX.Y.Z` 태그가 아직 없으면 태그 + GitHub Release(Changesets 노트)를 만든 뒤
차트를 **다음 두 곳 모두**에 배포합니다:

- `oci://ghcr.io/<owner>/hermes-agent-helm/hermes-agent`(OCI 아티팩트), 그리고
- `https://<owner>.github.io/hermes-agent-helm`의 클래식 Helm 저장소
  (`gh-pages` 브랜치에 배포되며, `index.yaml`은 이전 릴리즈들과 병합됨)

다른 이유로 `Chart.yaml`을 건드리는 커밋(예: `appVersion`, description)은
안전합니다 - 태그 존재 여부 가드가 이를 no-op으로 만듭니다.

> `appVersion`은 upstream Hermes 이미지(날짜 기반, 예: `v2026.6.5`)를
> 따라가며 수동으로 올립니다. 릴리즈를 일으키는 건 차트 `version`뿐입니다.

## Conventional Commits(권장)

강제하지는 않지만, [Conventional Commits](https://www.conventionalcommits.org/)
(`feat:`, `fix:`, `docs:`, `ci:`, `refactor:` 등)를 쓰면 히스토리가 읽기
쉬워집니다. 릴리즈 체인지로그는 커밋 제목이 아니라 Changeset 요약입니다.

## CI 검증

PR과 push는 lint + 격리된 **kind** 설치/테스트를 실행하고, 모든 릴리즈는
배포되어 cosign으로 서명된 아티팩트를 다시 검증합니다.

전체 파이프라인 - 병렬로 도는 default/existingClaim 테스트 시나리오, failover
모델 풀, fork PR 동작, 릴리즈 이후 검증 - 은
**[docs/reference/ci.md](docs/reference/ci.md)**를 참고하세요.

## 로컬 개발 환경

다음 내용은 **[docs/reference/local-development.md](docs/reference/local-development.md)**를
참고하세요:

- 로컬 Kubernetes 클러스터 준비(kind 권장, minikube와 MicroK8s도 다룸)
- 개발 테스트를 위한 원격 클러스터 에이전트 포트포워딩
- NVIDIA NIM 제공자와 `hermes gateway`로 Discord 봇 설정하기

## 로컬 체크(push 전에 실행)

```bash
make lint        # helm lint
make template    # 매니페스트 렌더링
make docs        # 차트 README 재생성(helm-docs) - 결과를 커밋하세요
make test        # 설치 + helm test(클러스터/kind 필요)
pnpm changeset   # 사용자에게 보이는 차트 변경에 대한 릴리즈 의도 추가
make propose     # 대기 중인 계산된 버전 미리보기
```

`values.yaml`을 수정한 뒤에는 항상 `make docs`를 실행하세요 - 차트 README가
오래되면 CI가 실패합니다.

차트 설계 원칙은 [AGENTS.md](AGENTS.md)를 참고하세요.
