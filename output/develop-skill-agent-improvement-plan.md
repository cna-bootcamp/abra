# develop 스킬 / agent-developer 개선 계획서

> 목적: `develop` 스킬과 `agent-developer` 에이전트를  
> 범용적이고 재사용 가능한 개발 실행 체계로 개편하기 위한 수정 계획 수립  
> 범위: 실제 문서 반영 제외, 개선 방향과 수정 항목만 정의

## 1. 작성 목적

- `dev-plan` 개선 과정에서 확인된 패턴을 `develop` 단계에도 반영하기 위함
- 고정형 개발 단계 대신 프로젝트별 공통/선택 실행 구조로 전환하기 위함
- 구현 범위, 제외 범위, 스텁 범위, 선택 실행 항목을 명확히 구분하기 위함
- 테스트 챗봇, E2E, Git 배포 같은 후반부 작업을 "항상 수행"이 아니라  
  "필요 시 수행" 구조로 바꾸기 위함
- 스킬은 얇게 유지하고, 개발계획 해석과 구현 판정은 에이전트가 담당하도록  
  역할을 재정리하기 위함

## 2. 현황 진단

### 2.1 `develop` 스킬의 주요 문제

1. 구현 후반부 단계의 고정 강제 구조
   - 테스트용 챗봇 생성, Playwright E2E, GitHub 배포가 프로젝트 특성과 무관하게  
     후반부 기본 단계처럼 배치되어 있음
   - 근거: [skills/develop/SKILL.md](/C:/Users/hiond/plugins/abra/skills/develop/SKILL.md:107),  
     [skills/develop/SKILL.md](/C:/Users/hiond/plugins/abra/skills/develop/SKILL.md:128),  
     [skills/develop/SKILL.md](/C:/Users/hiond/plugins/abra/skills/develop/SKILL.md:157)

2. 스킬 책임 과다 또는 책임 경계 불명확
   - `develop` 스킬이 개발계획 해석, 공통 구현 항목 추출, 특화 실행 판정까지  
     직접 담당하면 입력 구조가 과도하게 복잡해짐
   - 이 책임은 오히려 `agent-developer`가 내부 워크플로우로 처리하는 편이 단순함

3. 경로 가정의 과도한 세분화
   - 소스 루트를 `app`으로 표준화한 방향 자체는 타당함
   - 다만 `app/main.py`, `app/api/routes.py` 같은 세부 파일 구조까지 고정하면  
     프로젝트별 실제 구조와 충돌 가능성 존재
   - 근거: [skills/develop/SKILL.md](/C:/Users/hiond/plugins/abra/skills/develop/SKILL.md:113)

4. 구현 범위 판정 규칙 부족
   - `dev-plan`에 구현, 스텁, 제외, 향후 스프린트 항목이 섞여 있어도  
     이를 개발 단계에서 어떻게 해석할지 기준이 약함
   - 결과적으로 "무조건 다 구현" 또는 "임의 생략" 위험이 공존함
   - 근거: [skills/develop/SKILL.md](/C:/Users/hiond/plugins/abra/skills/develop/SKILL.md:73),  
     [skills/develop/SKILL.md](/C:/Users/hiond/plugins/abra/skills/develop/SKILL.md:222)

### 2.2 `agent-developer`의 주요 문제

1. 워크플로우는 있으나 단계별 작성 기준 부족
   - 제목 수준 가이드는 있으나, 실제로 무엇을 어떻게 해석해 구현에 반영할지  
     세부 기준이 약함
   - 근거: [agents/agent-developer/AGENT.md](/C:/Users/hiond/plugins/abra/agents/agent-developer/AGENT.md:20)

2. 개발계획 해석 책임이 충분히 명시되지 않음
   - `dev-plan`의 핵심 섹션을 읽고 구현 계약으로 내부 변환하는 단계가  
     에이전트 워크플로우에 명확히 자리 잡지 못함
   - 스킬이 대신 해석해야 하는지, 에이전트가 해석해야 하는지 경계가 흐림

