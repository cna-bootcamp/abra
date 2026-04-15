---
name: develop
description: AI Agent 개발 및 배포 (STEP 5)
user-invocable: true
type: orchestrator
---

# Develop

[DEVELOP 스킬 활성화 — STEP 5: AI Agent 개발]

## 목표

개발계획서에 따라 AI Agent를 코드 기반으로 구현하고 배포 가능한 상태로 만듦.
DSL 구조를 참조하여 LangChain/LangGraph 등으로 코드 구현하며,
빌드 성공, 테스트 통과, 산출물 보고까지 전체 개발 프로세스를 완료함.

## 활성화 조건

- "코드 개발해줘", "Agent 구현", "구현해줘" 키워드 감지 시
- 사용자가 `/abra:develop` 명령 호출 시

## 작업 환경 변수 로드 
CLAUDE.md에서 {ABRA_PLUGIN_DIR} 변수 로드함. 없으면 '/abra:scenario'를 먼저 수행하도록 안내하고 종료.   

## 에이전트 호출 규칙

### 에이전트 FQN

| 에이전트 | FQN |
|----------|-----|
| agent-developer | `abra:agent-developer:agent-developer` |

### 프롬프트 조립

1. `{ABRA_PLUGIN_DIR}/agents/agent-developer/` 에서 3파일 로드
   - AGENT.md (프롬프트 본문)
   - agentcard.yaml (tier, capabilities, handoff)
   - tools.yaml (추상 도구 선언)
2. `{ABRA_PLUGIN_DIR}/gateway/runtime-mapping.yaml` 참조하여 구체화:
   - **모델 구체화**: agentcard.yaml의 `tier: HIGH` → `tier_mapping`에서 `claude-opus-4-6` 결정
   - **툴 구체화**: tools.yaml의 추상 도구 → `tool_mapping`에서 실제 도구 결정
     - `file_read` → builtin Read
     - `file_write` → builtin Write
     - `code_execute` → builtin Bash
     - `code_search` → lsp: lsp_workspace_symbols
     - `code_diagnostics` → lsp: lsp_diagnostics, lsp_diagnostics_directory
   - **금지액션 구체화**: agentcard.yaml의 `forbidden_actions: ["user_interact"]` → `action_mapping`에서 AskUserQuestion 제외
   - **최종 도구** = (구체화된 도구) - (AskUserQuestion)
3. 3파일을 합쳐 하나의 프롬프트로 조립
   - **구성 순서**: 공통 정적(runtime-mapping) → 에이전트별 정적(AGENT.md + agentcard.yaml + tools.yaml) → 동적(작업 지시)
4. `Task(subagent_type="abra:agent-developer:agent-developer", model="opus", prompt=조립된 프롬프트)` 호출

## 워크플로우

### Phase 0: 입력 확인

개발계획서(`dev-plan.md`) + 검증된 DSL(`{app-name}.dsl.yaml`) 존재 확인.

**미존재 시 조치:**
- dev-plan.md 없음 → `/abra:dev-plan` 스킬로 위임
- DSL 파일 없음 → `/abra:dsl-generate` 스킬로 위임

### Phase 1: 코드 기반 구현 → Agent: agent-developer (`/oh-my-claudecode:ralph` 활용)

- **TASK**: 개발계획서에 따라 AI Agent 프로덕션 코드 구현 (LangChain/LangGraph 등)
- **EXPECTED OUTCOME**: 빌드 성공 + 테스트 통과 + README.md 포함 완성 코드
- **MUST DO**:
  - `{ABRA_PLUGIN_DIR}/agents/agent-developer/references/develop.md` 프롬프트 템플릿 활용
  - 개발계획서의 기술스택·아키텍처·모듈 설계 준수
  - DSL 구조를 참조하여 노드별 모듈 구현 (LLM 호출, 도구 연동, 조건 분기, 상태 관리)
  - 개발계획서에 정의된 모든 디렉토리·모듈을 빠짐없이 구현 (Mock과 Real 모두 포함)
  - 에러 핸들링 및 보안 요구사항 구현
  - 테스트 코드 작성 (단위·통합 테스트)
  - README.md 작성 (아키텍처 다이어그램, 디렉토리 구조, 실행 방법)
- **MUST NOT DO**:
  - 개발계획서 범위 외 기능 구현 금지
  - DSL 원본 수정 금지 (읽기 전용)
  - 'src' 디렉토리 하위에 결과파일 생성 금지 (Base 디렉토리 직접 사용)
- **CONTEXT**:
  - 개발계획서: `{output_dir}/dev-plan.md`
  - DSL: `{output_dir}/{app-name}.dsl.yaml`
  - 시나리오: `{output_dir}/scenario.md`
  - 출력 디렉토리: `{project_root}/`
  - 가상환경: `gateway/.venv` (Python 도구 실행 시 사용)

