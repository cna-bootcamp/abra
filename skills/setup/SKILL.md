---
name: setup
description: Dify 환경 구축 및 Abra 플러그인 초기 설정
user-invocable: true
disable-model-invocation: false
type: setup
---

# setup

[SETUP 활성화]

## 목표

Dify 로컬 환경 구축부터 Abra 플러그인 초기 설정까지 전 과정을 하나의 워크플로우로 완료함:
- Docker 환경 확인 및 Dify 컨테이너 실행
- Groq 모델 프로바이더 자동 설정
- Dify 접속 정보 수집 
- Python 가상환경 생성 및 의존성 설치
- Dify 연결 테스트

## 활성화 조건

사용자가 `/abra:setup` 명령을 호출하거나 "초기 설정", "setup", "플러그인 설정", "Dify 설치", "Docker 실행", "Dify 환경" 키워드 감지 시.

## 진행상황 업데이트 및 재개
`{PROJECT_DIR}/AGENTS.md`에 각 Step 완료 시 저장. 최종 완료 시 'Done'으로 표기.   
```
## 워크플로우 진행상황
- setup: Step3
```
진행상황 정보가 있는 경우 마지막 완료 단계 이후부터 자동 재개 

## 워크플로우

### Step 0: 환경변수 셋팅

- 프로젝트 디렉토리 생성 확인
  사용자에게 AskUserQuestion으로 현재 디렉토리가 프로젝트 루트인지 물어보고 아닌 경우    
  프로젝트 디렉토리를 생성하고 그 디렉토리로 이동 후 다시 수행하라고 안내하고 종료     

  사용자가 'YES'로 답한 경우 현재 디렉토리 경로를 변수 `{PROJECT_DIR}`에 셋팅   

- ABRA 플러그인, DMAP 플러그인 디렉토리 경로 설정 
`{PROJECT_DIR}/AGENTS.md` 파일에 `{ABRA_PLUGIN_DIR}`, `{DMAP_PLUGIN_DIR}` 변수가 설정되어 있는지 확인함.
미설정 시 아래 수행 
사용자에게 ABRA 플러그인, DMAP 플러그인 디렉토리 경로를 입력받음(경로명은 `~/path1/path2` 형식으로 안내)   
<!--ASK_USER-->
{"title":"{플러그인 이름} 플러그인 디렉토리","questions":[
  {"question":"{플러그인 이름} 플러그인 디렉토리 경로를 입력해주세요.","type":"text"}
]}
<!--/ASK_USER-->

- AGENTS.md에 환경변수 저장
  ```
  ## 환경변수
  - AI_RUNTIME: 현재 구동중인 런타임(Claude Code, Claude Cowork, Cursor, Antigravity, Codex 등)
  - PROJECT_DIR: `{PROJECT_DIR}`
  - ABRA_PLUGIN_DIR: `{ABRA_PLUGIN_DIR}`
  - DMAP_PLUGIN_DIR: `{DMAP_PLUGIN_DIR}`
  ```
- AI Runtime이 Claude Code 또는 Claude Cowork인 경우 `{PROJECT_DIR}/CLAUDE.md` 생성하고 아래 내용 저장  
  ```
  @AGENTS.md
  ```

### Step 1: install.yaml 로드 

`{ABRA_PLUGIN_DIR}/gateway/install.yaml`을 읽어 설치 대상 파악.

### Step 2: Docker 확인 

`docker --version`과 `docker compose version` 명령으로 Docker 설치 여부 확인.

**미설치 시 동작:**
- Docker Desktop 설치 안내 URL 제공:
  - Windows/macOS: https://docs.docker.com/desktop/
  - Linux: https://docs.docker.com/engine/install/
- 설치 안내 후 즉시 중단 (사용자가 설치 완료 후 재실행 필요)

### Step 3: Dify 소스 확인

AskUserQuestion으로 Dify 설치 위치 확인 (기본값: `~/workspace/dify`).

**설치 위치가 없는 경우:**
```bash
git clone https://github.com/langgenius/dify.git {DIFY_DIR}
```
`{PROJECT_DIR}/AGENTS.md`의 '## 환경변수'섹션에 DIFY 경로 추가: `~/path1/path2` 형식으로 저장  
```
## 환경변수
(다른 환경변수)
- DIFY_DIR: `{DIFY_DIR}`
```

**이미 설치된 경우:**
- 기존 디렉토리 사용

### Step 4: Dify Docker 환경 변수 파일 생성

```bash
cd {DIFY_DIR}/docker
cp .env.example .env
```

`{DIFY_DIR}/docker/.env` 파일이 이미 있으면 복사를 건너뜀 (기존 설정 보존).

