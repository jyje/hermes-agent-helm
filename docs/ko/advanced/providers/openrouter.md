---
title: OpenRouter
description: 하나의 OpenRouter key로 다양한 upstream 모델을 선택하는 구성
---

| 필수 Secret | 오버레이 |
| --- | --- |
| `OPENROUTER_API_KEY` | `values-openrouter.yaml` |

## 언제 사용하나요?

OpenRouter API key와 선택할 모델 ID가 필요합니다.

## 설치

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-openrouter.yaml \
  --set-string env.OPENROUTER_API_KEY='<real-value>' --wait
```

둘 이상의 자격 증명이 필요한 예제에서는 모든 값을 `--set-string`으로 전달하거나 `extraEnvFrom`으로 기존 Secret을 참조하세요.

## key 대신 OpenRouter 로그인으로 받기

`v2026.9.14`부터 Hermes는 OpenRouter 자체 로그인으로 key를 받을 수 있습니다:
`hermes auth add openrouter --type oauth`. PKCE를 쓰는 OAuth authorization-code
흐름으로, 브라우저에서 접근을 승인하고 한 번만 쓰는 코드를 붙여넣습니다. GitHub
Copilot이나 OpenAI Codex 같은 device-code 흐름이 아니어서, 차트의
`auth.deviceFlow`가 시작 시 무인으로 실행할 수 없습니다. 실행 중인 파드에서 한 번,
대화형으로 실행하세요.

1. 정적 key 없이 설치합니다. 빈 값을 주면 오버레이의 placeholder가 Hermes의
   자격 증명 풀에 들어가지 않습니다:

    ```bash
    helm upgrade --install hermes-agent ./charts/hermes-agent \
      --namespace hermes-agent --create-namespace \
      -f charts/hermes-agent/values-openrouter.yaml \
      --set-string env.OPENROUTER_API_KEY= --wait
    ```

2. 대화형 터미널에서 로그인합니다. `SSH_TTY`를 주면 Hermes가 코드를 붙여넣는
   흐름을 씁니다. 없으면 파드 안의 임의 포트에서 브라우저 콜백을 기다리는데, 사용자의
   브라우저는 거기에 닿을 수 없습니다:

    ```bash
    kubectl exec -it -n hermes-agent deploy/hermes-agent -c hermes-agent -- \
      env SSH_TTY=/dev/pts/0 hermes auth add openrouter --type oauth --priority 0
    ```

    출력된 URL을 아무 기기에서나 열어 접근을 승인하고, 프롬프트에 코드를
    붙여넣으세요. 코드는 한 번만 쓸 수 있고 약 10분 뒤 만료됩니다. OpenRouter가
    거부하면 명령을 다시 실행하세요.

3. 자격 증명을 확인합니다:

    ```bash
    kubectl exec -n hermes-agent deploy/hermes-agent -c hermes-agent -- hermes auth list
    ```

받는 것은 refresh token 없는 일반 OpenRouter API key입니다. Hermes는 이를
`HERMES_HOME`의 `auth.json`에 저장하므로 `persistence`가 켜져 있으면 재시작 후에도
유지되고, 꺼져 있으면 파드와 함께 사라집니다. 차트 업그레이드는 `auth.json`을
건드리지 않습니다. `OPENROUTER_API_KEY`도 설정돼 있다면 `--priority 0`이 로그인
key를 먼저 쓰게 합니다. 교체하려면 OpenRouter 설정에서 key를 폐기하고 다시 로그인한
뒤, 이전 항목을 `hermes auth remove openrouter <target>`으로 지우세요.

GitOps처럼 values만으로 재현돼야 하는 환경에는 정적 `OPENROUTER_API_KEY` Secret을
쓰세요.

## 배포 전 조정

모델 이름은 OpenRouter 카탈로그에 있는 provider/model 형식으로 지정합니다.

[원본 YAML 열기](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-openrouter.yaml)

## 전체 오버레이

```yaml title="charts/hermes-agent/values-openrouter.yaml"
--8<-- "charts/hermes-agent/values-openrouter.yaml"
```