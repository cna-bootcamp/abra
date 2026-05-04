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

AI_RUNTIME 자동 감지 및 업데이트:  
`{ABRA_PLUGIN_DIR}/resources/guides/call-subagent.md`의 **"0. AI_RUNTIME 자동 감지"** 규칙에 따라 현재 런타임을 감지하고 AGENTS.md의 `AI_RUNTIME` 값을 업데이트.

## 용어집

| 용어 | 정의 |
|---|---|
| `{PROJECT_DIR}` | AGENTS.md 환경변수 섹션의 `PROJECT_DIR` 값 |
| `{output_dir}` | `{PROJECT_DIR}/output` (고정) |
| `{ABRA_PLUGIN_DIR}` | AGENTS.md 환경변수 섹션의 `ABRA_PLUGIN_DIR` 값 |

## 참조

| 문서 | 경로 | 용도 |
|------|------|------|
| 개발 프롬프트 템플릿 | `{ABRA_PLUGIN_DIR}/agents/agent-developer/references/develop.md` | 백엔드 구현 위임 시 참조 |
| 프론트엔드 프롬프트 템플릿 | `{ABRA_PLUGIN_DIR}/agents/frontend-developer/references/frontend.md` | 프론트엔드 구현 위임 시 참조 |

## 에이전트 호출 규칙

### 에이전트 FQN

| 에이전트 | FQN |
|----------|-----|
| agent-developer | `abra:agent-developer:agent-developer` |
| frontend-developer | `abra:frontend-developer:frontend-developer` |

### 프롬프트 조립

- `{ABRA_PLUGIN_DIR}/resources/guides/combine-prompt.md`에 따라 AGENT.md + agentcard.yaml + tools.yaml 합치기
- `Agent(subagent_type=FQN, model=tier_mapping 결과, prompt=조립된 프롬프트)` 호출
- tier → 모델 매핑은 `{ABRA_PLUGIN_DIR}/gateway/runtime-mapping.yaml` 참조

### 서브 에이전트 호출

워크플로우 단계에 `Agent: {agent-name}`이 명시된 경우,
메인 에이전트는 해당 단계를 직접 수행하지 않고, `{ABRA_PLUGIN_DIR}/resources/guides/call-subagent.md`에 따라 서브 에이젼트 호출 

## 진행상황 업데이트 및 재개

`{PROJECT_DIR}/AGENTS.md`에 각 Phase 완료 시 저장. 최종 완료 시 `Done`으로 표기.

```md
## 워크플로우 진행상황
- {skill-name}: Phase3
```

진행상황 정보가 있는 경우 마지막 완료 단계 이후부터 자동 재개.

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

판정 룰 (오버라이드 우선 적용):

- 항목 5(MCP 여부) = Yes → 다른 항목과 무관하게 **"테스트 챗봇 미생성 추천"** (오버라이드)
- 항목 5 = No이고 항목 1~4 중 2개 이상 Yes → **"테스트 챗봇 생성 추천"**
- 그 외 → **"테스트 챗봇 미생성 추천"**

#### 실행 규칙

- 판정 근거를 사용자에게 제시하고 확인 요청
- 사용자 승인 시 `run_context.chatbot = force`
- 사용자 거부 시 `run_context.chatbot = skip`

### Phase 2: 코드 기반 구현 → Agent: agent-developer

- **TASK**: 개발계획서 기반 프로덕션 코드 구현 및 검증 수행
- **EXPECTED OUTCOME**: 빌드 성공 + 테스트 통과 + README.md 포함 완성 코드 + `{output_dir}/evidence/` 증거 파일 + 개발결과 레포트(`{output_dir}/develop-report.md`)
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
  - Playwright 테스트 안내 메시지 생성은 agent-developer에 위임 금지 (Phase 5에서 직접 처리)
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
- `{output_dir}/evidence/` 4개 파일 생성 여부
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
- 재호출 시 재시도 예산은 4개 카운터(`diagnostics=5`, `build=3`, `test=3`, `total=10`) 모두 재발급
- 재호출 누적 3회 초과 시 사용자에게 escalation

### Phase 3.5: 프론트엔드 개발

코드 기반 백엔드 구현이 통과한 뒤(Phase 3 완료), 사용자 인터페이스가 필요한 경우
프론트엔드 SPA를 생성하고 백엔드와 통합함. GitHub 배포(Phase 4) 전에 수행하여
push 시 프론트·백엔드·통합 패치가 함께 배포되도록 함.

