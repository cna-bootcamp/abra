# Dify Workflow DSL 작성 가이드

> 분할 문서: 5.1-5.7절: 핵심 노드 레퍼런스
> 인덱스: [README](./README.md)
> 기존 진입점: [../dify-workflow-dsl-guide.md](../dify-workflow-dsl-guide.md)

---

## 5. 노드 유형별 DSL 작성법

### 5.1 start (시작 노드)

모든 워크플로우의 진입점. 캔버스당 하나만 존재 가능:

```yaml
- data:
    desc: '사용자 입력 수집'
    title: 시작
    type: start
    variables:
    - label: 고객명              # UI 표시 레이블
      max_length: 100            # 최대 글자 수
      options: []                # 선택 옵션 (select 타입용)
      required: true             # 필수 여부
      type: text-input           # 입력 유형
      variable: customer_name    # 변수명 (영문)
    - label: 문의채널
      options:
      - Gmail
      - 콜센터
      required: true
      type: select               # 드롭다운 선택
      variable: inquiry_channel
    - label: 문의내용
      max_length: 2000
      options: []
      required: true
      type: paragraph            # 멀티라인 텍스트
      variable: inquiry_content
    - label: 파일
      allowed_file_extensions: []
      allowed_file_types:
      - document
      allowed_file_upload_methods:
      - local_file
      - remote_url
      max_length: 5
      required: false
      type: file                 # 파일 업로드
      variable: uploaded_file
  id: '1'
```

**필수 필드 (Pydantic 검증):**

| 필드 | 필수 | 검증 규칙 |
|------|------|----------|
| `title` | O | BaseNodeData 필수 (모든 노드 공통) |
| `type` | O | `start` 고정 |
| `variables` | X | Sequence[VariableEntity], 기본값: 빈 리스트 |

**입력 유형(type) 종류:**

| type | 설명 | 주요 속성 |
|------|------|----------|
| `text-input` | 짧은 텍스트 (256자) | `max_length` |
| `paragraph` | 멀티라인 텍스트 | `max_length` |
| `select` | 드롭다운 선택 | `options: [옵션1, 옵션2]` |
| `number` | 숫자 | - |
| `file` | 단일 파일 | `allowed_file_types`, `allowed_file_extensions` |
| `file-list` | 파일 목록 | 위와 동일 |
| `json` | JSON 코드 | - |

### 5.2 trigger (트리거 노드)

Workflow에서 User Input 대신 사용할 수 있는 자동 실행 시작 노드.
스케줄 또는 외부 이벤트에 응답하여 워크플로우를 자동으로 실행:

```yaml
- data:
    desc: '매일 오전 9시 자동 실행'
    title: 트리거
    type: trigger
    trigger_mode: schedule        # schedule 또는 webhook
    schedule:
      cron: '0 9 * * *'          # Cron 표현식
      timezone: Asia/Seoul
  id: '1'
```

**주요 특성:**
- User Input과 Trigger는 상호 배타적 (동일 캔버스에서 함께 사용 불가)
- Trigger로 시작된 워크플로우는 독립 웹 앱이나 MCP 서버로 배포 불가
- Chatflow는 Trigger로 시작할 수 없음

**트리거 유형:**

| 유형 | 설명 |
|------|------|
| `schedule` | Cron 표현식 기반 정기 실행 |
| `webhook` | 외부 시스템 이벤트에 의한 실행 |

> DSL 내부의 노드 타입 값은 `trigger`가 아닌 세부 타입으로 구분됨:
> `trigger-webhook`, `trigger-schedule`, `trigger-plugin`
> 이 3가지가 Dify 소스의 NodeType enum에 정의된 유효한 트리거 타입임.

### 5.3 llm (LLM 노드)

언어 모델을 호출하여 텍스트 처리:

```yaml
- data:
    context:
      enabled: false             # 컨텍스트 변수 활성화
      variable_selector: []      # 컨텍스트 소스 (Knowledge Retrieval 결과 등)
    desc: 'LLM으로 문의 분류'
    model:
      completion_params:
        max_tokens: 2048         # 최대 토큰
        temperature: 0.1         # 0=결정론적, 1=창의적
      mode: chat                 # chat 또는 completion
      name: llama-3.1-70b-versatile  # 모델명 (기본값: Groq llama-3.1-70b-versatile)
      provider: langgenius/groq/groq  # 프로바이더 경로 (기본값: Groq)
    prompt_template:
    - id: system-prompt
      role: system               # system, user, assistant
      text: "당신은 고객 문의 분류 전문가입니다.\n..."
    - id: user-prompt
      role: user
      text: '문의 내용: {{#1.inquiry_content#}}'
    selected: false
    structured_output_enabled: false   # 구조화된 출력
    title: LLM 문의분류
    type: llm
    vision:
      enabled: false             # 비전 기능
      configs:
        detail: high             # high 또는 low
        variable_selector:       # 이미지 소스
        - '1'
        - files
    memory:                      # 메모리 설정 (Chatflow)
      query_prompt_template: '{{#sys.query#}}'
      window:
        enabled: true
        size: 15                 # 보존할 메시지 수
  id: '2'
```

**필수 필드 (Pydantic 검증):**

| 필드 | 필수 | 검증 규칙 |
|------|------|----------|
| `title` | O | BaseNodeData 필수 |
| `type` | O | `llm` 고정 |
| `model` | O | ModelConfig 객체. provider, name, mode, completion_params 포함 필수 |
| `model.provider` | O | 예: `langgenius/openai/openai`, `langgenius/groq/groq` |
| `model.name` | O | 예: `gpt-4o`, `llama-3.1-8b-instant` |
| `model.mode` | O | `chat` 또는 `completion` |
| `model.completion_params` | O | dict 타입 (temperature, max_tokens 등) |
| `prompt_template` | O | chat 모드: `[{role, text}]` 배열, completion 모드: text 문자열 |
| `context` | O | `{enabled: bool, variable_selector: []}` 객체 |
| `memory` | X | 메모리 설정 (Chatflow에서 주로 사용) |
| `vision` | X | 비전 설정 |
| `structured_output_enabled` | X | 구조화 출력 활성화 여부 |

> LLM 노드는 전체 노드 중 가장 복잡한 검증 로직을 가짐.
> model.provider/name 누락, context 객체 누락, prompt_template 구조 불일치가
> 가장 흔한 Import 실패 원인임.

**프롬프트 role 종류:**

| role | 설명 |
|------|------|
| `system` | 시스템 지시 (동작 정의) |
| `user` | 사용자 입력 |
| `assistant` | 어시스턴트 예시 응답 |

**구조화된 출력 (Structured Output):**

LLM이 특정 JSON 스키마에 맞는 출력을 생성하도록 강제:

```yaml
structured_output_enabled: true
structured_output:
  schema:
    type: object
    properties:
      category:
        type: string
        description: '문의 카테고리'
        enum: ['결제', '배송', '일반']
      urgency:
        type: string
        description: '긴급도'
      summary:
        type: string
        description: '요약'
    required: ['category', 'urgency', 'summary']
```

구조화된 출력의 세 가지 구성 방법:

| 방법 | 설명 | 사용 시점 |
|------|------|----------|
| 시각적 편집기 | UI에서 필드/타입 정의 | 간단한 구조 |
| JSON 스키마 | JSON Schema 직접 작성 | 복잡한 중첩 객체 |
| AI 생성 | 자연어 설명으로 자동 생성 | 빠른 프로토타이핑 |

> 구조화된 출력 활성화 시 LLM 응답이 `text` 대신 정의된 스키마 필드별 변수로 출력

**컨텍스트(RAG) 연결:**
```yaml
context:
  enabled: true
  variable_selector:
  - '3'          # Knowledge Retrieval 노드 ID
  - result       # 검색 결과 변수
```

### 5.4 code (코드 노드)

Python 또는 JavaScript 코드 실행:

