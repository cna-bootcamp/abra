<script setup>
// 앱 진입 컴포넌트 — 화면별 컴포넌트는 src/components/ 아래에 배치하고
// 본 파일에서 라우팅·상태에 따라 분기 렌더링한다.
//
// 예시 (소상공인 이벤트 도우미 케이스):
//   import StoreSetup from './components/StoreSetup.vue'
//   import ChatView from './components/ChatView.vue'
//   const screen = ref('setup')
//   ...
//   <StoreSetup v-if="screen === 'setup'" @complete="..." />
//   <ChatView v-else :store-info="..." @reset="..." />
</script>

<template>
  <main class="app-root">
    <h1>AI Agent</h1>
    <p>frontend-developer 에이전트가 dev-plan §3 화면 매핑에 따라 본 컴포넌트를 교체할 것.</p>
  </main>
</template>

<style>
.app-root {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  max-width: 720px;
  margin: 0 auto;
  padding: 24px;
  font-size: 16px;     /* 50대+ 사용자 가정: 16px 이상 */
  line-height: 1.6;
  color: #222;
}
h1 {
  font-size: 24px;
  margin-bottom: 12px;
}
</style>
