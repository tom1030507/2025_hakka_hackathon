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
      >
        {{ block.text }}
      </div>
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

// 方塊資料，現在包含圖片和路由路徑
const blocks = ref([
  { id: 1, text: '基礎客語學習與翻譯', image: image1, route: '/Course/1' },
  { id: 2, text: '每日精選新聞', image: image2, route: '/course/2' },
  { id: 3, text: '自由訂定學習內容', image: image3, route: '/course/3' },
]);

// 目前顯示在第一格的方塊索引
const activeIndex = ref(0);
// 用於防止滾動過快
const isScrolling = ref(false);

// 計算整個 wrapper 的位移
const wrapperStyle = computed(() => {
  const blockHeight = 100 + 20; 
  return {
    transform: `translateY(-${activeIndex.value * blockHeight}px)`,
  };
});

// 計算容器的背景圖片樣式
const containerStyle = computed(() => ({
  backgroundImage: `url(${blocks.value[activeIndex.value].image})`
}));

// 計算當前啟用課程的路由
const activeCourseRoute = computed(() => blocks.value[activeIndex.value].route);

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

/* 右上角標題樣式 */
.page-title {
  position: absolute;
  top: 80px;
  right: 40px;
  z-index: 10;
  color: rgba(255, 255, 255, 0.7);
  font-size: 80px;
  font-weight: bold;
  text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.8);
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
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 18px;
  border-radius: 10px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  transition: transform 0.5s ease-in-out, background-color 0.5s, border-color 0.5s;
  transform-origin: left center;
  backdrop-filter: blur(10px);
}

.block.active {
  transform: scale(1.2);
  background-color: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.6);
}

/* 課程按鈕樣式 */
.course-button {
  position: absolute;
  bottom: 150px;
  right: 100px;
  z-index: 10; /* 確保按鈕在最上層 */
  padding: 15px 30px;
  background-color: #42b983;
  color: white;
  text-decoration: none;
  border-radius: 50px;
  font-size: 18px;
  font-weight: bold;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
}

.course-button:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
  background-color: #3a8a6e;
}
</style>