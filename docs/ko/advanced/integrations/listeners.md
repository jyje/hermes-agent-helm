---
title: 공개 리스너 목록
description: 버전별 HTTP 리스너, 인증, 명시적인 Kubernetes 라우팅을 설명합니다.
translation_source:
  path: docs/advanced/integrations/listeners.md
  commit: acccd84696f466447c0f84b957288819c332416e
---

# 공개 리스너 목록

**Hermes v0.22.2 태그의 소스**를 확인했습니다. 아래 값은 **해당 리스너를
활성화했을 때**의 기본값이며 기본 차트 설치에서 열리는 포트 목록이 아닙니다.
기본 게이트웨이는 메신저에 아웃바운드로 연결하며, 접근용 Service와 HTTP 라우팅은
선택 사항입니다. StatefulSet의 headless Service는 DNS만 제공합니다.
아래의 모든 인터페이스 바인딩은 업스트림 어댑터가 dual-stack 기본값을 쓰는 경우
IPv4와 IPv6를 포함합니다.

| 리스너와 태그 소스 | 활성화 시 기본 바인딩 / 포트 | 메시지·데이터 요청 인증 | 차트 연결 방식 |
| --- | --- | --- | --- |
| [관리 대시보드](https://github.com/NousResearch/hermes-agent/tree/v0.22.2/hermes_cli/dashboard_auth) | 이미지에서 모든 인터페이스, 9119 | basic/OAuth/OIDC 세션. 루프백 외에는 인증 제공자가 필수이며 로그인은 셸 접근과 같습니다. | `dashboard.enabled`, Service, Ingress/HTTPRoute. 제한 없는 공개 노출은 OAuth/OIDC를 사용하고 basic은 신뢰 네트워크·VPN에 한정합니다. |
| [OpenAI 호환 API](https://github.com/NousResearch/hermes-agent/blob/v0.22.2/gateway/platforms/api_server.py) | 업스트림은 루프백, 8642. 차트는 활성화 시 0.0.0.0으로 설정합니다. | 루프백에서도 필수인 Bearer `API_SERVER_KEY` | `apiServer.enabled`와 명시적 `service.ports` 및 라우팅 |
| [일반 웹훅](https://github.com/NousResearch/hermes-agent/blob/v0.22.2/gateway/platforms/webhook.py) | 모든 인터페이스, 8644 | 전역·경로별 서명 시크릿과 소스별 서명 검증 | `webhook.enabled`, `/webhooks/<route>` 및 프로필 접두사 경로. Service 포트를 명시합니다. |
| [A2A](https://github.com/NousResearch/hermes-agent/blob/v0.22.2/plugins/platforms/a2a/adapter.py) | 루프백, 9900. 원격 바인딩은 전송 계층 인증 설정이 필요합니다. | `A2A_BEARER_TOKEN` 또는 피어별 `A2A_PEER_TOKENS` | 자유 형식 `config.gateway.platforms.a2a`, 호스트·포트 환경변수와 명시적 Service. `values-a2a.yaml` 참고 |
| [Telegram 자체 웹훅](https://github.com/NousResearch/hermes-agent/blob/v0.22.2/plugins/platforms/telegram/adapter.py) | 모든 인터페이스, 8443. 웹훅 URL이 없으면 폴링합니다. | `TELEGRAM_WEBHOOK_SECRET`이 필수이며 수신기가 요청의 secret-token 헤더를 검증합니다. | 환경변수·설정과 명시적 Service·라우팅. `values-telegram-webhook.yaml` 참고 |
| [WhatsApp Cloud](https://github.com/NousResearch/hermes-agent/blob/v0.22.2/gateway/platforms/whatsapp_cloud.py) | 모든 인터페이스, 8090 | GET 확인용 토큰, POST용 앱 시크릿 HMAC | 환경변수·설정, 명시적 포트와 `/whatsapp/webhook` 라우팅 |
| [SMS / Twilio](https://github.com/NousResearch/hermes-agent/blob/v0.22.2/plugins/platforms/sms/adapter.py) | 루프백, 8080 | `TWILIO_AUTH_TOKEN`으로 `X-Twilio-Signature` 검증. `SMS_WEBHOOK_URL`은 공개 URL과 같아야 합니다. | Service로 연결하려면 `SMS_WEBHOOK_HOST=0.0.0.0`을 설정하고 `/webhooks/twilio`를 명시적으로 노출합니다. |
| [WeCom 콜백](https://github.com/NousResearch/hermes-agent/blob/v0.22.2/plugins/platforms/wecom/callback_adapter.py) | 모든 인터페이스, 8645 | 콜백 토큰, 메시지 서명, encoding AES 키 | 환경변수·설정, 명시적 포트와 `/wecom/callback` 라우팅. 아웃바운드 WeCom WebSocket 모드와 별개입니다. |
| [BlueBubbles 콜백](https://github.com/NousResearch/hermes-agent/blob/v0.22.2/gateway/platforms/bluebubbles.py) | 루프백, 8645 | 지원하는 콜백 쿼리·헤더 필드의 설정된 비밀번호 | Service로 연결하려면 `BLUEBUBBLES_WEBHOOK_HOST=0.0.0.0`을 설정하고 `/bluebubbles-webhook`를 명시적으로 라우팅합니다. 인증 정보가 로그에 남지 않게 합니다. |
| [Microsoft Graph 웹훅](https://github.com/NousResearch/hermes-agent/blob/v0.22.2/gateway/platforms/msgraph_webhook.py) | 모든 인터페이스, 8646 | `client_state`, 루프백 외에는 `allowed_source_cidrs`도 필수 | 환경변수·설정, 명시적 포트와 `/msgraph/webhook` 라우팅. 해당 태그의 소스가 CIDR 요건을 강제합니다. |

리스너를 노출하기 전에 어댑터·플러그인의 가용성과 인증 정보를 설정해야 합니다.
바인딩 기본값과 검증 요건은 위의 태그 소스를 기준으로 하며, 최신 업스트림
환경변수 문서가 소스 변경을 아직 반영하지 못했을 수 있습니다.
이 표는 소스 검사 기록이며 모든 메신저를 실제로 검증했다는 뜻은 아닙니다.

## 포트를 명시적으로 선택하세요

차트의 일반적인 `service.ports`와 라우팅 필드로 메신저 자체 수신기를 연결할
수 있습니다. 플랫폼마다 별도 values 블록을 추가하지 않습니다.
업스트림 리스너를 켜는 것만으로 Kubernetes 라우팅이 생기지는 않습니다.

- 비어 있지 않은 `service.ports`는 기존 대시보드 포트를 **대체**합니다.
  노출할 모든 리스너를 포함하고 각 호스트·경로를 해당 포트로 라우팅하세요.
- WeCom 콜백과 BlueBubbles는 모두 기본값이 8645입니다. 한 Pod에서 둘 다
  실행한다면 한 어댑터의 리스너 포트와 Service·라우팅 포트를 함께 바꾸세요.
- 루프백 리스너는 Service 트래픽을 받을 수 없습니다. 인증을 먼저 설정하고
  의도적으로 바인딩 범위를 넓히세요.
- NetworkPolicy를 켰다면 실제 Ingress 컨트롤러 피어가 해당 포트에 접근하도록
  허용하세요. 다른 웹훅 문제를 해결하려고 대시보드 접근을 넓히지 마세요.
- 제공자의 웹훅 경로와 서명 검증에 쓰는 외부 HTTPS URL을 보존하세요.
  프록시 재작성을 수용하려고 서명을 끄지 마세요.

## Telegram 웹훅 예제

선택한 네임스페이스에 외부 관리 Secret `hermes-agent-telegram-webhook-secrets`를
준비하고 `OPENAI_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_WEBHOOK_SECRET`,
`TELEGRAM_ALLOWED_USERS`를 넣으세요. 긴 임의 검증 시크릿을 생성하고 의도한
사용자만 허용하세요. 인증 정보를 커밋하지 마세요.

호스트·Ingress 클래스·TLS Secret 또는 cert-manager issuer 어노테이션을
환경에 맞춘 뒤 설치하세요.

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-telegram-webhook.yaml --wait
```

공개 URL은 HTTPS 443 포트를 쓰며, Ingress는 `/telegram`을 Service 8443과
Pod 수신기로 전달합니다. `TELEGRAM_WEBHOOK_SECRET`은 외부 Secret에 보관하며,
이 오버레이는 대시보드나 일반 웹훅 리스너를 켜지 않습니다.
폴링을 쓰려면 웹훅 URL과 이 선택적 네트워킹 리소스를 생략하세요.

```yaml title="charts/hermes-agent/values-telegram-webhook.yaml"
--8<-- "charts/hermes-agent/values-telegram-webhook.yaml"
```

다른 리스너도 같은 명시적 포트 패턴을 사용하되 어댑터의 바인딩·인증·경로에
맞추세요. 클러스터별 라우팅은 [대시보드 로그인](dashboard.md),
[Ingress](ingress.md), [HTTPRoute](httproute.md),
[NetworkPolicy](networkpolicy.md)를 참고하세요.