3. 개발계획서 섹션별 구현 변환 규칙 부족
   - `§4 모듈 설계`, `§7 데이터 모델`, `§8 테스트 전략`, `§9 배포 계획`을  
     각각 어떤 구현 작업으로 전환해야 하는지 명시되어 있지 않음
   - 근거: [agents/agent-developer/AGENT.md](/C:/Users/hiond/plugins/abra/agents/agent-developer/AGENT.md:38)

4. 검증 게이트의 증거 기준 부족
   - 빌드 성공, 테스트 통과 등은 적혀 있으나  
     어떤 명령을 실행했고 어떤 결과를 증거로 삼을지 기준이 약함
   - 근거: [agents/agent-developer/AGENT.md](/C:/Users/hiond/plugins/abra/agents/agent-developer/AGENT.md:63),  
     [agents/agent-developer/AGENT.md](/C:/Users/hiond/plugins/abra/agents/agent-developer/AGENT.md:101)

### 2.3 참조 템플릿의 주요 문제

1. `develop.md` 템플릿의 정보량 부족
   - 구현 단계, 선택 실행 조건, 검증 게이트, 제외 범위 처리 기준이 부족함
   - `/oh-my-claudecode:ralph` 전제가 하드코딩되어 있어 범용 템플릿으로 부적합함
   - 근거: [agents/agent-developer/references/develop.md](/C:/Users/hiond/plugins/abra/agents/agent-developer/references/develop.md:1)

2. 테스트 챗봇 템플릿의 프레임워크 편향
   - FastAPI + SSE + `/health` + Bearer API Key 전제가 강함
   - 모든 프로젝트에 자동 생성 템플릿으로 사용하기엔 가정이 과도함
   - 근거: [skills/develop/references/chatbot-template.py](/C:/Users/hiond/plugins/abra/skills/develop/references/chatbot-template.py:1)

## 3. 개선 원칙

1. 스킬은 얇게, 에이전트는 두껍게 구성
2. 공통 실행과 선택 실행의 분리
3. 개발계획 해석과 구현 판정은 `agent-developer`가 내부에서 수행
4. 구현 범위, 스텁 범위, 제외 범위의 명시적 분리
5. 증거 기반 검증 및 정직한 보고 강화
6. 소스 루트는 `app` 기준으로 통일하고 `src` 하위 코드 생성 금지 규칙은 유지
7. 과도한 사전 구조화 입력 대신 최소 실행 컨텍스트만 전달

## 4. `develop` 스킬 수정 계획

### 4.1 워크플로우 재구성 계획

현재의 Phase 0~8 구조는 아래와 같이 단순화하는 방향 권장.

1. **Phase 0: 입력 확인**
   - `dev-plan.md`, `scenario.md`, 최신 DSL 파일 존재 확인
   - 최신 DSL 선택 규칙을 `dev-plan`과 동일하게 통일
   - 소스 루트 기준을 `app`으로 확인

2. **Phase 1: 실행 옵션 확인**
   - 테스트 챗봇, E2E, Git 배포에 대해  
     `auto / force / skip` 수준의 최소 옵션만 정리
   - 명시 요청이 없는 경우 기본값은 `auto`

3. **Phase 2: 구현 실행 위임**
   - `agent-developer`에게 원본 입력과 최소 실행 컨텍스트를 전달
   - 개발계획 해석, 구현 범위 판정, 선택 트랙 활성 여부 판정은  
     에이전트 내부에서 수행

4. **Phase 3: 결과 검토 및 재실행 판단**
   - 에이전트가 제출한 빌드/테스트/진단 결과를 기준으로  
     추가 수정 재호출 여부 판단

5. **Phase 4: 최종 보고**
   - 실제 실행 결과, 미실행 항목, 제외 사유, 잔여 리스크 보고

### 4.2 전달 입력 단순화 계획

`develop` 스킬은 복잡한 `implementation_contract`를 사전 생성하지 않고,  
아래 수준의 최소 실행 컨텍스트만 넘기는 방향 권장.

```yaml
run_context:
  dev_plan_path: <path>
  scenario_path: <path>
  dsl_path: <path>
  source_root: app
  options:
    chatbot: auto|force|skip
    e2e_ui: auto|force|skip
    git_publish: auto|force|skip
```

