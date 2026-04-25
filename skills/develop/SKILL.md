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

AGENTS.md 파일에서 `## 환경변수` 섹션의 환경변수 로딩.  
로딩 실패 시 사용자에게 `/abra:setup`을 먼저 수행하라고 안내하고 종료.

## 용어집

| 용어 | 정의 |
|---|---|
| `{PROJECT_DIR}` | AGENTS.md 환경변수 섹션의 `PROJECT_DIR` 값 |
| `{output_dir}` | `{PROJECT_DIR}/output` (고정) |
| `{ABRA_PLUGIN_DIR}` | AGENTS.md 환경변수 섹션의 `ABRA_PLUGIN_DIR` 값 |
| `{project_root}` | `{PROJECT_DIR}` 동의어 (구버전 호환 용도만 사용) |

## 참조

| 문서 | 경로 | 용도 |
|------|------|------|
| 개발 프롬프트 템플릿 | `{ABRA_PLUGIN_DIR}/agents/agent-developer/references/develop.md` | 구현 위임 시 참조 |
| GitHub 저장소 생성 도구 | `{ABRA_PLUGIN_DIR}/resources/tools/create-repo.md` | 최종 배포 수행 기준 |
| DMAP Publish 스킬 | `C:\Users\hiond\plugins\dmap\skills\publish\SKILL.md` | 배포 전 사용자 질문 항목 참조 |

## 에이전트 호출 규칙

### 에이전트 FQN

| 에이전트 | FQN |
|----------|-----|
| agent-developer | `abra:agent-developer:agent-developer` |

### 프롬프트 조립

- `{ABRA_PLUGIN_DIR}/resources/guides/combine-prompt.md`에 따라 AGENT.md + agentcard.yaml + tools.yaml 합치기
- `Agent(subagent_type=FQN, model=tier_mapping 결과, prompt=조립된 프롬프트)` 호출
- tier → 모델 매핑은 `{ABRA_PLUGIN_DIR}/gateway/runtime-mapping.yaml` 참조

### 서브 에이전트 호출

워크플로우 단계에 `Agent: {agent-name}`이 명시된 경우,  
메인 에이전트는 해당 단계를 직접 수행하지 않고,  
반드시 위 프롬프트 조립 규칙에 따라 해당 에이전트를 호출하여 결과를 받아야 함.

서브에이전트 호출 없이 메인 에이전트가 해당 산출물을 직접 작성하면  
스킬 미준수로 간주함.

## 진행상황 업데이트 및 재개

`{PROJECT_DIR}/AGENTS.md`에 각 Phase 완료 시 저장. 최종 완료 시 `Done`으로 표기.

### 상태 해상도 (세분화)

```md
## 워크플로우 진행상황
- develop: Phase2.impl          # agent-developer 구현 중
- develop: Phase2.build         # 빌드 루프 진행 중
- develop: Phase2.test          # 테스트 루프 진행 중
- develop: Phase3.review        # 결과 검토 중
- develop: Phase4.github-ask    # GitHub 배포 확인 중
- develop: Done                 # 전체 완료
```

### 재개 캐시

실패·중단 발생 시 `{output_dir}/.develop-state.yaml`에 다음 정보 기록하여 재개 지원:

```yaml
phase: Phase2.build
retry_usage:
  diagnostics: 2
  build: 1
  test: 0
  total: 3
last_evidence: {output_dir}/evidence/build.log
generated_files:
  - app/main.py
  - app/graph/state.py
  # ...
handoff: null | {target, reason}
```

재개 시 이 파일을 먼저 읽어 중복 작업 방지.

## 워크플로우

### Phase 0: 입력 확인 및 유효성 검증

개발에 필요한 핵심 입력 존재 여부와 내용 유효성 확인.

#### 0.1 파일 존재 확인

- 개발계획서: `{output_dir}/dev-plan.md`
- 시나리오: `{output_dir}/scenario.md`
- DSL: `{output_dir}` 아래 최신 검증 버전 DSL 파일 (`*_v{MAX}.dsl.yaml`)

**미존재 시 조치**

- `dev-plan.md` 없음 → `/abra:dev-plan` 스킬로 위임
- DSL 파일 없음 → `/abra:dsl-generate` 스킬로 위임

#### 0.2 내용 유효성 게이트 (Hard Gate)

- **G0.1**: `dev-plan.md`에 `## 1. 개요` ~ `## 9. 배포 계획` 9개 섹션이 존재 (dev-plan 스킬 H1 재검증)
- **G0.2**: DSL YAML 파싱 성공 + 최소 키 존재 (`app.mode`, `workflow.graph.nodes`)
- **G0.3**: dev-plan `§4.1` 매핑 테이블 행 수 == DSL `type ∈ {llm, code, question-classifier}` 노드 수 (dev-plan H3 재검증)
- **G0.4**: dev-plan `§4.0` 트리의 루트가 `app/`임 (src/ 루트 금지)