#### Step 1: 프론트엔드 필요 여부 판정 + 사용자 확인

**판정 입력**: `{output_dir}/dev-plan.md`의 `§3 사용자 인터페이스` + `§9 배포 계획`만 사용

**판정 룰**:

| 조건 | 판정 |
|---|---|
| dev-plan에 "웹 UI", "모바일 웹", "관리자 화면", "사용자 화면" 등 명시 | **권장** |
| `MCP 서버 단독`, `API only`, `백엔드 only`, `Streaming HTTP MCP만` 명시 | **미권장** |
| §3 부재 또는 인터페이스 명세 모호 | **미권장** (사용자 확인 필요) |

**실행 규칙**:

- AskUserQuestion 도구로 판정 결과·근거 제시 후 사용자 승인 요청
- 사용자 승인 시 Step 2 진입
- 사용자 거부 시 `run_context_frontend.skip = true` → Phase 4로 직진

#### Step 2: 기술스택 선택

AskUserQuestion 도구로 다음 중 선택:

- `Vue 3 + Vite` (권장 — 검증 완료 스택)
- `React + Vite`
- `Skip` (이번 턴에는 프론트 미생성)

선택 결과를 `run_context_frontend.tech_stack`에 저장.
`Skip` 선택 시 `run_context_frontend.skip = true` → Phase 4로 직진.

#### Step 3: 이미지 자동 생성 옵션 + GEMINI_API_KEY 수집

AskUserQuestion 도구로 이미지 자동 생성 필요 여부 문의:

- `예` 선택 시:
  1. AskUserQuestion으로 GEMINI_API_KEY 입력 요청
     - 미보유 안내: `https://aistudio.google.com/apikey`
  2. 입력값을 `{ABRA_PLUGIN_DIR}/gateway/tools/.env` 파일의 `GEMINI_API_KEY=...` 행에 저장 (없으면 생성)

- `아니오` 선택 시: `image_generation.enabled = false` 로 진행

#### Step 4: frontend-developer 서브에이전트 호출 → Agent: frontend-developer

- **TASK**: 선택된 스택으로 SPA 구현 + 백엔드 통합 패치 + 빌드 검증 수행
- **EXPECTED OUTCOME**: `frontend/` 디렉토리, 백엔드 패치 3종(CORS/StaticFiles+SPA 라우트/멀티스테이지 Dockerfile), 빌드 성공, `GET /` 200 + HTML 검증, `{output_dir}/develop-frontend-report.md` + `{output_dir}/evidence/frontend/` 4개 증거 파일
- **MUST DO**:
  - `{ABRA_PLUGIN_DIR}/agents/frontend-developer/references/frontend.md` 프롬프트 템플릿 활용
  - 개발계획서·시나리오·DSL 원본 그대로 전달
  - 최소 실행 컨텍스트(`run_context_frontend`)만 전달 (재시도 한도 + Lessons Learned 5종 강제 주입)
  - 화면 매핑·컴포넌트 분리·API 클라이언트 설계는 frontend-developer가 수행
  - 백엔드 통합 패치는 frontend-developer가 직접 적용 (agent-developer 위임 금지)
- **MUST NOT DO**:
  - `develop` 스킬이 상세 구현 계약을 임의 작성하지 않음
  - 백엔드 통합 패치를 develop 스킬·agent-developer가 수행하지 않음 (frontend-developer 책임)
  - `app.mount("/", StaticFiles(html=True))` 패턴 사용 금지 — `/assets` 마운트 + `GET /` 명시 라우트만 허용
  - 시스템 `uvicorn` 사용 금지 — 검증은 `uv run uvicorn`으로 수행
- **CONTEXT**:
  - 개발계획서: `{output_dir}/dev-plan.md`
  - 시나리오: `{output_dir}/scenario.md`
  - DSL: `{output_dir}/<latest>.dsl.yaml`
  - 백엔드 진입점: `{PROJECT_DIR}/app/main.py`
  - 백엔드 라우트: `{PROJECT_DIR}/app/api/routes.py`
  - 선택된 스택 템플릿: `{ABRA_PLUGIN_DIR}/agents/frontend-developer/references/{tech_stack}-template/`
  - 증거 디렉토리: `{output_dir}/evidence/frontend/`

