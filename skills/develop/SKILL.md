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

## {ABRA_PLUGIN_DIR} 변수 해석
오케스트레이터는 실행 시작 시 다음 순서로 `{ABRA_PLUGIN_DIR}`를 결정:
0. 현재 프로젝트의 CLAUDE.md에 {ABRA_PLUGIN_DIR}변수가 있으면 해당 경로 사용하고 이후 진행 안함  
1. 아래 후보 경로 중 존재하는 첫 번째를 `PLUGIN_BASE_DIR`로 선택
   - `/mnt/.local-plugins/cache/unicorn/dmap` (Cowork VM)
   - `~/.claude/plugins/cache/unicorn/dmap` (Mac/Linux CLI)
   - `%APPDATA%/Claude/plugins/cache/unicorn/dmap` (Windows CLI)
2. `PLUGIN_BASE_DIR` 하위의 버전 디렉토리를 시맨틱 버전 비교하여 최신 버전 선택
3. 해당 디렉토리의 절대 경로를 `{ABRA_PLUGIN_DIR}`에 바인딩
4. 이후 모든 `{ABRA_PLUGIN_DIR}/...` 경로를 절대 경로로 치환하여 파일을 읽음
5. 현재 프로젝트의 CLAUDE.md에 {ABRA_PLUGIN_DIR}을 기록하여 이후 중복 계산 안하게 함     

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
  - 출력 디렉토리: `{output_dir}/`
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

### Phase 4: 완료 및 보고

산출물 목록, 실행 방법 등을 사용자에게 보고.

- 생성된 파일 목록 (소스 코드, 테스트, 설정 파일)
- 빌드 성공 로그
- 테스트 통과 결과
- 실행 방법 (가상환경 설정, 의존성 설치, 실행 명령)
- README.md 파일 경로

## 완료 조건

- [ ] 코드 빌드 성공
- [ ] 테스트 통과
- [ ] README.md 작성 완료
- [ ] 산출물 목록 보고 완료

## 검증 프로토콜

완료 전 다음 검증 수행:

1. **빌드 검증**: 빌드 성공 + lsp_diagnostics 에러 0 확인
2. **테스트 검증**: 단위·통합 테스트 통과
3. **문서 검증**: README.md 필수 섹션 포함 확인

## 상태 정리

완료 시 임시 파일 정리 (상태 파일 미사용).

## 취소

사용자 요청 시 즉시 중단.
- 생성된 코드 파일은 유지 (사용자가 수동 삭제 가능)

## 재개

구현 코드 존재 시 QA 단계(Phase 3)부터 재개 가능.

## 스킬 부스팅

| 단계 | OMC 스킬 | 효과 |
|------|----------|------|
| Phase 1: 코드 기반 구현 | `/oh-my-claudecode:ralph` | 완료 보장 실행 워크플로우 |
| Phase 2: 빌드 오류 수정 | `/oh-my-claudecode:build-fix` | 최소 수정 원칙 |
| Phase 3: QA/검증 | `/oh-my-claudecode:ultraqa` | QA 순환 워크플로우 |

## MUST 규칙

| # | 규칙 |
|---|------|
| 1 | 개발계획서의 기술스택 및 아키텍처를 준수한다 |
| 2 | 빌드 성공 및 테스트 통과를 확인한다 |
| 3 | README.md를 작성한다 (아키텍처, 디렉토리 구조, 실행 방법 포함) |
| 4 | {ABRA_PLUGIN_DIR}/agents/agent-developer/references/develop.md 프롬프트 템플릿을 활용한다 |

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
