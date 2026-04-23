# Dify Workflow DSL 작성 가이드

기존 단일 문서를 주제별 문서군으로 분할한 인덱스 문서임.  
기존 경로 호환성을 위해 이 파일을 유지하며, 실제 본문은 `dify-workflow-dsl/` 하위 파일에 위치함.

## 진입점

- 분할 가이드 루트: [dify-workflow-dsl/README.md](./dify-workflow-dsl/README.md)

## 권장 읽기 순서

1. 공통 구조 확인: [01-overview-and-top-level.md](./dify-workflow-dsl/01-overview-and-top-level.md)
2. workflow/변수 참조 확인: [02-workflow-and-variables.md](./dify-workflow-dsl/02-workflow-and-variables.md)
3. 노드 유형 확인: [03-node-reference-core.md](./dify-workflow-dsl/03-node-reference-core.md) 또는
   [04-node-reference-advanced.md](./dify-workflow-dsl/04-node-reference-advanced.md)
4. 검증/운영 규칙 확인:
   [06-validation-and-operations.md](./dify-workflow-dsl/06-validation-and-operations.md)
5. Chatflow일 때만 추가 확인: [07-chatflow.md](./dify-workflow-dsl/07-chatflow.md)
6. 예제가 필요할 때만 참고: [05-examples-and-patterns.md](./dify-workflow-dsl/05-examples-and-patterns.md)

## 분할 파일 목록

| 파일 | 범위 | 용도 |
|------|------|------|
| `README.md` | 인덱스 | 읽기 순서, 파일 안내 |
| `01-overview-and-top-level.md` | 1-2장 | DSL 개요, app/dependencies/kind/version |
| `02-workflow-and-variables.md` | 3-4장 | workflow 구조, graph, 변수 참조 |
| `03-node-reference-core.md` | 5.1-5.7절 | 핵심 노드 레퍼런스 |
| `04-node-reference-advanced.md` | 5.8-5.20절 | 확장 노드 레퍼런스 |
| `05-examples-and-patterns.md` | 6-7장 | 실전 예제, 플로우 패턴 |
| `06-validation-and-operations.md` | 8-11장 | 오류 처리, 검증, 운영 가이드 |
| `07-chatflow.md` | 12장 | advanced-chat 전용 규칙 |

## 참고

- 분할 문서는 원문 섹션 순서를 유지하여 비교와 추적이 쉽도록 구성함.
- 기존 문서 경로를 참조하는 문서는 이 파일을 통해 계속 진입 가능함.
