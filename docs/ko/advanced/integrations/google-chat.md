---
title: Google Chat
description: Cloud Pub/Sub pull 구독으로 Hermes를 Google Chat bot으로 실행하는 구성
---

| 필수 Secret | 오버레이 |
| --- | --- |
| 모델 제공자 key(예제에서는 `OPENAI_API_KEY`)와 서비스 계정 JSON Secret | `values-google-chat.yaml` |

## 언제 사용하나요?

팀이 Google Chat에서 Hermes와 대화할 때 사용합니다. 이벤트는 Cloud Pub/Sub
**pull** 구독으로 들어오므로 파드는 Google API로 나가는 연결만 만듭니다. 들어오는
Service, Ingress, 공개 엔드포인트가 필요 없고, 예제는 모든 리스너를 꺼둡니다.

`v2026.9.14` 이상이 필요합니다. 이 릴리스부터 공식 이미지에 Google Chat 의존성이
들어 있어, 새 파드가 첫 부팅 때 아무것도 설치하지 않습니다.

## Google Cloud 사전 준비

Workspace 쪽은 업스트림 [Google Chat 설정 가이드](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/google_chat)를
따르세요. 가장 자주 틀리는 부분은 IAM 바인딩이고, 서로 다른 두 리소스에 걸립니다:

- **topic**에: `chat-api-push@system.gserviceaccount.com`에 `Pub/Sub Publisher`가
  필요합니다. 없으면 Google Chat이 이벤트를 전달할 수 없습니다.
- **subscription**에: 사용자의 서비스 계정에 `Pub/Sub Subscriber`와 `Pub/Sub
  Viewer`가 필요합니다. Hermes가 시작할 때 구독을 확인합니다.

프로젝트 수준의 Pub/Sub 역할은 주지 마세요. Chat 앱 자체는 연결 설정을 **Cloud
Pub/Sub**로 하고 topic을 가리키게 합니다.

## 설치

먼저 서비스 계정 JSON을 Secret에 넣습니다. 오버레이가 이를 읽기 전용으로 마운트하고
`GOOGLE_CHAT_SERVICE_ACCOUNT_JSON`이 그 파일을 가리키게 합니다:

```bash
kubectl create secret generic google-chat-sa \
  --namespace hermes-agent \
  --from-file=sa.json=/path/to/key.json

helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-google-chat.yaml \
  --set-string env.OPENAI_API_KEY='<real-value>' --wait
```

Secret 볼륨의 기본 모드(`0644`)면 Hermes 런타임 사용자(uid `10000`)가 key를 읽을 수
있습니다. `defaultMode`를 `0440`으로 좁힌다면 `podSecurityContext.fsGroup: 10000`도
설정하세요.

## 배포 전 조정

`extraEnv`의 프로젝트 ID, 전체 구독 이름, 허용 이메일을 바꾸세요.
`GOOGLE_CHAT_ALLOWED_USERS`는 좁게 유지하세요: 목록에 있는 사람은 에이전트가 파드
안에서 명령을 실행하게 만들 수 있습니다. `GOOGLE_CHAT_HOME_CHANNEL`은 선택이며 cron
출력이 갈 곳만 정합니다.

일반 텍스트 메시지는 이 오버레이만으로 동작합니다. 네이티브 파일 첨부는 사용자별
OAuth 설정(채팅에서 `/setup-files`, 업스트림 가이드 Step 10)이 따로 필요하며, 이
예제는 이를 구성하지 않습니다.

## 확인한 범위

오버레이는 CI에서 다른 모든 `values-*.yaml`과 함께 렌더링됩니다. 고정된 이미지에서
Google Chat 어댑터가 시작되어 마운트된 경로의 서비스 계정 파일을 읽는 것까지
확인했습니다. 실제 Google Workspace 메시지 왕복은 Workspace 테넌트가 필요해 그
확인에 포함되지 않았습니다.

[원본 YAML 열기](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-google-chat.yaml)

## 전체 오버레이

```yaml title="charts/hermes-agent/values-google-chat.yaml"
--8<-- "charts/hermes-agent/values-google-chat.yaml"
```
