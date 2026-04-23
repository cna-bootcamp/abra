# Dify Workflow DSL 작성 가이드

> 분할 문서: 8-11장: 오류 처리, 검증, 운영 가이드
> 인덱스: [README](./README.md)
> 기존 진입점: [../dify-workflow-dsl-guide.md](../dify-workflow-dsl-guide.md)

---

## 8. 오류 처리

LLM, HTTP, Code, Tool 노드에서 오류 처리 전략 설정 가능:

**방식 1: 기본값 반환 (Default Value)**
```yaml
- data:
    error_strategy: default-value
    default_value:
    - id: text
      type: string
      value: '죄송합니다. 일시적으로 사용할 수 없습니다.'
    type: llm
    # ...
```

**방식 2: 대체 분기 (Fail Branch)**
```yaml
- data:
    error_strategy: fail-branch
    type: http-request
    # ...

# 엣지에서 실패 분기 연결
edges:
- source: '4'
  sourceHandle: fail          # 실패 시 경로
  target: '5'                 # 대체 처리 노드
```

**오류 변수:**
실패 시 `error_type`과 `error_message` 변수가 자동 생성되어 조건부 처리에 활용 가능

**재시도 설정:**
```yaml
retry_config:
  max_retries: 3              # 최대 재시도 횟수 (최대 10)
  retry_enabled: true
  retry_interval: 100         # 재시도 간격 (ms, 최대 5000)
```

### 8.1 노드별 오류 유형

워크플로우 디버깅 시 발생할 수 있는 주요 오류 유형:

**Code 노드 오류:**

| 오류 유형 | 설명 | 해결 방법 |
|----------|------|----------|
| `CodeNodeError` | Python/JavaScript 코드 실행 중 예외 발생 | 코드 로직 점검, 예외 처리 추가 |
| `OutputValidationError` | 반환값과 출력 변수 간 데이터 타입 불일치 | `outputs` 정의와 반환 딕셔너리 타입 일치 확인 |
| `DepthLimitError` | 중첩 데이터 구조가 5단계 초과 | 출력 객체 중첩 깊이 줄이기 |
| `CodeExecutionError` | 샌드박스에서 코드 실행 불가 | 허용된 패키지만 사용, 시스템 접근 제거 |

**LLM 노드 오류:**

| 오류 유형 | 설명 | 해결 방법 |
|----------|------|----------|
| `VariableNotFoundError` | 프롬프트에서 존재하지 않는 변수 참조 | 변수명 오타 확인, 삭제된 변수 참조 제거 |
| `InvalidContextStructureError` | 컨텍스트에 배열/객체 전달 (문자열만 허용) | 데이터 타입 변환 후 전달 |
| `NoPromptFoundError` | 프롬프트 필드가 비어 있음 | 프롬프트 작성 필수 |
| `ModelNotExistError` | 모델이 선택되지 않음 | LLM 모델 선택 |
| `LLMModeRequiredError` | 유효한 API 자격 증명 없음 | API 키 설정, 모델 권한 확인 |
| `InvalidVariableTypeError` | 비호환 Jinja2 구문 포함 | Jinja2 문법 오류 수정 |

**HTTP Request 노드 오류:**

| 오류 유형 | 설명 | 해결 방법 |
|----------|------|----------|
| `AuthorizationConfigError` | 인증 설정 누락/오류 | API 키, 토큰 재확인, 인증 유형 점검 |
| `Timeout` | 응답 시간 초과 | 타임아웃 값 증가, 외부 서비스 상태 점검 |
| `ResponseValidationError` | 응답 파싱 실패 | 응답 형식 확인, Content-Type 점검 |

**공통 오류:**

| 오류 유형 | 설명 | 해결 방법 |
|----------|------|----------|
| `VariableNotFoundError` | 참조 변수가 워크플로우에 존재하지 않음 | `value_selector` 경로, 노드 ID 점검 |
| `InvalidVariableTypeError` | 변수 타입 불일치 | 상위 노드 출력 타입과 입력 타입 일치 확인 |

