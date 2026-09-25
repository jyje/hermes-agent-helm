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

### HERMES_HOME 스토리지 선택

Hermes는 세션 저장소(`state.db`)와 다른 SQLite 데이터베이스를 `HERMES_HOME`에
두며, 기본값은 WAL 저널 모드입니다. WAL은 파일을 여는 모든 프로세스 사이에서
바이트 범위 잠금과 공유 메모리가 제대로 동작해야 안전합니다. PVC의 접근 모드
(`ReadWriteOnce`나 `ReadWriteMany`)는 그 아래 파일시스템이 이를 제공하는지 알려주지
않습니다. 접근 모드는 누가 볼륨을 마운트할 수 있는지를 말할 뿐, 파일시스템이 어떻게
동작하는지는 말하지 않습니다.

블록 기반 스토리지(대부분의 `ReadWriteOnce` 스토리지 클래스가 제공하는 ext4나 xfs)를
권장합니다. 스토리지 클래스를 믿기 전에 `persistence.mountPath`에 실제로 마운트된
파일시스템을 확인하세요:

```bash
kubectl exec deploy/hermes-agent -c hermes-agent -- sh -c 'grep " /opt/data " /proc/self/mountinfo'
```

Hermes가 스스로 감지하는 범위는 좁습니다. `v2026.9.14`부터 cross-VM 파일시스템,
구체적으로 `virtiofs`와 `9p`를 인식하고 WAL에 안전하지 않은 것으로 다룹니다:

- 그런 마운트 위의 **새** 데이터베이스는 `delete` 저널 모드로 만들어집니다.
- 디스크에 **이미 WAL 모드로 있는** 데이터베이스는 조용히 바뀌지 않습니다. Hermes는
  WAL을 유지하고 오류를 로그로 남깁니다.
- WAL이 반드시 필요한 경로는 계속 진행하지 않고 명시적인 오류로 실패합니다.

NFS와 CIFS는 이 감지기가 표시하지 **않습니다**. 그렇다고 그곳에서 WAL이 안전하다는
뜻은 아닙니다. `HERMES_HOME`을 네트워크 파일시스템에 둘 수밖에 없다면 첫 시작 전에
저널 모드를 명시하세요:

```yaml
config:
  database:
    journal_mode: delete
```

실행 중인 에이전트에서 이 값을 바꾸는 방식으로 기존 데이터베이스를 전환하지 마세요.
전환하려면 워크로드를 0으로 줄여(`replicaCount: 0`) 파일을 여는 프로세스가 없게 하고,
`HERMES_HOME`을 백업한 뒤, 데이터베이스 파일에 오프라인으로 `PRAGMA
journal_mode=DELETE`를 한 번 실행하고, `journal_mode: delete`를 설정한 다음 다시
늘리세요. 백업과 PVC 이전 전반에도 같은 원칙이 적용됩니다: 에이전트를 0으로 줄인
상태에서만 `HERMES_HOME`을 복사하세요.

에이전트마다 전용 `HERMES_HOME`을 하나씩 두세요. `ReadWriteMany` 스토리지라도 두
에이전트가 한 홈을 공유하면 안 됩니다. 여러 에이전트가 함께 봐야 하는 지식은 별도의
`team.sharedVolume`에 둡니다.