핵심 방향은 다음과 같음.

- 스킬은 입력 위치와 사용자 의도만 정리
- 개발계획 해석과 세부 구현 계약 생성은 `agent-developer`가 담당
- 공통 구현 항목과 특화 실행 항목의 분리는 에이전트 내부 워크플로우에서 처리

### 4.3 테스트 챗봇을 선택 항목으로 전환하는 계획

이 항목은 이번 개선의 핵심 항목으로 우선 반영 필요.

**변경 방향**

- 현재: 후반부 기본 단계처럼 수행
- 변경 후: `chatbot=force`일 때는 반드시 수행, `chatbot=skip`일 때는 생략,  
  `chatbot=auto`일 때는 `agent-developer`가 판정

**`auto` 판정 시 필요 기준**

1. 사용자가 직접 대화형 수동 검증 UI를 원한 경우
2. 구현 결과가 HTTP/SSE/WebSocket 기반 대화형 인터페이스를 제공하는 경우
3. 시나리오 검증이 브라우저 기반 상호작용을 통해서만 의미 있게 수행되는 경우
4. 데모, 시연, 운영자 테스트 화면이 명시적으로 필요한 경우

**`auto` 판정 시 불필요 기준**

1. 결과물이 라이브러리, 워커, 배치, CLI, 내부 도구 집합인 경우
2. API는 존재하더라도 사람용 대화 UI가 검증의 핵심이 아닌 경우
3. 개발계획서에 수동 UI 검증 또는 데모 요구가 없는 경우
4. 템플릿 가정과 구조가 크게 달라 오히려 검증 품질이 떨어지는 경우

### 4.4 E2E UI 테스트를 선택 항목으로 전환하는 계획

테스트 챗봇과 마찬가지로 E2E UI 테스트도 기본 단계가 아니라 선택 단계로 전환 필요.

**변경 방향**

- `e2e_ui=force`이면 수행
- `e2e_ui=skip`이면 생략
- `e2e_ui=auto`이면 `agent-developer`가 판정

**`auto` 활성 기준**

- 실제 브라우저 UI가 존재함
- 시나리오에 UI 흐름 검증이 포함됨
- 수동 테스트 대신 자동 UI 검증의 가치가 큼

**`auto` 비활성 기준**

- UI 자체가 없음
- API/CLI/배치 중심 검증이면 충분함
- 초기 스프린트에서 UI보다 코어 로직 안정성이 우선임

### 4.5 Git 원격 저장소 배포를 선택 항목으로 전환하는 계획

Git 배포는 개발 스킬의 기본 완료 조건이 아니라 별도 선택 실행으로 분리 필요.

**변경 방향**

- `git_publish=force`이면 수행
- `git_publish=skip`이면 생략
- `git_publish=auto`이면 `agent-developer`가 준비 상태를 판정하고  
  스킬은 사용자 요청 범위 내에서만 후속 실행

**`auto` 활성 기준**

- 사용자가 원격 저장소 배포를 요청함
- 배포용 인증과 권한이 준비됨
- 현재 작업이 실질적으로 배포 가능한 상태임

**`auto` 비활성 기준**

- 로컬 구현과 검증만 필요한 경우
- 사내 저장소 또는 다른 형상의 배포 대상인 경우
- 인증 미완료 상태에서 자동 원격 배포가 위험한 경우

### 4.6 규칙 수정 계획

다음 규칙은 현재 형태 유지보다 정교화 권장.

1. `src` 하위 코드 생성 금지 규칙은 유지
   - 전제: 개발계획 스킬/에이전트가 소스 루트를 `app`으로 표준화함
   - 변경 방향: `src` 금지 자체를 없애기보다  
     `app` 기준 구조를 따르도록 명시

2. `app` 루트는 표준화하되 세부 파일명은 고정하지 않음
   - `app/main.py`, `app/api/routes.py`를 무조건 가정하지 않음
   - 실제 엔트리/라우트 파일은 계획서 또는 코드 구조에서 판별

3. `모든 디렉토리·모듈을 Mock과 Real 모두 구현` 규칙 완화
   - 변경 방향:
     - 필수 구현
     - 스텁 구현
     - 이번 스프린트 제외
     - 선택 실행
     네 가지로 구분

