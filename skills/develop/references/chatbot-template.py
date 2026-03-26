"""{{APP_NAME}} Streamlit 챗봇 UI.

FastAPI SSE 스트리밍 엔드포인트({{STREAM_ENDPOINT}})와 연동하여
AI Agent를 테스트하는 챗봇 인터페이스.

자동 생성 파일 — ABRA develop Phase 5
"""

from __future__ import annotations

import json
import time

import httpx
import streamlit as st

# ---------------------------------------------------------------------------
# 상수 정의
# ---------------------------------------------------------------------------

API_KEY = "{{API_KEY}}"
DEFAULT_SERVER_URL = "{{API_BASE_URL}}"
STREAM_ENDPOINT = "{{STREAM_ENDPOINT}}"
INITIAL_MESSAGE = "안녕하세요, {{APP_NAME}} 에이전트입니다. 궁금한 점을 질문해 주세요."
INQUIRY_OPTIONS = {{INQUIRY_OPTIONS}}

# ---------------------------------------------------------------------------
# 페이지 설정
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="{{APP_NAME}} 챗봇",
    page_icon="💬",
    layout="wide",
)

# ---------------------------------------------------------------------------
# 세션 상태 초기화
# ---------------------------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": INITIAL_MESSAGE, "metadata": None}
    ]

if "server_url" not in st.session_state:
    st.session_state.server_url = DEFAULT_SERVER_URL

# ---------------------------------------------------------------------------
# 사이드바
# ---------------------------------------------------------------------------

with st.sidebar:
    st.title("⚙️ 설정")
    st.divider()

    if INQUIRY_OPTIONS:
        st.subheader("문의 채널")
        selected_channel = st.selectbox(
            label="채널 선택",
            options=INQUIRY_OPTIONS,
            label_visibility="collapsed",
        )
    else:
        selected_channel = ""

    st.divider()

    st.subheader("API 서버")
    server_url = st.text_input(
        label="서버 URL",
        value=st.session_state.server_url,
        placeholder=DEFAULT_SERVER_URL,
        label_visibility="collapsed",
    )
    st.session_state.server_url = server_url.rstrip("/")

    if st.button("🔍 서버 상태 확인", use_container_width=True):
        with st.spinner("확인 중..."):
            try:
                resp = httpx.get(
                    f"{st.session_state.server_url}/health",
                    headers={"Authorization": f"Bearer {API_KEY}"},
                    timeout=5.0,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    st.success(f"✅ 서버 정상 (v{data.get('version', '?')})")
                else:
                    st.error(f"❌ 응답 오류: HTTP {resp.status_code}")
            except httpx.ConnectError:
                st.error("❌ 서버에 연결할 수 없습니다")
            except Exception as e:
                st.error(f"❌ 오류: {e}")

    st.divider()

    if st.button("🗑️ 대화 초기화", use_container_width=True, type="secondary"):
        st.session_state.messages = [
            {"role": "assistant", "content": INITIAL_MESSAGE, "metadata": None}
        ]
        st.rerun()

    st.divider()
    st.caption("{{APP_NAME}} v0.1.0")

# ---------------------------------------------------------------------------
# 메인 영역 — 채팅 인터페이스
# ---------------------------------------------------------------------------

st.title("💬 {{APP_NAME}} 챗봇")
st.caption("AI Agent 테스트 인터페이스")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        meta = msg.get("metadata")
        if meta and meta.get("process_type") == "auto":
            cols = st.columns(4)
            cols[0].metric("카테고리", meta.get("category", "-"))
            cols[1].metric("복잡도", meta.get("complexity", "-"))
            cols[2].metric("검색 시도", f"{meta.get('search_attempts', 0)}회")
            cols[3].metric("절감 비용", f"{meta.get('saved_cost', 0):,}원")
            if meta.get("cost_note"):
                st.info(f"💰 {meta['cost_note']}")

        elif meta and meta.get("process_type") == "escalation":
            with st.expander("📋 상담원 배정 정보"):
                cols = st.columns(3)
                cols[0].metric("담당 상담원", meta.get("agent_name") or "배정 대기")
                cols[1].metric("대기 순번", f"{meta.get('queue_position', 0)}번")
                cols[2].metric("예상 대기", f"{meta.get('estimated_wait_minutes', 0)}분")
                if meta.get("priority") == "high":
                    st.warning("⚡ 우선 처리 대상입니다.")

# ---------------------------------------------------------------------------
# SSE 스트리밍 호출 함수
# ---------------------------------------------------------------------------

def call_api_streaming(query: str, channel: str, server_url: str):
    """SSE 스트리밍 API 호출."""
    url = f"{server_url}{STREAM_ENDPOINT}"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
    }
    body = {"query": query}
    if channel:
        body["inquiry_channel"] = channel

    try:
        with httpx.stream("POST", url, headers=headers, json=body, timeout=60.0) as response:
            if response.status_code != 200:
                error_text = response.read().decode("utf-8", errors="replace")
                yield {"type": "error", "content": f"서버 오류 (HTTP {response.status_code}): {error_text}"}
                return

            event_type = None
            data_lines: list[str] = []

            for line in response.iter_lines():
                line = line.strip()
                if line.startswith("event:"):
                    event_type = line[len("event:"):].strip()
                elif line.startswith("data:"):
                    data_lines.append(line[len("data:"):].strip())
                elif line == "":
                    if data_lines:
                        raw_data = " ".join(data_lines)
                        try:
                            payload = json.loads(raw_data)
                        except json.JSONDecodeError:
                            payload = {}

                        if event_type == "message":
                            msg_type = payload.get("type", "token")
                            yield {"type": msg_type, "content": payload.get("content", "")}
                        elif event_type == "metadata":
                            yield {"type": "metadata", "content": payload}
                        elif event_type == "done":
                            yield {"type": "done", "content": {}}

                    event_type = None
                    data_lines = []

    except httpx.ConnectError:
        yield {"type": "error", "content": f"서버에 연결할 수 없습니다. {server_url} 에서 실행 중인지 확인하세요."}
    except httpx.TimeoutException:
        yield {"type": "error", "content": "요청 시간이 초과되었습니다 (60초)."}
    except Exception as e:
        yield {"type": "error", "content": f"오류: {e}"}

