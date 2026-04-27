# 프론트엔드 개발 프롬프트 템플릿

개발계획서 §3 사용자 인터페이스, 시나리오 화면 흐름, DSL API 인터페이스를 일관되게
연결하는 SPA를 구현하고, **백엔드 통합 패치(CORS / StaticFiles / SPA 라우트 / 멀티스테이지 Dockerfile)**
까지 한 턴에 완료할 것.

스킬은 최소 실행 컨텍스트만 전달하며,
화면 매핑·컴포넌트 분리·빌드 검증은 에이전트가 직접 수행할 것.

## 입력

- Base 디렉토리: `{{Base 디렉토리}}`
- 개발 계획서: `{{Base 디렉토리}}/{{개발 계획서 파일 경로}}`
- 시나리오: `{{Base 디렉토리}}/{{시나리오 파일 경로}}`
- DSL: `{{Base 디렉토리}}/{{DSL 파일 경로}}`
- 백엔드 진입점: `{{Base 디렉토리}}/app/main.py`
- 백엔드 라우트: `{{Base 디렉토리}}/app/api/routes.py`
- 선택된 스택 템플릿: `{{ABRA_PLUGIN_DIR}}/agents/frontend-developer/references/{{tech_stack}}-template/`

## run_context_frontend

```yaml
run_context_frontend:
  backend_source_root: app
  frontend_source_root: frontend
  tech_stack: {{tech_stack}}              # vue3-vite | react-vite
  image_generation:
    enabled: {{image_enabled}}            # true | false
    api_key_env: GEMINI_API_KEY
    tool_path: "{{ABRA_PLUGIN_DIR}}/gateway/tools/generate_image.py"
  api_key_env: VITE_API_KEY
  retry_budget:
    diagnostics: 3
    build: 3
    test: 2
    total: 8
```

옵션 해석 규칙:

- `tech_stack=vue3-vite`: Vue 3 + Vite 템플릿 사용 (검증 완료 권장 스택)
- `tech_stack=react-vite`: React + Vite 템플릿 사용
- `image_generation.enabled=true`: `generate_image.py`로 이미지 자동 생성, 결과를 `frontend/src/assets/`에 배치
- `image_generation.enabled=false`: 텍스트/아이콘만 사용

## 에이전트 책임

1. 개발계획서 + 시나리오 + DSL 해석
   - §3 사용자 인터페이스 항목별 화면 분리
   - 시나리오의 사용자 여정에서 화면 전환 흐름 추출
   - DSL의 API 엔드포인트와 입출력 스키마 활용
2. 백엔드 인터페이스 교차 검증
   - `app/api/routes.py`의 실제 라우트 추출
   - 백엔드 `.env`의 `API_KEY` 키 → 프론트 `VITE_API_KEY` 매핑
   - 라우트 미존재·모호 시 핸드오프 (target: agent-developer)
3. 화면별 컴포넌트 매핑
   - 화면 1개 = 컴포넌트 파일 1개 원칙
   - 공용 UI는 `src/components/common/` 분리
   - API 클라이언트는 `src/api/<domain>.{js|ts}` 단일 진입점
4. 코드 구현
   - 선택된 스택 템플릿 디렉토리 `frontend/`로 복사
   - 화면별 컴포넌트, API 클라이언트, Vite 설정, `frontend/.env` 작성
   - 50대+ 접근성 등 특화 요구 반영 (개발계획서 §3 명시 시)
5. 백엔드 통합 패치 (Hard Gate)
   - `app/main.py`에 `CORSMiddleware` + `/assets` mount + `GET /` SPA 라우트 추가
   - `deploy/Dockerfile`을 멀티스테이지(node build → python runtime)로 변경
   - `.gitignore`에 `static/`, `frontend/node_modules/`, `frontend/dist/` 추가
6. 이미지 자동 생성 (선택)
   - `image_generation.enabled=true`인 경우만 `generate_image.py` 호출
   - GEMINI_API_KEY는 `~/plugins/abra/gateway/tools/.env`에서 로드 후 `--api-key=` 파라미터 전달
7. 빌드 검증 (재시도 한도 내)
   - `npm install` → `npm run build` → `cp dist→static/`
   - `uv run uvicorn`으로 띄운 백엔드의 `GET /` + `/health` 200 응답 확인
   - **시스템 `uvicorn` 사용 금지** (silent 404 위험)
8. 증거 파일 저장 (`{output_dir}/evidence/frontend/`)
9. 정직한 결과 보고

> **주의**: 사용자에게 질문·확인하지 않음 (forbidden_actions: user_interact).
> 사용자 상호작용은 `develop` 스킬 Phase 3.5 Step 1~3에서 이미 완료됨.

