# Dify Workflow DSL 작성 가이드

> 분할 문서: 5.8-5.20절: 확장 노드 레퍼런스
> 인덱스: [README](./README.md)
> 기존 진입점: [../dify-workflow-dsl-guide.md](../dify-workflow-dsl-guide.md)

---

### 5.8 knowledge-retrieval (지식 검색 노드)

지식 베이스에서 관련 정보 검색:

```yaml
- data:
    dataset_ids:                  # 지식 베이스 ID 목록
    - 'kb-uuid-1'
    - 'kb-uuid-2'
    desc: '제품 지식 검색'
    multiple_retrieval_config:
      reranking_model:
        provider: ''
        model: ''
      top_k: 3                   # 반환할 최대 결과 수
      score_threshold: 0.5       # 최소 유사도 점수
      reranking_enable: false
    query_variable_selector:     # 검색 쿼리 소스
    - '1'
    - query
    retrieval_mode: multiple     # single 또는 multiple
    title: 지식 검색
    type: knowledge-retrieval
  id: '3'
```

**출력 변수:** `result` (문서 청크 배열 - 콘텐츠, 메타데이터, 제목 포함)

### 5.9 question-classifier (질문 분류기 노드)

LLM 기반 질문 분류:

```yaml
- data:
    classes:
    - id: class-1
      name: 결제 문의
    - id: class-2
      name: 배송 문의
    - id: class-3
      name: 일반 문의
    desc: '고객 문의 분류'
    instructions: '결제 관련 키워드: 환불, 카드, 포인트...'
    model:
      name: gpt-4o
      provider: langgenius/openai/openai
      completion_params:
        temperature: 0.1
    query_variable_selector:
    - sys
    - query
    title: 질문 분류기
    type: question-classifier
  id: '4'
```

> 각 클래스는 별도의 출력 핸들(sourceHandle)로 엣지 연결

### 5.10 agent (에이전트 노드)

LLM이 도구를 자율적으로 선택하고 호출하여 복잡한 작업을 수행:

```yaml
- data:
    agent_strategy: function_call  # function_call 또는 react
    desc: '도구를 사용하여 사용자 요청 처리'
    instructions: |
      당신은 고객 지원 에이전트입니다.
      사용자의 요청을 분석하고 적절한 도구를 사용하여 처리하세요.
      주문 정보 조회가 필요하면 order_lookup 도구를 사용하세요.
    max_iteration: 5               # 최대 반복 횟수 (무한 루프 방지)
    memory:
      role_prefix:
        assistant: ''
        user: ''
      window:
        enabled: true
        size: 10                   # 보존할 메시지 수
    model:
      completion_params:
        temperature: 0.3
      mode: chat
      name: gpt-4o
      provider: langgenius/openai/openai
    title: 고객 지원 에이전트
    tools:
    - provider_id: google_search
      provider_name: google
      provider_type: builtin
      tool_configurations:
        result_type:
          type: constant
          value: link
      tool_label: Google 검색
      tool_name: google_search
      tool_parameters:
        query:
          type: mixed
          value: ''                # AI가 자동 결정
    - provider_id: custom_api
      provider_type: api
      tool_name: order_lookup
      tool_parameters:
        order_id:
          type: mixed
          value: ''
    type: agent
  id: '5'
```

**Agent 전략:**

| 전략 | 설명 | 적합한 모델 |
|------|------|------------|
| `function_call` | 네이티브 LLM function calling 사용 | GPT-4, Claude 3.5 등 |
| `react` | Thought -> Action -> Observation 추론 주기 | 모든 LLM (function call 미지원 포함) |

**최대 반복 횟수 가이드:**
- 간단한 작업: 3~5회
- 복잡한 연구: 10~15회

**출력 변수:**
`text` (최종 답변), `tool_results`, `reasoning_trace`, `iteration_count`, `is_success`, `logs`

### 5.11 answer (응답 노드 - Chatflow 전용)

Chatflow에서 사용자에게 응답 전달:

```yaml
- data:
    answer: |
      문서 처리 완료!

      결과: {{#2.text#}}
    desc: ''
    title: 응답
    type: answer
    variables: []
  id: '5'
```

> 정적 텍스트와 `{{#노드ID.변수명#}}` 동적 변수를 조합 가능
> Chatflow 내에서 여러 Answer 노드 사용 가능

### 5.12 end (출력 노드 - Workflow 전용)

Workflow의 최종 출력 정의:

```yaml
- data:
    desc: ''
    outputs:
    - value_selector:            # 출력할 변수 소스
      - '9'
      - category
      variable: category         # 출력 변수명
    - value_selector:
      - '9'
      - summary
      variable: summary
    - value_selector:
      - '1'
      - customer_name
      variable: customer_name
    title: 완료
    type: end
  id: '8'
```

**필수 필드 (Pydantic 검증):**

