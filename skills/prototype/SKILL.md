---
name: prototype
description: Dify 프로토타이핑 자동화 (STEP 3)
user-invocable: true
type: orchestrator
---

# Prototype

[PROTOTYPE 스킬 활성화]

## 목표

DSL을 Dify에 Import → Publish → Run → Export하여 프로토타이핑을 수행함.
에러 발생 시 DSL 수정 → 재검증 → 재시도 루프를 자동 실행하여 검증 완료된 DSL을 확보함.

## 활성화 조건

다음 키워드 감지 시 또는 `/abra:prototype` 호출 시:
- "프로토타이핑", "프로토타입", "Dify 업로드", "Dify 실행", "Dify 테스트"

## 작업 환경 변수 로드 
AGENTS.md 파일에서 환경변수를 로딩. 로딩 실패 시 사용자에게 `/abra:setup`을 먼저 수행하라고 안내하고 종료.     
```
## 환경변수
- AI_RUNTIME: 현재 구동중인 런타임
- PROJECT_DIR: 현재 프로젝트 경로
- ABRA_PLUGIN_DIR: ABRA 플러그인 경로
- DIFY_DIR: DIFY 설치 경로
```

## 에이전트 호출 규칙

### 에이전트 FQN

| 에이전트 | FQN |
|----------|-----|
| prototype-runner | `abra:prototype-runner:prototype-runner` |

### 프롬프트 조립
- `{ABRA_PLUGIN_DIR}/resources/guides/combine-prompt.md`에 따라 AGENT.md + agentcard.yaml + tools.yaml 합치기
- `Agent(subagent_type=FQN, model=tier_mapping 결과, prompt=조립된 프롬프트)` 호출
- tier → 모델 매핑은 `{ABRA_PLUGIN_DIR}/gateway/runtime-mapping.yaml` 참조

### 서브 에이전트 호출
워크플로우 단계에 `Agent: {agent-name}`이 명시된 경우,
메인 에이전트는 해당 단계를 직접 수행하지 않고,
반드시 위 프롬프트 조립 규칙에 따라 해당 에이전트를 호출하여 결과를 받아야 함.

서브에이전트 호출 없이 메인 에이전트가 해당 산출물을 직접 작성하면
스킬 미준수로 간주함.

## 워크플로우

### Phase 0: 입력 확인

DSL 파일 존재 확인.
- 있음 → Phase 1 진행
- 없음 → dsl-generate 스킬로 위임

### Phase 1: 프로토타이핑 실행 → Agent: prototype-runner (`ulw` 활용)

- **TASK**: DSL을 Dify에 import → publish → run → export 수행. 에러 시 DSL 수정 → 재검증 → 재시도 루프 자동 실행
- **EXPECTED OUTCOME**: 검증 완료된 DSL 파일 (export된 최종 버전)
- **MUST DO**: import 전 반드시 validate_dsl로 사전 검증, publish/run 에러 시 DSL 수정 → validate_dsl → update 반복, 성공 시 export로 최종 DSL 확보
- **MUST NOT DO**: 사용자에게 직접 질문 금지, DSL 구조 대규모 변경 금지 (대규모 변경 시 dsl-architect로 핸드오프)
- **CONTEXT**: DSL 파일: `{output_dir}/{app-name}.dsl.yaml`, 가상환경: `gateway/.venv`

**에러 수정 루프:**

```
import → publish → [에러?] → DSL 수정 → validate_dsl → update → 재게시
                                                                  ↓
                   run → [에러?] → DSL 수정 → validate_dsl → update → 재실행
                                                                       ↓
                                                    [성공] → export → 완료
```

### Phase 2: 결과 확인 및 보고

검증된 DSL 파일 확인, 실행 결과 사용자 보고:
- Dify 앱 ID
- 최종 상태 (성공/실패)
- 에러 수정 횟수
- Export된 DSL 파일 경로

## 완료 조건

- [ ] Dify import 성공
- [ ] publish 성공
- [ ] run 성공 (에러 0, 100% 정상 실행)
- [ ] export로 검증된 DSL 확보

**완료 보장 규칙:**
- run이 100% 정상 실행될 때까지 에러 수정 루프를 반복함
- 단, 총 소요 시간이 8시간을 초과하면 즉시 중단하고 사용자에게 문제 보고
  - 보고 내용: 현재 상태, 발생 에러 목록, 시도한 수정 내역, 권장 다음 조치

**요구사항 변형 금지:**
- 에러 수정 과정에서 원래 요구사항(시나리오)을 변형해야 하는 경우,
  반드시 사용자에게 확인 후 진행
- DSL 구조의 대규모 변경이 필요한 경우 dsl-architect로 핸드오프

## 검증 프로토콜

run 성공 확인 + export 파일 존재 확인.

## 상태 정리

완료 시 임시 파일 없음.

## 취소

사용자 요청 시 즉시 중단. Dify에 생성된 앱은 수동 삭제 안내.

## 재개

Dify 앱 존재 시 publish/run 단계부터 재개 가능.

## 스킬 부스팅

이 스킬은 다음 OMC 스킬을 활용하여 검증된 워크플로우를 적용함:

| 단계 | OMC 스킬 | 목적 |
|------|----------|------|
| Phase 1 | `ulw` 매직 키워드 | 프로토타이핑 실행 + 에러 수정 루프의 완료 보장 |

## MUST 규칙

| # | 규칙 |
|---|------|
| 1 | import 전 반드시 validate_dsl로 사전 검증을 수행한다 |
| 2 | publish/run 에러 시 DSL 수정 → validate_dsl → update 루프를 실행한다 |
| 3 | 성공 시 export로 검증된 최종 DSL을 확보한다 |
| 4 | run이 100% 정상 실행될 때까지 에러 수정 루프를 반복한다 |

## MUST NOT 규칙

| # | 금지 사항 |
|---|----------|
| 1 | DSL 구조를 대규모로 변경하지 않는다 (대규모 변경 시 dsl-architect로 핸드오프) |
| 2 | 원래 요구사항(시나리오)을 사용자 확인 없이 변형하지 않는다 |
| 3 | 사용자에게 직접 질문하지 않는다 (에이전트 내에서) |

## 검증 체크리스트

- [ ] Dify import가 성공했는가
- [ ] publish가 성공했는가
- [ ] run이 100% 정상 실행되었는가 (에러 0)
- [ ] export된 최종 DSL 파일이 존재하는가
