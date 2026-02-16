---
name: dev-plan
description: 개발계획서 작성 (STEP 4)
user-invocable: true
type: orchestrator
---

# dev-plan

[dev-plan 활성화]

## 목표

검증된 DSL과 시나리오를 기반으로 개발계획서를 작성함.
기술스택, 아키텍처, 모듈 설계, 테스트 전략, 배포 계획을 포함하는 포괄적 계획서를 산출함.

## 활성화 조건

- 사용자가 `/abra:dev-plan` 호출 시
- "개발계획서", "계획서 작성", "개발 계획" 키워드 감지 시

## 에이전트 호출 규칙

### 에이전트 FQN

| 에이전트 | FQN |
|----------|-----|
| plan-writer | `abra:plan-writer:plan-writer` |

### 프롬프트 조립

1. `agents/plan-writer/` 에서 3파일 로드 (AGENT.md + agentcard.yaml + tools.yaml)
2. `gateway/runtime-mapping.yaml` 참조하여 구체화:
   - **모델 구체화**: agentcard.yaml의 `tier: MEDIUM` → `tier_mapping`에서 `claude-sonnet-4-5` 모델 결정
   - **툴 구체화**: tools.yaml의 추상 도구 → `tool_mapping`에서 실제 도구 결정
     - `file_read` → builtin `Read`
     - `file_write` → builtin `Write`
   - **금지액션 구체화**: agentcard.yaml의 `forbidden_actions: ["file_delete", "code_execute"]` → `action_mapping`에서 제외할 실제 도구 결정
     - `file_delete` → `Bash(rm)` 제외
     - `code_execute` → `Bash` 제외
   - **최종 도구** = (Read, Write) - (Bash)
3. 3파일을 합쳐 하나의 프롬프트로 조립
   - **프롬프트 구성 순서**: 공통 정적(runtime-mapping) → 에이전트별 정적(3파일) → 동적(작업 지시)
4. `Task(subagent_type="abra:plan-writer:plan-writer", model="sonnet", prompt=조립된 프롬프트)` 호출

## 워크플로우

### Phase 0: 입력 확인

#### no_workflow 모드

`no_workflow: true`가 ARGS로 전달된 경우, DSL/시나리오 존재 검증을 스킵하고
Phase 1로 직행함. 이는 Short Path (Dify 워크플로우 없이 코드만 개발)에서 사용됨.

#### Skill→Skill 사전 입력 처리

`ARGS` 루트 키 존재 시 plugin-to-plugin 호출로 판별하고, 내부 값을 사용:

| ARGS 내부 키 | 대응 항목 | 동작 |
|-------------|----------|------|
| `source_plugin` | — | 호출자 플러그인 식별 |
| `domain_context` | — | 개발계획서 작성 시 컨텍스트로 전달 |
| `service_purpose` | — | 개발계획서 작성 시 서비스 목적으로 전달 |
| `requirement` | — | 개발계획서 작성 시 요구사항으로 전달 |
| `references` | — | 개발계획서 작성 시 참고 자료로 전달 |
| `project_dir` | 프로젝트 디렉토리 | 제공된 경로 사용 |
| `allowed_options` | 기술스택 선호 (Phase 1) | 제공된 옵션만 표시 |
| `no_workflow` | Phase 0 검증 | `true` 시 DSL/시나리오 검증 스킵 |

`ARGS` 키 미존재 시 사용자 직접 호출로 판별하고, AskUserQuestion으로 입력 수집.

#### 기본 모드 (no_workflow 미설정)

검증된 DSL 파일과 scenario.md 파일의 존재 여부를 확인함.

**검증 항목:**
- DSL 파일: `{project_dir}/{app-name}.dsl.yaml` 존재 확인
- 시나리오: `{project_dir}/scenario.md` 존재 확인

**미존재 시:**
- DSL 파일 없음 → `dsl-generate` 스킬로 위임
- 시나리오 파일 없음 → `scenario` 스킬로 위임

### Phase 1: 비기능요구사항 수집 (`ulw` 활용)

AskUserQuestion으로 비기능요구사항을 수집함.

**질문 항목:**