### Phase 2: 빌드 오류 수정 (`/oh-my-claudecode:build-fix` 활용)

빌드 에러 발생 시 최소 수정 원칙으로 해결.

#### 검증 항목
- lsp_diagnostics로 파일별 오류 확인
- 빌드 명령 실행 결과 확인 (에러 0)

#### 실패 시 조치
- 에러 원인 분석 → 코드 수정 → 재빌드 → 재검증 (반복)

### Phase 3: QA/검증 (`/oh-my-claudecode:ultraqa` 활용)

- [ ] 모든 파일 lsp_diagnostics 통과 (에러 0)
- [ ] 빌드 성공 (컴파일/트랜스파일 에러 없음)
- [ ] 모든 테스트 통과
- [ ] README.md 필수 섹션 포함 (아키텍처, 디렉토리 구조, 실행 방법)
- [ ] 개발계획서의 기술스택·아키텍처와 일치

### Phase 4: 테스트 챗봇 생성

구현된 AI Agent의 API를 호출하는 Streamlit 테스트 챗봇을 자동 생성함.

#### 실행 조건
- Phase 3 완료 후 자동 진행
- `app/main.py` 및 `app/api/routes.py` 존재 확인

#### 실행 내용
1. API 엔드포인트 구조 분석 (`routes.py` 파싱)
2. `chatbot.py` 생성 (Streamlit + SSE 스트리밍)
   - `{ABRA_PLUGIN_DIR}/skills/develop/references/chatbot-template.py` 참조
   - 템플릿 미존재 시 `routes.py`를 분석하여 LLM 기반 동적 생성
3. 의존성 설치 (`streamlit`, `httpx`)
4. 문법 검증 (`python -m py_compile chatbot.py`)
5. README.md에 챗봇 수행방법 추가 (실행 명령, 접속 URL, 필요 환경변수 등)

#### 실패 시 조치
- `py_compile` 실패 → 자동 수정 (최대 3회)
- 3회 초과 실패 → Phase 4 스킵, Phase 5도 스킵하여 Phase 6으로 이동

### Phase 5: E2E 테스트 + 스크린샷 (Playwright MCP)

API 서버와 Streamlit을 백그라운드 기동한 후 Playwright MCP로 E2E 테스트를 수행함.

#### 실행 조건
- Phase 4 완료 (`chatbot.py` 존재)
- Playwright MCP 도구 사용 가능 (진입 시 `browser_navigate` 호출로 감지, 실패 시 Phase 5 스킵)

#### 실행 내용
1. API 서버 + Streamlit 백그라운드 기동
2. 헬스체크 대기 (최대 30초)
3. `scenario.md` 기반 테스트 시나리오 자동 생성
   - 자동 응답 테스트: FAQ 질문 1건 이상
   - 이관 테스트: 비FAQ 질문 1건 이상
   - `scenario.md`에 질문 없으면 기본 질문 사용
4. Playwright MCP E2E 테스트 실행
   - `browser_navigate` → `browser_wait_for` → `browser_type` → `browser_take_screenshot`
   - 초기 화면 + 자동 응답 + 이관 스크린샷 저장
5. 테스트 결과 판정 (PASS/FAIL)
6. 서버 종료 (포트 기반 PID 탐색 → `taskkill`/`kill`)

#### 스크린샷 저장 규칙
- 디렉토리: `{project_root}/screenshots/`
- 파일명: `{순번2자리}_{테스트유형}.png` (예: `01_initial.png`, `02_auto_answer.png`, `03_escalation.png`)

#### 실패 시 조치
- 핫픽스 루프 (최대 2회): 에러 분석 → 코드 수정 → 서버 재기동 → 재테스트
- 2회 초과 시 FAIL 상태로 보고, Phase 6으로 진행

### Phase 6: Git 원격 저장소 배포

완성된 프로젝트를 GitHub에 배포함.

#### 실행 조건
- `gh auth status` 인증 확인
- `git --version` 설치 확인
- 미인증 시 Phase 6 스킵, 수동 배포 안내

#### 실행 내용
1. `.gitignore` 설정 (필수 제외: `.env`, `.omc/`, `.claude/`, `__pycache__/`, `.venv/`)
2. `git init` (미초기화 시)
3. `gh repo create` (원격 저장소 생성)
4. `git add -A` → `git commit` (한글 메시지) → `git push -u origin main`
5. 배포 확인 (원격 저장소 URL + 스크린샷 이미지 URL 보고)

#### 실패 시 조치
- `gh` 미인증 → Phase 6 스킵, 수동 배포 안내 출력

### Phase 7: 프로세스 정리