**필수 환경변수 설정:**

`{DIFY_DIR}/docker/.env` 파일 생성 후(또는 기존 파일이 있는 경우), 아래 항목이 비어 있으면 설정:

| 변수명 | 설정값 | 용도 |
|--------|--------|------|
| `CONSOLE_API_URL` | `http://localhost` | 콘솔 API URL (OAuth 콜백 URI 생성에 필수) |
| `CONSOLE_WEB_URL` | `http://localhost` | 콘솔 프론트엔드 URL |
| `APP_WEB_URL` | `http://localhost` | WebApp URL |

> **주의**: 이 값들이 비어 있으면 OAuth 플러그인(Google Drive 등) 연동 시
> `redirect_uri` 오류(400 invalid_request)가 발생한다.
> 외부 도메인으로 접속하는 경우 `http://localhost` 대신 해당 도메인으로 설정.

### Step 5: Docker Compose 실행

```bash
cd {DIFY_DIR}/docker
docker compose up -d
```

### Step 6: 컨테이너 상태 확인 및 헬스체크

1. `docker compose ps` 명령으로 컨테이너 상태 확인
2. HTTP 헬스체크 (최대 60초 대기):
   ```bash
   curl -f http://localhost/install || echo "Health check failed"
   ```

**컨테이너 시작 실패 시:**
- `docker compose logs` 명령으로 에러 로그 확인
- 주요 원인 안내:
  - 포트 충돌 (80, 443 포트 사용 중)
  - 메모리 부족
  - Docker 데몬 미실행
- 사용자에게 에러 내용 보고 후 중단

(중요) 컨테이너 헬스 체크하여 정상일때까지 다음 단계 진행 하지 말것   

### Step 7: 초기 설정 안내 

Dify 관리자 계정 생성 안내:
- 접속 URL: `http://localhost/install`
- 브라우저에서 위 URL로 접속하여 관리자 계정 생성 필요
- 계정 생성 완료 후 다음 단계(Step 8)로 진행

### Step 8: Groq 모델 설정 

관리자 계정 생성 완료 후, Groq 모델 프로바이더를 자동 설정한다.

**8-1. Dify 로그인 정보 확인**

`{DIFY_DIR}/docker/.env` 파일에서 `DIFY_EMAIL`, `DIFY_PASSWORD`를 읽는다.
값이 없으면 AskUserQuestion으로 Dify 관리자 이메일과 비밀번호를 입력받아 `{DIFY_DIR}/docker/.env`에 저장한다.

**8-2. Groq API Key 입력**

`{DIFY_DIR}/docker/.env` 파일에서 GROQ_API_KEY 읽음.  
없으면 AskUserQuestion으로 사용자에게 Groq API Key를 입력받는다:
- 안내 메시지: "Groq API Key를 입력해주세요. (https://console.groq.com/keys 에서 발급 가능)"
- 입력값이 `gsk_`로 시작하는지 기본 형식 검증
- 사용자가 건너뛰기를 원하면 (빈 값 또는 "skip" 입력) Step 9로 이동
- `{DIFY_DIR}/docker/.env` 파일에 GROQ_API_KEY={사용자_입력_API_KEY} 형식으로 저장

**8-3. Dify Console API 로그인**

`{ABRA_PLUGIN_DIR}/gateway/tools/dify_client.py`의 `DifyClient`를 사용하여 Dify Console API에 로그인한다.

```python
from config import DifyConfig
from dify_client import DifyClient

config = DifyConfig()
client = DifyClient(config)
# _ensure_authenticated()가 자동 호출됨
```

**로그인 실패 시:**
- 에러 메시지 출력 후 Step 9로 이동 (수동 설정 안내)

**8-4. Groq 플러그인 설치**

Groq 마켓플레이스 플러그인이 설치되어 있는지 확인하고, 없으면 설치한다:

```python
# 설치된 플러그인 목록 조회
plugins = await client.list_plugins()

# Groq 플러그인이 없으면 설치
if not any("groq" in p.get("plugin_id", "") for p in plugins.get("plugins", [])):
    # 1) 마켓플레이스 API에서 최신 identifier 동적 조회
    import httpx
    async with httpx.AsyncClient(timeout=15.0) as http:
        resp = await http.post(
            "https://marketplace.dify.ai/api/v1/plugins/batch",
            json={"plugin_ids": ["langgenius/groq"]},
        )
        uid = resp.json()["data"]["plugins"][0]["latest_package_identifier"]

    # 2) 플러그인 설치 요청
    result = await client.install_marketplace_plugin([uid])

    # 3) 비동기 설치 완료 대기 (최대 120초, 10초 간격 폴링)
    import asyncio
    for _ in range(12):
        await asyncio.sleep(10)
        resp = await client._request("GET", "/workspaces/current/plugin/tasks")
        tasks = resp.get("tasks", [])
        if not tasks:
            break  # 태스크가 비어있으면 설치 완료
        plugin_status = tasks[0]["plugins"][0]["status"]
        if plugin_status == "success":
            break
        if plugin_status == "failed":
            raise Exception(f"Groq 플러그인 설치 실패: {tasks[0]['plugins'][0].get('message', '')}")
```

