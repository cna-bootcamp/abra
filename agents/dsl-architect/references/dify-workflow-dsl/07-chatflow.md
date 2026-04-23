# Dify Workflow DSL 작성 가이드

> 분할 문서: 12장: Chatflow(advanced-chat) 완전 가이드
> 인덱스: [README](./README.md)
> 기존 진입점: [../dify-workflow-dsl-guide.md](../dify-workflow-dsl-guide.md)

---

## 12. Chatflow(advanced-chat) 모드 완전 가이드

> `app.mode: advanced-chat`(=Chatflow)는 Workflow와 구조·실행·저장 스키마가 달라 별도 규칙이 필요함.
> 본 섹션은 3절(conversation_variables), 5.11절(answer), 9절(Import Failures)에 흩어진 규칙을 한 곳에 통합.

### 12.1 모드 구분

| 항목 | Workflow | Chatflow(advanced-chat) |
|------|----------|-------------------------|
| `app.mode` | `workflow` | `advanced-chat` |
| 목적 | 단발 자동화(배치·변환·리포트) | 대화형(멀티턴) 어시스턴트 |
| 터미널 노드 | `type: end` | **`type: answer`** |
| 대화 상태 | 없음 | `workflow.conversation_variables[]` |
| 메모리 | 없음 | LLM/classifier 노드의 `memory` 블록 |
| 실행 API | `POST /v1/workflows/run` | `POST /v1/chat-messages` (streaming) |
| 세션 키 | `workflow_run_id` | `conversation_id` + `message_id` |

**결정 기준**: 여러 턴에 걸친 맥락 유지가 필요하면 Chatflow, 한 번의 입력으로 단일 산출물을 만들면 Workflow.

### 12.2 필수 구조

- `type: start` 노드 1개
- `type: answer` 노드 **≥1개** (모든 실행 경로가 수렴)
- `type: end` 노드 **사용 금지** — Chatflow는 end로 워크플로우를 종료하지 않고 answer가 응답 메시지를 생성함

### 12.3 conversation_variables 스키마

멀티턴 상태(사용자 프로필, 대화 진행 단계, 누적 이벤트 안 등)는 `workflow.conversation_variables[]`에 저장.

```yaml
workflow:
  conversation_variables:
    - id: 34b5e6a7-8c9d-4ef1-9a0b-1234567890ab   # UUID v4 필수
      name: stage_of_event
      value_type: string
      value: "gather"                              # 초기값
      description: "대화 단계: gather | deploy | past | general"
    - id: 7a1b2c3d-4e5f-4a6b-8c9d-0e1f2a3b4c5d
      name: event_draft
      value_type: object
      value: {}
      description: "현재 이벤트 초안 누적"
```

- **`id`는 UUID v4 필수** (Python: `uuid.uuid4()`). PostgreSQL `uuid` 컬럼이므로 비-UUID 문자열은 import 시 500 에러(`psycopg2 InvalidTextRepresentation: invalid input syntax for type uuid`)로 실패.
- `value_type`: `string | number | object | array[string] | array[number] | array[object]`.
- 노드에서 읽고 쓰기: `value_selector: [conversation, <name>]` 형태의 할당/참조, 템플릿에서는 `{{#conversation.<name>#}}`.
- 참고: `[conversation, ...]`, `[sys, ...]`, `[env, ...]`는 예약 스코프로 노드 ID 정규식 규칙(12.4) 예외.

### 12.4 Answer 노드 템플릿과 노드 ID 규칙

- Answer 노드의 `answer` 필드는 `{{#nodeId.field#}}` 템플릿을 포함할 수 있음.
- **Dify `VariableTemplateParser`는 정규식 `[a-zA-Z0-9_]{1,50}`으로 nodeId를 추출** — 하이픈(`-`)이 포함되면 매칭 실패.
- **귀결**: 모든 `node.id`, `edges[].source`, `edges[].target`, `value_selector`의 첫 요소, 템플릿의 `nodeId` 부분은 `^[a-zA-Z0-9_]{1,50}$`를 준수해야 함. 하이픈 금지, 언더스코어 사용.
- **예외**: `question-classifier`의 `classes[].id`(예: `class-gather`)는 클래스 핸들 ID로 별도 규칙이 적용되어 하이픈 허용.
- **위반 시 증상**(조용한 실패): 템플릿이 해석되지 않아 `{{#aggregator-1.output#}}` 원문이 사용자에게 그대로 응답됨. Workflow 실행 결과는 "Succeeded"이지만 최종 텍스트가 깨짐.

