// API 클라이언트 — Vite 프록시(/chat → :8000)를 사용하므로
// 절대 http://localhost:8000 하드코딩하지 말 것.
const API_KEY = import.meta.env.VITE_API_KEY || 'dev-api-key'

export async function sendMessage({ message, sessionId }) {
  const res = await fetch('/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${API_KEY}`,
    },
    body: JSON.stringify({
      session_id: sessionId || null,
      message,
    }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || `서버 오류 (${res.status})`)
  }
  return res.json()
}

export async function getHealth() {
  const res = await fetch('/health')
  if (!res.ok) throw new Error(`/health ${res.status}`)
  return res.json()
}