```yaml
run_context_frontend:
  dev_plan_path: "{output_dir}/dev-plan.md"
  scenario_path: "{output_dir}/scenario.md"
  dsl_path: "{output_dir}/<latest>.dsl.yaml"
  backend_source_root: "app"
  frontend_source_root: "frontend"
  tech_stack: vue3-vite | react-vite
  image_generation:
    enabled: true | false
    api_key_env: "GEMINI_API_KEY"
    tool_path: "{ABRA_PLUGIN_DIR}/gateway/tools/generate_image.py"
  api_key_env: "VITE_API_KEY"
  retry_budget:
    diagnostics: 3
    build: 3
    test: 2
    total: 8
  lessons_learned:
    - "[HIGH] 시스템 uvicorn(0.34) vs uv run uvicorn(0.46) 버전 차이로 정적 파일 silent 404 → 반드시 `uv run uvicorn` — 출처: develop/Phase3.5"
    - "[HIGH] FastAPI에서 `app.mount('/', StaticFiles(html=True))` 동작 불안정 → `/assets` 마운트 + `GET /` 라우트로 `FileResponse(static/index.html)` 명시 — 출처: develop/Phase3.5"
    - "[MED] `os.path.dirname(__file__)` 상대경로 문제 → `Path(__file__).resolve().parent.parent` 사용 — 출처: develop/Phase3.5"
    - "[MED] Windows에서 포트 점유 프로세스는 PowerShell `Stop-Process -Id <pid> -Force` 필요 — 출처: develop/Phase3.5"
    - "[MED] Git Bash `curl`의 `/` 경로 변환 문제 → `urllib.request.urlopen` 사용 — 출처: develop/Phase3.5"
```

#### Step 5: 결과 검토

frontend-developer 결과를 검토하고 다음을 확인:

1. `frontend/` 디렉토리에 source(`src/`, `vite.config.js|ts`, `package.json`) 생성 여부
2. 백엔드 통합 3종 패치 적용 여부:
   - `app/main.py` — `CORSMiddleware` + `/assets` 마운트 + `GET /` SPA 라우트
   - `deploy/Dockerfile` — node:20-slim 빌드 스테이지 + `COPY --from`
   - `frontend/.env` (`VITE_API_KEY` = 백엔드 `API_KEY`)
3. `npm install` + `npm run build` 성공 여부 + `static/` 정적 산출물 생성
4. 통합 검증 결과 (`urllib.request`로 `GET /` 200 + HTML, `GET /health` 200 확인)
5. `{output_dir}/evidence/frontend/` 4종 증거 파일 (build.log, npm-audit.json, verify-output.txt, commands.md)
6. `{output_dir}/develop-frontend-report.md` 12개 항목 작성 여부
7. handoff 보고 여부 (있다면 차단성 확인)

**한도 도달 시 조치** (Phase 3과 동일 패턴):

- **build_exhausted**: 근본원인 가설 3개 사용자 제시 → 사용자 판단 반영하여 재호출
- **verify_exhausted**: 실패한 검증 항목 사용자 보고 → 사용자 판단(skip/재호출) 반영

**Handoff 수신 시 조치**:

- `target: agent-developer` + `blocker: true` → Phase 2(백엔드) 재호출 사용자 확인
- `target: plan-writer` + `blocker: true` → `/abra:dev-plan` 재실행 사용자 확인
- `blocker: false` → 임시 처리된 항목을 보고에 표시하고 Phase 4 진행

### Phase 4: GitHub 배포 여부 사용자 확인

### Step 0: GitHub 배포 여부 확인

AskUserQuestion 도구로 사용자에게 GitHub Repository 생성·배포 진행 여부를 확인함.  
배포를 원하지 않으면 Phase 4 전체를 스킵하고 Phase 5(최종 보고)로 직진함.  
배포를 원하면 Step 1 진행.

### Step 1: GitHub 인증 정보 수집

사용자에게 GitHub 인증 정보를 수집함.

AskUserQuestion 도구로 다음 정보를 순차적으로 문의:

1. **GitHub 계정 보유 여부**
   - 보유: 다음 단계로 진행
   - 미보유: 계정 생성 안내 (`https://github.com/signup`)

2. **GitHub Username** 입력 요청

3. **Private Repository 사용 여부** 입력 요청

4. **Personal Access Token (PAT)** 입력 요청
   - 미보유 시: 토큰 생성 안내 (`https://github.com/settings/tokens/new?scopes=repo`)
   - PAT 필요 권한: `repo` (전체)

5. **Organization 사용 여부**
   - 개인 계정 사용: username을 owner로 설정
   - Organization 사용: org 이름 입력 요청
   - Organization 미보유 시: 생성 안내 (`https://github.com/account/organizations/new`)

