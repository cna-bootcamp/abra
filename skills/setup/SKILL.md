---
name: setup
description: Abra 플러그인 초기 설정
user-invocable: true
disable-model-invocation: false
type: setup
---

# setup

[SETUP 활성화]

## 목표

Abra 플러그인의 초기 설정을 수행함:
- Dify 접속 정보 확인 및 `.env` 파일 생성
- Python 가상환경 생성 및 의존성 설치
- Dify 연결 테스트

## 활성화 조건

사용자가 `/abra:setup` 명령을 호출하거나 "초기 설정", "setup", "플러그인 설정" 키워드 감지 시.

## 선행 조건

`/abra:dify-setup` 완료 (Dify 실행 중)

## 워크플로우

### Step 1: install.yaml 로드 (`ulw` 활용)

`gateway/install.yaml`을 읽어 설치 대상 파악.

### Step 2: Dify 접속 정보 수집 (`ulw` 활용)

AskUserQuestion으로 Dify 접속 정보 수집:
- `DIFY_BASE_URL` (기본값: `http://localhost/console/api`)
- `DIFY_EMAIL`
- `DIFY_PASSWORD`

### Step 3: .env 파일 생성 (`ulw` 활용)

`gateway/.env` 파일 생성 또는 갱신.

```env
DIFY_BASE_URL=http://localhost/console/api
DIFY_EMAIL=admin@example.com
DIFY_PASSWORD=your_password
```

### Step 4: Python 가상환경 생성 및 의존성 설치 (`ulw` 활용)

```bash
cd gateway
python -m venv .venv
# Windows
.venv\Scripts\activate && pip install -r requirements.txt
# macOS/Linux
source .venv/bin/activate && pip install -r requirements.txt
```

### Step 5: 도구 동작 확인 (`ulw` 활용)

```bash
# Windows
gateway\.venv\Scripts\python gateway\tools\dify_cli.py list
# macOS/Linux
gateway/.venv/bin/python gateway/tools/dify_cli.py list
```

Dify 연결 테스트 (앱 목록 조회 성공 여부 확인).

### Step 6: 결과 보고

설치 결과 요약:
- `.env` 설정 완료 여부
- 가상환경 및 의존성 설치 완료 여부
- Dify 연결 테스트 결과
- 사용 안내는 /abra:help 참조

## 사용자 상호작용

AskUserQuestion으로 Dify 접속 정보 수집 (Step 2).

## 스킬 부스팅

이 스킬은 다음 OMC 스킬을 활용하여 검증된 워크플로우를 적용함:

| 단계 | OMC 스킬 | 목적 |
|------|----------|------|
| Step 1~5 | `ulw` 매직 키워드 | 각 단계의 완료 보장 |

## MUST 규칙

| # | 규칙 |
|---|------|
| 1 | install.yaml을 참조하여 설치를 수행한다 |
| 2 | .env 파일 생성 전 사용자에게 접속 정보를 확인한다 |
| 3 | Python 가상환경을 생성하고 requirements.txt 의존성을 설치한다 |
| 4 | 설치 완료 후 Dify 연결 테스트를 수행한다 |

## MUST NOT 규칙

| # | 금지 사항 |
|---|----------|
| 1 | install.yaml에 정의되지 않은 도구를 설치하지 않는다 |
| 2 | 기존 .env 파일을 사용자 확인 없이 덮어쓰지 않는다 |
| 3 | Dify 연결 테스트 실패 시 무시하고 진행하지 않는다 |

## 검증 체크리스트

- [ ] install.yaml 파일을 정상 로드했는가
- [ ] .env 파일이 올바른 위치(gateway/.env)에 생성되었는가
- [ ] Python 가상환경이 생성되었는가
- [ ] requirements.txt 의존성이 설치되었는가
- [ ] Dify 연결 테스트(앱 목록 조회)가 성공했는가
