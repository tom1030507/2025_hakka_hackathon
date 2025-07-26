<script setup>
</script>

<template>
  <header>
    <div class="cover">
      <router-link to="/">首頁</router-link>
    </div>
    <nav>
      <router-link to="/blank1">學習</router-link>
      <router-link to="/dashboard">學習計畫</router-link>
    </nav>
  </header>
  <main>
    <slot />
  </main>

<!-- 註解掉footer -->

</template>

<style scoped>
header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  width: 100%;
  margin: 0;
  border-bottom: 1px solid rgba(204, 204, 204, 0.3);
  background-color: rgba(255, 255, 255, 0.05); /* 半透明背景 */
  box-sizing: border-box;
}

.cover a {
  font-weight: bold;
  text-decoration: none;
  color: #000;
}

nav {
  display: flex;
  gap: 1rem;
}

nav a {
  text-decoration: none;
  color: #000;
  background-color: rgba(0, 0, 0, 0.03); /* 更透明的背景 */
  border: 1px solid rgba(0, 0, 0, 0.08); /* 更透明的邊框 */
  padding: 0.5rem 1rem; /* 內邊距 */
  border-radius: 5px; /* 圓角 */
  transition: all 0.3s ease; /* 平滑過渡效果 */
}

nav a:hover {
  background-color: rgba(0, 0, 0, 0.08); /* 懸停時的背景色 */
  border-color: rgba(0, 0, 0, 0.15); /* 懸停時的邊框色 */
  transform: translateY(-2px); /* 懸停時輕微上移 */
}

nav a.router-link-active {
  background-color: rgba(0, 0, 0, 0.12); /* 活躍狀態的背景色 */
  border-color: rgba(0, 0, 0, 0.2); /* 活躍狀態的邊框色 */
}

main {
  padding: 0;
  width: 100%;
  min-height: auto;
  margin: 0;
  flex: 1;
}
</style>