| 필드 | 필수 | 검증 규칙 |
|------|------|----------|
| `title` | O | BaseNodeData 필수 |
| `type` | O | `end` 고정 |
| `outputs` | O | list[OutputVariableEntity]. 각 항목에 variable, value_selector 필수 |

> 최소 하나의 출력 변수를 지정해야 함
> API로 호출 시 여기에 정의된 변수만 반환

### 5.13 iteration (반복 노드)

배열의 각 요소에 워크플로우 단계를 적용:

```yaml
- data:
    desc: '각 챕터별 요약 생성'
    error_handle_mode: terminated   # terminated, continue-on-error, remove-abnormal-output
    is_parallel: false              # 병렬 실행 여부
    parallel_nums: 10               # 병렬 시 동시 처리 수 (최대 10)
    iterator_selector:              # 입력 배열 소스
    - '3'
    - chapters
    output_selector:                # 출력 수집 대상
    - '5'
    - text
    title: 챕터별 요약
    type: iteration
    # 내부 노드는 별도로 정의
  id: '4'
```

**내장 변수:**
- `items[object]` - 현재 요소
- `index[number]` - 현재 인덱스 (0부터)

### 5.14 loop (루프 노드)

반복적으로 결과를 개선하는 루프 (조건 기반 while-loop).

> ⚠️ **Dify 1.12.1 검증 완료 — 아래 포맷을 정확히 따를 것**

#### loop 노드 (컨테이너)

```yaml
- data:
    break_conditions:               # 조기 종료 조건 배열 (없으면 [] 빈 배열)
    - comparison_operator: ≥        # 비교 연산자: ≥, ≤, >, <, =, ≠  (Unicode 사용)
      value: '90'                   # 비교값 (문자열)
      variable_selector:            # 비교 대상 변수 (루프 내부 노드 ID 사용)
      - '노드ID'
      - output_key
    logical_operator: and           # 복수 조건 연산: and | or
    loop_count: 5                   # 최대 반복 횟수 (필수)
    loop_variables:                 # 루프 변수 (반복 간 상태 유지)
    - label: 품질 점수
      name: quality_score
      type: number
      value: 0                      # 초기값
      value_type: constant          # 반드시 constant (variable 사용 불가)
      var_type: number
    - label: 초안
      name: draft
      type: string
      value: ''
      value_type: constant
      var_type: string
    start_node_id: loop-1-start     # loop-start 노드 ID
    title: 품질 개선 루프
    type: loop
  height: 400
  id: loop-1
  position:
    x: 400
    y: 200
  positionAbsolute:
    x: 400
    y: 200
  selected: false
  sourcePosition: right             # 필수
  targetPosition: left              # 필수
  type: custom
  width: 900
  zIndex: 1                         # 필수
```

#### loop-start 노드 (루프 내부 — 필수 포함)

> ⚠️ **가장 중요한 규칙**: 외부 타입을 `type: custom-loop-start`로 설정해야 함.
> `type: custom`으로 설정하면 Dify 프론트엔드가 React #130 에러로 크래시됨.

```yaml
- data:
    desc: ''
    isInLoop: true                  # 필수
    selected: false
    title: 루프 시작                 # 빈 문자열 불가, 반드시 값 있어야 함
    type: loop-start
  draggable: false                  # 필수
  height: 48                        # 고정값 (변경 금지)
  id: loop-1-start                  # 관례: {loop-id}-start 또는 {loop-id}start
  parentId: loop-1                  # 루프 노드 ID와 일치
  position:
    x: 24                           # 루프 컨테이너 기준 상대 좌표
    y: 68
  positionAbsolute:
    x: 424                          # loop.position.x + position.x
    y: 268                          # loop.position.y + position.y
  selectable: false                 # 필수
  selected: false
  sourcePosition: right
  targetPosition: left
  type: custom-loop-start           # ← 반드시 custom-loop-start (custom 아님!)
  width: 44                         # 고정값 (변경 금지)
  zIndex: 1002                      # 필수
```

#### loop-end 노드

> ✅ **DSL에 포함하지 않는다.** Dify가 자동으로 처리한다.
> loop-end를 명시적으로 추가하면 렌더링 문제가 발생할 수 있다.

#### 루프 내부 노드

- `parentId: loop-1` 필수
- `positionAbsolute` = loop의 position + 노드의 position
- 일반 노드와 동일하게 `type: custom` 사용

#### 루프 내부 변수 참조

루프 변수는 LLM 프롬프트에서 `{{#loop-1.variable_name#}}` 형식으로 참조:

```
[이전 피드백] {{#loop-1.improvement_suggestions#}}
```

루프 외부에서 루프 내부 노드 결과 참조 시 노드 ID 직접 사용:

```yaml
value_selector:
  - '루프내부노드ID'     # 예: '4' (loop-1 내부의 LLM 노드)
  - text
```

