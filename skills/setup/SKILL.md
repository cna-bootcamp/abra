---
name: setup
description: Abra 플러그인 초기 설정
user-invocable: true
disable-model-invocation: false
---

# setup

[SETUP 활성화]

## 목표

Abra 플러그인의 초기 설정을 수행함:
- Dify 접속 정보 확인 및 `.env` 파일 생성
- Python 가상환경 생성 및 의존성 설치
- Dify 연결 테스트

## 선행 조건

`/abra:dify-setup` 완료 (Dify 실행 중)

## 워크플로우

### Step 1: install.yaml 로드

`gateway/install.yaml`을 읽어 설치 대상 파악.

### Step 2: Dify 접속 정보 수집

AskUserQuestion으로 Dify 접속 정보 수집:
- `DIFY_BASE_URL` (기본값: `http://localhost/console/api`)
- `DIFY_EMAIL`
- `DIFY_PASSWORD`

### Step 3: .env 파일 생성

`gateway/.env` 파일 생성 또는 갱신.

```env
DIFY_BASE_URL=http://localhost/console/api
DIFY_EMAIL=admin@example.com
DIFY_PASSWORD=your_password
```

### Step 4: Python 가상환경 생성 및 의존성 설치

```bash
cd gateway
python -m venv .venv
# Windows
.venv\Scripts\activate && pip install -r requirements.txt
# macOS/Linux
source .venv/bin/activate && pip install -r requirements.txt
```

### Step 5: 도구 동작 확인

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