1. **기술스택 선호**
   - 질문: "어떤 기술스택을 선호하시나요?"
   - 전체 옵션:
     - "Option A: Dify 런타임 활용 (DSL을 Dify API로 배포)"
     - "Option B: 코드 기반 전환 (Python + LangChain/LangGraph)"
     - "Option C: 코드 기반 전환 (TypeScript + LangChain.js)"
   - 기본값: "Option B"
   - **allowed_options 적용**: ARGS에 `allowed_options`가 제공된 경우,
     해당 목록에 포함된 옵션만 사용자에게 표시함.
     예: `allowed_options: [B, C]` → Option A(Dify) 제외, Option B/C만 표시

2. **배포 환경**
   - 질문: "배포 환경은 무엇인가요?"
   - 옵션:
     - "로컬 환경"
     - "Docker 컨테이너"
     - "Kubernetes"
     - "서버리스 (AWS Lambda, Vercel 등)"
   - 기본값: "Docker 컨테이너"

3. **성능 요구사항**
   - 질문: "응답 속도 요구사항은?"
   - 옵션:
     - "빠름 (1초 이내)"
     - "보통 (3초 이내)"
     - "느림 (5초 이상 허용)"
   - 기본값: "보통"

4. **보안 요구사항**
   - 질문: "보안 요구사항이 있나요?"
   - 옵션:
     - "높음 (인증/권한/암호화 필수)"
     - "보통 (기본 인증)"
     - "낮음 (내부 사용만)"
   - 기본값: "보통"

5. **기타 제약 사항**
   - 질문: "추가로 고려해야 할 제약 사항이 있나요? (선택)"
   - 입력: 자유 텍스트

### Phase 2: 개발계획서 작성 → Agent: plan-writer (`/oh-my-claudecode:ralplan` 활용)

- **TASK**: 검증된 DSL과 시나리오를 기반으로 기술스택, 아키텍처, 모듈 설계, 테스트 전략, 배포 계획을 포함하는 개발계획서 작성
- **EXPECTED OUTCOME**: 완성된 개발계획서 마크다운 파일 (`{project_dir}/dev-plan.md`)
- **MUST DO**:
  - `references/develop-plan-generate.md` 프롬프트 템플릿 활용
  - DSL 구조와 계획의 일관성 확보
  - Phase 1에서 수집한 비기능요구사항 반영
  - 9개 섹션(개요, 기술스택, 아키텍처, 모듈 설계, 프롬프트 최적화, API 설계서, 데이터 모델, 테스트 전략, 배포 계획) 모두 포함
- **MUST NOT DO**:
  - 코드 작성 금지
  - DSL 파일 수정 금지
  - 시나리오 파일 수정 금지
- **CONTEXT**:
  - DSL 파일: `{project_dir}/{app-name}.dsl.yaml`
  - 시나리오: `{project_dir}/scenario.md`
  - 비기능요구사항: `{nfr}`
  - 출력 파일: `{project_dir}/dev-plan.md`

**오케스트레이션 스킬 활용:**

이 Phase는 `/oh-my-claudecode:ralplan`을 활용하여 수행함.
ralplan은 Planner + Architect + Critic 에이전트가 반복 합의하여 최적의 계획을 도출하는 검증된 워크플로우를 제공함.

### Phase 3: 리뷰 포인트 체크 및 결과 보고 (`/oh-my-claudecode:review` 활용)

이 Phase는 `/oh-my-claudecode:review`를 활용하여 수행함.
review는 Critic 에이전트가 계획서의 완성도와 일관성을 체계적으로 검토하는 검증된 워크플로우를 제공함.

개발계획서를 사용자에게 보고하고, 다음 리뷰 포인트를 확인함.

**리뷰 포인트:**

1. **DSL-계획 일관성**
   - DSL의 노드 구조와 개발계획서의 모듈 설계가 일치하는가?
   - DSL의 입출력 변수와 API 설계서의 스키마가 일치하는가?

2. **비기능요구사항 반영**
   - Phase 1에서 수집한 모든 비기능요구사항이 계획서에 반영되었는가?
   - 기술스택 선택이 요구사항을 충족하는가?