#### 완전한 엣지 예시

```yaml
# 루프 진입 엣지 (외부 → 루프)
- data:
    isInIteration: false
    isInLoop: false
    sourceType: code
    targetType: loop
  id: edge-3-loop1
  source: '3'
  sourceHandle: source
  target: loop-1
  targetHandle: target
  type: custom
  zIndex: 0

# 루프 내부 첫 엣지 (loop-start → 첫 번째 노드)
- data:
    isInLoop: true
    sourceType: loop-start
    targetType: llm
  id: edge-loopstart-4
  source: loop-1-start
  sourceHandle: source
  target: '4'
  targetHandle: target
  type: custom

# 루프 탈출 엣지 (루프 → 다음 노드)
- data:
    isInLoop: false
    sourceType: loop
    targetType: code
  id: edge-loop1-5
  source: loop-1
  sourceHandle: source
  target: '5'
  targetHandle: target
  type: custom
```

**Loop vs Iteration 차이:**

| 특성 | Loop | Iteration |
|------|------|-----------|
| 처리 방식 | 순차적, 이전 결과에 의존 | 독립적, 각 항목 별도 처리 |
| 상태 유지 | 변수가 주기 간 누적 | 각 항목 독립 |
| 조기 종료 | `break_conditions`로 가능 | 불가 |
| 병렬 실행 | 불가 | 가능 (최대 10개) |
| 사용 사례 | 콘텐츠 품질 개선, 수렴 | 일괄 처리, 대량 변환 |

### 5.15 template-transform (템플릿 노드)

Jinja2 템플릿으로 데이터 형식화:

> **주의:** DSL에서 이 노드의 `data.type` 값은 반드시 `template-transform`이어야 함.
> `template`(X)이 아닌 `template-transform`(O)이 정확한 값임.

```yaml
- data:
    desc: '보고서 형식화'
    template: |
      # 분석 보고서

      **고객명:** {{ customer_name }}
      **분류:** {{ category }}

      {% if urgency == "긴급" %}
      > 긴급 처리가 필요합니다!
      {% endif %}

      ## 상세 내용
      {% for item in items %}
      - {{ loop.index }}. {{ item }}
      {% endfor %}
    title: 보고서 템플릿
    type: template-transform
    variables:
    - value_selector:
      - '1'
      - customer_name
      variable: customer_name
    - value_selector:
      - '9'
      - category
      variable: category
  id: '10'
```

**필수 필드 (Pydantic 검증):**

| 필드 | 필수 | 검증 규칙 |
|------|------|----------|
| `title` | O | BaseNodeData 필수 |
| `type` | O | `template-transform` 고정 (NOT `template`) |
| `template` | O | Jinja2 템플릿 문자열 |
| `variables` | O | list[VariableSelector] 입력 변수 |

> 출력은 `text` 변수로 제공 (최대 80,000자)

**주요 Jinja2 필터:**

| 필터 | 설명 | 예시 |
|------|------|------|
| `default(value)` | 변수 미존재 시 기본값 반환 | `{{ name \| default("없음") }}` |
| `length` | 시퀀스 요소 수 반환 | `{{ items \| length }}` |
| `join(sep)` | 배열 요소를 구분자로 연결 | `{{ items \| join(", ") }}` |
| `first` / `last` | 첫 번째/마지막 요소 반환 | `{{ items \| first }}` |
| `upper` / `lower` | 대문자/소문자 변환 | `{{ name \| upper }}` |
| `capitalize` | 첫 글자 대문자 변환 | `{{ name \| capitalize }}` |
| `title` | 각 단어 첫 글자 대문자 | `{{ name \| title }}` |
| `trim` / `strip` | 앞뒤 공백 제거 | `{{ text \| trim }}` |
| `replace(old, new)` | 문자열 치환 | `{{ text \| replace("a", "b") }}` |
| `truncate(n)` | 지정 길이로 자르기 | `{{ text \| truncate(100) }}` |
| `int` / `float` | 정수/실수 변환 | `{{ value \| int }}` |
| `round(n)` | 반올림 | `{{ score \| round(2) }}` |
| `sort` | 정렬 | `{{ items \| sort }}` |
| `reverse` | 역순 | `{{ items \| reverse }}` |
| `batch(n)` | 배치 분할 | `{{ items \| batch(3) }}` |
| `groupby(attr)` | 속성별 그룹화 | `{{ users \| groupby("role") }}` |
| `reject(test)` | 조건 불일치 필터링 | `{{ items \| reject("none") }}` |
| `escape` | HTML 특수문자 이스케이프 | `{{ html \| escape }}` |
| `striptags` | HTML 태그 제거 | `{{ html \| striptags }}` |
| `urlencode` | URL 인코딩 | `{{ query \| urlencode }}` |
| `wordcount` | 단어 수 반환 | `{{ text \| wordcount }}` |
| `indent(n)` | 들여쓰기 적용 | `{{ text \| indent(4) }}` |
| `filesizeformat` | 파일 크기 형식화 | `{{ size \| filesizeformat }}` |

