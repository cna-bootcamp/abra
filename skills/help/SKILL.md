---
name: help
description: Abra 플러그인 사용 안내
user-invocable: true
---

# Help

[HELP 활성화]

## 목표

Abra 플러그인의 사용 가능한 명령, 자동 라우팅 규칙, 주요 기능을 안내함.
런타임 상주 파일(CLAUDE.md)에 라우팅 테이블을 등록하는 대신,
이 스킬이 호출 시에만 토큰을 사용하여 사용자 발견성을 제공함.

## 활성화 조건

사용자가 `/abra:help` 호출 시 또는 "도움말", "뭘 할 수 있어", "명령어 목록" 키워드 감지 시.

## 워크플로우

### Step 1: 안내 출력

**중요: 추가적인 파일 탐색이나 에이전트 위임 없이, 아래 내용을 즉시 사용자에게 출력하세요.**

**사용 가능한 명령:**

| 명령 | 설명 |
|------|------|
| `/abra:dify-setup` | Dify Docker 환경 구축 |
| `/abra:setup` | 플러그인 초기 설정 (.env, 가상환경, 연결 테스트) |
| `/abra:scenario` | 요구사항 시나리오 생성 및 선택 |
| `/abra:dsl-generate` | Dify DSL 자동 생성 |
| `/abra:prototype` | Dify 프로토타이핑 자동화 |
| `/abra:dev-plan` | 개발계획서 작성 |
| `/abra:develop` | AI Agent 개발 및 배포 |
| `/abra:help` | 본 사용 안내 |

**자동 라우팅:**

다음과 같은 요청은 자동으로 abra 플러그인이 처리:
- "에이전트 만들어줘", "Agent 개발" → 전체 5단계 워크플로우
- "시나리오 생성해줘", "요구사항 정의" → /abra:scenario
- "DSL 생성해줘", "워크플로우 DSL" → /abra:dsl-generate
- "프로토타이핑 해줘", "Dify 업로드" → /abra:prototype
- "개발계획서 써줘" → /abra:dev-plan
- "코드 개발해줘", "Agent 구현" → /abra:develop
- "Dify 설치", "Docker 실행" → /abra:dify-setup

## 명령어

| 명령 | 설명 |
|------|------|
| `/abra:help` | 전체 사용 안내 |