[Top](#dify-workflow-dsl-작성-가이드)

---

## 9. DSL Import 검증

DSL 파일을 Dify에 Import할 때 수행되는 검증 과정과
사전에 오류를 방지하기 위한 실무 가이드.

### 9.1 Import 검증 흐름

Dify 소스 코드 기반의 전체 검증 체인:

```
HTTP POST /apps/imports
  +-- YAML 파싱 (yaml.safe_load)
  +-- 기본 구조 검증 (dict 타입 확인)
  +-- 버전 호환성 검증
  +-- app 섹션 검증
  +-- AppMode 검증
  +-- workflow 데이터 검증
  +-- 변수 빌드 및 검증 (variable_factory)
  +-- 피처 구조 검증 (validate_features_structure)
  +-- 그래프 구조 검증 (validate_graph_structure)
  +-- DB 저장
```

**단계별 검증 상세:**

| 단계 | 검증 항목 | 실패 시 동작 |
|------|----------|-------------|
| YAML 파싱 | yaml.safe_load() 성공, dict 타입 | Import 즉시 실패 |
| 버전 검증 | version이 문자열, 시맨틱 버전 형식 | PENDING 또는 FAILED |
| app 검증 | app 섹션 존재, mode 유효 | Import 실패 |
| AppMode 검증 | 유효한 모드 값 확인 | ValueError 발생 |
| workflow 검증 | workflow/advanced-chat 모드에서 필수 | Import 실패 |
| 변수 검증 | name, value_type, value 필수, 200KB 제한 | VariableError 발생 |
| 피처 검증 | 모드별 허용 피처만 검증 | 인식되지 않는 키는 무시 |
| 그래프 검증 | START/트리거 노드 공존 불가, 노드 타입 유효성 | Import 실패 |

**자동 보정 항목:**
- `version` 누락 시 -> `"0.1.0"` 자동 설정
- `kind` 누락 또는 `"app"` 아닌 경우 -> `"app"` 자동 설정

### 9.2 Import 실패 주요 원인 Top 10

| 순위 | 원인 | 설명 |
|------|------|------|
| 1 | YAML 문법 오류 | 들여쓰기, 특수문자 이스케이프 문제 |
| 2 | YAML 스칼라 스타일 오류 | `>` (folded) 대신 `\|` (literal) 사용해야 프롬프트 줄바꿈 유지 |
| 3 | version 필드 문제 | 누락 또는 잘못된 타입 (문자열 `"0.5.0"` 필수) |
| 4 | app 섹션 누락 | 최소 name, mode 필수 |
| 5 | 잘못된 AppMode | `workflow`, `advanced-chat` 등 유효한 값만 허용 |
| 6 | workflow 섹션 누락 | workflow/advanced-chat 모드에서 필수 |
| 7 | 노드 title 필드 누락 | 모든 노드에서 필수 (BaseNodeData) |
| 8 | LLM 노드 model 설정 오류 | provider, name, mode 필수 |
| 9 | 의존성 해시 불일치 | 가짜 해시 사용 시 플러그인 확인 단계에서 실패 |
| 10 | 변수 타입 불일치 | value와 value_type 간 타입 일치 필요 |

### 9.3 YAML 작성 시 주의사항

#### 리터럴 블록 (`|`) vs 폴딩 블록 (`>`)

YAML에서 여러 줄 문자열을 표현하는 두 가지 블록 스칼라 스타일:

```yaml
# | (리터럴): 줄바꿈 유지 -- 프롬프트, 코드에 사용
text: |
  첫째 줄
  둘째 줄
  셋째 줄
# 결과: "첫째 줄\n둘째 줄\n셋째 줄\n"

# > (폴딩): 줄바꿈 -> 공백으로 변환 -- 긴 문단에만 사용
text: >
  첫째 줄
  둘째 줄
  셋째 줄
# 결과: "첫째 줄 둘째 줄 셋째 줄\n"
```

**필수 규칙:** prompt_template의 text, code 노드의 code, http-request의 body에서는
반드시 `|` (리터럴 블록) 사용.
`>`를 사용하면 줄바꿈이 공백으로 변환되어 프롬프트 구조가 깨짐.
Import 자체는 성공하더라도 실행 시 의도치 않은 동작 발생.

**블록 스칼라 변형:**

| 표기 | 마지막 줄바꿈 | 사용 예시 |
|------|-------------|----------|
| `\|` | 하나의 줄바꿈 유지 | 일반적인 프롬프트, 코드 |
| `\|-` | 마지막 줄바꿈 제거 | 줄바꿈 없이 끝나야 하는 텍스트 |
| `\|+` | 모든 후행 줄바꿈 유지 | 후행 공백이 중요한 경우 |

#### 인라인 문자열의 특수문자 이스케이프

```yaml
# 쌍따옴표 안에서 이스케이프 시퀀스 동작
text: "첫째 줄\n둘째 줄\n셋째 줄"
# 결과: 실제 줄바꿈이 포함된 문자열

# 홑따옴표 안에서는 이스케이프 불가 (그대로 출력)
text: '첫째 줄\n둘째 줄'
# 결과: "첫째 줄\n둘째 줄" (리터럴 백슬래시 n)
```

> 프롬프트에 줄바꿈이 필요한 경우 인라인 쌍따옴표보다 `|` 블록 스칼라를 권장.
> 가독성이 높고 이스케이프 실수를 방지 가능.

#### YAML 특수문자 주의

```yaml
# 콜론(:) 뒤에 공백이 있으면 key-value로 해석
text: "Content-Type: application/json"   # 따옴표 필수

# 중괄호({})는 YAML flow mapping으로 해석될 수 있음
text: "결과: {{#1.text#}}"              # 따옴표 권장

# 퍼센트(%)로 시작하면 YAML 지시자로 해석
text: "%ENV_VAR%"                        # 따옴표 필수
```

#### 노드 타입 정확한 값

일부 노드 타입은 하이픈이 포함됨. 정확한 값을 사용해야 함:

| 정확한 값 (O) | 흔한 실수 (X) |
|--------------|-------------|
| `template-transform` | `template` |
| `if-else` | `ifelse`, `if_else` |
| `http-request` | `http`, `http_request` |
| `knowledge-retrieval` | `knowledge` |
| `variable-aggregator` | `variable_aggregator` |
| `question-classifier` | `question_classifier` |
| `document-extractor` | `document_extractor` |
| `parameter-extractor` | `parameter_extractor` |
| `list-operator` | `list_operator` |
| `trigger-webhook` | `trigger` |
| `trigger-schedule` | `trigger` |
| `trigger-plugin` | `trigger` |

**전체 유효 노드 타입 목록 (Dify 소스 NodeType enum):**

```
start, end, answer, llm, knowledge-retrieval, knowledge-index,
if-else, code, template-transform, question-classifier, http-request,
tool, datasource, variable-aggregator, variable-assigner, loop,
loop-start, loop-end, iteration, iteration-start, parameter-extractor,
assigner, document-extractor, list-operator, agent, trigger-webhook,
trigger-schedule, trigger-plugin, human-input
```

### 9.4 사전 검증 도구

DSL 파일을 Dify에 Import하기 전에 오프라인으로 검증할 수 있는 도구:

```bash
# DSL 파일 검증
python {ABRA_PLUGIN_DIR}/gateway/tools/validate_dsl.py <yaml_file>

# 예시
python {ABRA_PLUGIN_DIR}/gateway/tools/validate_dsl.py smart-inquiry-routing.yml
```

**위치:** `{ABRA_PLUGIN_DIR}/gateway/tools/validate_dsl.py`

**검증 항목:**
- YAML 구문 및 기본 구조 (dict 타입)
- 버전 호환성 (시맨틱 버전 비교)
- app 섹션 (mode, name, icon_type)
- 그래프 구조 (노드 ID 고유성, 엣지 참조 유효성)
- 노드별 필수 필드 (LLM, Code, If/Else, HTTP, Template Transform, End, Variable Aggregator)
- 변수 참조 일관성 (`{{#nodeId.var#}}` 패턴의 nodeId 존재 여부)
- value_selector 참조 유효성
- START/트리거 노드 상호 배타성 검증
- 환경변수/대화변수 타입 검증
- 의존성 타입 검증

**출력 예시 (통과):**
```
======================================================================
  Dify DSL Validator -- smart-inquiry-routing.yml
======================================================================

  [i] INFO (1건)
  ------------------------------------------------------------------
  [i] [FILE]
      파일 크기: 22,597 bytes

======================================================================
  결과: PASS  |  오류: 0  |  경고: 0  |  정보: 1
======================================================================

  DSL 파일이 기본 검증을 통과함. Import 가능성 높음.
```

**출력 예시 (실패):**
```
======================================================================
  Dify DSL Validator -- broken-workflow.yml
======================================================================

  [X] ERROR (2건)
  ------------------------------------------------------------------
  [X] [LLM] @ workflow.graph.nodes[1].data.model.provider
      model.provider 누락
      -> 예: langgenius/openai/openai, langgenius/groq/groq

  [X] [NODE] @ workflow.graph.nodes[3].data.title
      노드 title 누락 (BaseNodeData 필수 필드)
      -> 모든 노드에 title 필드 필수

======================================================================
  결과: FAIL  |  오류: 2  |  경고: 0  |  정보: 1
======================================================================

  오류 2건 해결 필요. Import 실패 가능성 높음.
```

> 상세 검증 분석 문서:
> `develop-agent/examples/dify/dsl/validation/dify-dsl-import-validation-analysis.md` 참조

[Top](#dify-workflow-dsl-작성-가이드)

---

## 10. DSL 내보내기 및 가져오기

DSL 파일을 통해 Dify 앱을 다른 인스턴스로 이식하고 공유 가능.

### 내보내기 (Export)

Dify Studio에서 **앱 설정 -> DSL 내보내기**로 `.yml` 파일을 다운로드.

**DSL 파일에 포함되는 항목:**

| 항목 | 설명 |
|------|------|
| 앱 설정 | `app` 섹션 (이름, 모드, 아이콘 등) |
| 워크플로우 구성 | 전체 `workflow` 섹션 (노드, 엣지, 변수) |
| 모델 매개변수 | LLM 노드의 모델명, 프로바이더, completion_params |
| 지식 베이스 연결 | `dataset_ids` (참조 ID만, 실제 콘텐츠는 미포함) |
| 플러그인 의존성 | `dependencies` 섹션의 플러그인 식별자 |
| 환경 변수 | `environment_variables` (값 포함 -- 주의 필요) |
| 기능 설정 | `features` 섹션 (파일 업로드, TTS 등) |

**DSL 파일에 포함되지 않는 항목:**

| 항목 | 사유 |
|------|------|
| API 키 | 보안 (모델 프로바이더 키는 별도 설정 필요) |
| 지식 베이스 콘텐츠 | 용량 (KB 데이터는 별도 이관 필요) |
| 분석/로그 데이터 | 환경별 데이터 (실행 이력, 대시보드 통계) |

> **보안 주의:** `environment_variables`에 저장된 웹훅 URL, API 키 등 민감 정보는
> DSL 파일에 그대로 포함되므로 파일 공유 시 값을 제거하거나 변경 필요

### 가져오기 (Import)

Dify Studio에서 **앱 생성 -> DSL 파일에서 가져오기**로 `.yml` 파일 업로드.

**가져오기 시 확인사항:**

| 확인 항목 | 설명 |
|----------|------|
| 버전 호환성 | DSL `version`과 대상 Dify 인스턴스 간 호환성 자동 검사 |
| 플러그인 설치 | `dependencies`의 플러그인이 대상 환경에 설치되어 있어야 함 |
| 모델 프로바이더 | 사용 중인 모델의 프로바이더가 설정되어 있어야 함 |
| 지식 베이스 | 참조하는 KB가 대상 환경에 존재해야 함 (ID 기반 매칭) |
| 환경 변수 | 민감 정보는 가져오기 후 대상 환경에 맞게 재설정 |

**가져오기 검증 체인 ([9.1 Import 검증 흐름](#91-import-검증-흐름) 참조):**

```
DSL 파일 선택
  +-- YAML 파싱 및 구조 검증
  +-- 버전 호환성 검사
  +-- app/workflow 데이터 검증
  +-- 변수/피처/그래프 검증
  +-- 플러그인 의존성 확인
  +-- 앱 생성 및 DB 저장
  +-- 환경 변수/KB 연결 재설정
  +-- 테스트 실행
```

[Top](#dify-workflow-dsl-작성-가이드)

---

## 11. 모범 사례 및 주의사항

### 노드 ID 관리
- 노드 ID는 고유해야 함 (숫자 문자열 `'1'`, `'2'` 또는 타임스탬프 `'1739416823091'` 형식)
- 엣지의 `source`/`target`과 변수 참조의 노드 ID가 일치해야 함
- ID 변경 시 모든 참조를 함께 업데이트해야 함

### 변수 참조
- 텍스트 필드: `{{#노드ID.변수명#}}` 형식 사용
- 셀렉터 필드: `value_selector: ['노드ID', '변수명']` 배열 형식 사용
- 두 형식을 혼동하지 않도록 주의

### 환경 변수 보안
- API 키, 웹훅 URL 등 민감 정보는 반드시 `environment_variables`에 저장
- 프롬프트나 URL에서 `{{#env.변수명#}}`으로 참조
- DSL 파일을 공유할 때 환경 변수 값이 포함되어 있으므로 주의

### Workflow vs Chatflow 선택
- **Workflow**: 단일 실행, API 통합, 일괄 처리에 적합. `end` 노드로 결과 반환
- **Chatflow**: 대화형 상호작용, 다중 턴에 적합. `answer` 노드로 응답 반환
- Chatflow는 `conversation_variables`, `memory`, `sys.query` 사용 가능

### 플로우 설계 원칙
- 하나의 캔버스에 하나의 시작 노드만 허용
- 병렬 실행 시 최대 10개 브랜치, 3단계 중첩 제한 준수
- If-Else 분기 후에는 Variable Aggregator로 합류하여 다운스트림 노드 중복 방지
- 복잡한 조건 분기보다 Question Classifier 노드 활용 권장

### Code 노드 제약
- 샌드박스 환경: 파일 시스템, 네트워크, 시스템 명령 접근 불가
- 출력 제한: 문자열 80,000자, 중첩 5레벨
- 반드시 출력 변수(`outputs`)를 선언하고 딕셔너리로 반환

### 배포 및 버전 관리
- 배포 시 즉시 라이브 버전이 교체되므로 드래프트에서 충분히 테스트
- DSL 파일로 내보내기하여 버전별 백업 유지
- 환경 간 이식 시 `dependencies`의 플러그인이 대상 환경에 설치되어 있는지 확인

### YAML 스칼라 스타일 규칙
- 프롬프트 텍스트: `|` (리터럴 블록) 사용 필수
- 코드 블록: `|` (리터럴 블록) 사용 필수
- HTTP 바디: `|` (리터럴 블록) 사용 필수
- `>` (폴딩 블록): 줄바꿈을 공백으로 변환하므로 위 항목에 사용 금지

### Import 전 체크리스트
- [ ] `version: "0.5.0"` (문자열, 따옴표 포함)
- [ ] `kind: app`
- [ ] `app.mode`가 유효한 값 (`workflow`, `advanced-chat` 등)
- [ ] `app.name` 존재
- [ ] 모든 노드에 `data.title` 존재
- [ ] 모든 노드에 유효한 `data.type` (`template-transform`, NOT `template`)
- [ ] LLM 노드: `model.provider`, `model.name`, `model.mode` 필수
- [ ] Code 노드: `outputs`의 type이 허용 값만 사용
- [ ] 엣지의 `source`/`target`이 존재하는 노드 ID 참조
- [ ] 변수 참조 `{{#nodeId.var#}}`의 nodeId가 존재하는 노드
- [ ] `dependencies`의 플러그인 해시가 실제 마켓플레이스 값
- [ ] `validate_dsl.py`로 사전 검증 실행

### 노드 타입 정확한 값
주의: 일부 노드 타입은 하이픈이 포함됨. 정확한 값을 사용해야 함:
```
template-transform (NOT template)
if-else (NOT ifelse, if_else)
http-request (NOT http, http_request)
knowledge-retrieval (NOT knowledge)
variable-aggregator (NOT variable_aggregator)
question-classifier (NOT question_classifier)
document-extractor (NOT document_extractor)
parameter-extractor (NOT parameter_extractor)
list-operator (NOT list_operator)
```

[Top](#dify-workflow-dsl-작성-가이드)

---
