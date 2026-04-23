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
- "프로토타입 개선", "워크플로우 개선"

## 작업 환경 변수 로드 
AGENTS.md 파일에서 `## 환경변수`섹션의 환경변수 로딩. 로딩 실패 시 사용자에게 `/abra:setup`을 먼저 수행하라고 안내하고 종료.     

## 에이전트 호출 규칙

### 에이전트 FQN

| 에이전트 | FQN |
|----------|-----|
| dsl-architect | `abra:dsl-architect:dsl-architect` |
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

## 진행상황 업데이트 및 재개
`{PROJECT_DIR}/AGENTS.md`에 각 Phase 완료 시 저장. 최종 완료 시 'Done'으로 표기.   
```
## 워크플로우 진행상황
- {skill-name}: Phase3
```
진행상황 정보가 있는 경우 마지막 완료 단계 이후부터 자동 재개

## 워크플로우

### Phase 0: 입력 모드 판별

사용자 입력과 파일 존재 여부를 조합하여 실행 모드를 결정함.

**A) 개선 요청 모드**: 프롬프트에 `"프로토타입 개선: {설명}"` 또는 `"워크플로우 개선: {설명}"` 패턴 존재
   + DSL 파일(원본 또는 버전 파일) 존재
   → Phase 0.5 진행

**B) DSL 없음**: DSL 파일 미존재 → dsl-generate 스킬로 위임

**C) 일반 실행**: DSL 파일 있음 + 개선 요청 없음 → Phase 1 진행

### Phase 0.5: 개선 DSL 생성 → Agent: dsl-architect

- **TASK**: 사용자의 개선 설명을 기반으로 기존 DSL 수정 및 검증
- **EXPECTED OUTCOME**: 수정된 DSL YAML (`validate_dsl` 통과)
- **MUST DO**:
  - 입력 DSL: `{output_dir}/{app-name}_v{MAX}.dsl.yaml` (버전 파일 없으면 `{output_dir}/{app-name}.dsl.yaml`)
  - 개선 설명: 사용자 입력의 `"프로토타입 개선:"` 또는 `"워크플로우 개선:"` 이후 텍스트 추출
  - 수정 후 `validate_dsl`로 반드시 검증
  - 검증 통과 시 `{output_dir}/{app-name}.wip.dsl.yaml`로 저장
- **MUST NOT DO**: 원래 요구사항(시나리오)의 핵심 목적 변경 금지
- **NEXT**: wip 파일 저장 완료 후 Phase 1 진행

### Phase 1: 프로토타이핑 실행 → Agent: prototype-runner

- **TASK**: DSL을 Dify에 import → publish → run → export 수행. 에러 시 DSL 수정 → 재검증 → 재시도 루프 자동 실행
- **EXPECTED OUTCOME**: 검증 완료된 DSL 파일 (export된 최종 버전)
- **MUST DO**:
  - import 전 반드시 validate_dsl로 사전 검증
  - publish/run 에러 시 DSL 수정 → validate_dsl → update 반복
  - 성공 시 export 전 `{output_dir}/{app-name}_v*.dsl.yaml` 스캔으로 다음 버전 번호 결정
  - export 파일명을 `{app-name}_v{N}.dsl.yaml` 형태로 저장
- **MUST NOT DO**: 사용자에게 직접 질문 금지, DSL 구조 대규모 변경 금지 (대규모 변경 시 dsl-architect로 핸드오프)
- **CONTEXT**:
  - 입력 DSL 우선순위:
    1. `{output_dir}/{app-name}.wip.dsl.yaml` (존재하면 최우선)
    2. `{output_dir}/{app-name}_v{MAX}.dsl.yaml` (버전 파일 있는 경우)
    3. `{output_dir}/{app-name}.dsl.yaml` (원본)
  - 가상환경: `gateway/.venv`
  - 버전 관리:
    - export 전 `{output_dir}/{app-name}_v*.dsl.yaml` 파일 목록 스캔하여 MAX 버전 추출
    - export 저장 경로: `{output_dir}/{app-name}_v{MAX+1}.dsl.yaml` (버전 파일 없으면 `_v1`)
    - export 성공 후 `{output_dir}/{app-name}.wip.dsl.yaml` 파일이 존재하면 삭제

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
- Export된 DSL 파일 경로 (버전 포함): `{app-name}_v{N}.dsl.yaml`
- 누적 버전 목록: `v1 ~ v{N}` (output_dir 내 파일 기준)

