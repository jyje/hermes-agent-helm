---
title: 로컬 개발 가이드
description: 로컬 Kubernetes와 개발 워크플로입니다.
---

# 로컬 개발 가이드

## 로컬 Kubernetes 클러스터

`make test`를 쓰거나 차트를 로컬에서 반복 작업하려면 실행 중인 클러스터가
필요합니다. **kind**를 권장합니다 - CI가 쓰는 것과 같은 런타임입니다.

### kind(권장)

```bash
# 설치
brew install kind          # macOS
# 또는: https://kind.sigs.k8s.io/docs/user/quick-start/#installation

# 클러스터 생성
kind create cluster --name hermes-dev

# 확인
kubectl cluster-info --context kind-hermes-dev
```

정리하려면:

```bash
kind delete cluster --name hermes-dev
```

### minikube

```bash
# 설치
brew install minikube      # macOS

# 시작(Docker 드라이버는 VM 없이도 동작)
minikube start --driver=docker

# kubectl 컨텍스트 전환
kubectl config use-context minikube
```

### MicroK8s(Linux)

```bash
sudo snap install microk8s --classic
microk8s enable dns storage
sudo microk8s kubectl config view --raw > ~/.kube/config
```

---

## 로컬 클러스터에 개발용 설치

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  --set-string env.NVIDIA_API_KEY='nvapi-...' \
  --set-string env.DISCORD_BOT_TOKEN='...' \
  --set-string env.DISCORD_HOME_CHANNEL='...' \
  --set config.model.provider=nvidia \
  --set config.model.default='meta/llama-3.3-70b-instruct' \
  --wait
```

설치 후 차트 자체의 테스트 스위트를 실행하세요:

```bash
make test
```

`values.yaml`을 수정했다면(값 추가, 기본값 변경, 새 섹션) helm-docs로 차트
README를 재생성하고 결과를 커밋하세요 - CI의 `lint` job은 `README.md`와
`README.md.gotmpl` 사이에 드리프트가 있으면 실패합니다:

```bash
make docs
```

---

## CI 테스트 시나리오를 로컬에서 실행하기

[validate-chart.yaml](../../../.github/workflows/validate-chart.yaml)의
`test` job은 시나리오 다섯 개를 **매트릭스**로 실행하며, 각각 자기만의 임시
kind 클러스터에서 돕니다. 시나리오 로직 자체는
[.github/scripts](../../../.github/scripts)(`lib.sh` + 시나리오별 스크립트)에
있으므로, CI가 하는 일을 시나리오 단위로 로컬 kind 클러스터에서 그대로
재현할 수 있습니다:

```bash
kind create cluster --name hermes-verify

export NS=test-hermes-chart
export CI_MODELS="nvidia/nemotron-3-nano-omni-30b-a3b-reasoning,google/gemma-4-31b-it,openai/gpt-oss-20b"
export NVIDIA_API_KEY='nvapi-...'   # 생략하면 doctor 전용 실행(라이브 chat 없음)

# 클러스터마다 정확히 하나의 시나리오를 선택하세요:
.github/scripts/scenario-message.sh
# .github/scripts/scenario-existing-claim.sh
# .github/scripts/scenario-team.sh
# .github/scripts/scenario-security-hardened.sh
# .github/scripts/scenario-bootstrap-overwrite.sh

