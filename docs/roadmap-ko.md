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
| 리더 주도 팀(Discord 스레드, 명시적 봇 멘션) | ✅ kind의 `v2026.7.20`에서 두 번 실증: 사람→리더→may→리더→march→리더→사람 완주, 마지막 턴에 멤버 멘션 없음, 두 번째 실행에서 마지막 줄 TEAM 메타데이터 확인; 전용 지식 마운트는 이후 추가되어 구조적으로 검증; [teams-ko.md](teams-ko.md) 참고 |
| 팀 패턴용 차트 확장점(`extraVolumes`, `extraVolumeMounts`, `extraInitContainers`) | ✅ 완료 — 파일 기반 자격증명과 1회성 볼륨 준비를 커버 |
| CI 커버리지(시나리오별 kind 매트릭스, appVersion 범프 포함 기능 변경 감지, docs drift 게이트, 서명된 릴리즈) | ✅ 단일 인스턴스와 구조적 팀 시나리오 완료; CI는 세션/멘션 설정, 리더 쓰기/멤버 읽기 전용 지식 PVC, 공유 파일 조정 부재를 검증하고 실제 Discord 실증이 봇 대 봇 완료를 커버 |
| EN/KO 문서 동등성 | ✅ 지속적인 규율로 유지 |
| 메신저 플랫폼 커버리지 | Discord와 Telegram은 v1.0 사람-에이전트 기준선; 리더 팀 실증은 Discord 전용. Telegram 봇 대 봇 오케스트레이션은 별도 플랫폼 실증이 필요. Slack과 그 밖의 플랫폼은 **v1.0 이후** |
| 공유 RWX 지식 베이스 | ✅ 리더 팀 레시피의 필수 구성; 리더 읽기/쓰기, 멤버 읽기 전용, kind에서 구조적 교차 읽기 검증 |
| git-backed 위키 게시 | ⏸️ 후속 게시 단계 설계만 존재, v1.0 필수 아님 |

## 함께 보기

- [Hermes 팀](teams-ko.md) — ApplicationSet 기반 팀 패턴 상세.
- [차트 README](../charts/hermes-agent/README.md) — 전체 값 테이블과
  `replicaCount` 단일 writer 근거.
