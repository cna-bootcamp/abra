# Dify Workflow DSL 작성 가이드

> 분할 문서: 1-2장: 개요 및 최상위 구조
> 인덱스: [README](./README.md)
> 기존 진입점: [../dify-workflow-dsl-guide.md](../dify-workflow-dsl-guide.md)

---

## 1. DSL 개요

Dify DSL(Domain-Specific Language)은 Dify 앱의 전체 구성을 YAML 형식으로 표현하는 언어임.
Dify Studio에서 구축한 워크플로우를 `.yml` 파일로 내보내거나,
DSL 파일에서 직접 앱을 생성하여 다른 Dify 인스턴스로 이식 및 공유 가능.

**두 가지 앱 유형:**

| 유형 | mode 값 | 설명 |
|------|---------|------|
| Workflow | `workflow` | 단일 턴 작업 처리, Output(End) 노드로 결과 반환 |
| Chatflow | `advanced-chat` | 대화형 앱, Answer 노드로 응답 반환 |

[Top](#dify-workflow-dsl-작성-가이드)

---

## 2. 최상위 구조

### 2.1 전체 구조 개요

DSL 파일의 최상위 구조는 다음 4개 섹션으로 구성:

```yaml
app:          # 앱 메타데이터
  ...
dependencies: # 외부 플러그인 의존성
  ...
kind: app     # 리소스 종류 (항상 'app')
version: 0.5.0  # DSL 버전
workflow:     # 워크플로우 본체
  ...
```

### 2.2 app 섹션

앱의 기본 정보를 정의:

```yaml
app:
  description: '앱에 대한 설명'
  icon: "\U0001F916"        # 이모지 아이콘 (유니코드 이스케이프)
  icon_background: '#FFEAD5' # 아이콘 배경색 (HEX)
  icon_type: emoji           # 아이콘 타입 (image, emoji, link)
  mode: workflow             # 'workflow' 또는 'advanced-chat'
  name: 앱 이름
  use_icon_as_answer_icon: false
```

| 필드 | 필수 | 설명 |
|------|------|------|
| `name` | O | 앱 이름 |
| `mode` | O | `workflow` (Workflow) 또는 `advanced-chat` (Chatflow) |
| `description` | X | 앱 설명 |
| `icon` | X | 이모지 아이콘 |
| `icon_background` | X | 아이콘 배경색 |
| `icon_type` | X | 아이콘 타입: `image`, `emoji`, `link` |
| `use_icon_as_answer_icon` | X | 응답 아이콘으로 앱 아이콘 사용 여부 |

### 2.3 dependencies 섹션

외부 마켓플레이스 플러그인(모델 프로바이더, 도구 등)의 의존성 목록:

```yaml
dependencies:
# 기본값: Groq 플러그인
- current_identifier: null
  type: marketplace
  value:
    marketplace_plugin_unique_identifier: langgenius/groq:0.0.12@38f75b2f...  # Groq (기본값)
    version: null
# OpenAI 사용 시:
# - current_identifier: null
#   type: marketplace
#   value:
#     marketplace_plugin_unique_identifier: langgenius/openai:0.2.8@aae2be09...
#     version: null
```

> 플러그인을 사용하지 않는 경우 빈 배열 `[]`로 설정 가능

**의존성 타입:**

| type 값 | 설명 |
|---------|------|
| `marketplace` | Dify 마켓플레이스의 공식 플러그인 |
| `github` | GitHub 저장소 기반 플러그인 |
| `package` | 패키지 형태의 플러그인 |

**주의사항:**
- `marketplace_plugin_unique_identifier`에 포함된 해시(`@` 뒤의 값)가 실제 마켓플레이스에
  등록된 값과 일치해야 함. 가짜 해시 사용 시 Import 후 플러그인 확인 단계에서 실패
- DSL v0.1.5 이하 버전에서는 워크플로우/모델에서 의존성을 자동 추출하므로
  `dependencies` 섹션을 직접 작성할 필요 없음

### 2.4 kind 및 version

```yaml
kind: app        # 항상 'app' 고정
version: 0.5.0   # 현재 DSL 버전
```

**버전 호환성 검증 규칙:**

Import 시 DSL 파일의 `version`과 Dify 인스턴스의 현재 DSL 버전을 비교하여 처리:

| 조건 | Import 상태 | 설명 |
|------|------------|------|
| imported > current | PENDING | 사용자 확인 필요 (더 높은 버전) |
| imported.major < current.major | PENDING | 메이저 버전 차이로 호환성 확인 필요 |
| imported.minor < current.minor | COMPLETED_WITH_WARNINGS | 경고와 함께 진행 |
| 그 외 (호환) | COMPLETED | 정상 진행 |
| 파싱 실패 | FAILED | Import 실패 |

> `version` 필드는 반드시 문자열 타입이어야 함. `version: 0.5.0`(숫자)이 아닌
> `version: "0.5.0"`(문자열) 형식 사용 권장. YAML에서 따옴표 없이 `0.5.0`을 쓰면
> 문자열로 해석되지만, 명시적 따옴표가 더 안전함.

[Top](#dify-workflow-dsl-작성-가이드)

---