### 4.7 최종 보고 형식 개선 계획

최종 보고는 완료 나열이 아니라 아래 구조를 따르도록 변경 권장.

- 실행한 단계
- 자동 판정으로 활성화된 선택 트랙
- 스킵한 단계와 이유
- 생성 파일 목록
- 빌드/테스트/진단 결과
- 증거 로그 요약
- 남은 리스크
- 후속 작업 제안

## 5. `agent-developer` 개선 계획

### 5.1 입력 컨텍스트 재정의 계획

필수 입력은 아래 수준으로 단순화 권장.

- `dev-plan.md`
- 최신 DSL
- `scenario.md`
- `run_context`

여기서 중요한 점은 다음과 같음.

- `develop` 스킬은 복잡한 사전 구현 계약을 만들지 않음
- `agent-developer`가 입력 문서를 직접 읽고 내부 구현 계획으로 변환
- 선택 트랙의 `auto` 판정도 에이전트가 수행

### 5.2 워크플로우 상세화 계획

`agent-developer`는 다음 흐름으로 개편 권장.

1. 입력 로드
2. 개발계획 해석 및 구현 준비성 리뷰
3. 공통 구현 항목과 선택 실행 항목 내부 도출
4. `app` 기준 디렉토리/파일 생성 계획 수립
5. 코어 로직 구현
6. 테스트 및 문서 구현
7. 빌드/진단/테스트 실행
8. 오류 수정 루프
9. 선택 트랙 수행 여부 판정 및 필요 시 실행
10. 증거 수집 및 보고

### 5.3 개발계획서 섹션별 구현 가이드 추가 계획

`plan-writer`에서 했던 것처럼,  
`agent-developer`에도 "계획서의 어느 섹션을 무엇으로 구현하는지" 가이드 필요.

**권장 추가 가이드**

- `§4.1 DSL 노드 ↔ 파일 매핑`
  → 실제 생성 파일과 1:1 대응 검증 기준
- `§4.2 핵심 워크플로우`
  → 그래프/서비스 흐름 구현 기준
- `§4.3 입출력 인터페이스`
  → API/도구 스키마, DTO, 검증 모델 생성 기준
- `§4.5 갭 및 커스텀 개발 범위`
  → 구현 / 스텁 / 제외 / 선택 실행 판정 기준
- `§4.6 에러 핸들링`
  → 예외 처리, 재시도, 사용자 메시지 구현 기준
- `§4.7 개발 순서 및 일정`
  → 실제 구현 순서와 검증 순서 조정 기준
- `§7 데이터 모델`
  → 상태 모델, 저장 모델, 외부 연동 모델 구현 기준
- `§8 테스트 전략`
  → 단위/통합/E2E 테스트 구성 기준
- `§9 배포 계획`
  → Docker/K8s/Serverless 설정 파일 생성 기준

### 5.4 검증 게이트 강화 계획

현재 체크리스트는 방향성만 있고 증거 기준이 약함.  
아래처럼 게이트를 명시하는 방향 권장.

**Hard Gate**

- 진단 에러 0
- 빌드 성공
- 테스트 통과
- 필수 파일 존재
- 계획서상 필수 모듈 대응 완료

**Business Gate**

- 구현 범위가 계획서와 일치
- 제외 범위가 근거와 함께 보고됨
- 선택 트랙 자동 판정 근거가 보고됨
- 특화 요구가 코드/설정/문서 중 최소 1곳 이상에 반영됨

**Evidence Gate**

- 실행한 명령 존재
- 주요 명령 결과 요약 존재
- 미실행 항목의 사유 존재

### 5.5 정직한 보고 강화 계획

다음 보고 규칙을 명시 필요.

- 실행하지 않은 빌드/테스트를 통과로 적지 않음
- 생성만 하고 실행하지 않은 산출물을 완료로 적지 않음
- 스텁 구현은 스텁 구현으로 명시
- 외부 API 미연동은 "연동 완료"가 아니라 "인터페이스 준비"로 보고
- 자동 판정으로 스킵한 선택 트랙은 근거와 함께 보고

