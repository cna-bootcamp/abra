# Dify Workflow DSL 작성 가이드

> 분할 문서: 3-4장: workflow 섹션 및 변수 참조 규칙
> 인덱스: [README](./README.md)
> 기존 진입점: [../dify-workflow-dsl-guide.md](../dify-workflow-dsl-guide.md)

---

## 3. workflow 섹션

워크플로우의 실제 로직을 정의하는 핵심 섹션:

```yaml
workflow:
  conversation_variables: []   # 대화 변수 (Chatflow 전용)
  environment_variables: []    # 환경 변수
  features: {}                 # 앱 기능 설정
  graph:                       # 노드 및 연결 그래프
    edges: []
    nodes: []
    viewport: {}
  rag_pipeline_variables: []   # RAG 파이프라인 변수
```

### 3.1 environment_variables (환경 변수)

API 키 등 민감한 정보를 저장하는 상수 변수. 워크플로우 실행 중 변경 불가:

```yaml
environment_variables:
- description: 'Slack 결제팀 웹훅 URL'
  id: ec77ba47-3714-443f-8f90-868c5feff1ae
  name: SLACK_WEBHOOK_PAYMENT
  selector:
  - env
  - SLACK_WEBHOOK_PAYMENT
  value: https://hooks.slack.com/services/...
  value_type: string
```

| 필드 | 필수 | 설명 |
|------|------|------|
| `id` | X | UUID 형식의 고유 식별자 |
| `name` | O | 변수 이름 (대문자 + 언더스코어 권장) |
| `value` | O | 변수 값 |
| `value_type` | O | 데이터 타입 (`string`, `number` 등) |
| `selector` | X | 참조 경로 (`['env', '변수명']`) |
| `description` | X | 설명 |

**검증 규칙:**
- `name`, `value_type`, `value` 3개 필드는 필수. 누락 시 VariableError 발생
- 변수 데이터 크기 제한: 200KB (MAX_VARIABLE_SIZE)
- `value_type`은 아래 지원 목록의 값만 허용

**지원 value_type:**

| value_type | 설명 |
|-----------|------|
| `string` | 문자열 |
| `secret` | 비밀 문자열 |
| `number` | 숫자 (정수/실수 자동 판별) |
| `integer` | 정수 |
| `float` | 실수 |
| `boolean` | 불리언 |
| `object` | 객체 |
| `array[string]` | 문자열 배열 |
| `array[number]` | 숫자 배열 |
| `array[object]` | 객체 배열 |
| `array[boolean]` | 불리언 배열 |

### 3.2 conversation_variables (대화 변수)

Chatflow 전용. 대화 세션 동안 상태를 유지하는 변수:

```yaml
conversation_variables:
- description: '번역할 텍스트'
  id: e520bb9f-da6f-49a3-9da6-a3c74f1d68d6
  name: text
  selector:
  - conversation
  - text
  value: ''             # 초기값
  value_type: string    # string, number, boolean, object, array[string] 등
```

> Variable Assigner(assigner) 노드를 통해 업데이트 가능

### 3.3 features (기능 설정)

앱의 부가 기능 설정:

```yaml
features:
  file_upload:
    allowed_file_extensions:    # 허용 확장자
    - .JPG
    - .PNG
    - .PDF
    allowed_file_types:         # 허용 파일 유형
    - image
    - document
    allowed_file_upload_methods: # 업로드 방식
    - local_file
    - remote_url
    enabled: false              # 파일 업로드 활성화 여부
    fileUploadConfig:
      file_size_limit: 15       # 파일 크기 제한 (MB)
      workflow_file_upload_limit: 10
    number_limits: 3            # 최대 파일 수
  opening_statement: ''         # 대화 시작 메시지 (Chatflow)
  retriever_resource:
    enabled: false              # 인용 표시
  sensitive_word_avoidance:
    enabled: false              # 민감어 필터링
  speech_to_text:
    enabled: false              # 음성->텍스트
  suggested_questions: []       # 제안 질문 목록
  suggested_questions_after_answer:
    enabled: false              # 답변 후 후속 질문 제안
  text_to_speech:
    enabled: false              # 텍스트->음성
    language: ''
    voice: ''
```

**모드별 검증 대상 피처:**

| 앱 모드 | 검증 대상 피처 |
|---------|--------------|
| `workflow` | file_upload, text_to_speech, sensitive_word_avoidance |
| `advanced-chat` | file_upload, opening_statement, suggested_questions, speech_to_text, text_to_speech, retriever_resource, sensitive_word_avoidance |

> workflow 모드에서 opening_statement, suggested_questions, speech_to_text 등을
> 설정해도 무시됨. advanced-chat 모드에서만 유효.

### 3.4 graph (그래프)