3. **프로덕션 전환 전략**
   - DSL 기반 프로토타입을 프로덕션 코드로 전환하는 전략이 명확한가?
   - 테스트 전략이 품질을 보장할 수 있는가?

4. **배포 실현 가능성**
   - 배포 계획이 선택된 환경에서 실현 가능한가?
   - CI/CD 파이프라인이 구체적으로 정의되었는가?

**결과 보고 형식:**

```markdown
# dev-plan 완료 보고

## 산출물
- 개발계획서: `{project_dir}/dev-plan.md`

## 리뷰 포인트
- [✓/✗] DSL-계획 일관성
- [✓/✗] 비기능요구사항 반영
- [✓/✗] 프로덕션 전환 전략
- [✓/✗] 배포 실현 가능성

## 다음 단계
- 개발계획서 검토 후 `/abra:develop` 호출하여 구현 시작
```

## 완료 조건

- [ ] 검증된 DSL 파일 존재 확인
- [ ] scenario.md 파일 존재 확인
- [ ] 비기능요구사항 수집 완료
- [ ] 개발계획서 파일 생성 완료 (`dev-plan.md`)
- [ ] 개발계획서에 9개 섹션 모두 포함
- [ ] 리뷰 포인트 체크 완료

## 검증 프로토콜

개발계획서 필수 섹션 존재 확인:

```bash
# 섹션 존재 여부 확인
grep -E "^## [0-9]\. (개요|기술스택|아키텍처|모듈 설계|프롬프트 최적화|API 설계서|데이터 모델|테스트 전략|배포 계획)" {project_dir}/dev-plan.md
```

9개 섹션이 모두 출력되어야 검증 통과.

## 상태 정리

완료 시 임시 파일 없음 (상태 파일 미사용).

## 취소

사용자가 "cancelomc" 또는 "stopomc" 요청 시 즉시 중단.
작업 중 생성된 파일은 유지됨 (사용자가 수동 삭제 가능).

## 재개

`dev-plan.md` 파일이 이미 존재하면 Phase 3(리뷰 단계)부터 재개 가능.
사용자에게 기존 파일 덮어쓰기 여부를 질문함.

## 스킬 부스팅

이 스킬은 다음 OMC 스킬을 활용하여 검증된 워크플로우를 적용함:

| 단계 | OMC 스킬 | 목적 |
|------|----------|------|
| Phase 1 | `ulw` 매직 키워드 | 비기능요구사항 수집의 완료 보장 |
| Phase 2 | `/oh-my-claudecode:ralplan` | 반복 합의 기반 계획 수립 (Planner + Architect + Critic) |
| Phase 3 | `/oh-my-claudecode:review` | 계획서 완성도 및 일관성 체계적 검토 (Critic) |

ralplan의 반복 합의 메커니즘을 통해 개발계획서의 품질과 일관성을 보장하고,
review를 통해 최종 리뷰 포인트를 체계적으로 검증함.

## MUST 규칙

| # | 규칙 |
|---|------|
| 1 | 개발계획서에 9개 섹션(개요, 기술스택, 아키텍처, 모듈 설계, 프롬프트 최적화, API 설계서, 데이터 모델, 테스트 전략, 배포 계획)을 모두 포함한다 |
| 2 | Phase 1에서 수집한 비기능요구사항을 반드시 반영한다 |
| 3 | references/develop-plan-generate.md 프롬프트 템플릿을 활용한다 |
| 4 | DSL 구조와 개발계획서의 모듈 설계 일관성을 확보한다 |

## MUST NOT 규칙

| # | 금지 사항 |
|---|----------|
| 1 | 코드를 작성하지 않는다 (개발은 별도 STEP) |
| 2 | DSL 파일을 수정하지 않는다 |
| 3 | 시나리오 파일을 수정하지 않는다 |

## 검증 체크리스트

- [ ] dev-plan.md 파일이 output/ 디렉토리에 존재하는가
- [ ] 9개 필수 섹션이 모두 포함되어 있는가
- [ ] 비기능요구사항이 반영되어 있는가
- [ ] DSL-계획 일관성 리뷰 포인트가 통과했는가
- [ ] 배포 실현 가능성 리뷰 포인트가 통과했는가