kind delete cluster --name hermes-verify
```

각 스크립트는 독립적입니다 - 설치, 각 시나리오의 검증, 그리고(`scenario-message.sh`의
경우, `NVIDIA_API_KEY`가 설정되어 있을 때) skill 주입 + chat 라운드트립까지,
CI가 실행하는 것과 정확히 같습니다. `DISCORD_BOT_TOKEN` /
`DISCORD_HOME_CHANNEL`은 선택이며 `scenario-message.sh`에서만 씁니다. 각
시나리오는 **자기만의** 클러스터에서 실행하세요(위처럼) - 모든 스크립트가
`NS` 기본값이 `test-hermes-chart`로, CI의 매트릭스별 job 격리와
일치합니다. 하나의 클러스터를 두 시나리오에 연달아 재사용하면 실행 사이에
네임스페이스를 지우거나 `NS`를 재정의하지 않는 한 충돌합니다.

> macOS는 bash 3.2를 기본 탑재하는데(`/bin/bash --version`), `set -u`
> 아래에서 **빈** 배열을 확장하면 "unbound variable" 오류가 나는 오래전에
> 고쳐진 버그가 있습니다(bash 4.4+에서 수정됨). 스크립트들은 이미 이를
> 방어하고 있으므로(`"${arr[@]+"${arr[@]}"}"`) 그냥 동작할 겁니다 - 이
> 스크립트들을 확장하다 비슷한 오류를 만난다면 거의 확실히 이게
> 원인입니다.

### 라운드트립에 다른 제공자 쓰기

`scenario-message.sh`는 (CI가 검증하는 제공자인) NVIDIA NIM으로
하드코딩되어 있지만, `lib.sh`의 `install_release`는 `helm upgrade`를
얇게 감싼 래퍼일 뿐이라, 시나리오 스크립트를 복사해 `config.model.provider`를
다른 곳으로 향하게 하는 걸 막을 이유가 없습니다 - 예를 들어 로컬 LM
Studio 서버를 커스텀 OpenAI 호환 제공자로 쓸 수 있습니다(차트 README의
[제공자 설정](../../../charts/hermes-agent/README-ko.md#configure-your-provider)
참고). 다만 이건 여기서 엔드투엔드로 검증되지 않습니다: 에이전트 파드는
kind 노드의 네트워크 네임스페이스 안에서 돌기 때문에, 호스트의 LM Studio
인스턴스에 닿으려면 파드가 호스트를 resolve해야 합니다(예:
`host.docker.internal` - 컨테이너 런타임/CNI에 따라 파드 안에서 resolve될
수도, 안 될 수도 있습니다) - 이걸 의존하기 전에 먼저 확인하세요.

---

## 원격 클러스터 에이전트 포트포워딩

로컬 kind 클러스터를 새로 띄우는 대신, 스테이징이나 프로덕션 클러스터에
이미 떠 있는 에이전트를 대상으로 테스트하고 싶다면, 관리 대시보드를
여러분 컴퓨터로 포트포워딩하세요:

```bash
kubectl port-forward svc/hermes-agent 9119:9119 -n hermes-agent
```

그러면 Hermes 대시보드가 `http://localhost:9119`에서 열립니다.

`exec` 기반 디버깅:

```bash
# 실행 중인 에이전트 파드 안에서 셸 열기
kubectl exec -it deploy/hermes-agent -n hermes-agent -- sh

# gateway 상태 확인
hermes gateway status
```

> 에이전트는 Discord와 AI 제공자로 **아웃바운드로만** 연결합니다 - 노출할
> 인바운드 웹훅이 없습니다. 포트포워딩은 관리 대시보드에 닿거나, 파드를
> 통해 임시로 `hermes` CLI 명령을 실행할 때만 필요합니다.

---

## Discord 봇 + NVIDIA 제공자 + gateway

### 사전 준비

| 항목 | 어디서 얻나 |
|---|---|
| Discord 봇 토큰 | [Discord 개발자 포털](https://discord.com/developers/applications) → Bot → Token |
| Discord 채널 ID | 채널 우클릭 → Copy Channel ID(Developer Mode가 켜져 있어야 함) |
| NVIDIA API 키 | [NVIDIA NIM](https://build.nvidia.com) → Get API Key |

### values 파일

`values-local-dev.yaml`을 만드세요(버전 관리에는 올리지 마세요):

```yaml
config:
  model:
    provider: nvidia
    default: meta/llama-3.3-70b-instruct

env:
  NVIDIA_API_KEY: "nvapi-<your-key>"
  DISCORD_BOT_TOKEN: "<your-bot-token>"
  DISCORD_HOME_CHANNEL: "<channel-id>"
```

### 설치

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f values-local-dev.yaml \
  --wait
```

### 확인

```bash
# 에이전트가 떴는지 확인
kubectl get pods -n hermes-agent

# Discord 연결을 지켜보며 로그 확인
kubectl logs -f deploy/hermes-agent -n hermes-agent

# 내장 헬스체크 실행
make test
```

정상적으로 시작되면 `gateway connected` 같은 로그 줄이 남고 봇이 Discord에서
온라인으로 표시됩니다. 홈 채널에 메시지를 보내 엔드투엔드로 확인하세요.

### 팀 테스트용 최소 gateway values

공유하는 Discord 채널에 여러 에이전트를 띄운다면(참고:
[Hermes 팀](../advanced/teams/reference.md)), 에이전트들이 서로 응답할 수 있도록
allow-bots 플래그를 설정하세요:

```yaml
extraEnv:
  - name: DISCORD_ALLOW_BOTS
    value: "1"
  - name: DISCORD_THREAD_REQUIRE_MENTION
    value: "1"
```

전체 멀티 에이전트 설정은
[Hermes 협업](../advanced/teams/collaboration.md)를 참고하세요.