**완료 메시지 필수 포함 내용:**

```
Dify에서 워크플로우를 실행해보신 후 개선이 필요하면 아래 형식으로 입력하세요.

> 프로토타입 개선: [개선사항 설명]

예시:
- 프로토타입 개선: LLM 응답 파싱 노드에 에러 처리 추가
- 프로토타입 개선: 입력 변수 검증 로직 강화
- 프로토타입 개선: 프롬프트 템플릿 한국어로 변경
```

## 완료 조건

- [ ] Dify import 성공
- [ ] publish 성공
- [ ] run 성공 (에러 0, 100% 정상 실행)
- [ ] export로 검증된 DSL 확보

**완료 보장 규칙:**
- run이 100% 정상 실행될 때까지 에러 수정 루프를 반복함
- 단, 총 소요 시간이 10분을 초과하면 즉시 중단하고 사용자에게 문제 보고
  - 보고 내용: 현재 상태, 발생 에러 목록, 시도한 수정 내역, 권장 다음 조치

**요구사항 변형 금지:**
- 에러 수정 과정에서 원래 요구사항(시나리오)을 변형해야 하는 경우,
  반드시 사용자에게 확인 후 진행
- DSL 구조의 대규모 변경이 필요한 경우 dsl-architect로 핸드오프

## 검증 프로토콜

run 성공 확인 + export 파일 존재 확인.

## 상태 정리

완료 시 임시 파일 없음. `{app-name}.wip.dsl.yaml`은 export 성공 후 삭제함.

## MUST 규칙

| # | 규칙 |
|---|------|
| 1 | import 전 반드시 validate_dsl로 사전 검증을 수행한다 |
| 2 | publish/run 에러 시 DSL 수정 → validate_dsl → update 루프를 실행한다 |
| 3 | 성공 시 export로 검증된 최종 DSL을 확보한다 |
| 4 | run이 100% 정상 실행될 때까지 에러 수정 루프를 반복한다 |
| 5 | export 전 output_dir 내 버전 파일 스캔 후 다음 버전 번호를 결정한다 |
| 6 | export 파일명은 반드시 `{app-name}_v{N}.dsl.yaml` 형태로 저장한다 |

## MUST NOT 규칙

| # | 금지 사항 |
|---|----------|
| 1 | DSL 구조를 대규모로 변경하지 않는다 (대규모 변경 시 dsl-architect로 핸드오프) |
| 2 | 원래 요구사항(시나리오)을 사용자 확인 없이 변형하지 않는다 |
| 3 | 사용자에게 직접 질문하지 않는다 (에이전트 내에서) |
| 4 | 개선 요청 시 시나리오의 핵심 목적을 변경하지 않는다 (Phase 0.5 dsl-architect 포함) |

## 검증 체크리스트

- [ ] Dify import가 성공했는가
- [ ] publish가 성공했는가
- [ ] run이 100% 정상 실행되었는가 (에러 0)
- [ ] export된 최종 DSL 파일이 `{app-name}_v{N}.dsl.yaml` 형태로 존재하는가
- [ ] export 성공 후 wip 파일이 삭제되었는가
- [ ] 완료 메시지에 개선 요청 가이드가 포함되었는가
- [ ] 개선 요청 시 Phase 0.5에서 dsl-architect가 호출되었는가