**실패 시 조치**

- 어느 하나라도 실패하면 사용자에게 결함 내역을 보고하고 `/abra:dev-plan` 또는 `/abra:dsl-generate` 재실행 권고 후 종료

#### 0.3 Lessons Learned 로드

- 프로젝트 `AGENTS.md`의 `Lessons Learned` 섹션을 로드
- 매칭되는 교훈을 Phase 2 프롬프트에 포함하여 agent-developer에 전달

#### 0.4 기본 전제

- 소스 루트는 `app` 기준 사용
- 결과 파일은 `src` 하위에 생성하지 않음
- 증거 파일은 `{output_dir}/evidence/` 하위에 저장

### Phase 1: 챗봇 필요 여부 결정 및 사용자 확인

`develop` 스킬이 개발계획서만 읽고 테스트용 챗봇 필요 여부를 먼저 판정한 뒤,  
반드시 사용자에게 확인받음.

#### 판정 입력

- 오직 `{output_dir}/dev-plan.md`만 사용

#### 검토 기준 (서로 배타적 카테고리)

| # | 카테고리 | 확인 항목 |
|---|---|---|
| 1 | 인터페이스 | 입출력이 대화형 HTTP/SSE/WebSocket/Streaming인가 |
| 2 | 검증 방식 | 테스트 전략에 사람 UI 기반 검증이 필요한가 |
| 3 | 시연 용도 | 시연·데모·프레젠테이션 대상으로 기재되었는가 |
| 4 | 운영 사용자 | 운영자 수동 테스트 화면이 요구되는가 |
| 5 | MCP 여부 | MCP 서버만으로 검증 가능한가 (Yes이면 챗봇 불필요) |

2개 이상 Yes이면 "테스트 챗봇 생성 추천".  
MCP 서버만으로 충분하면 "테스트 챗봇 미생성 추천".

#### 실행 규칙

- 판정 근거를 사용자에게 제시하고 확인 요청
- 사용자 승인 시 `run_context.chatbot = force`
- 사용자 거부 시 `run_context.chatbot = skip`

### Phase 2: 코드 기반 구현 → Agent: agent-developer

- **TASK**: 개발계획서 기반 프로덕션 코드 구현 및 검증 수행
- **EXPECTED OUTCOME**: 빌드 성공 + 테스트 통과 + README.md 포함 완성 코드 + `output/evidence/` 증거 파일
- **MUST DO**:
  - `{ABRA_PLUGIN_DIR}/agents/agent-developer/references/develop.md` 프롬프트 템플릿 활용
  - 개발계획서, 시나리오, DSL 원본을 그대로 전달
  - 최소 실행 컨텍스트(`run_context`)만 전달 (재시도 한도 포함)
  - Lessons Learned 매칭 교훈 포함
  - 개발계획 해석, 구현/스텁/제외 판정은 `agent-developer`가 수행
  - 챗봇 생성 여부는 Phase 1 사용자 확인 결과만 전달
- **MUST NOT DO**:
  - `develop` 스킬이 상세 구현 계약을 임의 작성하지 않음
  - 개발계획서 범위 외 기능 구현 지시 금지
  - DSL 원본 수정 금지
  - `src` 디렉토리 하위에 결과 파일 생성 금지
  - Playwright 테스트 안내 메시지 생성은 agent-developer에 위임 금지 (Phase 6에서 직접 처리)
- **CONTEXT**:
  - 개발계획서: `{output_dir}/dev-plan.md`
  - 시나리오: `{output_dir}/scenario.md`
  - DSL: `{output_dir}/<latest>.dsl.yaml`
  - 출력 디렉토리: `{PROJECT_DIR}/`
  - 증거 디렉토리: `{output_dir}/evidence/`
  - 가상환경: `gateway/.venv`

```yaml
run_context:
  dev_plan_path: "{output_dir}/dev-plan.md"
  scenario_path: "{output_dir}/scenario.md"
  dsl_path: "{output_dir}/<latest>.dsl.yaml"
  source_root: "app"
  options:
    chatbot: force|skip
  retry_budget:
    diagnostics: 5
    build: 3
    test: 3
    total: 10
  lessons_learned: <AGENTS.md 매칭 교훈 배열>
```

### Phase 3: 결과 검토 및 재실행 판단

`agent-developer` 결과를 검토하고 재실행 여부 판단.

#### 3.1 필수 확인 항목

- 진단 에러 0 여부 (또는 한도 도달 보고)
- 빌드 성공 여부 (또는 한도 도달 보고)
- 테스트 통과 여부 (또는 한도 도달 보고)
- README.md 작성 여부
- 개발계획서와 구현 범위 일치 여부
- `구현 / 스텁 / 제외` 판정 결과 보고 여부
- `output/evidence/` 4개 파일 생성 여부
- 스텁 항목에 `TODO(sprint-2)` 마커 존재 여부
- handoff 보고 여부 (있다면 차단성 확인)