```yaml
# 올바른 예
- id: aggregator_1     # 언더스코어 사용
  type: variable-aggregator
  ...
- id: answer_1
  type: answer
  answer: '{{#aggregator_1.output#}}'   # VariableTemplateParser가 해석 가능

# 잘못된 예 — 조용한 실패
- id: aggregator-1     # 하이픈 포함
  type: variable-aggregator
  ...
- id: answer-1
  type: answer
  answer: '{{#aggregator-1.output#}}'   # 파서 매칭 실패 → 원문 출력
```

### 12.5 memory 블록 (권장 위치)

대화 흐름상 이전 발화를 참조해야 하는 LLM·classifier 노드에 포함. Chatflow 전용.

```yaml
- id: llm_propose_1
  type: llm
  data:
    model:
      provider: groq
      name: meta-llama/llama-4-scout-17b-16e-instruct
      mode: chat
    memory:
      window:
        enabled: true
        size: 10
      query_prompt_template: '{{#sys.query#}}'
    prompt_template:
      - role: system
        text: "..."
      - role: user
        text: '{{#sys.query#}}'
```

- `sys.query`는 사용자의 현재 입력(자동 주입).
- `memory.window.size`는 최근 N 턴만 context로 사용 (토큰 절약).
- classifier 노드에도 `memory` 블록을 넣으면 multi-turn intent 분류 정확도 향상.

### 12.6 실행 API

**서비스 API**:
```
POST /v1/chat-messages
Authorization: Bearer <app-api-key>
Content-Type: application/json

{
  "inputs": { "store_type": "cafe", "region": "강남" },
  "query": "이번 주말 이벤트 기획해줘",
  "user": "end-user-123",
  "conversation_id": "",            // 첫 턴은 빈 문자열, 이후 턴은 서버 반환값
  "response_mode": "streaming",     // Chatflow 권장 (answer 노드 출력 SSE)
  "files": [],
  "auto_generate_name": false
}
```

- 응답은 SSE(`event: message` / `event: message_end` 등) 스트림.
- 멀티턴 연속 호출 시 직전 응답의 `conversation_id`를 다음 요청에 그대로 전달.

**콘솔 API(관리자 기능)**: 쿠키 기반 인증, `/console/api/apps/{app_id}/...` 경로. 배포·관리는 콘솔 API, 사용자 런타임은 서비스 API로 분리.

### 12.7 Chatflow 고유 Import / Runtime Failures Top 5

| # | 증상 | 근본 원인 | 수정 |
|---|------|----------|------|
| 1 | Import 500 — `psycopg2 InvalidTextRepresentation: invalid input syntax for type uuid` | `conversation_variables[].id`가 UUID 형식 아님 | 각 id를 `uuid.uuid4()` 값으로 교체 |
| 2 | Run 성공이지만 Answer 노드가 `{{#x.y#}}` 원문 반환 | 노드 ID에 하이픈 포함 → VariableTemplateParser 매칭 실패 | 모든 `node.id` / 엣지 / selector / 템플릿 참조의 `-`→`_` 일괄 치환 |
| 3 | Run 실패 — `Output X is missing.` (code 노드) | 특정 branch/preset가 선언된 outputs 키를 반환하지 않음 | `main()` 끝에 `setdefault` 루프로 누락 필드 보충 |
| 4 | classifier 간헐 실패 — `got invalid json object. error: Expecting ',' delimiter` | reasoning 모델(예: `openai/gpt-oss-120b`)이 JSON에 reasoning 토큰 주입 | instruction-tuned 모델로 교체(`meta-llama/llama-4-scout-17b-16e-instruct` 등) + `temperature: 0` |
| 5 | Import는 성공하지만 실행 결과가 저장되지 않거나 응답이 없음 | Chatflow 모드인데 터미널이 `type: end` | 모든 터미널을 `type: answer`로 교체 |

[Top](#dify-workflow-dsl-작성-가이드)