최종 보고 전 실행 중인 모든 백그라운드 프로세스를 중지함.

#### 실행 내용
1. API 서버 프로세스 중지 (포트 기반 PID 탐색 → `taskkill`/`kill`)
2. Streamlit 프로세스 중지
3. 기타 테스트용 백그라운드 프로세스 중지
4. 포트 점유 해제 확인

### Phase 8: 최종 보고

Phase 1~7 결과를 종합 보고.

- 생성된 파일 목록 (소스 코드, 테스트, 설정 파일)
- 빌드 성공 로그
- 테스트 통과 결과
- 실행 방법 (가상환경 설정, 의존성 설치, 실행 명령)
- README.md 파일 경로
- chatbot.py 생성 여부
- E2E 테스트 결과 (PASS/FAIL, 스크린샷 URL)
- GitHub 저장소 URL
- 전체 산출물 목록

## 완료 조건

- [ ] 코드 빌드 성공
- [ ] 테스트 통과
- [ ] README.md 작성 완료
- [ ] 산출물 목록 보고 완료
- [ ] chatbot.py 생성 및 문법 검증 통과 (Phase 4)
- [ ] E2E 테스트 PASS 및 스크린샷 저장 (Phase 5)
- [ ] GitHub 원격 저장소 배포 완료 (Phase 6)

## 검증 프로토콜

완료 전 다음 검증 수행:

1. **빌드 검증**: 빌드 성공 + lsp_diagnostics 에러 0 확인
2. **테스트 검증**: 단위·통합 테스트 통과
3. **문서 검증**: README.md 필수 섹션 포함 확인
4. **E2E 검증**: API 서버 기동 + 챗봇 테스트 + 스크린샷 존재 확인
5. **배포 검증**: `gh repo view`로 원격 저장소 접근 가능 확인

## 상태 정리

완료 시 임시 파일 정리 (상태 파일 미사용).

## 취소

사용자 요청 시 즉시 중단.
- 생성된 코드 파일은 유지 (사용자가 수동 삭제 가능)

## 재개

구현 코드 존재 시 QA 단계(Phase 3)부터 재개 가능.
chatbot.py 존재 시 Phase 5부터 재개 가능.
screenshots/ 존재 시 Phase 6부터 재개 가능.

## 스킬 부스팅

| 단계 | OMC 스킬 | 효과 |
|------|----------|------|
| Phase 1: 코드 기반 구현 | `/oh-my-claudecode:ralph` | 완료 보장 실행 워크플로우 |
| Phase 2: 빌드 오류 수정 | `/oh-my-claudecode:build-fix` | 최소 수정 원칙 |
| Phase 3: QA/검증 | `/oh-my-claudecode:ultraqa` | QA 순환 워크플로우 |
| Phase 5: E2E 테스트 | Playwright MCP | 브라우저 자동화 E2E 테스트 |

## MUST 규칙

| # | 규칙 |
|---|------|
| 1 | 개발계획서의 기술스택 및 아키텍처를 준수한다 |
| 2 | 빌드 성공 및 테스트 통과를 확인한다 |
| 3 | README.md를 작성한다 (아키텍처, 디렉토리 구조, 실행 방법 포함) |
| 4 | {ABRA_PLUGIN_DIR}/agents/agent-developer/references/develop.md 프롬프트 템플릿을 활용한다 |
| 5 | 개발계획서에 정의된 모든 디렉토리·모듈을 빠짐없이 구현한다 (Mock과 Real 모두 포함, 외부 API 미확보 시 stub 구현) |

## MUST NOT 규칙

| # | 금지 사항 |
|---|----------|
| 1 | 개발계획서 범위 외 기능을 구현하지 않는다 |
| 2 | DSL 원본 파일을 수정하지 않는다 (읽기 전용) |
| 3 | src 디렉토리 하위에 결과파일을 생성하지 않는다 (Base 디렉토리 직접 사용) |

## 검증 체크리스트

- [ ] 코드 빌드가 성공했는가
- [ ] 테스트가 통과했는가
- [ ] README.md가 작성되었는가
- [ ] 개발계획서의 기술스택/아키텍처와 구현이 일치하는가
- [ ] 산출물 목록이 보고되었는가
- [ ] 개발계획서의 디렉토리 구조와 실제 생성 파일이 1:1 대응하는가
- [ ] Mock 전용이 아닌 Real API 모듈도 구현되었는가 (stub 포함)
- [ ] chatbot.py가 생성되고 py_compile을 통과했는가 (Phase 4)
- [ ] E2E 테스트가 PASS이고 screenshots/ 에 스크린샷이 존재하는가 (Phase 5)
- [ ] GitHub 원격 저장소에 코드가 푸시되었는가 (Phase 6)
