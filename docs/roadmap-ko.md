# 로드맵

[English](roadmap.md) · [한국어](roadmap-ko.md)

이 차트는 **하나**의 에이전트를 잘 배포·관리하고, 팀이 곧 확장 수단입니다.

| 단계 | 내용 | 시점 | 상태 |
| --- | --- | --- | --- |
| **단일 에이전트** | 이 차트 — 릴리즈당 잘 관리된 Hermes 인스턴스 1개 | 현재 | ✅ 제공 |
| **에이전트 팀 (ArgoCD ApplicationSet)** | 하나의 ApplicationSet으로 팀의 에이전트별 릴리즈를 생성(명부는 데이터, 이 차트는 템플릿) — 공유 gateway 채널 1개, 멤버별 유일한 `fullname`, 팀원마다 Application 파일을 손으로 관리할 필요 없음 | 현재 | ✅ 권장 — [docs/teams-ko.md](teams-ko.md) |
| **오퍼레이터** | Kubernetes 오퍼레이터(`Agent` / `AgentTeam` CRD, 별도 레포) — ApplicationSet을 대체해 팀 전체 상태를 보여주는 단일 오브젝트, 팀 단위 불변식의 admission-time 검증, 능동적 reconcile을 제공. 이 레포는 그 **설치용 차트**를 호스팅 | 장기 | ⏸️ 미착수 — [`charts/hermes-operator/`](../charts/hermes-operator/) 플레이스홀더 (TBA) |

즉 흐름은 **단일 인스턴스 → ApplicationSet 기반 팀(현재) → `Agent` / `AgentTeam`
CRD 오퍼레이터(장기, 미착수)**입니다. ApplicationSet은 이미 "팀"에 필요한 것을
지금 충분히 커버하고 있으며, 오퍼레이터는 그 템플릿 전용 모델이 실제로 부족하다고
드러날 때만(위 세 가지 이유) 가치가 있는, 일정 없는 장기 후보로 남겨둡니다.
[`charts/hermes-operator/`](../charts/hermes-operator/) 디렉터리는 그 가능한 미래
차트를 위한 의도적으로 비워 둔 플레이스홀더입니다.

## 함께 보기

- [Hermes 팀](teams-ko.md) — ApplicationSet 기반 팀 패턴 상세.
- [차트 README](../charts/hermes-agent/README.md) — 전체 값 테이블과
  `replicaCount` 단일 writer 근거.
