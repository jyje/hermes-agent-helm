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

## v1.0 준비 상태

이 차트는 첫 릴리즈부터 지금까지 pre-1.0(`0.x`)이었습니다. `1.0.0`의
기준선은 단일 에이전트 경로뿐 아니라 **멀티 에이전트 팀 스토리**가 문서화
수준을 넘어 실제로 증명되는 것입니다.

| 항목 | 상태 |
| --- | --- |
| 단일 에이전트, 프로덕션 검증 | ✅ 완료 — 실제 배포가 15일+/26일+ 가동 중 |
| 페어 협업(`@mention` 핸드오프) | ✅ 레시피 배포·실증 완료; 🔜 [collaboration-ko.md](collaboration-ko.md)에 필드 데모 증거는 아직 미첨부 |
| 리더 주도 팀(스타 토폴로지, 공유 워크스페이스) | ✅ 레시피 배포, 임시 kind 클러스터에서 필드 테스트 완료; 🔜 지속형 클러스터에서는 아직 미증명 |
| 팀 패턴용 차트 확장점(`extraVolumes`, `extraVolumeMounts`, `extraInitContainers`) | ✅ 완료 — 파일 기반 자격증명과 1회성 볼륨 준비를 커버 |
| CI 커버리지(시나리오별 kind 매트릭스, appVersion 범프 포함 기능 변경 감지, docs drift 게이트, 서명된 릴리즈) | ✅ 완료 |
| EN/KO 문서 동등성 | ✅ 지속적인 규율로 유지 |
| 메신저 플랫폼 커버리지 | Discord와 Telegram이 v1.0 기준선; Slack과 그 밖의 플랫폼은 명시적으로 **v1.0 이후** (플랫폼 env var만 바꾸면 같은 스타 토폴로지 그대로 적용) |
| git-backed 위키 볼트(팀 지식 큐레이션) | ⏸️ 설계만 존재([teams-ko.md](teams-ko.md) § Team + wiki vault), v1.0 필수 아님 |

## 함께 보기

- [Hermes 팀](teams-ko.md) — ApplicationSet 기반 팀 패턴 상세.
- [차트 README](../charts/hermes-agent/README.md) — 전체 값 테이블과
  `replicaCount` 단일 writer 근거.