워크플로우의 노드와 연결을 정의하는 핵심 구조:

```yaml
graph:
  edges: []      # 노드 간 연결
  nodes: []      # 노드 목록
  viewport:      # 캔버스 뷰 설정
    x: 0
    y: 0
    zoom: 0.8
```

#### 3.4.1 edges (엣지)

노드 간 연결을 정의. 워크플로우의 실행 흐름을 결정:

```yaml
edges:
- data:
    sourceType: start        # 출발 노드 유형
    targetType: llm          # 도착 노드 유형
  id: edge-start-llm         # 엣지 고유 ID
  source: '1'                # 출발 노드 ID
  sourceHandle: source       # 출발 핸들 (source, true, false 등)
  target: '2'                # 도착 노드 ID
  targetHandle: target       # 도착 핸들 (항상 target)
  type: custom               # 항상 'custom'
```

**sourceHandle 값:**

| 값 | 사용 상황 |
|----|----------|
| `source` | 일반 노드의 기본 출력 |
| `true` | if-else 노드의 IF/ELIF 조건 충족 시 |
| `false` | if-else 노드의 ELSE 경로 |
| `{case_id}` | if-else 노드의 ELIF 분기 ID |

#### 3.4.2 nodes (노드)

각 노드의 구성 정보:

```yaml
nodes:
- data:
    desc: '노드 설명'
    selected: false
    title: 노드 제목
    type: start              # 노드 유형
    # ... 노드 유형별 추가 속성
  height: 186                # 노드 높이 (px)
  id: '1'                    # 노드 고유 ID
  position:                  # 캔버스 위치
    x: 3.75
    y: 285.75
  positionAbsolute:          # 절대 위치
    x: 3.75
    y: 285.75
  selected: false
  type: custom               # 항상 'custom' (custom-note: 메모)
  width: 242                 # 노드 너비 (px)
```

**노드 공통 필드:**

| 필드 | 설명 |
|------|------|
| `id` | 노드 고유 ID (문자열, 숫자 또는 타임스탬프 형식) |
| `data.type` | 노드 유형 (start, llm, code, if-else 등) |
| `data.title` | 캔버스에 표시되는 노드 제목 |
| `data.desc` | 노드 설명 |
| `data.selected` | 선택 상태 (보통 false) |
| `position` | 캔버스 상 위치 좌표 |
| `height`, `width` | 노드 크기 |

#### 3.4.3 viewport (뷰포트)

캔버스 뷰 설정:

```yaml
viewport:
  x: -367.9    # X 오프셋
  y: 29.4      # Y 오프셋
  zoom: 0.8    # 확대/축소 비율
```

[Top](#dify-workflow-dsl-작성-가이드)

---

## 4. 변수 참조 규칙

Dify DSL에서 변수를 참조하는 두 가지 방식이 존재:

### 4.1 노드 출력 변수 참조

프롬프트, URL, 요청 본문 등 텍스트 필드에서 사용:

```
{{#노드ID.변수명#}}
```

**예시:**
```
{{#1.customer_name#}}     -> 노드 '1'의 customer_name 변수
{{#2.text#}}               -> 노드 '2'의 text 출력
{{#9.category#}}           -> 노드 '9'의 category 변수
```

### 4.2 환경 변수 참조

```
{{#env.변수명#}}
```

**예시:**
```
{{#env.SLACK_WEBHOOK_PAYMENT#}}
{{#env.API_KEY#}}
```

### 4.3 대화 변수 참조

Chatflow에서 대화 변수 참조:

```
{{#conversation.변수명#}}
```

**예시:**
```
{{#conversation.text#}}
{{#conversation.user_preference#}}
```

### 4.4 시스템 변수 참조

```
{{#sys.변수명#}}
```

| 변수명 | 설명 |
|--------|------|
| `sys.user_id` | 사용자 ID |
| `sys.app_id` | 앱 ID |
| `sys.workflow_id` | 워크플로우 ID |
| `sys.workflow_run_id` | 실행 ID |
| `sys.timestamp` | 실행 시작 시간 |
| `sys.query` | Chatflow 사용자 입력 텍스트 |
| `sys.files` | 사용자 업로드 파일 |
| `sys.dialogue_count` | 대화 횟수 (Chatflow) |

### 4.5 value_selector 방식

노드 구성에서 프로그래밍적으로 변수를 참조할 때 배열 형식 사용:

```yaml
value_selector:
- '1'            # 노드 ID
- customer_name  # 변수명
```

**특수 셀렉터:**
```yaml
# 환경 변수
selector:
- env
- SLACK_WEBHOOK_PAYMENT

# 대화 변수
selector:
- conversation
- text

# 시스템 변수
variable_selector:
- sys
- query
```

[Top](#dify-workflow-dsl-작성-가이드)

---
