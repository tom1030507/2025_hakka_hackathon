<template>
  <div class="page-wrapper">
    <div class="course-container">
      
      <div class="header-controls">
        <h1>客家新聞語音導讀 &nbsp; &nbsp; &nbsp; &nbsp;</h1>
        <button @click="fetchNewsAndAudio" :disabled="loading" class="fetch-button">
          <span v-if="loading">載入中，請稍候...</span>
          <span v-else>讀取最新新聞</span>

        </button>
      </div>
      
      <div v-if="error" class="error-message">
        <p>讀取時發生錯誤：</p>
        <pre>{{ error }}</pre>
      </div>

      <div v-if="loading" class="loading-container">
        <div class="spinner"></div>
        <p>客語語音生成中，請稍候...</p>
      </div>

      <div v-if="newsContent.length > 0" class="content-container">
        <div class="news-content">
          <h2 :class="['h2', { active_h2: currentIndex === 0 }]">{{ newsContent[0] }}</h2>
          <p v-for="(paragraph, index) in newsContent.slice(1)" :key="index" :class="['news-paragraph', { active: currentIndex-1 === index }]">
            {{ paragraph }}
          </p>
        </div>
      </div>

      <div v-if="audioUrl" class="audio-player-fixed-bottom">
        <div class="audio-player-container">
          <audio controls :src="fullAudioUrl" class="audio-player"
            ref="audioRef"
            @timeupdate="onTimeUpdate">
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
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import axios from 'axios';

const subtitles = ref([]) // 來自後端字幕區間
const currentIndex = ref(-2)
const audioRef = ref(null)

const loading = ref(false);
const newsContent = ref([]);
const audioUrl = ref(null);
const error = ref(null);

// Backend server address
const backendBaseUrl = import.meta.env.VITE_BACKEND_BASE_URL || 'http://127.0.0.1:8000';

const fullAudioUrl = computed(() => {
  return audioUrl.value ? `${backendBaseUrl}${audioUrl.value}` : null;
});

const fetchNewsAndAudio = async () => {
  loading.value = true;
  error.value = null;
  newsContent.value = [];
  audioUrl.value = null;
  currentIndex.value = -2;

  try {
    const response_news = await axios.get(`${backendBaseUrl}/api/news`);
    if (response_news.data) {
      newsContent.value = response_news.data.news || [];
      const response_audio = await axios.get(`${backendBaseUrl}/api/audio`);
      if (response_audio.data) {
        audioUrl.value = response_audio.data.audio_url || null;
        subtitles.value = response_audio.data.subtitles.map(s => ({
          start: s.start / 1000,
          end: s.end / 1000,
          text: s.text
        }))
      }
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
    loading.value = false;
  }
};

function onTimeUpdate() {
  const t = audioRef.value.currentTime
  console.log('目前播放時間:', t.toFixed(2))
  const index = subtitles.value.findIndex(
    (s) => t >= s.start && t <= s.end
  )
  currentIndex.value = index
  console.log('目前字幕 index:', index)
}

</script>

<style scoped>
.page-wrapper {
  position: relative;
  min-height: 100vh;
  background-image: url('./Course_background/Course1_page.jpg');
  background-size: cover;
  background-position: center;
  background-attachment: fixed;
  display: flex;
  justify-content: center;
  align-items: center;
}



.course-container {
  max-width: 1000px;
  margin: 2rem auto;
  padding: 4rem;
  background-color: #f9f9f9; /* Fallback color */
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
  /* color: #2c3e50; */
  margin-bottom: 1rem;
  font-size: 1.8rem;
  text-align: center;
}

.h2 {
  color: #2c3e50;
  margin-bottom: 1rem;
  font-size: 1.8rem;
  text-align: center;
}

.active_h2 {
  background-color: #ffeaea;
  color: rgb(137, 27, 7);
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

.active {
  /* font-size: 1.1rem; */
  background-color: #ffeaea;
  color: rgb(137, 27, 7);
  /* margin-bottom: 1rem; */
  font-weight: bold;
  /* text-align: justify;
  line-height: 1.8; */
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

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  color: #555;
}

.spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border-left-color: #007bff;
  margin-bottom: 1rem;
  animation: spin 1s ease infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>