6. **토큰 저장**
   - 플러그인 디렉토리에 `{PROJECT_DIR}/.temp/secrets/` 디렉토리 생성
   - `{PROJECT_DIR}/.temp/secrets/git-token.env` 파일에 저장:
     ```
     GITHUB_USERNAME={username}
     GITHUB_TOKEN={token}
     GITHUB_OWNER={owner}
     ```
   - `{PROJECT_DIR}/.gitignore`에 `.temp/` 패턴이 포함되어 있는지 확인, 없으면 추가

### Step 2: 원격 저장소 생성 및 Push

`{ABRA_PLUGIN_DIR}/gateway/tools/create_repo.py` 도구를 사용하여 GitHub 저장소 생성 + 로컬 Git 초기화 + Push를 한번에 수행함.
`gh` CLI 설치가 불요하며, Python 표준 라이브러리만 사용.

**분기 결정**: 현재 프로젝트가 이미 git 저장소이고 `git remote -v`에 origin이 설정되어 있으면 5단계(업데이트 배포)만 수행함. 그 외 신규 저장소는 1~4단계(신규 생성)를 수행함.

1. 저장소명 결정: 현재 프로젝트 디렉토리명에서 추출
2. Description: `{output_dir}/dev-plan.md`의 '프로젝트명, 목적' 참조하여 작성  
3. `.gitignore` 존재 확인 
4. `create_repo.py` 실행:
   ```
   python {ABRA_PLUGIN_DIR}/gateway/tools/create_repo.py \
     --name {repo-name} \
     --desc "{description}" \
     --private {true/false} \
     --token {PAT} \
     --dir {PROJECT_DIR}
   ```
   - Organization 사용 시: `--org {org}` 옵션 추가
5. 이미 git 저장소이고 원격이 설정된 경우 (업데이트 배포):
   ```
   git add .
   git commit -m "{변경사항}"
   git push
   ```

> `create_repo.py`가 수행하는 작업: 저장소 존재 여부 확인 → 원격 저장소 생성 →
> `git init` → `git remote add origin` → 초기 커밋 → `git push -u origin main`

### Step 2.5: 원격 URL 보안 검증 (자동)

1. 원격 URL 확인:
   ```
   git remote -v
   ```
2. 토큰 패턴 감지 (`ghp_`, `github_pat_`, `gho_`, `ghu_` 등):
   - 정규식: `https://[^@]+@github\.com/`
3. 토큰 발견 시 자동 수정:
   ```
   git remote set-url origin https://github.com/{owner}/{repo}.git
   ```
4. 수정 후 사용자에게 알림 및 PAT 폐기 안내:
   > ⚠️ 원격 URL에서 토큰이 발견되어 제거함. 해당 토큰을 즉시 폐기 권장.
   > GitHub → Settings → Developer settings → Personal access tokens → 해당 토큰 삭제
5. 토큰 미발견 시: `✅ 원격 URL에 토큰 노출 없음` 한 줄 보고로 검증 완료 표시

### Step 3: 완료 메시지 

Git Push 완료 후 Git Repository 등록 메시지 표시 


### Phase 5: 최종 보고 + 수동 Playwright 테스트 안내

Phase 0~4 결과를 종합 보고.

- 개발 결과 레포트 경로 
- 어플리케이션 수행 방법  
- 사용자 검증 방법
  최종 보고에 3단계 검증 수단을 명시.

  | 단계 | 수단 | 자동화 | 책임 |
  |---|---|---|---|
  | 1차 | MCP Client E2E (`tests/e2e/`) | 자동 | agent-developer |
  | 2차 | 테스트 챗봇 (선택) | 반자동 | agent-developer (Phase 1 force일 때) |
  | 3차 | 수동 Playwright | 사용자 | develop 스킬 (프론트엔드 개발 시에만. 아래 안내 메시지) |

  Playwright 테스트 안내 메시지: 
  E2E 자동 실행 대신, 최종 보고 시 아래 예제를 프로젝트에 맞게 수정하여 안내 메시지로 제공.
  ```md
  # Playwright MCP를 이용하여 AI 직접 테스트 요청
  ※ 주의: Playwright MCP는 스크린샷 이미지를 캡처해서 수행하므로 토큰 소비 많음  
  ※ 낮은 모델 사용 권장, 사용자가 일부 준비 동작 직접 수행

  - 아래 프롬프트로 요청
    > Playwright MCP로 {프론트엔드 URL}에 접근해 주세요.
    > {로그인이 필요하면} id: {본인id}, pw: {본인pw}로 로그인해 주세요.
  - 사용자가 테스트할 대상 화면을 직접 열거나 필요한 사전 동작 수행
  - 에러 발생 또는 개선 필요 시 수정 요청
    > {에러 또는 개선 내용}
  ```

