<template>
  <div class="course-container">
    <div class="header-controls">
      <h1>客家新聞語音閱讀</h1>
      <button @click="fetchNewsAndAudio" :disabled="loading" class="fetch-button">
        <span v-if="loading">載入中，請稍候...</span>
        <span v-else>讀取最新新聞</span>
      </button>
    </div>
    
    <div v-if="error" class="error-message">
      <p>讀取時發生錯誤：</p>
      <pre>{{ error }}</pre>
    </div>

    <div v-if="loading" class="progress-bar-container">
      <div class="progress-bar" :style="{ width: progress + '%' }"></div>
      <div class="progress-text">{{ Math.floor(progress) }}%</div>
    </div>

    <div v-if="newsContent.length > 0" class="content-container">
      <div class="news-content">
        <h2>{{ newsContent[0] }}</h2>
        <p v-for="(paragraph, index) in newsContent.slice(1)" :key="index" class="news-paragraph">
          {{ paragraph }}
        </p>
      </div>
    </div>

    <div v-if="audioUrl" class="audio-player-fixed-bottom">
      <div class="audio-player-container">
        <audio controls :src="fullAudioUrl" class="audio-player">
          您的瀏覽器不支援音訊播放。
        </audio>
        <a :href="fullAudioUrl" download class="download-link">下載音檔</a>
      </div>
    </div>
    <div v-else-if="loading === false && newsContent.length > 0" class="audio-player-fixed-bottom">
      <div class="audio-player-container">
        <p>無法生成音檔，或音檔生成中發生錯誤。</p>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import axios from 'axios';

const loading = ref(false);
const newsContent = ref([]);
const audioUrl = ref(null);
const error = ref(null);
const progress = ref(0); // 新增進度條狀態
let progressInterval = null; // 用於清除定時器

// Backend server address
const backendBaseUrl = 'http://127.0.0.1:8000';

const fullAudioUrl = computed(() => {
  return audioUrl.value ? `${backendBaseUrl}${audioUrl.value}` : null;
});

const startFakeProgress = () => {
  progress.value = 0;
  progressInterval = setInterval(() => {
    if (progress.value < 90) { // 模擬進度到90%後變慢
      progress.value += Math.random() * 1; // 每次增加隨機值，速度減慢
    } else if (progress.value < 99) {
      progress.value += Math.random() * 0.2; // 接近完成時變慢，速度減慢
    }
    if (progress.value > 99) progress.value = 99; // 防止超過99%
  }, 100); // 每100毫秒更新一次
};

const stopFakeProgress = () => {
  clearInterval(progressInterval);
  progress.value = 100; // 完成時設定為100%
  // 可以延遲一下再隱藏進度條，讓使用者看到100%
  setTimeout(() => {
    progress.value = 0; // 重置進度條
  }, 500); // 0.5秒後重置
};

const fetchNewsAndAudio = async () => {
  loading.value = true;
  error.value = null;
  newsContent.value = [];
  audioUrl.value = null;
  startFakeProgress(); // 開始模擬進度

  try {
    const response_news = await axios.get(`${backendBaseUrl}/api/news`);
    if (response_news.data) {
      newsContent.value = response_news.data.news || [];
      const response_audio = await axios.get(`${backendBaseUrl}/api/audio`);
      if (response_audio.data) {
        audioUrl.value = response_audio.data.audio_url || null;
      }
      // audioUrl.value = response.data.audio_url || null;
      if (newsContent.value.length === 0) {
          error.value = '未找到新聞內容。';
      }
    } else {
      error.value = '回傳資料格式不正確。';
    }
  } catch (err) {
    error.value = err.response ? (err.response.data.detail || err.message) : err.message;
    console.error("Error fetching news and audio:", err);
  } finally {
    stopFakeProgress(); // 停止模擬進度
    loading.value = false;
  }
};
</script>

<style scoped>
.course-container {
  max-width: 1000px;
  margin: 2rem auto;
  padding: 2rem;
  background-color: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  font-family: 'Helvetica Neue', Arial, sans-serif;
  padding-bottom: 150px; /* 增加底部填充，為固定播放器留出空間 */
}

.header-controls {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 2rem;
}

h1 {
  color: #333;
  margin: 0;
}

.fetch-button {
  padding: 12px 25px;
  font-size: 1rem;
  color: #fff;
  background-color: #007bff;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s ease, transform 0.2s ease;
}

.fetch-button:hover:not(:disabled) {
  background-color: #0056b3;
  transform: translateY(-2px);
}

.fetch-button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.content-container {
  margin-top: 2rem;
}

.news-content {
  padding: 1.5rem;
  background-color: #fff;
  border: 1px solid #ddd;
  border-radius: 8px;
  margin-bottom: 2rem;
}

.news-content h2 {
  color: #2c3e50;
  margin-bottom: 1rem;
  font-size: 1.8rem;
  text-align: center;
}

.news-paragraph {
  font-size: 1.1rem;
  color: #34495e;
  margin-bottom: 1rem;
  text-align: justify;
  line-height: 1.8;
}

.audio-player-fixed-bottom {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  background-color: transparent; /* 完全透明背景 */
  box-shadow: none; /* 移除陰影 */
  z-index: 1000;
  padding: 10px 0;
}

.audio-player-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 1rem;
  background-color: transparent; /* 完全透明背景 */
  border: none; /* 移除邊框 */
  border-radius: 8px;
  text-align: center;
}

.audio-player-container h3 {
    margin-bottom: 1rem;
    color: #333;
}

.audio-player {
  width: 100%;
  margin-bottom: 1rem;
}

.download-link {
    font-size: 0.9rem;
    color: #007bff;
    text-decoration: none;
}

.download-link:hover {
    text-decoration: underline;
}

.error-message {
  margin-top: 1rem;
  padding: 1rem;
  background-color: #ffebee;
  color: #c62828;
  border: 1px solid #c62828;
  border-radius: 5px;
}

.error-message pre {
  white-space: pre-wrap;
  word-wrap: break-word;
}

/* 進度條樣式 */
.progress-bar-container {
  width: 100%;
  background-color: #e0e0e0;
  border-radius: 5px;
  margin-top: 1rem;
  overflow: hidden; /* 確保進度條在容器內 */
  position: relative;
  height: 25px; /* 進度條高度 */
}

.progress-bar {
  height: 100%;
  background-color: #4CAF50; /* 進度條顏色 */
  width: 0%;
  border-radius: 5px;
  text-align: center;
  line-height: 25px; /* 垂直居中文字 */
  color: white;
  transition: width 0.1s ease-out; /* 平滑過渡 */
}

.progress-text {
  position: absolute;
  width: 100%;
  text-align: center;
  line-height: 25px;
  color: #333;
  top: 0;
  left: 0;
}
</style>