**Jinja2 제어 구문:**
```jinja2
{# 조건문 #}
{% if condition %}...{% elif other %}...{% else %}...{% endif %}

{# 반복문 #}
{% for item in items %}
  {{ loop.index }}. {{ item }}    {# loop.index: 1부터 시작 #}
{% endfor %}

{# 변수 설정 #}
{% set greeting = "안녕하세요" %}
```

### 5.16 variable-aggregator (변수 집계기 노드)

여러 분기의 출력을 하나의 변수로 통합:

```yaml
- data:
    advanced_settings:
      group_enabled: false
    desc: '분기 결과 통합'
    output_type: string           # 집계할 데이터 타입
    title: 결과 통합
    type: variable-aggregator
    variables:
    - - '4'                       # 분기 1의 노드 ID
      - result                    # 분기 1의 변수명
    - - '5'                       # 분기 2의 노드 ID
      - result                    # 분기 2의 변수명
  id: '7'
```

**필수 필드 (Pydantic 검증):**

| 필드 | 필수 | 검증 규칙 |
|------|------|----------|
| `title` | O | BaseNodeData 필수 |
| `type` | O | `variable-aggregator` 고정 |
| `output_type` | O | 출력 타입 문자열 |
| `variables` | O | list[list[str]] 형식 (2차원 배열) |

> 모든 집계 변수는 동일한 데이터 타입이어야 함
> 런타임에 실제로 실행된 분기의 값만 출력

### 5.17 document-extractor (문서 추출기 노드)

업로드된 파일에서 텍스트 추출:

```yaml
- data:
    desc: '문서 텍스트 추출'
    is_array_file: false          # 배열 파일 여부
    title: 문서 추출
    type: document-extractor
    variable_selector:
    - '1'                         # 파일 소스 노드 ID
    - uploaded_file               # 파일 변수명
  id: '3'
```

**지원 형식:**
TXT, Markdown, HTML, DOCX, PDF, Excel(.xls/.xlsx), CSV, PowerPoint, EPUB, JSON, YAML

**출력 변수:**
- 단일 파일: `text` (String)
- 복수 파일: `text` (Array[String])

### 5.18 assigner (변수 할당기 노드)

대화 변수 업데이트 (Chatflow 전용):

```yaml
- data:
    assigned_variable_selector:  # 대상 대화 변수
    - conversation
    - text
    desc: ''
    input_variable_selector:     # 소스 변수
    - '3'
    - text
    title: 변수 할당
    type: assigner
    write_mode: over-write       # over-write, append, clear, set 등
  id: '5'
```

**write_mode (작업 모드):**

| 타입 | 사용 가능한 모드 |
|------|-----------------|
| String | `over-write`, `clear`, `set` |
| Number | `over-write`, `clear`, `set`, `+`, `-`, `*`, `/` |
| Boolean | `over-write`, `clear`, `set` |
| Array | `over-write`, `clear`, `append`, `extend` |
| Object | `over-write`, `clear`, `set` |

### 5.19 parameter-extractor (파라미터 추출기 노드)

LLM을 활용하여 비구조화 텍스트에서 구조화된 데이터 추출:

```yaml
- data:
    desc: '주문 정보 추출'
    extraction_parameters:
    - name: order_id
      type: string
      description: '주문 번호'
      required: true
    - name: amount
      type: number
      description: '주문 금액'
      required: false
    instructions: '문의 내용에서 주문 번호와 금액을 추출하세요.'
    model:
      name: gpt-4o
      provider: langgenius/openai/openai
      completion_params:
        temperature: 0.1
    query_variable_selector:
    - '1'
    - inquiry_content
    title: 파라미터 추출
    type: parameter-extractor
    reasoning_mode: function_call  # function_call 또는 prompt
  id: '4'
```

**출력 변수:**
- 정의한 각 파라미터가 개별 변수로 출력
- `__is_success` (Boolean) - 추출 성공 여부
- `__reason` (String) - 실패 사유

### 5.20 list-operator (리스트 연산자 노드)

배열 필터링, 정렬, 선택:

```yaml
- data:
    desc: '이미지 파일만 필터링'
    filter_by:
      conditions:
      - key: type
        comparison_operator: is
        value: image
    order_by:
      enabled: false
    limit:
      enabled: true
      size: 5                    # 최대 N개 선택
    title: 이미지 필터
    type: list-operator
    variable:
    - '1'
    - files
  id: '3'
```

**출력 변수:** `result` (필터링된 배열), `first_record`, `last_record`

[Top](#dify-workflow-dsl-작성-가이드)

---
