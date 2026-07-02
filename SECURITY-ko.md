# 보안 정책 (Security Policy)

> 🇺🇸 [English Document](SECURITY.md)

이 문서는 이 저장소의 **Helm 차트**(`charts/hermes-agent`) — 템플릿, 기본
값, 예제, CI — 에 대한 보안 정책을 다룹니다. 이 차트는 커뮤니티가 유지보수하는
프로젝트이며, Nous Research의 공식 릴리스가 아닙니다.

## 취약점 신고

[GitHub Security Advisories](https://github.com/jyje/hermes-agent-helm/security/advisories/new)를
통해 비공개로 신고해 주세요.
**보안 취약점을 공개 이슈로 등록하지 마세요.**

유용한 신고에는 다음이 포함됩니다:

- 간결한 설명과 심각도 평가.
- 영향을 받는 템플릿, 값, 예제 (파일 경로와 줄 범위).
- 차트 버전(`Chart.yaml`의 `version`)과, 관련이 있다면 이미지 태그
  (`appVersion` 또는 오버라이드한 값).
- 문제를 보여주는 렌더링 결과(`helm template`) 또는 재현 절차.

자원봉사로 유지되는 프로젝트이므로 SLA나 버그 바운티 프로그램은 없지만,
합리적인 기간 내에 초기 응답을 드리도록 노력합니다.

## 범위 (Scope)

**범위 내 — 여기로 신고:**

- 안전하지 않은 리소스를 렌더링하는 차트 템플릿 (예: 시크릿이 ConfigMap,
  로그, 어노테이션으로 유출; 의도치 않은 권한 상승).
- `values.yaml`의 안전하지 않은 기본값 (예: 관리 대시보드나 자격 증명을
  기본으로 노출하는 모든 것).
- 사용자를 안전하지 않은 배포로 오도할 수 있는 예제 매니페스트
  (`values-*.yaml`, `examples/argocd/`)의 취약점.
- 이 저장소의 릴리스 파이프라인(GitHub Actions 워크플로, 게시된 OCI
  아티팩트)의 공급망 문제.

**범위 외 — 업스트림으로 신고:**

- Hermes Agent 자체(이미지 내부 애플리케이션)의 취약점. 업스트림 정책을
  따르세요:
  [NousResearch/hermes-agent SECURITY.md](https://github.com/NousResearch/hermes-agent/blob/main/SECURITY.md).
- Kubernetes, Helm, 서드파티 차트/컨트롤러(인그레스 컨트롤러,
  sealed-secrets 등)의 취약점.
- 운영자가 차트의 안전한 기본값을 이미 스스로 변경해야만 성립하는 문제
  (예: `--insecure`와 무인증으로 대시보드를 노출하는 것은 문서화된 의도적
  선택입니다).

## 지원 버전

**최신 릴리스 차트 버전**(최신 `vX.Y.Z` 태그)만 보안 수정을 받습니다. 이전
버전은 패치되지 않으므로 최신 릴리스로 업그레이드하세요.

## 차트의 보안 모델

배포 전에 알아둘 사실:

- **파드가 곧 샌드박스입니다.** 에이전트는 자신의 파드 안에서 명령을
  실행합니다(`config.terminal.backend: local`). 네임스페이스,
  `securityContext`, 리소스 제한, NetworkPolicy 등 Kubernetes 수준의 격리가
  보안 경계입니다. `docker` 터미널 백엔드는 Docker 데몬/소켓이 필요하므로
  클러스터 내에서는 지원하지 않습니다.
- **기본적으로 인바운드 API가 없습니다.** 에이전트는 아웃바운드 연결만
  만듭니다. 유일한 HTTP 표면은 선택적 관리 **대시보드**(포트 9119)이며,
  `127.0.0.1`에 바인딩되고 **API 키를 노출**합니다. 차트는
  `service.enabled: false`, `ingress.enabled: false`로 배포되며, 대시보드
  노출은 명시적 옵트인과 업스트림의 `--insecure` 플래그가 필요합니다 —
  반드시 앞단에 인증을 두세요(`values-ingress.yaml` 참고).
- **시크릿은 `envFrom`으로 주입**되며 Kubernetes `Secret`으로 렌더링됩니다 —
  ConfigMap에는 절대 들어가지 않습니다. GitOps에서는 실제 시크릿을 커밋하지
  말고 [`examples/argocd/`](examples/argocd/#sealedsecret-walkthrough-nvidia-nim--discord)의
  SealedSecret 패턴을 사용하세요.
- **`podSecurityContext` / `securityContext`는 기본적으로 비어 있습니다**
  (이미지 호환성 때문). 이미지가 허용하는 범위에서 강화(non-root, 읽기 전용
  루트 파일시스템, capability 제거)를 권장합니다 — 사용 환경에서 검증하세요.

## 저장소 보호 장치

이 저장소에는 GitHub 시크릿 스캐닝(푸시 보호 포함), Dependabot 보안 업데이트,
비공개 취약점 신고가 활성화되어 있습니다.
