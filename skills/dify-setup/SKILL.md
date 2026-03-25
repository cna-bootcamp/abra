---
name: dify-setup
description: Dify 로컬 환경 구축 (Docker Compose)
user-invocable: true
disable-model-invocation: false
type: setup
---

# dify-setup

[dify-setup 활성화]

## 목표

Docker Compose를 사용하여 Dify 로컬 개발 환경을 구축함.
Docker 설치 확인 → Dify 소스 클론 → 환경 변수 파일 생성 → 컨테이너 실행 → 헬스체크 → 초기 설정 안내 순으로 진행.

## 활성화 조건

사용자가 `/abra:dify-setup` 명령을 호출하거나 "Dify 설치", "Docker 실행", "Dify 환경" 키워드 감지 시.

## {ABRA_PLUGIN_DIR} 변수 해석
오케스트레이터는 실행 시작 시 다음 순서로 `{ABRA_PLUGIN_DIR}`를 결정:
0. 현재 프로젝트의 CLAUDE.md에 {ABRA_PLUGIN_DIR}변수가 있으면 해당 경로 사용하고 이후 진행 안함  
1. 아래 후보 경로 중 존재하는 첫 번째를 `PLUGIN_BASE_DIR`로 선택
   - `/mnt/.local-plugins/cache/unicorn/dmap` (Cowork VM)
   - `~/.claude/plugins/cache/unicorn/dmap` (Mac/Linux CLI)
   - `%APPDATA%/Claude/plugins/cache/unicorn/dmap` (Windows CLI)
2. `PLUGIN_BASE_DIR` 하위의 버전 디렉토리를 시맨틱 버전 비교하여 최신 버전 선택
3. 해당 디렉토리의 절대 경로를 `{ABRA_PLUGIN_DIR}`에 바인딩
4. 이후 모든 `{ABRA_PLUGIN_DIR}/...` 경로를 절대 경로로 치환하여 파일을 읽음
5. 현재 프로젝트의 CLAUDE.md에 {ABRA_PLUGIN_DIR}을 기록하여 이후 중복 계산 안하게 함     

## 사전 요구사항

| 항목 | 최소 사양 |
|------|----------|
| CPU | 2 Core 이상 |
| RAM | 4 GiB 이상 |
| Docker | 설치 필요 |
| Docker Compose | 설치 필요 |

## 워크플로우

### Step 1: Docker 확인 (`ulw` 활용)

`docker --version`과 `docker compose version` 명령으로 Docker 설치 여부 확인.

**미설치 시 동작:**
- Docker Desktop 설치 안내 URL 제공:
  - Windows/macOS: https://docs.docker.com/desktop/
  - Linux: https://docs.docker.com/engine/install/
- 설치 안내 후 즉시 중단 (사용자가 설치 완료 후 재실행 필요)

### Step 2: Dify 소스 확인 (`ulw` 활용)

AskUserQuestion으로 Dify 설치 위치 확인 (기본값: `~/workspace/dify`).

**설치 위치가 없는 경우:**
```bash
git clone https://github.com/langgenius/dify.git {설치_위치}
```

**이미 설치된 경우:**
- 기존 디렉토리 사용

### Step 3: 환경 변수 파일 생성 및 설정 (`ulw` 활용)

```bash
cd {설치_위치}/docker
cp .env.example .env
```

`.env` 파일이 이미 있으면 복사를 건너뜀 (기존 설정 보존).

**필수 환경변수 설정:**

`.env` 파일 생성 후(또는 기존 파일이 있는 경우), 아래 항목이 비어 있으면 설정:

| 변수명 | 설정값 | 용도 |
|--------|--------|------|
| `CONSOLE_API_URL` | `http://localhost` | 콘솔 API URL (OAuth 콜백 URI 생성에 필수) |
| `CONSOLE_WEB_URL` | `http://localhost` | 콘솔 프론트엔드 URL |
| `APP_WEB_URL` | `http://localhost` | WebApp URL |

> **주의**: 이 값들이 비어 있으면 OAuth 플러그인(Google Drive 등) 연동 시
> `redirect_uri` 오류(400 invalid_request)가 발생한다.
> 외부 도메인으로 접속하는 경우 `http://localhost` 대신 해당 도메인으로 설정.

### Step 4: Docker Compose 실행 (`ulw` 활용)

```bash
cd {설치_위치}/docker
docker compose up -d
```

### Step 5: 컨테이너 상태 확인 및 헬스체크 (`ulw` 활용)

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

### Step 6: 초기 설정 안내 (`ulw` 활용)

Dify 관리자 계정 생성 안내:
- 접속 URL: `http://localhost/install`
- 브라우저에서 위 URL로 접속하여 관리자 계정 생성 필요
- 계정 생성 완료 후 다음 단계(Step 7)로 진행

### Step 7: Groq 모델 설정 (`ulw` 활용)

관리자 계정 생성 완료 후, Groq 모델 프로바이더를 자동 설정한다.

**7-1. Dify 로그인 정보 확인**

`gateway/.env` 파일에서 `DIFY_EMAIL`, `DIFY_PASSWORD`를 읽는다.
값이 없으면 AskUserQuestion으로 Dify 관리자 이메일과 비밀번호를 입력받아 `gateway/.env`에 저장한다.

**7-2. Groq API Key 입력**

AskUserQuestion으로 사용자에게 Groq API Key를 입력받는다:
- 안내 메시지: "Groq API Key를 입력해주세요. (https://console.groq.com/keys 에서 발급 가능)"
- 입력값이 `gsk_`로 시작하는지 기본 형식 검증
- 사용자가 건너뛰기를 원하면 (빈 값 또는 "skip" 입력) Step 8로 이동

**7-3. Dify Console API 로그인**

