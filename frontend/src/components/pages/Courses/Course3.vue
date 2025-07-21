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

    <div v-if="newsContent.length > 0" class="content-container">
      <div class="news-content">
        <h2>{{ newsContent[0] }}</h2>
        <p v-for="(paragraph, index) in newsContent.slice(1)" :key="index" class="news-paragraph">
          {{ paragraph }}
        </p>
      </div>

      <div v-if="audioUrl" class="audio-player-container">
        <h3>新聞語音</h3>
        <audio controls :src="fullAudioUrl" class="audio-player">
          您的瀏覽器不支援音訊播放。
        </audio>
        <a :href="fullAudioUrl" download class="download-link">下載音檔</a>
      </div>
       <div v-else-if="loading === false && newsContent.length > 0" class="audio-player-container">
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

// Backend server address
const backendBaseUrl = 'http://127.0.0.1:8000';

const fullAudioUrl = computed(() => {
  return audioUrl.value ? `${backendBaseUrl}${audioUrl.value}` : null;
});

const fetchNewsAndAudio = async () => {
  loading.value = true;
  error.value = null;
  newsContent.value = [];
  audioUrl.value = null;

  try {
    const response = await axios.get(`${backendBaseUrl}/api/news_with_audio`);
    if (response.data) {
      newsContent.value = response.data.news || [];
      audioUrl.value = response.data.audio_url || null;
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
}

.header-controls {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 2rem; /* 增加一些底部間距 */
}

h1 {
  color: #333;
  /* text-align: center; */ /* 移除此行，讓flexbox控制對齊 */
  margin: 0; /* 移除預設邊距 */
}

/* 移除原先的p標籤樣式，因為該p標籤已被移除 */
/* p {
  color: #666;
  line-height: 1.6;
  text-align: center;
  margin-bottom: 1.5rem;
} */

.fetch-button {
  /* display: block; */ /* 移除此行，讓flexbox控制對齊 */
  /* margin: 0 auto 2rem auto; */ /* 移除此行，讓flexbox控制對齊 */
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

.audio-player-container {
  padding: 1.5rem;
  background-color: #fff;
  border: 1px solid #ddd;
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
</style>
