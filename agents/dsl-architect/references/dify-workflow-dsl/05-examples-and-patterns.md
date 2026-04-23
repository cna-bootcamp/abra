# Dify Workflow DSL 작성 가이드

> 분할 문서: 6-7장: 실전 예제 및 플로우 패턴
> 인덱스: [README](./README.md)
> 기존 진입점: [../dify-workflow-dsl-guide.md](../dify-workflow-dsl-guide.md)

---

## 6. 실전 예제

### 6.1 간단한 Workflow: 텍스트 요약기

사용자 입력을 받아 LLM으로 요약 후 결과를 반환하는 기본 워크플로우:

```yaml
app:
  description: 입력 텍스트를 요약하는 워크플로우
  icon: "\U0001F4DD"
  icon_background: '#E8F5E9'
  mode: workflow
  name: 텍스트 요약기
  use_icon_as_answer_icon: false
dependencies: []
kind: app
version: 0.5.0
workflow:
  conversation_variables: []
  environment_variables: []
  features:
    file_upload:
      enabled: false
    opening_statement: ''
    retriever_resource:
      enabled: false
    sensitive_word_avoidance:
      enabled: false
    speech_to_text:
      enabled: false
    suggested_questions: []
    suggested_questions_after_answer:
      enabled: false
    text_to_speech:
      enabled: false
      language: ''
      voice: ''
  graph:
    edges:
    - data:
        sourceType: start
        targetType: llm
      id: edge-1-2
      source: '1'
      sourceHandle: source
      target: '2'
      targetHandle: target
      type: custom
    - data:
        sourceType: llm
        targetType: end
      id: edge-2-3
      source: '2'
      sourceHandle: source
      target: '3'
      targetHandle: target
      type: custom
    nodes:
    - data:
        desc: '요약할 텍스트 입력'
        selected: false
        title: 시작
        type: start
        variables:
        - label: 원문 텍스트
          max_length: 5000
          options: []
          required: true
          type: paragraph
          variable: source_text
        - label: 요약 길이
          options:
          - 1줄 요약
          - 3줄 요약
          - 상세 요약
          required: true
          type: select
          variable: summary_length
      height: 150
      id: '1'
      position:
        x: 30
        y: 300
      positionAbsolute:
        x: 30
        y: 300
      selected: false
      type: custom
      width: 242
    - data:
        context:
          enabled: false
          variable_selector: []
        desc: 'LLM으로 텍스트 요약'
        model:
          completion_params:
            max_tokens: 1024
            temperature: 0.3
          mode: chat
          name: gpt-4o
          provider: langgenius/openai/openai
        prompt_template:
        - id: system-prompt
          role: system
          text: |
            당신은 텍스트 요약 전문가입니다.
            사용자가 제공한 텍스트를 요청된 길이로 요약하세요.
            핵심 내용을 빠짐없이 포함하되 간결하게 작성하세요.
        - id: user-prompt
          role: user
          text: |
            [요약 길이] {{#1.summary_length#}}

            [원문]
            {{#1.source_text#}}
        selected: false
        title: 텍스트 요약
        type: llm
        vision:
          enabled: false
      height: 120
      id: '2'
      position:
        x: 334
        y: 300
      positionAbsolute:
        x: 334
        y: 300
      selected: false
      type: custom
      width: 242
    - data:
        desc: ''
        outputs:
        - value_selector:
          - '2'
          - text
          variable: summary
        selected: false
        title: 완료
        type: end
      height: 120
      id: '3'
      position:
        x: 638
        y: 300
      positionAbsolute:
        x: 638
        y: 300
      selected: false
      type: custom
      width: 242
    viewport:
      x: 0
      y: 0
      zoom: 1.0
  rag_pipeline_variables: []
```

**플로우:** `시작` -> `LLM 요약` -> `완료`

### 6.2 조건 분기 Workflow: 문의 분류 및 라우팅

LLM으로 고객 문의를 분류한 후 카테고리별로 다른 Slack 채널에 전송:

```
시작 -> LLM 분류 -> Code(JSON 파싱) -> If-Else(결제?)
                                        +-- true -> HTTP(결제팀 Slack) -> 완료
                                        +-- false -> If-Else(배송?)
                                                     +-- true -> HTTP(배송팀 Slack) -> 완료
                                                     +-- false -> HTTP(일반CS Slack) -> 완료
```

> 전체 DSL은 `develop-agent/examples/dify/dsl/customer-inquiry-routing.yml` 참조

**핵심 패턴:**
1. LLM으로 JSON 형식의 분류 결과를 생성
2. Code 노드로 JSON을 파싱하여 개별 변수로 분리
3. If-Else 체이닝으로 카테고리별 분기
4. 환경 변수로 웹훅 URL을 관리하여 보안 확보
5. 모든 분기가 하나의 End 노드로 합류

### 6.3 Chatflow: 파일 번역 봇

파일 업로드 -> 텍스트 추출 -> 번역 -> 후속 대화에서 스타일 조정:

```
시작 -> If-Else(첫 대화?)
         +-- true -> Doc Extractor -> Variable Assigner -> Answer("처리 완료")
         |                                                    |
         |                                              LLM 번역 -> Answer(번역 결과)
         +-- false(2회차~) -> LLM(사용자 의도 파악) -> LLM 재번역 -> Answer(수정 번역)
```

> 전체 DSL은 `develop-agent/examples/dify/dsl/File Translation.yml` 참조

**핵심 패턴:**
1. `sys.dialogue_count`로 첫 대화/후속 대화 분기
2. 대화 변수(`conversation.text`)로 추출된 텍스트 저장
3. Variable Assigner로 대화 변수 업데이트
4. 메모리 활성화로 대화 컨텍스트 유지

[Top](#dify-workflow-dsl-작성-가이드)

---

## 7. 플로우 로직 패턴

### 7.1 직렬 실행

노드가 순차적으로 연결되어 차례로 실행. 다운스트림 노드는 이전 노드의 변수에 접근 가능:

```yaml
edges:
- source: '1'    # 시작
  target: '2'    # LLM
- source: '2'    # LLM
  target: '3'    # Code
- source: '3'    # Code
  target: '4'    # 완료
```

### 7.2 병렬 실행

하나의 노드에서 여러 노드로 동시 분기. 독립적인 작업의 처리 속도 향상:

```yaml
# LLM 노드('2')에서 3개의 리뷰 LLM으로 동시 분기
edges:
- source: '2'
  target: '3'    # 리뷰어 1
- source: '2'
  target: '4'    # 리뷰어 2
- source: '2'
  target: '5'    # 리뷰어 3
# 3개 결과를 종합 LLM으로 합류
- source: '3'
  target: '6'    # 종합
- source: '4'
  target: '6'
- source: '5'
  target: '6'
```

**제약사항:**
- 최대 10개 병렬 브랜치
- 최대 3단계 중첩 병렬
- 병렬 노드 간에는 서로의 출력 참조 불가
- 합류 노드에서 모든 병렬 출력에 접근 가능

### 7.3 조건 분기 후 합류

Variable Aggregator를 사용하여 분기 결과를 통합:

```yaml
# If-Else에서 분기
edges:
- source: '3'              # If-Else
  sourceHandle: 'true'
  target: '4'              # 분기 A
- source: '3'
  sourceHandle: 'false'
  target: '5'              # 분기 B
# 합류
- source: '4'
  target: '6'              # Variable Aggregator
- source: '5'
  target: '6'
# 통합 결과 처리
- source: '6'
  target: '7'              # 후속 처리
```

[Top](#dify-workflow-dsl-작성-가이드)

---
