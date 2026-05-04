---
name: dsl-generate
description: Dify DSL 자동생성 (STEP 2)
user-invocable: true
type: orchestrator
---

# DSL Generate

[DSL-GENERATE 활성화]

## 목표

선택된 시나리오 문서를 기반으로 Dify Workflow DSL(YAML)을 자동 생성함.
DSL 구조 검증을 통과한 유효한 파일을 산출하며, 에러 발생 시 수정 루프를 통해 자동 복구함.

## 활성화 조건

- "DSL 생성", "워크플로우 DSL", "YAML 만들어", "dsl-generate" 키워드 감지 시
- `/abra:dsl-generate` 명령 호출 시

## 작업 환경 변수 로드 
AGENTS.md 파일에서 `## 환경변수`섹션의 환경변수 로딩. 로딩 실패 시 사용자에게 Setup 스킬을 먼저 수행하라고 안내하고 종료.

AI_RUNTIME 자동 감지 및 업데이트:  
`{ABRA_PLUGIN_DIR}/resources/guides/call-subagent.md`의 **"0. AI_RUNTIME 자동 감지"** 규칙에 따라 현재 런타임을 감지하고 AGENTS.md의 `AI_RUNTIME` 값을 업데이트.

## 에이전트 호출 규칙

### 에이전트 FQN

| 에이전트 | FQN |
|----------|-----|
| dsl-architect | `abra:dsl-architect:dsl-architect` |

### 프롬프트 조립
- `{ABRA_PLUGIN_DIR}/resources/guides/combine-prompt.md`에 따라 AGENT.md + agentcard.yaml + tools.yaml 합치기
- `Agent(subagent_type=FQN, model=tier_mapping 결과, prompt=조립된 프롬프트)` 호출
- tier → 모델 매핑은 `{ABRA_PLUGIN_DIR}/gateway/runtime-mapping.yaml` 참조

### 서브 에이전트 호출
워크플로우 단계에 `Agent: {agent-name}`이 명시된 경우,
메인 에이전트는 해당 단계를 직접 수행하지 않고, `{ABRA_PLUGIN_DIR}/resources/guides/call-subagent.md`에 따라 서브 에이젼트 호출 

## 진행상황 업데이트 및 재개
`{PROJECT_DIR}/AGENTS.md`에 각 Phase 완료 시 저장. 최종 완료 시 'Done'으로 표기.   
```
## 워크플로우 진행상황
- dsl-generate: Phase3
```
진행상황 정보가 있는 경우 마지막 완료 단계 이후부터 자동 재개

## 워크플로우

### Phase 0: 입력문서 확인

scenario.md 파일 존재 여부를 확인함.

- **존재**: Phase 1로 진행
- **없음**: scenario 스킬로 위임 (`/abra:scenario`)

### Phase 1: 기술 설정 수집 (대화형)
대화형 질문을 수행하고 결과를 Phase 1 호출 프롬프트에 context로 전달함.

**질문 규칙:**
- 한 번에 하나의 질문만 하고, 응답을 받은 후 다음으로 진행
- 가능한 **객관식 선택지** 제공, 직접 입력 옵션 포함
- 사용자가 "기본값" / "기본" / "default" 응답 시 남은 질문에 모두 기본값 적용
- 사용자가 "전부 기본값"이라고 답하면 남은 질문 모두 건너뛰고 기본값 적용
- 사용자가 `0` / `취소` / `cancel` 선택 시 DSL 생성 즉시 중단 + 안내 출력
- 모든 질문 완료 후 설정 요약을 보여주고 사용자 확인 후 Phase 1 진행

**조건부 질문:** 요구사항 문서(`output/scenario.md`)를 먼저 파싱하여 아래 조건에 따라 질문 4~6 표시 여부 결정.
- 질문 4 (외부 서비스): 요구사항에 외부 연동/API 호출이 있는 경우만
- 질문 5 (파일 업로드): 요구사항에 파일 처리가 있는 경우만
- 질문 6 (시작 메시지): 서비스 유형이 Chatflow인 경우만

---
질문 시작 전 요구사항 문서(`output/scenario.md`)를 바탕으로 AI 사용 목적을 식별하여 `{AI 사용 목적}`변수에 할당.  

**질문 1: AI 모델 제공자**
```
AI의 사용 목적은 `{AI 사용 목적}`입니다.
어떤 AI 제공자(공급사)를 사용할지 선택합니다.

1. OpenAI
2. Anthropic
3. Google
4. Groq
5. 직접 입력 (provider 이름): ___
0. 취소
```
- 확정 결과 → `selected_provider`

---

**질문 2: AI 모델명**