#### 3.2 한도 도달 시 조치

agent-developer가 재시도 예산을 소진하고 중단했을 때:

- **diagnostics_exhausted**: 남은 에러 사용자 보고 → 사용자 승인 시 추가 5회 예산으로 재호출 or 해당 파일 스킵 결정
- **build_exhausted**: 근본원인 가설 3개 사용자 제시 → 사용자 판단 반영하여 재호출
- **test_exhausted**: 실패 테스트 분류(skip/fix_later/real_bug) 사용자 확인 → `skip/fix_later`는 마커 처리 후 통과, `real_bug`만 추가 예산으로 재호출

#### 3.3 Handoff 수신 시 조치

- `blocker: true` → `/abra:dsl-generate` 또는 `/abra:dev-plan` 재실행 사용자 확인
- `blocker: false` → 스텁 처리된 항목을 보고에 표시하고 Phase 4 진행

#### 3.4 실패 시 조치 (일반)

- 원인 분석
- 필요한 수정 범위만 지정하여 `agent-developer` 재호출
- 재호출 시 재시도 예산은 재발급 (`retry_budget.total=10` 초기화)
- 재호출 누적 3회 초과 시 사용자에게 escalation

### Phase 4: GitHub 배포 여부 사용자 확인

최종 보고 전에 GitHub 원격 저장소 배포 여부를 반드시 사용자에게 확인함.

#### 질문 기준

`C:\Users\hiond\plugins\dmap\skills\publish\SKILL.md`의 사용자 질문 항목을 참조하여  
아래 정보를 순차적으로 확인.

1. GitHub 계정 보유 여부
2. GitHub Username
3. Personal Access Token 보유 여부 및 입력 가능 여부 (`repo` 권한)
4. Organization 사용 여부 및 Organization 이름

#### 확인 결과 처리

- 사용자가 배포를 원하지 않으면 배포 단계 스킵 후 최종 보고로 이동
- 인증 정보가 준비되지 않았으면 필요한 정보만 안내하고 배포 스킵 가능
- 사용자가 배포를 원하고 정보가 준비되면 Phase 5 진행

### Phase 5: GitHub 원격 저장소 배포

사용자 확인이 완료된 경우에만 배포 수행.

#### 수행 기준

- `{ABRA_PLUGIN_DIR}/resources/tools/create-repo.md`를 참조하여 수행
- `create_repo.py` 기반으로 원격 저장소 생성 및 초기 푸시 수행
- `repo` 권한 PAT 사용

#### 필수 보안 규칙

- 토큰을 출력/로그에 노출하지 않음
- 원격 URL에 토큰이 남지 않도록 검증
- 기존 저장소를 사용자 확인 없이 덮어쓰지 않음

#### 배포 후 확인

- 원격 저장소 URL 확인
- 푸시 성공 여부 확인
- 필요 시 원격 URL 보안 재검증

### Phase 6: 최종 보고 + 수동 Playwright 테스트 안내

Phase 0~5 결과를 종합 보고.

#### 6.1 필수 보고 항목

- 실행한 단계
- 챗봇 생성 여부와 사용자 확인 결과
- 생성 파일 목록
- 빌드/테스트/진단 결과 (재시도 사용 횟수 포함)
- 증거 파일 경로 (`{output_dir}/evidence/*`)
- 실행 방법
- README.md 경로
- GitHub 배포 수행 여부 및 결과
- 스텁 항목 목록 + 프로덕션 전환 조건
- 남은 리스크
- 후속 작업 제안

#### 6.2 검증 수단 계층 안내

최종 보고에 3단계 검증 수단을 명시.

| 단계 | 수단 | 자동화 | 책임 |
|---|---|---|---|
| 1차 | MCP Client E2E (`tests/e2e/`) | 자동 | agent-developer |
| 2차 | 테스트 챗봇 (선택) | 반자동 | agent-developer (Phase 1 force일 때) |
| 3차 | 수동 Playwright | 사용자 | develop 스킬 (아래 안내 메시지) |

#### 6.3 수동 Playwright 테스트 안내 메시지

E2E 자동 실행 대신, 최종 보고 시 아래 예제를 프로젝트에 맞게 수정하여 안내 메시지로 제공.

