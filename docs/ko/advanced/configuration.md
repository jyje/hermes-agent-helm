---
title: 설정 모델
description: config.yaml, 환경 변수, Secret, 그리고 영속적인 Hermes 홈이 어떻게 함께 동작하는지 이해합니다.
---

## 우선순위

Hermes는 부분적인 차트 설정을 자체 내장된 버전별 기본값과 병합합니다. 실제
우선순위는 **CLI > config.yaml > 환경 변수 > 내장 기본값**입니다. 따라서 이
차트는 upstream의 전체 설정을 그대로 재현하려 하지 않습니다.

## 설정을 시딩하는 이유

이 차트는 init container로 `$HERMES_HOME`에 `config.yaml`을 시딩합니다.
읽기 전용으로 마운트하지 않는데, Hermes가 자신의 홈 디렉터리에 런타임
상태를 기록하기 때문입니다. 기본값인 `bootstrap.overwrite: false`는 파일이 없을 때만
시드해 업그레이드 중 런타임 수정을 보존합니다. 롤아웃마다 차트 설정으로 교체하려면
`true`로 설정하세요. 시드하거나 기존 파일을 보존한 뒤 init 컨테이너가 Hermes의
비대화형 설정 마이그레이션을 실행하며 변경 전에 `config.yaml`과 `.env`를 백업합니다.
버전 표기가 없는 설정은 마이그레이션하지만, Hermes 지원 기준보다 낮은 버전을 명시한
설정은 그대로 둡니다. 이 경우 [차트 README의 복구 절차](../../../charts/hermes-agent/README-ko.md#마이그레이션-지원-기준보다-오래된-설정-복구)를
따르세요.

## 컨트롤러 선택

일반적인 단일 에이전트 상황에는 Deployment를 사용하세요. 워크로드에 안정적인
Pod 아이덴티티가 중요하다면 StatefulSet을 사용하세요. 두 모드 모두 Namespace를
생성하지 않으므로, Helm의 `--namespace` 플래그로 선택하세요.