# ---------------------------------------------------------------------------
# 사용자 입력 처리
# ---------------------------------------------------------------------------

if prompt := st.chat_input("질문을 입력하세요..."):
    st.session_state.messages.append({"role": "user", "content": prompt, "metadata": None})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        answer_placeholder = st.empty()
        status_placeholder = st.empty()

        full_answer = ""
        metadata = None
        has_error = False

        status_placeholder.status("🔄 처리 중...", state="running")

        for event in call_api_streaming(
            query=prompt,
            channel=selected_channel if INQUIRY_OPTIONS else "",
            server_url=st.session_state.server_url,
        ):
            etype = event["type"]

            if etype == "token":
                full_answer += event["content"]
                answer_placeholder.markdown(full_answer + "▌")
            elif etype == "escalation":
                full_answer = event["content"]
                answer_placeholder.markdown(full_answer)
            elif etype == "metadata":
                metadata = event["content"]
            elif etype == "done":
                break
            elif etype == "error":
                has_error = True
                full_answer = f"⚠️ {event['content']}"
                answer_placeholder.error(full_answer)
                break

        if not has_error:
            answer_placeholder.markdown(full_answer)

        status_placeholder.empty()

        if metadata and not has_error:
            if metadata.get("process_type") == "auto":
                cols = st.columns(4)
                cols[0].metric("카테고리", metadata.get("category", "-"))
                cols[1].metric("복잡도", metadata.get("complexity", "-"))
                cols[2].metric("검색 시도", f"{metadata.get('search_attempts', 0)}회")
                cols[3].metric("절감 비용", f"{metadata.get('saved_cost', 0):,}원")
                if metadata.get("cost_note"):
                    st.info(f"💰 {metadata['cost_note']}")
            elif metadata.get("process_type") == "escalation":
                with st.expander("📋 상담원 배정 정보", expanded=True):
                    cols = st.columns(3)
                    cols[0].metric("담당 상담원", metadata.get("agent_name") or "배정 대기")
                    cols[1].metric("대기 순번", f"{metadata.get('queue_position', 0)}번")
                    cols[2].metric("예상 대기", f"{metadata.get('estimated_wait_minutes', 0)}분")
                    if metadata.get("priority") == "high":
                        st.warning("⚡ 우선 처리 대상입니다.")

    if full_answer:
        st.session_state.messages.append({
            "role": "assistant",
            "content": full_answer,
            "metadata": metadata,
        })