```yaml
- data:
    code: |
      import json

      def main(llm_output: str) -> dict:
          try:
              result = json.loads(llm_output)
              return {
                  "category": result.get("category", "일반"),
                  "summary": result.get("summary", "")
              }
          except json.JSONDecodeError:
              return {
                  "category": "일반",
                  "summary": "파싱 실패"
              }
    code_language: python3       # python3 또는 javascript
    desc: 'JSON 파싱'
    outputs:                     # 출력 변수 정의 (필수)
      category:
        children: null
        type: string
      summary:
        children: null
        type: string
    title: JSON 파싱
    type: code
    variables:                   # 입력 변수 매핑
    - value_selector:
      - '2'                     # 소스 노드 ID
      - text                    # 소스 변수명
      variable: llm_output      # 코드 내 변수명
  id: '9'
```

**필수 필드 (Pydantic 검증):**

| 필드 | 필수 | 검증 규칙 |
|------|------|----------|
| `title` | O | BaseNodeData 필수 |
| `type` | O | `code` 고정 |
| `code` | O | 실행할 코드 문자열 |
| `code_language` | O | `python3` 또는 `javascript` |
| `outputs` | O | dict[str, Output] 형식 |
| `variables` | O | list[VariableSelector] 입력 변수 매핑 |

**출력 변수 type (허용/금지):**

| 구분 | type 값 |
|------|--------|
| 허용 | `string`, `number`, `object`, `boolean`, `array[string]`, `array[number]`, `array[object]`, `array[boolean]` |
| 금지 | `file`, `secret`, `array[file]` -- 사용 시 검증 실패 |

**출력 변수 제한:**

| type | 설명 |
|------|------|
| `string` | 문자열 (최대 80,000자) |
| `number` | 숫자 (-999999999 ~ 999999999) |
| `boolean` | 불리언 |
| `object` | 객체 (최대 5레벨 중첩) |
| `array[string]` | 문자열 배열 |
| `array[number]` | 숫자 배열 |
| `array[object]` | 객체 배열 |

**사용 가능한 Python 패키지:**
`json`, `math`, `datetime`, `re`, `numpy`, `pandas`, `requests`

**사용 가능한 JavaScript 패키지:**
표준 내장 객체, `lodash`, `moment`

### 5.5 if-else (조건 분기 노드)

조건에 따라 실행 경로를 분기:

```yaml
- data:
    cases:
    - case_id: 'true'                # IF 분기
      conditions:
      - comparison_operator: is      # 비교 연산자
        id: cond1
        value: 결제                   # 비교 값
        variable_selector:
        - '9'                        # 비교 대상 노드 ID
        - category                   # 비교 대상 변수명
      id: 'true'
      logical_operator: and          # 조건 결합 (and/or)
    - case_id: d8e58cc8-...          # ELIF 분기 (UUID)
      conditions:
      - comparison_operator: '>'
        id: cond2
        value: '1'
        varType: number
        variable_selector:
        - sys
        - dialogue_count
      id: d8e58cc8-...
      logical_operator: and
    desc: ''
    title: 결제문의 확인
    type: if-else
  id: '3'
```

**필수 필드 (Pydantic 검증):**

| 필드 | 필수 | 검증 규칙 |
|------|------|----------|
| `title` | O | BaseNodeData 필수 |
| `type` | O | `if-else` 고정 |
| `cases` | 조건부 | 새 형식. case_id, logical_operator, conditions 포함 |
| `conditions` | 조건부 | 레거시 형식 |

> `cases` 또는 `conditions` 중 하나는 반드시 존재해야 함. 둘 다 없으면 검증 실패.

**comparison_operator 종류:**

| 연산자 | 설명 | 대상 타입 |
|--------|------|----------|
| `is` | 같음 (정확히 일치) | 문자열 |
| `is not` | 같지 않음 | 문자열 |
| `contains` | 포함 | 문자열 |
| `not contains` | 미포함 | 문자열 |
| `start with` | ~로 시작 | 문자열 |
| `end with` | ~로 끝남 | 문자열 |
| `empty` | 비어 있음 | 모든 타입 |
| `not empty` | 비어 있지 않음 | 모든 타입 |
| `in` | 목록에 포함 | 문자열/숫자 |
| `not in` | 목록에 미포함 | 문자열/숫자 |
| `all of` | 모두 포함 | 배열 |
| `=` | 같음 | 숫자 |
| `≠` | 같지 않음 | 숫자 |
| `>` | 보다 큼 | 숫자 |
| `<` | 보다 작음 | 숫자 |
| `≥` | 이상 | 숫자 |
| `≤` | 이하 | 숫자 |
| `null` | null 값 | 모든 타입 |
| `not null` | null 아님 | 모든 타입 |
| `exists` | 존재함 | 모든 타입 |
| `not exists` | 존재하지 않음 | 모든 타입 |