## 완료 조건

- [ ] 코드 빌드 성공 (한도 내)
- [ ] 테스트 통과 (한도 내)
- [ ] README.md 작성 완료
- [ ] `{output_dir}/develop-report.md` 생성
- [ ] `{output_dir}/evidence/` 4개 증거 파일 생성
- [ ] (Phase 3.5 진행 시) `frontend/` 디렉토리 + 백엔드 통합 패치 3종 + `static/` 정적 산출물 생성 + `{output_dir}/develop-frontend-report.md` + `{output_dir}/evidence/frontend/` 4개 파일 생성
- [ ] (Phase 3.5 진행 시) `uv run uvicorn` 백엔드 기동 후 `urllib.request`로 `GET /` 200(HTML) + `GET /health` 200 검증 완료
- [ ] 산출물 및 증거 보고 완료
- [ ] 수동 Playwright 테스트 안내 메시지 제공 완료 (develop 스킬이 직접 생성)
- [ ] GitHub 배포를 수행한 경우 배포 결과 보고 완료

## 상태 정리
- 백엔드/프론트엔드 프로세스를 모두 종료  
- 임시 파일 없음.  
- 완료 시 AGENTS.md 진행상황을 `develop: Done`으로 최종 갱신함.

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
| 10 | 수동 Playwright 테스트 안내 메시지는 develop 스킬이 Phase 5에서 직접 생성함 |
| 11 | Phase 3.5에서 프론트엔드 필요 여부는 dev-plan §3·§9만 보고 판정한 뒤 반드시 사용자 확인을 거침 |
| 12 | Phase 3.5에서 기술스택 선택 + 이미지 생성 옵션 + GEMINI_API_KEY 수집을 사용자에게 순차 문의함 |
| 13 | 백엔드 통합 패치(CORSMiddleware, StaticFiles, FileResponse SPA 라우트, 멀티스테이지 Dockerfile)는 frontend-developer가 직접 적용함 |
| 14 | 검증 시 `uv run uvicorn`을 사용함 (시스템 `uvicorn` 사용 금지) |
| 15 | HTTP 검증은 `urllib.request`로 수행함 (Git Bash `curl` 경로변환 회피) |

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
| 8 | 프론트엔드 필수 여부 자동 판정(사용자 확인 없이 자동 진행) 금지 |
| 9 | `app.mount("/", StaticFiles(html=True))` 패턴 사용 금지 — `/assets` 마운트 + `GET /` 명시 라우트만 허용 |
| 10 | `os.path.dirname(__file__)` 상대경로 사용 금지 — `Path(__file__).resolve()` 사용 |
| 11 | 백엔드 통합 패치를 develop 스킬·agent-developer에 위임 금지 (frontend-developer 책임) |

## 검증 체크리스트

- [ ] Phase 0.2 입력 유효성 게이트 G0.1~G0.4 전부 통과
- [ ] 코드 진단 결과 에러 0 확인 (또는 한도 도달 후 사용자 승인 기록)
- [ ] 개발계획서의 기술스택/아키텍처와 구현 일치 확인
- [ ] `app` 기준 소스 구조 사용 및 `src` 하위 미생성 확인
- [ ] 구현 / 스텁 / 제외 판정 결과가 보고되었는가
- [ ] 스텁 항목에 `TODO(sprint-2)` 마커가 존재하는가
- [ ] 챗봇 생성 여부를 개발계획서로 먼저 판단하고 사용자 확인을 거쳤는가
- [ ] 재시도 한도 사용 현황이 최종 보고에 포함되었는가
- [ ] (Phase 3.5 진행 시) 프론트엔드 필요 여부·기술스택·이미지 옵션·GEMINI_API_KEY 4개 질의를 순차 수행했는가
- [ ] (Phase 3.5 진행 시) 백엔드 통합 패치 3종(`app/main.py` CORS+`/assets`+`GET /`, 멀티스테이지 Dockerfile, `.gitignore` 보강)이 모두 적용되었는가
- [ ] (Phase 3.5 진행 시) `uv run uvicorn` + `urllib.request` 검증으로 `GET /` 200(HTML) 응답을 확인했는가
