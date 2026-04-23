# Dify Workflow DSL 분할 가이드

대형 단일 문서였던 `dify-workflow-dsl-guide.md`를 주제별로 분할한 참조 루트임.
기존 진입점은 `../dify-workflow-dsl-guide.md`를 유지하며, 실제 본문은 아래 파일들에 위치함.

## 권장 읽기 순서

1. 공통 구조 확인: `01-overview-and-top-level.md`
2. workflow/변수 참조 확인: `02-workflow-and-variables.md`
3. 노드 유형 확인: `03-node-reference-core.md` 또는 `04-node-reference-advanced.md`
4. 검증/운영 규칙 확인: `06-validation-and-operations.md`
5. Chatflow일 때만 추가 확인: `07-chatflow.md`
6. 예제가 필요할 때만 참고: `05-examples-and-patterns.md`

## 파일 목록

| 파일 | 범위 | 용도 |
|------|------|------|
| `01-overview-and-top-level.md` | 1-2장 | DSL 개요, app/dependencies/kind/version |
| `02-workflow-and-variables.md` | 3-4장 | workflow 구조, graph, 변수 참조 |
| `03-node-reference-core.md` | 5.1-5.7절 | start, trigger, llm, code, if-else, http-request, tool |
| `04-node-reference-advanced.md` | 5.8-5.20절 | knowledge-retrieval 이후 확장 노드 전체 |
| `05-examples-and-patterns.md` | 6-7장 | 실전 예제, 직렬/병렬/분기 패턴 |
| `06-validation-and-operations.md` | 8-11장 | 오류 처리, import 검증, 내보내기/가져오기, 모범 사례 |
| `07-chatflow.md` | 12장 | advanced-chat 전용 규칙과 실패 사례 |

## 참고

- 기존 파일 경로를 참조하는 문서는 `../dify-workflow-dsl-guide.md`를 통해 계속 진입 가능함.
- 분할 문서는 원문 섹션 순서를 유지하여 diff와 추적이 쉽도록 구성함.
