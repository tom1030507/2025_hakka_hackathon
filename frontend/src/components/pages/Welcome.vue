<template>
  <div class="cover-container">
    <div class="top-images-container">
      <img src="/images/white_pic.png" alt="Background Image" class="top-image background-image">
      <img src="/images/title_pic.png" alt="Title Image" class="top-image foreground-image">
    </div>
    <div class="content">
      <h1 class="main-title"></h1>
      <p class="subtitle"></p>

      <div class="courses-grid">
        <button 
          v-for="feature in courses" 
          :key="feature.id"
          class="cta-button"
          @click="goToFeature(feature)"
        >
          {{ feature.title }}
          <span class="arrow">></span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';

// --- 背景圖片設定 ---
// 使用 public 資料夾中的圖片路徑
const backgroundImage = '/images/Course1.jpg';

const router = useRouter();

// 特色功能資料 - 更新路由以匹配 Layout.vue 中的導航
const courses = ref([
  {
    id: 1,
    number: '01',
    title: '學習',
    description: '學習簡介',
    route: '/blank1'  // 更新為匹配 Layout.vue 中的路由
  },
  {
    id: 2,
    number: '02', 
    title: '學習計畫',
    description: '學習計畫簡介',
    route: '/dashboard'  // 更新為匹配 Layout.vue 中的路由
  }
]);

// 直接導航到特定功能
const goToFeature = (feature) => {
  router.push(feature.route);
};
</script>

<style scoped>
.top-image {
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
  max-width: 500px; /* or any other size */
  z-index: 3;
  opacity: 0.5;
}

.cover-container {
  position: relative;
  height: 100vh;
  width: 100vw;
  margin: 0;
  padding: 0;
  /* 使用傳統傘背景圖片 */
  background-image: url('/images/welcome_background.jpg');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.cover-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.3), rgba(255, 255, 255, 0.1));
  z-index: 1;
}

.content {
  position: relative;
  z-index: 2;
  text-align: center;
  color: #2c3e50;
  width: 100vw;
  max-width: none;
  padding: 40px 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.main-title {
  font-size: 7rem;
  font-weight: 900;
  margin-bottom: 20px;
  text-shadow: 
    4px 4px 12px rgba(0, 0, 0, 0.6),
    2px 2px 6px rgba(0, 0, 0, 0.4),
    0px 0px 20px rgba(0, 0, 0, 0.3);
  animation: fadeInUp 1s ease-out;
  color: rgba(255, 255, 255, 0.9);
  text-align: center;
  letter-spacing: 2px;
  line-height: 1.1;
}

.subtitle {
  font-size: 1.5rem;
  margin-bottom: 40px;
  opacity: 0.8;
  text-shadow: 
    2px 2px 8px rgba(0, 0, 0, 0.5),
    1px 1px 4px rgba(0, 0, 0, 0.3),
    0px 0px 12px rgba(0, 0, 0, 0.2);
  animation: fadeInUp 1s ease-out 0.3s both;
  color: rgba(255, 255, 255, 0.85);
}

.courses-grid {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin: 50px 0;
  animation: fadeInUp 1s ease-out 0.6s both;
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
  align-items: center;
}

/* 按鈕改成白色 */
.cta-button {
  /* 核心：白色半透明背景 + 毛玻璃效果 */
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px); /* 支援 Safari */
  
  /* 邊框：增加輪廓感 */
  border: 1px solid rgba(255, 255, 255, 0.3);
  
  /* 文字：維持白色，但加上深色陰影以提高對比度 */
  color: white;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
  
  /* 其他既有樣式 */
  padding: 25px 50px;
  border-radius: 50px;
  font-size: 1.5rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
  animation: fadeInUp 1s ease-out 0.9s both;
  width: 100%;
  max-width: 400px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 按鈕改成白色 */
.cta-button:hover {
  /* 滑鼠懸停時，提高亮度和邊框清晰度 */
  background: rgba(255, 255, 255, 0.35);
  border: 1px solid rgba(255, 255, 255, 0.5);
  
  /* 讓陰影更明顯 */
  box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.4);
  transform: translateY(-3px);
}


.arrow {
  font-size: 1.6rem;
  transition: transform 0.3s ease;
  margin-left: 20px;
}

.cta-button:hover .arrow {
  transform: translateX(5px);
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>