## 화면 매핑 기준

### 매핑 표 형식

| 화면 | 책임 컴포넌트 파일 | 호출 API | 주요 상태 | 접근성 요구 |
|------|------------------|---------|---------|-----------|
| ... | ... | ... | ... | ... |

### 매핑 원칙

- 화면 1개 = 컴포넌트 파일 1개 (단, 1000줄 초과 시 분할)
- 공용 컴포넌트(말풍선, 버튼, 모달)는 `src/components/common/`
- 화면 단위 컴포넌트는 `src/components/{domain}/{Screen}.{vue|tsx}`
- 라우팅 필요 시(2개 이상 화면) vue-router/react-router-dom 추가
- 단일 화면 SPA면 라우터 미사용

## API 클라이언트 작성 기준

### 패턴 (Vue/React 공통)

```js
// src/api/chat.js
const API_KEY = import.meta.env.VITE_API_KEY || 'dev-api-key'

export async function sendChat(payload) {
  const r = await fetch('/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${API_KEY}`,
    },
    body: JSON.stringify(payload),
  })
  if (!r.ok) throw new Error(`chat ${r.status}`)
  return r.json()
}
```

### 원칙

- 절대 `http://localhost:8000` 하드코딩 금지 → Vite 프록시 사용
- 인증 헤더는 `Authorization: Bearer ${VITE_API_KEY}` 표준
- 세션 ID는 `localStorage.setItem('session_id', ...)` 보존
- 에러 응답 처리: `r.ok` 체크 후 의미 있는 에러 throw

## 백엔드 통합 패치 표준

### `app/main.py` 패치 (필수 3종)

#### 1) CORSMiddleware 추가

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 2) `/assets` 정적 파일 마운트 + `GET /` SPA 라우트

> **금지**: `app.mount("/", StaticFiles(html=True))` — 일부 FastAPI 버전에서 silent 404 발생
> **금지**: `os.path.dirname(__file__)` — 상대경로 문제로 정적 파일 검출 실패

```python
from pathlib import Path
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

try:
    static_dir = (Path(__file__).resolve().parent.parent / "static").resolve()
    if static_dir.is_dir():
        assets_dir = static_dir / "assets"
        if assets_dir.is_dir():
            app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")
        index_html = str(static_dir / "index.html")

        @app.get("/")
        async def _spa_root() -> FileResponse:
            return FileResponse(index_html)
except Exception as exc:
    logger.warning("static_mount_skipped", error=str(exc))
```

### `deploy/Dockerfile` 멀티스테이지화

```dockerfile
FROM node:20-slim AS frontend-builder
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci --ignore-scripts
COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim
WORKDIR /app
RUN apt-get update -y && apt-get install -y --no-install-recommends curl \
  && rm -rf /var/lib/apt/lists/* \
  && pip install --no-cache-dir uv

COPY pyproject.toml /app/
RUN uv pip install --system -e .
COPY app /app/app
COPY README.md /app/README.md
COPY --from=frontend-builder /frontend/dist /app/static

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### `.gitignore` 보강

```gitignore
static/
frontend/node_modules/
frontend/dist/
```

## 빌드 검증 표준

### 시퀀스

```bash
# 1) 의존성 설치 (한도: 1회)
cd frontend && npm install

# 2) 프로덕션 빌드 (한도: build_remaining)
cd frontend && npm run build