선택한 제공자(`{selected_provider}`)에서 사용할 모델을 선택합니다.
제공자별 대표 모델을 기본 옵션으로 제시하고, "최신 모델 추천"을 통해 웹 검색으로 최신 모델을 조회할 수 있습니다.

```
`{selected_provider}`에서 사용할 모델을 선택합니다.

<제공자별 대표 모델 옵션 동적 생성 — 2026-04 기준, 모두 instruction-tuned 권장 모델>
- OpenAI     → 1. gpt-5.4 (고성능)               2. gpt-5.4-mini (경량)           3. gpt-5.4-nano (초경량)
- Anthropic  → 1. claude-opus-4-7 (고성능)        2. claude-sonnet-4-6 (범용)      3. claude-haiku-4-5-20251001 (경량)
- Google     → 1. Gemini 3.1 Pro Preview (고성능)  2. Gemini 3.1 Flash-Lite Preview (경량)
- Groq       → 1. gpt-oss-120b (고성능)
               2. gpt-oss-20b (범용)
               3. deepseek-r1-distill-llama-70b (추론)
               4. moonshotai/kimi-k2-instruct (범용)
               5. qwen3-32b (범용)
               6. meta-llama/llama-4-scout-17b-16e-instruct (멀티모달, 기본값)

N-1. 최신 모델 추천 — `{selected_provider}`의 최신 모델을 웹 검색으로 조회 후 재선택
N.   직접 입력 (모델명): ___
0.   취소
```

> **⚠ 비권장 모델 (선택 금지)**: reasoning 계열 모델은 question-classifier 노드의 JSON 출력에
> reasoning 토큰을 주입하여 `Expecting ',' delimiter` 류의 파싱 오류를 간헐적으로 일으킴.
> `selected_model`은 워크플로우 전체 LLM/Classifier 노드 기본값으로 적용되므로 classifier가
> 하나라도 포함된 DSL에서는 런타임 실패로 이어짐.
>
> - Groq: `qwen-qwq-32b`, `llama-3.1-405b-reasoning`
> - 기타 provider: `o1-*`, `o3-*`(OpenAI reasoning), `gemini-*-thinking` 계열 등 동일 원리 적용
>
> "직접 입력"으로 위 모델이 입력되면 경고를 띄우고 재선택 유도.

- "최신 모델 추천" 선택 시: 웹 검색으로 `{selected_provider}`의 현재 최신 instruction-tuned 모델 조회
  → 고성능/경량 2가지 추천 (reasoning 모델 제외) → 사용자 재선택
- 확정 결과 → `selected_model`
- 입력값 검증: 확정 전 비권장 모델 목록과 대조, 일치 시 경고 후 재확인 필요

---

**질문 3: AI 응답 스타일**
```
AI의 사용 목적은 `{AI 사용 목적}`입니다. 
AI가 얼마나 일관되게 또는 유연하게 답변할지를 결정합니다.
분류처럼 정확한 결과가 필요하면 '정확하게', 콘텐츠 생성처럼 다양한 표현이 필요하면 '창의적'을 선택합니다.

1. 정확하게 (temperature=0.2) — 분류/추출 등 정확도 중심
2. 균형 (temperature=0.7) — 기본값
3. 창의적 (temperature=1.0) — 생성/브레인스토밍
4. 직접 입력 (0.0~1.0): ___
0. 취소
```
- 확정 결과 → `response_style` (`precise` / `balanced` / `creative` / float)

---

**질문 4: 외부 서비스 연동 정보** (요구사항에 외부 연동이 있는 경우만)
```
요구사항에서 {연동 서비스명}과의 연동이 필요합니다.
연결 주소(URL)나 인증 키를 지금 입력하면 DSL에 바로 반영됩니다.

1. 나중에 설정 (기본값)
2. 직접 입력: ___
0. 취소
```

- 확정 결과 → `external_service_config` (빈 문자열 또는 URL/키)

---

**질문 5: 파일 업로드 허용** (요구사항에 파일 처리가 있는 경우만)
```
사용자가 스크린샷·문서 등 파일을 첨부할 수 있도록 할지 결정합니다.

1. 허용하지 않음 (기본값)
2. 이미지만 허용
3. 문서만 허용 (PDF, DOCX, Excel 등)
4. 이미지 + 문서 모두 허용
5. 직접 입력: ___
0. 취소
```

- 확정 결과 → `file_upload` (`none` / `image` / `document` / `both` / 문자열)

---

**질문 6: 대화 시작 메시지** (Chatflow인 경우만)
```
사용자가 처음 접속했을 때 대화창에 보여줄 안내 메시지를 설정할 수 있습니다.

1. 없음 (기본값)
2. "안녕하세요! 무엇을 도와드릴까요?"
3. 요구사항의 서비스 목적을 기반으로 자동 생성
4. 직접 입력: ___
0. 취소
```