## 6. 참조 문서 수정 계획

### 6.1 `references/develop.md` 개편 계획

현재 템플릿은 지나치게 짧고 하드코딩이 강함.

**수정 방향**

- `/oh-my-claudecode:ralph` 제거 또는 선택형으로 변경
- 복잡한 `implementation_contract` 설명 대신  
  최소 `run_context` 전달 구조 반영
- 스킬은 얇게, 에이전트는 해석과 구현을 담당하는 역할 분리 반영
- 코어 구현 / 선택 실행 트랙 / 검증 게이트 / 보고 형식 포함
- `src` 하위 코드 생성 금지 유지 전제 아래  
  `app` 기준 소스 구조 설명 보강
- "Mock + Real 모두 구현" 문구를 범위 기반 문구로 치환

### 6.2 `chatbot-template.py` 사용 기준 개편 계획

템플릿 자체보다 "언제 쓰는가" 규칙이 먼저 필요.

**수정 방향**

- 템플릿은 선택 트랙 전용 참조 리소스로 격하
- `chatbot=auto` 판정 기준과 연결
- FastAPI/SSE 전제와 맞지 않으면 동적 생성 또는 스킵

## 7. 파일별 수정 대상 계획

1. [skills/develop/SKILL.md](/C:/Users/hiond/plugins/abra/skills/develop/SKILL.md)
   - 워크플로우 단순화
   - 최소 실행 컨텍스트 전달 구조 도입
   - 선택 트랙 옵션 도입
   - 완료 조건 재정의

2. [agents/agent-developer/AGENT.md](/C:/Users/hiond/plugins/abra/agents/agent-developer/AGENT.md)
   - 개발계획 해석 책임 명확화
   - 단계별 상세 가이드 추가
   - 계획서 섹션 → 구현 규칙 매핑 추가
   - 선택 트랙 자동 판정 기준 추가
   - 검증 게이트 강화

3. [agents/agent-developer/references/develop.md](/C:/Users/hiond/plugins/abra/agents/agent-developer/references/develop.md)
   - 템플릿 전면 개편

4. [skills/develop/references/chatbot-template.py](/C:/Users/hiond/plugins/abra/skills/develop/references/chatbot-template.py)
   - 즉시 수정 대상은 아니나  
     선택 트랙 규칙 정립 후 보조 개선 대상으로 검토

## 8. 우선순위

### P0

- 테스트 챗봇을 선택 단계로 전환
- `develop` 스킬의 해석 책임 축소
- 개발계획 해석과 공통/선택 트랙 도출 책임을 `agent-developer`로 이동
- 최소 `run_context` 전달 구조 도입
- `app` 기준 소스 구조 정렬 및 세부 경로 하드코딩 완화
- 계획서 기반 구현 / 스텁 / 제외 / 선택 실행 판정 규칙 도입

### P1

- E2E UI 테스트 선택 단계 전환
- Git 배포 선택 단계 전환
- `agent-developer` 단계별 가이드 강화
- `develop.md` 템플릿 전면 개편

### P2

- 챗봇 템플릿 일반화
- 보고 형식 정교화
- 상태 재개 단위 세분화

## 9. 완료 기준

- `develop` 스킬이 얇은 오케스트레이터 역할만 수행함
- 개발계획 해석과 구현 범위 판정은 `agent-developer`가 담당함
- 테스트 챗봇 생성이 기본 단계가 아니라 조건 기반 선택 단계가 됨
- `app` 기준 소스 구조와 `src` 하위 코드 생성 금지 규칙이 일관되게 유지됨
- 과도한 사전 구조화 입력 없이도 에이전트가 구현 판단을 수행할 수 있음
- 검증 게이트와 증거 기반 보고 형식이 문서화됨

## 10. 적용 상태

본 계획서 기준 반영 상태는 다음과 같음.

- 적용 완료
  - `skills/develop/SKILL.md`
  - `agents/agent-developer/AGENT.md`
  - `agents/agent-developer/references/develop.md`
- 보류
  - `skills/develop/references/chatbot-template.py`
    - 선택 트랙 기준 정립 이후 보조 개선 대상으로 유지