# 3) 정적 산출물 복사
cp -r frontend/dist/* static/

# 4) 백엔드 기동 (검증 후 종료)
uv run uvicorn app.main:app --port 8000 &
sleep 5
```

> **MUST**: `uv run uvicorn` 사용. 시스템 `uvicorn` 사용 금지 (Lessons Learned).

### HTTP 검증

`curl` 사용 금지 (Git Bash가 `/`를 Windows 경로로 변환). `urllib.request` 사용:

```python
import urllib.request
r = urllib.request.urlopen('http://localhost:8000/')
assert r.status == 200
assert b'<!DOCTYPE html>' in r.read(80)
r2 = urllib.request.urlopen('http://localhost:8000/health')
assert r2.status == 200
```

### 정리

```bash
pkill -f "uvicorn app.main" 2>/dev/null
# 포트 점유 잔존 시 (Windows):
#   Stop-Process -Id $(Get-NetTCPConnection -LocalPort 8000 -State Listen).OwningProcess -Force
```

## 재시도 한도 운영 규칙

### 카운터 초기화

```yaml
diagnostics_remaining: 3
build_remaining: 3
test_remaining: 2
total_remaining: 8
```

각 시도마다 해당 카운터와 `total_remaining`를 함께 차감.
한도 도달 시 즉시 중단하고 보고로 전환.

### 한도 도달 시 보고 형식

**빌드 한도**:

```yaml
build_exhausted:
  last_command: <cmd>
  last_exit_code: <n>
  root_cause_hypotheses:
    - <가설 1>
    - <가설 2>
    - <가설 3>
  log: {output_dir}/evidence/frontend/build.log
```

**검증 한도**:

```yaml
verify_exhausted:
  failed_checks:
    - check: "GET / returns 200"
      actual_status: <n>
      reason: <설명>
  output: {output_dir}/evidence/frontend/verify-output.txt
```

## 환경변수 표준

### `frontend/.env`

```
VITE_API_KEY={백엔드 .env의 API_KEY 값과 동일}
```

### `frontend/.env.example`

```
VITE_API_KEY=
```

### 동기화 규칙

- 백엔드 `.env`의 `API_KEY=...` 라인을 읽어 동일 값을 `VITE_API_KEY`에 복사
- 백엔드 `.env.example`이 있으면 `frontend/.env.example`도 동일 패턴으로 빈 키만 포함

## 이미지 생성 (선택)

`image_generation.enabled=true`인 경우만:

```bash
# GEMINI_API_KEY는 ~/plugins/abra/gateway/tools/.env에서 로드 (develop 스킬 Phase 3.5 Step 3에서 저장됨)
GEMINI_API_KEY=$(grep GEMINI_API_KEY {ABRA_PLUGIN_DIR}/gateway/tools/.env | cut -d= -f2)

python {ABRA_PLUGIN_DIR}/gateway/tools/generate_image.py \
  --api-key=${GEMINI_API_KEY} \
  --prompt="{프롬프트}" \
  --output={프로젝트}/frontend/src/assets/{name}.png
```

생성된 이미지를 컴포넌트에서 import:

```js
import storeIcon from '@/assets/store-icon.png'
```

## 증거 파일 저장 기준

`{output_dir}/evidence/frontend/` 디렉토리에 다음 파일 기록:

- `build.log` — `npm install`, `npm run build`, `cp dist→static` 명령·stdout·stderr·exit code
- `npm-audit.json` — `npm audit --json` 결과 (보안 취약점 스캔)
- `verify-output.txt` — `urllib.request.urlopen` 검증 결과 (status, content-type, html 첫 80바이트)
- `commands.md` — 전체 실행 명령 목록 + 타임스탬프 + exit code

## Handoff 프로토콜

백엔드 결함·계획서 결함 발견 시 에스컬레이션.

- 대상: `agent-developer` (백엔드 코드 결함) 또는 `plan-writer` (계획서 §3 결함)
- 정보: 구체적 결함, 영향 범위, 권장 수정사항, blocker 여부
- `blocker: true`인 경우 구현 중단 후 보고만 반환

## Lessons Learned 연동

프로젝트 `AGENTS.md`의 `Lessons Learned` 섹션을 작업 전 로드.
또한 다음 5종 교훈을 항상 사전 반영 (run_context_frontend.lessons_learned로 주입됨):

1. [HIGH] 시스템 `uvicorn`(0.34) vs `uv run uvicorn`(0.46) 버전 차이로 정적 파일 silent 404 → 반드시 `uv run uvicorn`
2. [HIGH] `app.mount('/', StaticFiles(html=True))` 동작 불안정 → `/assets` 마운트 + `GET /` 명시 라우트
3. [MED] `os.path.dirname(__file__)` 상대경로 문제 → `Path(__file__).resolve().parent.parent` 사용
4. [MED] Windows 포트 점유 정리 → `pkill` 무력. PowerShell `Stop-Process -Id <pid> -Force` 사용
5. [MED] Git Bash `curl` `/` 경로 변환 문제 → `urllib.request.urlopen` 사용

## 결과 보고 형식

- 실행한 단계
- 백엔드 인터페이스 교차 검증 결과 (라우트·API_KEY 매핑)
- 화면별 컴포넌트 매핑 표
- 선택된 기술스택 (vue3-vite | react-vite)
- 생성된 주요 파일 목록 (`frontend/` + 백엔드 패치 diff 요약)
- 백엔드 통합 패치 3종 적용 결과
- 빌드 결과 (재시도 사용 횟수 포함) + `static/` 복사 검증
- 통합 검증 결과 (`/`, `/health` 200 + HTML 콘텐츠 확인)
- 증거 파일 경로 (`{output_dir}/evidence/frontend/*`)
- 이미지 생성 사용 여부 (사용 시 생성된 파일 목록)
- 남은 리스크
- 후속 작업 제안
