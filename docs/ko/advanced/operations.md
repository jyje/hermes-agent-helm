---
title: 운영과 테스트
description: 안전하게 렌더링하고, 차트를 검증하고, gateway 생명주기를 이해합니다.
---

## 로컬 검증

```bash
make docs
make lint
make template
```

## 런타임 검증

설치 후 `helm test <release> --namespace <namespace>`를 실행하세요. 제공자
엔드투엔드 확인이 필요하면 `tests.chat.enabled`를 의도적으로 켜세요 - 일반
설치에는 필수가 아닙니다.

## Gateway 동작

`hermes gateway run`은 외부로 나가는 메신저 프로세스이며, upstream 이미지는
s6로 관리됩니다. 이미지의 entrypoint는 건드리지 마세요. 포트 9119의 선택적
관리 대시보드는 민감하므로 인증 뒤에서만 노출해야 합니다.
