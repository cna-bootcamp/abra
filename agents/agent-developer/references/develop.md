# 개발 프롬프트 템플릿

개발계획서에 따라 AI Agent를 개발할 것.  
스킬은 최소 실행 컨텍스트만 전달하며,  
개발계획 해석과 구현 범위 판정은 에이전트가 직접 수행할 것.

## 입력

- Base 디렉토리: `{{Base 디렉토리}}`
- 개발 계획서: `{{Base 디렉토리}}/{{개발 계획서 파일 경로}}`
- 시나리오: `{{Base 디렉토리}}/{{시나리오 파일 경로}}`
- DSL: `{{Base 디렉토리}}/{{DSL 파일 경로}}`

## run_context

```yaml
run_context:
  source_root: app       # §2.0에서 dev-plan §4.0과 교차 검증
  options:
    chatbot: {{chatbot 옵션}}
  retry_budget:
    diagnostics: 5
    build: 3
    test: 3
    total: 10
```

옵션 해석 규칙:

- `force`: 테스트 챗봇 생성 수행
- `skip`: 테스트 챗봇 생성 생략

## 에이전트 책임

1. 개발계획서 해석
   - 기술스택, 디렉토리 구조, 모듈 설계, 데이터 모델, 테스트 전략, 배포 계획 분석
2. 소스 루트 교차 검증
   - dev-plan `§4.0` 트리의 루트가 `app/`인지 확인
   - 불일치 시 handoff 프로토콜로 에스컬레이션
3. 내부 구현 범위 판정
   - 각 항목을 `구현 / 스텁 / 제외`로 분류
   - MOCK 노드·custom_required·excluded_this_sprint 규칙 적용
4. 의존관계 분석 및 실행 계획 수립
   - 선후행 관계 분석
   - 순차 작업 / 병렬 가능 작업 분리
   - 파일 쓰기 충돌 가능 시 병렬 작업을 순차로 재분류
5. 소스 구조 준수
   - 소스 루트는 `app`
   - 결과 파일은 `src` 하위에 생성하지 않음
6. 프로덕션 코드 구현
   - DSL 구조와 개발계획서 기준으로 코드 생성
7. 환경변수·시크릿·의존성 표준 준수
8. 검증 수행 (재시도 한도 내)
   - 진단, 빌드, 테스트 실행
   - 한도 도달 시 가설·분류 보고 후 중단
9. 증거 파일 저장 (`{output_dir}/evidence/`)
10. 테스트 챗봇 생성
    - `chatbot=force`인 경우에만 수행
11. 정직한 결과 보고

> **주의**: 수동 Playwright 테스트 안내 메시지 생성은 `develop` 스킬 책임이며 이 에이전트 범위 아님.

## 구현 범위 기준

### 구현

- 개발계획서상 이번 범위에 포함된 필수 기능
- 필수 파일 및 필수 모듈
- `dev-plan §4.5 custom_required` 전항목

### 스텁

- 외부 API, 인증정보, 운영 환경 미비로 실제 연동이 불가하나  
  인터페이스는 이번 범위에 포함되는 항목
- DSL의 `[MOCK]` 코드 노드
- 코드 주석에 `[MOCK]` prefix + `TODO(sprint-2): real API integration` 마커 필수

### 제외

- 개발계획서에서 명시적으로 제외된 항목
- `dev-plan §4.5 excluded_this_sprint` 전항목
- 향후 스프린트 항목

## 개발계획서 섹션 매핑 기준

- `§4.1 DSL 노드 ↔ 파일 매핑`
  - 생성 파일과 DSL 노드 대응 검증
- `§4.2 핵심 워크플로우`
  - 그래프/서비스 흐름 구현
- `§4.3 입출력 인터페이스`
  - DTO, API 스키마, 도구 입출력 모델 구현
- `§4.5 시나리오-DSL 갭 및 커스텀 개발 범위`
  - 커스텀 구현 및 범위 판정 연결
- `§4.6 에러 핸들링`
  - 예외 처리, 재시도, 사용자 메시지 구현
- `§4.7 개발 순서 및 일정`
  - 구현 순서 및 검증 순서 정렬
- `§7 데이터 모델`
  - 상태/저장/연동 모델 구현
- `§8 테스트 전략`
  - 단위/통합/E2E 테스트 및 수동 검증 지원 구성
  - E2E 표의 각 행 → `tests/e2e/` 파일 1개 이상 매핑
- `§9 배포 계획`
  - 배포 설정 파일 구현
  - 실제 GitHub 원격 배포는 `develop` 스킬 단계에서 수행

## 의존관계 기반 실행 계획 기준

개발 시작 전에 구현 항목 간 의존관계를 분석하여 실행 계획 수립.

### 순차 작업

- 공통 설정, 공용 상태 모델, 핵심 엔트리, 기반 인터페이스처럼 선행 완료가 필요한 작업
- 이후 구현이나 테스트가 직접 의존하는 작업

### 병렬 가능 작업

- 파일 쓰기 대상이 겹치지 않는 독립 모듈 구현
- 독립 테스트 파일 작성
- 문서 보완, 배포 설정 보완 등 핵심 로직과 분리 가능한 작업

### 재분류 규칙

- 동일 파일 또는 동일 책임 영역을 동시에 수정해야 하면 병렬 가능 작업이라도 순차 작업으로 전환
- 테스트는 대응 구현이 완료된 뒤 실행되도록 순서 조정
- 최종 보고에 의존관계 분석 결과와 순차/병렬 실행 계획을 포함