> **참고**: identifier를 하드코딩하지 않고 마켓플레이스 batch API로 동적 조회해야 해시값 불일치를 방지할 수 있다.
> 설치 실패 시 "Settings > Model Providers에서 Groq 플러그인을 수동 설치해주세요" 안내 후 계속 진행.

**8-5. Groq Credentials 검증 및 저장**

```python
credentials = {"api_key": "{사용자_입력_API_KEY}"}

# 1) credentials 검증
await client.validate_provider_credentials("langgenius/groq/groq", credentials)

# 2) 검증 성공 시 저장
await client.save_provider_credentials("langgenius/groq/groq", credentials)
```

**검증 실패 시:**
- "Groq API Key가 유효하지 않습니다. 키를 확인 후 Settings > Model Providers에서 수동 설정해주세요" 안내
- Step 9로 이동

**검증 성공 시:**
- "Groq 모델 프로바이더 설정 완료" 메시지 출력

### Step 9: Dify 접속 정보 수집 

`{DIFY_DIR}/docker/.env` 파일에서 Dify 접속 정보 읽음.   
없으면 AskUserQuestion으로 Dify 접속 정보 수집:
- `DIFY_EMAIL`
- `DIFY_PASSWORD`

`{DIFY_DIR}/docker/.env` 파일 생성 또는 갱신:

```env
DIFY_API_BASE_URL=http://localhost/console/api
DIFY_EMAIL=admin@example.com
DIFY_PASSWORD=your_password
```

### Step 10: Python 가상환경 생성 및 의존성 설치

```bash
cd {ABRA_PLUGIN_DIR}/gateway
python -m venv .venv
# Windows
.venv\Scripts\activate && pip install -r requirements.txt
# macOS/Linux
source .venv/bin/activate && pip install -r requirements.txt
```

### Step 11: 도구 동작 확인 

```bash
# Windows
{ABRA_PLUGIN_DIR}\gateway\.venv\Scripts\python {ABRA_PLUGIN_DIR}\gateway\tools\dify_cli.py list
# macOS/Linux
{ABRA_PLUGIN_DIR}/gateway/.venv/bin/python {ABRA_PLUGIN_DIR}/gateway/tools/dify_cli.py list
```

Dify 연결 테스트 (앱 목록 조회 성공 여부 확인).

#### Step 12: ABRA 플러그인 디렉토리 접근 권한 셋팅 
플러그인 디렉토리에 대한 에이전트의 Read/Write/Edit/Bash 권한을 설정하여 개발 및 검증 과정에서 파일 생성/수정/실행 가능하도록 함.
`{PROJECT_DIR}/.claude/settings.local.json` 파일의 "permissions" 섹션에 아래 권한 추가:  
```
"permissions": {
  "allow": [
    "Read({ABRA_PLUGIN_DIR}/**)",
    "Write({ABRA_PLUGIN_DIR}/**)",
    "Edit({ABRA_PLUGIN_DIR}/**)",
    "Bash(python {ABRA_PLUGIN_DIR}/**)",
    "Bash(python3 {ABRA_PLUGIN_DIR}/**)"
  ],
  "additionalDirectories": [
    "{ABRA_PLUGIN_DIR}"
  ]
}
```

### Step 13: 결과 보고

설치 결과 요약:
- 컨테이너 상태 (실행 중인 서비스 목록)
- Groq 모델 설정 상태 (성공/건너뜀/실패)
- `.env` 설정 완료 여부
- 가상환경 및 의존성 설치 완료 여부
- Dify 연결 테스트 결과
- 사용 안내는 /abra:help 참조

**출력 형식:**
```
✅ Abra 플러그인 초기 설정 완료

📦 컨테이너 상태:
- {서비스명1}: Running
- {서비스명2}: Running
...

🤖 Groq 모델 설정: {완료 ✅ / 건너뜀 ⏭️ / 실패 ❌}

🌐 Dify 접속 URL: http://localhost

⚙️ `{DIFY_DIR}/docker/.env` 설정: 완료
🐍 Python 가상환경: 완료
🔗 Dify 연결 테스트: {성공 ✅ / 실패 ❌}

📌 다음 단계:
1. AI Runtime(Claude Code, Cursor 등) 재시작
2. /abra:scenario 명령으로 시나리오 생성 시작

🔑 비밀번호 초기화:
cd {DIFY_DIR}/docker && docker compose exec api flask reset-password
```