`{ABRA_PLUGIN_DIR}/gateway/tools/dify_client.py`의 `DifyClient`를 사용하여 Dify Console API에 로그인한다.

```python
from config import DifyConfig
from dify_client import DifyClient

config = DifyConfig()
client = DifyClient(config)
# _ensure_authenticated()가 자동 호출됨
```

**로그인 실패 시:**
- 에러 메시지 출력 후 Step 8로 이동 (수동 설정 안내)

**7-4. Groq 플러그인 설치**

Groq 마켓플레이스 플러그인이 설치되어 있는지 확인하고, 없으면 설치한다:

```python
# 설치된 플러그인 목록 조회
plugins = await client.list_plugins()

# Groq 플러그인이 없으면 설치
if not any("groq" in p.get("plugin_id", "") for p in plugins.get("plugins", [])):
    await client.install_marketplace_plugin([
        "langgenius/groq:0.0.12@38f75b2fd3d5dded2a0fe236dbcfe38a56d1028cc tried2d1cf7ea0e18ba1f4e40"
    ])
```

> **참고**: 플러그인 identifier의 해시값은 Dify 버전에 따라 다를 수 있다.
> 설치 실패 시 "Settings > Model Providers에서 Groq 플러그인을 수동 설치해주세요" 안내 후 계속 진행.

**7-5. Groq Credentials 검증 및 저장**

```python
credentials = {"api_key": "{사용자_입력_API_KEY}"}

# 1) credentials 검증
await client.validate_provider_credentials("langgenius/groq/groq", credentials)

# 2) 검증 성공 시 저장
await client.save_provider_credentials("langgenius/groq/groq", credentials)
```

**검증 실패 시:**
- "Groq API Key가 유효하지 않습니다. 키를 확인 후 Settings > Model Providers에서 수동 설정해주세요" 안내
- Step 8로 이동

**검증 성공 시:**
- "Groq 모델 프로바이더 설정 완료" 메시지 출력

### Step 8: 결과 보고

설치 결과 요약:
- 컨테이너 상태 (실행 중인 서비스 목록)
- Dify 접속 URL (`http://localhost`)
- Groq 모델 설정 상태 (성공/건너뜀/실패)
- 다음 단계 안내: `/abra:setup` 명령으로 플러그인 초기 설정

**출력 형식:**
```
✅ Dify 로컬 환경 구축 완료

📦 컨테이너 상태:
- {서비스명1}: Running
- {서비스명2}: Running
...

🤖 Groq 모델 설정: {완료 ✅ / 건너뜀 ⏭️ / 실패 ❌}

🌐 Dify 접속 URL: http://localhost

📌 다음 단계:
1. /abra:setup 명령으로 플러그인 초기 설정 진행

🔑 비밀번호 초기화:
cd {설치_위치}/docker && docker compose exec api flask reset-password
```

## 사용자 상호작용

- AskUserQuestion으로 Dify 설치 위치 확인 (Step 2)
- AskUserQuestion으로 Groq API Key 입력받기 (Step 7-2, 건너뛰기 가능)

## 문제 해결

| 문제 | 원인 | 해결 방법 |
|------|------|----------|
| Docker 미설치 | Docker/Docker Compose 미설치 | 설치 URL 안내 후 사용자 설치 대기 |
| 포트 충돌 (80, 443) | 다른 서비스가 포트 사용 중 | 기존 서비스 중지 또는 Dify 포트 변경 안내 |
| 컨테이너 시작 실패 | 메모리 부족, 설정 오류 | `docker compose logs` 확인 안내 |
| 헬스체크 실패 | 컨테이너 부팅 지연 | 60초 대기 후 재시도 안내 |
| Dify 로그인 실패 | 이메일/비밀번호 불일치 | gateway/.env 확인 또는 비밀번호 초기화 명령 안내 |
| Groq 플러그인 설치 실패 | 네트워크 또는 Dify 버전 이슈 | Settings > Model Providers에서 수동 설치 안내 |
| Groq API Key 검증 실패 | 잘못된 API Key | https://console.groq.com/keys 에서 키 재발급 안내 |

## 스킬 부스팅

이 스킬은 다음 OMC 스킬을 활용하여 검증된 워크플로우를 적용함:

| 단계 | OMC 스킬 | 목적 |
|------|----------|------|
| Step 1~7 | `ulw` 매직 키워드 | 각 단계의 완료 보장 |

## MUST 규칙

| # | 규칙 |
|---|------|
| 1 | Docker 및 Docker Compose 설치 여부를 먼저 확인한다 |
| 2 | Docker Compose 실행 후 헬스체크를 수행한다 |
| 3 | 컨테이너 시작 실패 시 에러 로그를 확인하고 원인을 안내한다 |
| 4 | 초기 설정 안내(관리자 계정 생성 URL)를 반드시 제공한다 |

## MUST NOT 규칙

| # | 금지 사항 |
|---|----------|
| 1 | Docker 미설치 상태에서 Docker Compose를 실행하지 않는다 |
| 2 | 기존 .env 파일을 덮어쓰지 않는다 (이미 존재하면 건너뜀) |
| 3 | 헬스체크 실패를 무시하고 다음 단계로 진행하지 않는다 |

## 검증 체크리스트

- [ ] Docker 및 Docker Compose가 설치되어 있는가
- [ ] Dify 소스가 지정 위치에 존재하는가
- [ ] .env 파일이 생성 또는 보존되었는가
- [ ] Docker Compose 컨테이너가 정상 실행 중인가
- [ ] 헬스체크(HTTP)가 통과했는가
- [ ] 초기 설정 URL이 안내되었는가
- [ ] Groq API Key가 입력되었는가 (건너뛰기 허용)
- [ ] Groq 플러그인이 설치되었는가
- [ ] Groq credentials가 검증 및 저장되었는가
