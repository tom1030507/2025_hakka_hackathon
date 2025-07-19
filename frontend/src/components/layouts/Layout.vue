<script setup>
</script>

<template>
  <header>
    <div class="cover">
      <router-link to="/">首頁</router-link>
    </div>
    <nav>
      <router-link to="/blank1">按鈕1</router-link>
      <router-link to="/dashboard">按鈕2</router-link>
      <router-link to="/blank2">按鈕3</router-link>
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
  padding: 1rem;
  width: 100%;
  max-width: 1400px;  /* 調整header 寬度 */
  margin: 0 auto;
  border-bottom: 1px solid #ccc;
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
}


main {
  padding: 1rem;
  width: 100%;
  max-width: 1400px;  /* 調整body 寬度 */
  height: 530px;   /* 調整body 長度 */
  min-height: auto;
  margin: 0 auto;
  flex: 1;
}
</style>