## 문제 해결

| 문제 | 원인 | 해결 방법 |
|------|------|----------|
| Docker 미설치 | Docker/Docker Compose 미설치 | 설치 URL 안내 후 사용자 설치 대기 |
| 포트 충돌 (80, 443) | 다른 서비스가 포트 사용 중 | 기존 서비스 중지 또는 Dify 포트 변경 안내 |
| 컨테이너 시작 실패 | 메모리 부족, 설정 오류 | `docker compose logs` 확인 안내 |
| 헬스체크 실패 | 컨테이너 부팅 지연 | 60초 대기 후 재시도 안내 |
| API 컨테이너 unhealthy (워커 미부팅) | Docker Desktop 첫 실행 시 gunicorn 워커가 "Booting worker" 로그 없이 멈춤 (CPU 0%, 메모리 ~87MiB) | `docker compose restart api` 후 "Booting worker with pid" 로그 확인 |
| Groq 플러그인 설치 120초 초과 후 실패 보고 | Python 소스 pre-compile 등 실제 설치에 2분 이상 소요되어 120초 타임아웃 초과 | 폴링 대기를 240초(24회×10초)로 늘리거나, 타임아웃 후 task 상태를 별도 조회하여 success 여부 확인 |
| Dify 로그인 실패 | 이메일/비밀번호 불일치 | `{DIFY_DIR}/docker/.env` 확인 또는 비밀번호 초기화 명령 안내 |
| Groq 플러그인 설치 실패 | 네트워크 또는 Dify 버전 이슈 | Settings > Model Providers에서 수동 설치 안내 |
| Groq API Key 검증 실패 | 잘못된 API Key | https://console.groq.com/keys 에서 키 재발급 안내 |
| Dify 연결 실패 | 접속 정보 불일치 | `{DIFY_DIR}/docker/.env` 확인 또는 비밀번호 초기화 안내 |

## MUST 규칙

| # | 규칙 |
|---|------|
| 1 | install.yaml을 참조하여 설치를 수행한다 |
| 2 | Docker 및 Docker Compose 설치 여부를 먼저 확인한다 |
| 3 | Docker Compose 실행 후 헬스체크를 수행한다 |
| 4 | 컨테이너 시작 실패 시 에러 로그를 확인하고 원인을 안내한다 |
| 5 | 초기 설정 안내(관리자 계정 생성 URL)를 반드시 제공한다 |
| 6 | .env 파일 생성 전 사용자에게 접속 정보를 확인한다 |
| 7 | Python 가상환경을 생성하고 requirements.txt 의존성을 설치한다 |
| 8 | 설치 완료 후 Dify 연결 테스트를 수행한다 |

## MUST NOT 규칙

| # | 금지 사항 |
|---|----------|
| 1 | Docker 미설치 상태에서 Docker Compose를 실행하지 않는다 |
| 2 | 기존 Dify docker/.env 파일을 덮어쓰지 않는다 (이미 존재하면 건너뜀) |
| 3 | 헬스체크 실패를 무시하고 다음 단계로 진행하지 않는다 |
| 4 | install.yaml에 정의되지 않은 도구를 설치하지 않는다 |
| 5 | 기존 `{DIFY_DIR}/docker/.env` 파일을 사용자 확인 없이 덮어쓰지 않는다 |
| 6 | Dify 연결 테스트 실패 시 무시하고 진행하지 않는다 |

## 검증 체크리스트

- [ ] install.yaml 파일을 정상 로드했는가
- [ ] Docker 및 Docker Compose가 설치되어 있는가
- [ ] Dify 소스가 지정 위치에 존재하는가
- [ ] Dify docker/.env 파일이 생성 또는 보존되었는가
- [ ] Docker Compose 컨테이너가 정상 실행 중인가
- [ ] 헬스체크(HTTP)가 통과했는가
- [ ] 초기 설정 URL이 안내되었는가
- [ ] Groq API Key가 입력되었는가 (건너뛰기 허용)
- [ ] Groq 플러그인이 설치되었는가
- [ ] Groq credentials가 검증 및 저장되었는가
- [ ] `{DIFY_DIR}/docker/.env` 파일이 올바른 위치에 생성되었는가
- [ ] Python 가상환경이 생성되었는가
- [ ] requirements.txt 의존성이 설치되었는가
- [ ] Dify 연결 테스트(앱 목록 조회)가 성공했는가