```md
# Playwright MCP를 이용하여 AI 직접 테스트 요청
※ 주의: Playwright MCP는 스크린샷 이미지를 캡처해서 수행하므로 토큰 소비 많음  
※ 낮은 모델 사용 권장, 사용자가 일부 준비 동작 직접 수행

- Claude Code는 터미널에서 Claude Code 실행
- Angigravity, Cursor, Codex는 프롬프트창에서 요청
- 아래 프롬프트로 요청
  > Playwright MCP로 {테스트 대상 URL 또는 UI}에 접근해 주세요.
  > {로그인이 필요하면} id: {본인id}, pw: {본인pw}로 로그인해 주세요.
- 사용자가 테스트할 대상 화면을 직접 열거나 필요한 사전 동작 수행
- 테스트 요청
  > dev-plan.md와 DSL 파일을 읽어 테스트 계획을 세우고 테스트하세요.
- 에러 발생 시 수정 요청
  > 구현 에러: {에러 내용}
```

안내 메시지 작성 원칙:

- 실제 테스트 대상 URL 또는 UI 기준으로 작성
- 로그인 필요 시 로그인 지시 포함
- `dev-plan.md`와 DSL 파일을 읽고 테스트 계획을 세우라고 안내
- 에러 발생 시 재수정 요청 문구 포함

## 완료 조건

- [ ] 코드 빌드 성공 (한도 내)
- [ ] 테스트 통과 (한도 내)
- [ ] README.md 작성 완료
- [ ] `output/evidence/` 4개 증거 파일 생성
- [ ] 산출물 및 증거 보고 완료
- [ ] 수동 Playwright 테스트 안내 메시지 제공 완료 (develop 스킬이 직접 생성)
- [ ] GitHub 배포를 수행한 경우 배포 결과 보고 완료

## 상태 정리

완료 시 `{output_dir}/.develop-state.yaml` 임시 파일 정리.  
AGENTS.md 진행상황은 `develop: Done`으로 최종 갱신.

## MUST 규칙

| # | 규칙 |
|---|------|
| 1 | 개발계획서의 기술스택 및 아키텍처를 준수함 |
| 2 | Phase 0.2 입력 유효성 게이트(G0.1~G0.4)를 모두 통과한 뒤 Phase 1 진행함 |
| 3 | 빌드 성공 및 테스트 통과를 실제로 확인함 |
| 4 | README.md를 작성함 |
| 5 | `{ABRA_PLUGIN_DIR}/agents/agent-developer/references/develop.md` 템플릿을 활용함 |
| 6 | 소스 코드는 `app` 루트를 기준으로 생성함 |
| 7 | 챗봇 생성 여부는 개발계획서만 읽고 먼저 판단한 뒤 반드시 사용자 확인을 거침 |
| 8 | 재시도 한도(`retry_budget`)를 agent-developer에 전달하고 한도 도달 시 사용자 확인을 거침 |
| 9 | GitHub 배포 전에는 반드시 사용자 확인과 필수 질문 수집을 수행함 |
| 10 | 수동 Playwright 테스트 안내 메시지는 develop 스킬이 Phase 6에서 직접 생성함 |

## MUST NOT 규칙

| # | 금지 사항 |
|---|----------|
| 1 | 개발계획서 범위 외 기능을 구현하지 않음 |
| 2 | DSL 원본 파일을 수정하지 않음 |
| 3 | `src` 디렉토리 하위에 결과 파일을 생성하지 않음 |
| 4 | E2E Playwright 테스트를 자동 필수 단계로 수행하지 않음 |
| 5 | 사용자 확인 없이 GitHub 원격 저장소에 배포하지 않음 |
| 6 | 재시도 한도 없이 무한 루프로 진단/빌드/테스트를 반복하지 않음 |
| 7 | Playwright 안내 메시지 생성을 agent-developer에 위임하지 않음 |

## 검증 체크리스트

- [ ] Phase 0.2 입력 유효성 게이트 G0.1~G0.4 전부 통과
- [ ] 코드 진단 결과 에러 0 확인 (또는 한도 도달 후 사용자 승인 기록)
- [ ] 코드 빌드 성공 확인 (또는 한도 도달 후 사용자 승인 기록)
- [ ] 테스트 통과 확인 (또는 한도 도달 후 사용자 승인 기록)
- [ ] README.md 작성 확인
- [ ] 증거 파일 4종 (`diagnostics.json`, `build.log`, `test-report.xml`, `commands.md`) 생성 확인
- [ ] 개발계획서의 기술스택/아키텍처와 구현 일치 확인
- [ ] `app` 기준 소스 구조 사용 및 `src` 하위 미생성 확인
- [ ] 구현 / 스텁 / 제외 판정 결과가 보고되었는가
- [ ] 스텁 항목에 `TODO(sprint-2)` 마커가 존재하는가
- [ ] 챗봇 생성 여부를 개발계획서로 먼저 판단하고 사용자 확인을 거쳤는가
- [ ] 재시도 한도 사용 현황이 최종 보고에 포함되었는가
- [ ] 수동 Playwright 테스트 안내 메시지가 Phase 6에서 제공되었는가
- [ ] GitHub 배포를 수행한 경우 사용자 질문 및 배포 결과가 보고되었는가