> **주의:** `>=`, `<=`, `!=` 사용 시 Dify Import 오류 발생.
> 반드시 유니코드 기호 `≥`, `≤`, `≠`를 사용해야 함.

**엣지 연결 시 sourceHandle:**
- `'true'` -> IF 조건 충족
- `'false'` -> ELSE (모든 조건 미충족)
- `'{case_id}'` -> ELIF 분기

### 5.6 http-request (HTTP 요청 노드)

외부 API 호출:

```yaml
- data:
    authorization:
      config: null
      type: no-auth              # no-auth, api-key
    body:
      data:
      - type: text
        value: |
          {
            "text": "메시지: {{#9.summary#}}"
          }
      type: json                 # json, form-data, binary, raw-text
    desc: 'Slack 웹훅 전송'
    headers: Content-Type:application/json
    method: post                 # get, post, put, patch, delete, head
    params: ''                   # 쿼리 파라미터
    retry_config:
      max_retries: 3
      retry_enabled: true
      retry_interval: 100        # ms
    ssl_verify: true
    timeout:
      max_connect_timeout: 10    # 초
      max_read_timeout: 60
      max_write_timeout: 60
    title: Slack 결제팀
    type: http-request
    url: '{{#env.SLACK_WEBHOOK_PAYMENT#}}'
  id: '4'
```

**필수 필드 (Pydantic 검증):**

| 필드 | 필수 | 검증 규칙 |
|------|------|----------|
| `title` | O | BaseNodeData 필수 |
| `type` | O | `http-request` 고정 |
| `method` | O | get, post, put, patch, delete, head, options |
| `url` | O | 요청 URL 문자열 |
| `authorization` | O | 인증 설정 객체 |
| `headers` | O | 헤더 문자열 |
| `params` | O | 파라미터 문자열 |
| `body` | X | 요청 바디 |

**인증(authorization) 검증 규칙:**
- `type: "no-auth"` -> `config`은 반드시 `null`이어야 함
- `type: "api-key"` -> `config`은 반드시 dict 타입이어야 함

**인증(authorization) 유형:**
```yaml
# 인증 없음
authorization:
  config: null
  type: no-auth

# API Key (Bearer)
authorization:
  config:
    api_key: '{{#env.API_KEY#}}'
    type: bearer
  type: api-key

# API Key (Basic)
authorization:
  config:
    api_key: '{{#env.API_KEY#}}'
    type: basic
  type: api-key
```

**출력 변수:**
`body` (응답 본문), `status_code` (HTTP 상태 코드), `headers` (응답 헤더), `files` (파일)

### 5.7 tool (도구 노드)

내장/사용자 정의/MCP 도구 호출:

```yaml
- data:
    desc: 'FireCrawl로 웹 스크래핑'
    provider_id: firecrawl
    provider_name: firecrawl
    provider_type: builtin       # builtin, api, workflow, mcp
    retry_config:
      max_retries: 3
      retry_enabled: true
      retry_interval: 1000
    title: 웹 스크래핑
    tool_configurations:         # 도구 설정 (고정값)
      formats:
        type: constant
        value: markdown
      onlyMainContent:
        type: constant
        value: 1
      timeout:
        type: constant
        value: 30000
    tool_label: 단일 페이지 스크래핑
    tool_name: scrape
    tool_node_version: '2'
    tool_parameters:             # 도구 파라미터 (동적값)
      url:
        type: mixed              # mixed (변수 참조), constant (고정값)
        value: '{{#1.url#}}'
    type: tool
  id: '3'
```
