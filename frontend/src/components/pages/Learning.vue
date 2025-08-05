<template>
  <div class="learning-container" :style="containerStyle">
    <!-- 右上角標題 -->
    <div class="page-title">
      {{ blocks[activeIndex].text }}
    </div>

    <div class="blocks-wrapper" :style="wrapperStyle">
      <div
        v-for="(block, index) in blocks"
        :key="block.id"
        class="block"
        :class="{ 'active': index === activeIndex }"
        @click="handleBlockClick(index)"
      >
        {{ block.text }}
      </div>
    </div>

    <!-- 課程描述區域 -->
    <div class="course-description">
      {{ blocks[activeIndex].description }}
    </div>

    <!-- 動態課程連結按鈕 -->
    <router-link :to="activeCourseRoute" class="course-button">
      進入課程
    </router-link>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';

// --- 圖片路徑設定 ---
import image1 from '../../Photos/Course1.jpg';
import image2 from '../../Photos/Course2.jpg';
import image3 from '../../Photos/Course3.jpg';

// 方塊資料，現在包含圖片、路由路徑和描述
const blocks = ref([
  { 
    id: 1, 
    text: '基礎客語學習與翻譯', 
    image: image1, 
    route: '/course/1',
    description: '學習客語基礎發音和詞彙，以及常用的日常對話，並且提供中文與客語的翻譯功能。適合初學者建立客語基礎。'
  },
  { 
    id: 2, 
    text: '每日精選新聞', 
    image: image2, 
    route: '/course/2',
    description: '透過每日精選的新聞內容學習客語，同時了解時事議題。結合語言學習與知識獲取的雙重效果。'
  },
  { 
    id: 3, 
    text: '自由訂定學習內容', 
    image: image3, 
    route: '/course/3',
    description: '根據個人興趣和需求自由設定學習主題和內容，可自由訂定難度並使用對應主題生成的練習題查看學習成效，享受個人化的學習體驗。'
  },
]);

// 目前顯示在第一格的方塊索引
const activeIndex = ref(0);
// 用於防止滾動過快
const isScrolling = ref(false);

// 移除 wrapper 位移，改為顯示所有 blocks
const wrapperStyle = computed(() => {
  return {
    transform: 'translateY(0px)',
  };
});

// 計算容器的背景圖片樣式
const containerStyle = computed(() => ({
  backgroundImage: `url(${blocks.value[activeIndex.value].image})`
}));

// 計算當前啟用課程的路由
const activeCourseRoute = computed(() => blocks.value[activeIndex.value].route);

// 處理方塊點擊事件
const handleBlockClick = (index) => {
  activeIndex.value = index;
};

// 處理滑鼠滾輪事件
const handleWheel = (event) => {
  if (isScrolling.value) return;
  isScrolling.value = true;
  
  if (event.deltaY > 0) {
    activeIndex.value = (activeIndex.value + 1) % blocks.value.length;
  } else {
    activeIndex.value = (activeIndex.value - 1 + blocks.value.length) % blocks.value.length;
  }

  setTimeout(() => {
    isScrolling.value = false;
  }, 500);
};

// 在組件掛載時添加事件監聽並處理圖片預載入
onMounted(() => {
  window.addEventListener('wheel', handleWheel);
  document.documentElement.style.overflow = 'hidden';

  blocks.value.forEach(block => {
    const img = new Image();
    img.src = block.image;
  });
});

// 在組件卸載時移除事件監聽並恢復頁面滾動條
onUnmounted(() => {
  window.removeEventListener('wheel', handleWheel);
  document.documentElement.style.overflow = '';
});
</script>

<style scoped>
.learning-container {
  position: relative;
  display: flex;
  justify-content: flex-start;
  align-items: flex-start;
  padding: 40px;
  height: 100vh;
  width: 100%;
  box-sizing: border-box;
  overflow: hidden;
  
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  transition: background-image 0.7s ease-in-out;
}

.learning-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.4);
  z-index: 1;
}

/* 右上角標題樣式 - 平衡版 */
.page-title {
  position: absolute;
  top: 80px;
  right: 40px;
  z-index: 10;
  color: rgba(255, 255, 255, 0.9);
  font-size: 80px;
  font-weight: 700;
  text-shadow: 
    2px 2px 4px rgba(0, 0, 0, 0.8),
    0 0 6px rgba(0, 0, 0, 0.5);
  letter-spacing: 1px;
  text-rendering: optimizeLegibility;
  -webkit-font-smoothing: antialiased;
}

.blocks-wrapper {
  position: relative;
  z-index: 2;
  transition: transform 0.5s ease-in-out;
}

.block {
  width: 200px;
  height: 100px;
  margin-bottom: 20px;
  background-color: rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 16px;
  font-weight: 500;
  border-radius: 10px;
  border: 2px solid rgba(255, 255, 255, 0.2);
  transition: all 0.5s ease-in-out;
  transform-origin: left center;
  backdrop-filter: blur(8px);
  text-shadow: 
    1px 1px 3px rgba(0, 0, 0, 0.6),
    0 0 5px rgba(0, 0, 0, 0.3);
  text-align: center;
  line-height: 1.2;
  cursor: pointer;
}

.block:hover {
  background-color: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.4);
  color: rgba(255, 255, 255, 0.85);
  transform: scale(1.05);
}

.block.active {
  transform: scale(1.3);
  background-color: rgba(255, 255, 255, 0.25);
  border-color: rgba(255, 255, 255, 0.8);
  color: rgba(255, 255, 255, 0.95);
  font-size: 18px;
  font-weight: 600;
  text-shadow: 
    1px 1px 3px rgba(0, 0, 0, 0.8),
    0 0 8px rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(12px);
}

.block.active:hover {
  transform: scale(1.3);
}

/* 課程描述樣式 */
.course-description {
  position: absolute;
  bottom: 100px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10;
  max-width: 850px;
  min-height: 180px;
  padding: 30px;
  background-color: rgba(0, 0, 0, 0.3);
  color: rgba(255, 255, 255, 0.65);
  font-size: 25px;
  line-height: 1.7;
  border-radius: 20px;
  backdrop-filter: blur(15px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.7);
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
}

/* 課程按鈕樣式 - 白色半透明 */
.course-button {
  position: absolute;
  bottom: 150px;
  right: 100px;
  z-index: 10;
  padding: 15px 30px;
  
  /* 核心：白色半透明背景 + 毛玻璃效果 */
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px); /* 支援 Safari */
  
  /* 邊框：增加輪廓感 */
  border: 1px solid rgba(255, 255, 255, 0.3);

  /* 文字：維持白色，但加上深色陰影以提高對比度 */
  color: white;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);

  text-decoration: none;
  border-radius: 50px;
  font-size: 18px;
  font-weight: bold;
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
  transition: all 0.3s ease;
}


.course-button:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
  background-color: #3a8a6e;
}
</style>