## 재시도 한도 운영 규칙

### 카운터 초기화

```yaml
diagnostics_remaining: 5
build_remaining: 3
test_remaining: 3
total_remaining: 10
```

각 시도마다 해당 카운터와 `total_remaining`를 함께 차감.  
한도 도달 시 즉시 중단하고 아래 형식으로 보고.

### 한도 도달 시 보고 형식

**진단 한도**:

```yaml
diagnostics_exhausted:
  remaining_errors:
    - file: <path>
      line: <n>
      message: <msg>
  snapshot: {output_dir}/evidence/diagnostics.json
```

**빌드 한도**:

```yaml
build_exhausted:
  last_command: <cmd>
  last_exit_code: <n>
  root_cause_hypotheses:
    - <가설 1>
    - <가설 2>
    - <가설 3>
  log: {output_dir}/evidence/build.log
```

**테스트 한도**:

```yaml
test_exhausted:
  failed_tests:
    - name: <test>
      classification: skip | fix_later | real_bug
      reason: <설명>
  report: {output_dir}/evidence/test-report.xml
```

## 환경변수·시크릿 관리 표준

### `.env.example` 생성 의무

- 실제 시크릿 값 포함 금지 (`GROQ_API_KEY=your-key-here` 형태)
- dev-plan §2, §6에 명시된 모든 외부 의존성 키 포함
- 주석으로 각 변수의 용도 설명

### `.gitignore` 필수 항목

```gitignore
.env
.env.*
!.env.example
*.key
*.pem
credentials.json
secrets.yaml
output/evidence/*.log
```

### 로드 전략

- 프로세스 시작 시 필수 환경변수 누락되면 명확한 에러 메시지로 실패 (fail-fast)
- `.env` 파일 우선, OS 환경변수 후순위 병합
- README 환경변수 표에 `필수 | 선택` 구분 명시

## 의존성 관리 표준

### Python

- `pyproject.toml` 기반 (Poetry 또는 uv 권장)
- 프로덕션·개발 의존성 분리 (`[project.optional-dependencies.dev]`)
- 버전 범위 `^x.y` 형식 (dev-plan §2와 일치)
- 가상환경 격리 (`.venv` 또는 `gateway/.venv`)
- 빌드 검증: `python -c "import app"` smoke 실행

### TypeScript

- `package.json` + `pnpm-lock.yaml` 고정
- 버전 범위 `^x.y` 형식
- `engines.node` 명시
- 빌드 검증: `pnpm build` 통과

## 테스트 챗봇 작성 기준

주의 사항:

- `app/main.py`, `app/api/routes.py`를 고정 가정하지 않음
- 실제 엔트리 구조를 먼저 확인
- `chatbot-template.py`는 Python 참조 리소스
- TypeScript 프로젝트는 실제 구조에 맞는 최소 챗봇 동적 생성
- 템플릿과 구조가 맞지 않으면 실제 구조에 맞게 동적 생성

## README.md 필수 항목

- 언어 정책: 프로젝트 `AGENTS.md` 언어 규칙 상속, 없으면 한국어
- 아키텍처 다이어그램
- 디렉토리 구조
- 실행 방법
- 환경변수 표 (`필수 | 선택` 구분)
- 주요 구성 설명
- MCP 서버인 경우 Claude Code 추가 방법

```bash
# Streaming HTTP
claude mcp add --transport http [-s local|user|project] {MCP서버명} {MCP서버 주소}

# stdio
claude mcp add-json {MCP서버명} '{
  "type": "stdio",
  "command": "python",
  "args": ["{MCP 서버 파일 경로}"],
  "env": {
    "{Key}": "{Value}"
  }
}' [-s local|user|project]
```

## 증거 파일 저장 기준

`{output_dir}/evidence/` 디렉토리에 다음 파일 기록:

- `diagnostics.json` — 파일별 에러/경고 스냅샷 (최종 상태)
- `build.log` — 빌드 명령·stdout·stderr·exit code
- `test-report.xml` — JUnit 호환 포맷
- `commands.md` — 전체 실행 명령 목록 + 타임스탬프 + exit code

## Handoff 프로토콜

DSL 결함·계획서 결함 발견 시 에스컬레이션.

- 대상: `dsl-architect` (DSL 결함) 또는 `plan-writer` (계획서 결함)
- 정보: 구체적 결함, 영향 범위, 권장 수정사항, blocker 여부
- `blocker: true`인 경우 구현 중단 후 보고만 반환

## Lessons Learned 연동

프로젝트 `AGENTS.md`의 `Lessons Learned` 섹션을 작업 전 로드.

- 매칭 교훈은 실행 계획에 사전 반영
- 새로운 시행착오는 `notepad_write_working`로 기록

## 결과 보고 형식

- 실행한 단계
- 소스 루트 교차 검증 결과
- 의존관계 분석 요약
- 순차 작업 / 병렬 가능 작업 실행 계획
- `구현 / 스텁 / 제외` 판정 결과
- 생성 파일 목록
- 빌드/테스트/진단 결과 (재시도 사용 횟수 포함)
- 증거 파일 경로 (`{output_dir}/evidence/*`)
- 실행한 주요 명령 요약
- README.md 경로
- 테스트 챗봇 생성 여부
- 스텁 항목 목록 + 프로덕션 전환 조건
- 남은 리스크
- 후속 작업 제안