- 확정 결과 → `conversation_start` (빈 문자열 또는 메시지)

---

**수집 완료 후:** 아래 형태의 요약을 사용자에게 보여주고 확인 후 Phase 1 진행.

```yaml
context:
  selected_provider: <값>
  selected_model: <값>
  response_style: <값>
  external_service_config: <값>
  file_upload: <값>
  conversation_start: <값>
```

> 이 context는 Phase 2의 dsl-architect 호출 프롬프트에 명시적으로 포함되어야 함.

### Phase 2: DSL 생성 → Agent: dsl-architect

- **TASK**: 시나리오 문서를 기반으로 Dify Workflow DSL(YAML) 생성 및 사전 검증
- **EXPECTED OUTCOME**: `validate_dsl` 검증을 통과한 유효한 DSL YAML 파일 + DSL 구조 설명서
- **MUST DO**:
  - `{ABRA_PLUGIN_DIR}/agents/dsl-architect/references/dify-workflow-dsl-guide.md` DSL 작성 가이드 준수
  - **Phase 0.5에서 수집한 기술 설정(context)을 호출 프롬프트에 명시적으로 포함**
  - 생성 후 `{tool:dsl_validation}`으로 반드시 사전 검증
  - 노드 설계 (Start → LLM/Tool/IF-ELSE → End)
  - 엣지 연결 및 변수 흐름 정의
  - 프롬프트 템플릿 작성
- **MUST NOT DO**:
  - Dify 실행 금지 (프로토타이핑은 별도 STEP)
  - 시나리오 수정 금지
  - 사용자에게 직접 질문 금지
- **CONTEXT**:
  - 시나리오 파일: `output/scenario.md` (기본값)
  - Phase 1 수집 결과: `selected_provider`, `selected_model`, `response_style`,
    `external_service_config`, `file_upload`, `conversation_start`

### Phase 3: DSL 검증 확인

dsl-architect 에이전트가 내부 Step 8에서 이미 `validate_dsl`을 실행했음.  
본 단계는 에이전트 산출물의 검증 통과 여부를 오케스트레이터가 최종 확인하는 단일 통과 단계임.

#### 검증 절차

1. `PYTHONIOENCODING=utf-8` 환경 변수 설정 후 `validate_dsl` 도구로 DSL YAML 파일 검증
2. 검증 결과 판정:
   - **PASS**: Phase 4로 진행
   - **FAIL**: 에러 항목을 사용자에게 보고하고 중단 (재시도 없음)  
     → 재실행 필요 시 사용자가 `/abra:dsl-generate`를 다시 호출하거나 오류 내용 확인 후 수동 수정

### Phase 4: 결과 보고

DSL 파일 생성 완료를 사용자에게 보고함.

**보고 내용:**
- DSL 파일 경로
- DSL 구조 설명서
- 다음 단계 안내: `/abra:prototype` (프로토타이핑)

## 완료 조건

- [ ] DSL YAML 파일 생성 완료
- [ ] validate_dsl 검증 통과
- [ ] DSL 구조 설명서 출력 완료

## 검증 프로토콜

완료 전 검증:
- DSL 파일이 `output/` 디렉토리에 존재하는지 확인
- validate_dsl 검증 결과가 PASS인지 확인
- DSL 구조 설명서가 출력되었는지 확인

## 상태 정리

완료 시 임시 파일 없음. 상태 파일 미사용.

## MUST 규칙

| # | 규칙 |
|---|------|
| 1 | validate_dsl 검증을 반드시 통과해야 한다 |
| 2 | Phase 0.5에서 수집한 기술 설정을 dsl-architect 호출 프롬프트에 context로 전달한다 |
| 3 | {ABRA_PLUGIN_DIR}/agents/dsl-architect/references/dify-workflow-dsl-guide.md DSL 작성 가이드를 준수한다 |
| 4 | 노드 설계, 엣지 연결, 변수 흐름을 모두 정의한다 |
| 5 | DSL 구조 설명서를 출력한다 |

## MUST NOT 규칙

| # | 금지 사항 |
|---|----------|
| 1 | Dify에 직접 실행(import/publish/run)하지 않는다 (프로토타이핑은 별도 STEP) |
| 2 | 시나리오 문서를 수정하지 않는다 |
| 3 | 사용자에게 직접 질문하지 않는다 (에이전트 내에서) |

## 검증 체크리스트

- [ ] DSL YAML 파일이 output/ 디렉토리에 존재하는가
- [ ] validate_dsl 검증 결과가 PASS인가
- [ ] DSL 구조 설명서가 출력되었는가
- [ ] 노드-엣지 연결이 완전한가 (orphan 노드 없음)
