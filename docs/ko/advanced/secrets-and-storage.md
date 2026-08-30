---
title: Secret과 영속성
description: values 파일을 시크릿 저장소로 만들지 않으면서 자격증명을 안전하게 전달하고 Hermes 상태를 보존합니다.
---

## 자격증명

이 차트는 `envFrom`으로 차트가 관리하는 Secret을 Hermes에 전달합니다. 환경
변수가 `config.yaml`보다 우선하므로, 제공자 자격증명은 `env`나
`extraEnvFrom`에 두어야 하며, 커밋되는 `.env` 파일에 두면 안 됩니다.

프로덕션에서는 Helm 바깥에서 Secret을 만들고 `extraEnvFrom`으로 참조하세요.
Bitwarden 예제는 또 다른 부트스트랩 패턴을 문서화합니다.

### External Secrets Operator

`externalSecret.enabled: true`로 설정하면 차트가 자체 Secret 대신
ExternalSecret을 렌더링합니다. 이는 추가가 아니라 대체입니다 - 차트의
Secret은 더 이상 렌더링되지 않고, `env`는 무시되며, 차트가 소유한 모든
`envFrom`(메인 컨테이너, auth device-login init 컨테이너, helm test Job)이
`extraEnvFrom` 없이도 ExternalSecret의 target 이름을 자동으로 따라갑니다.
클러스터에 External Secrets Operator CRD가 이미 설치되어 있어야 하며,
`externalSecret.secretStoreRef`로 기존 SecretStore/ClusterSecretStore를
가리키고 `externalSecret.data`/`dataFrom`을 채우세요.

차트의 Pod 템플릿 체크섬은 ExternalSecret의 `target`/`data`/`dataFrom`
변경을 반영하므로, values에서 이 값들을 수정하면 롤아웃이 트리거됩니다.
반대 방향은 다룰 수 없습니다 - *외부 제공자*가 나중에 시크릿 내용을
회전(rotate)하면 ESO는 자체 주기로 target Secret을 갱신하지만, 실행 중인
Pod를 재시작해 새 값을 반영하지는 않습니다. 이는 Reloader, Stakater 같은
reloader 컨트롤러의 역할이며, 이 차트는 그런 컨트롤러를 함께 제공하지
않습니다.

## 영속 홈

기본 영속 볼륨은 의도적으로 작게 잡혀 있습니다. 설정, 로그인 상태, 세션,
에이전트 메모리를 저장합니다. values로 크기나 스토리지 클래스를 조정하세요.
공유 에이전트 지식은 별개의 문제입니다 - 여러 에이전트가 진짜로 같은 쓰기
가능한 디렉터리를 필요로 할 때만 RWX 볼륨을 사용하세요.
