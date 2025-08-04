<template>
  <div class="page-wrapper">
    <div class="background-overlay"></div>
    <div class="container">
      <h1>使用單字卡學習後進行測驗!</h1>
      <div class="tabs">
        <button @click="showSection('flashcard')" :class="{ active: currentSection === 'flashcard' }">單字卡</button>
        <button @click="showSection('quiz')" :class="{ active: currentSection === 'quiz' }">測驗</button>
        <button @click="showSection('translate')" :class="{ active: currentSection === 'translate' }">翻譯</button>
      </div>

      <!-- Flashcard Section -->
      <div v-if="currentSection === 'flashcard'" id="flashcard-section">
        <div id="card">
          <p id="chinese" class="big">{{ cards[currentCard].chinese }}</p>
          <div class="hakka-content">
            <p id="hakka" class="roman">{{ cards[currentCard].hakka }}</p>
            <!-- Hakka TTS Button -->
            <div class="audio-section">
              <button @click="playHakkaAudio(cards[currentCard].hakka)" :disabled="isPlayingAudio" class="audio-btn hakka-audio">
                <span>{{ isPlayingAudio ? '播放中...' : '🔊 播放客語' }}</span>
              </button>
            </div>
          </div>
        </div>
        <div class="nav">
          <button @click="prevCard">上一張</button>
          <button @click="nextCard">下一張</button>
        </div>
        <p id="progress">第 {{ currentCard + 1 }} / {{ cards.length }} 張</p>
      </div>

      <!-- Quiz Section -->
      <div v-if="currentSection === 'quiz'" id="quiz-section">
        <p id="quiz-question" class="big">{{ currentQuizQuestion.chinese }}</p>
        
        <!-- Audio button for quiz question -->
        <div class="quiz-audio-section">
          <button @click="playHakkaAudio(currentQuizQuestion.hakka)" :disabled="isPlayingAudio" class="audio-btn hakka-audio">
            <span>{{ isPlayingAudio ? '播放中...' : '🔊 播放客語' }}</span>
          </button>
        </div>
        
        <div id="quiz-options">
          <button 
            v-for="(option, index) in quizOptions" 
            :key="index" 
            @click="selectOption(option)"
            :style="option.style">
            {{ option.hakka }}
          </button>
        </div>
        <button @click="nextQuizQuestion">下一題</button>
        <p id="quiz-score">目前得分：{{ quizScore }}</p>
      </div>

      <!-- Translate Section -->
      <div v-if="currentSection === 'translate'" id="translate-section">
        <div id="translate-container">
          <div class="input-section">
            <label for="chinese-input" class="input-label">請輸入中文：</label>
            <textarea 
              id="chinese-input" 
              v-model="chineseInput" 
              placeholder="請輸入要翻譯的中文..."
              rows="3"
              :disabled="isTranslating">
            </textarea>
          </div>
          
          <div class="translate-button-section">
            <button class="translate-btn" @click="translateSingleText" :disabled="isTranslating || !chineseInput.trim()">
              <span>{{ isTranslating ? '翻譯中...' : '翻譯成客語' }}</span>
            </button>
          </div>
          
          <div class="result-section" v-if="translationResult || translationError">
            <label class="result-label">客語翻譯：</label>
            <div id="translation-result">
              <p v-if="translationResult" class="hakka-text success">{{ translationResult }}</p>
              <p v-else-if="translationError" class="hakka-text error">{{ translationError }}</p>
              
              <!-- Audio button for translation results -->
              <div v-if="translationResult" class="translation-audio-section">
                <button class="audio-btn hakka-audio" @click="playHakkaAudio(translationResult)" :disabled="isPlayingAudio">
                  <span>{{ isPlayingAudio ? '播放中...' : '🔊 播放客語' }}</span>
                </button>
              </div>
            </div>
          </div>
          
          <div class="history-section" v-if="translationHistory.length > 0">
            <h3>翻譯記錄</h3>
            <div class="history-list">
              <div v-for="(item, index) in translationHistory" :key="index" class="history-item">
                <div class="history-content" @click="loadHistoryItem(item)">
                  <div class="history-chinese">{{ item.chinese }}</div>
                  <div class="history-hakka">{{ item.hakka }}</div>
                  <div class="history-timestamp">{{ item.timestamp }}</div>
                </div>
                <div class="history-audio-controls">
                  <button class="history-audio-btn hakka" @click="playHakkaAudio(item.hakka)" :disabled="isPlayingAudio" title="播放客語">
                    <span>🔊</span>
                  </button>
                </div>
              </div>
            </div>
            <button class="clear-btn" @click="clearHistory">清除記錄</button>
          </div>
        </div>
      </div>

      <!-- Debug Information -->
      <div v-if="debugMode" class="debug-section">
        <h3>Debug Info</h3>
        <p>API Base URL: {{ API_BASE_URL }}</p>
        <p>Last TTS Request: {{ lastTTSRequest }}</p>
        <p>Last TTS Response: {{ lastTTSResponse }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';

// API Configuration
const API_BASE_URL = import.meta.env.VITE_BACKEND_BASE_URL || 'http://127.0.0.1:8000';

// Debug mode (set to true for troubleshooting)
const debugMode = ref(false);
const lastTTSRequest = ref('');
const lastTTSResponse = ref('');

// Tab switching
const currentSection = ref('flashcard');
function showSection(section) {
  currentSection.value = section;
}

// Audio state management
const isPlayingAudio = ref(false);
const currentAudio = ref(null);

// Flashcard data and functions
const cards = ref([
  { chinese: "你好", hakka: "你好" },
  { chinese: "謝謝", hakka: "恁仔細" },
  { chinese: "再見", hakka: "正來尞" },
  { chinese: "早安", hakka: "恁早啊" },
  { chinese: "午安", hakka: "當晝好" },
  { chinese: "晚安", hakka: "暗安" },
  { chinese: "水", hakka: "水" },
  { chinese: "火", hakka: "火" },
  { chinese: "吃", hakka: "食" },
  { chinese: "喝", hakka: "食" },
  { chinese: "學習", hakka: "學習" },
  { chinese: "請", hakka: "請" },
  { chinese: "對不起", hakka: "失禮啦" },
  { chinese: "是", hakka: "係" },
  { chinese: "不是", hakka: "毋係" },
  { chinese: "朋友", hakka: "朋友" },
  { chinese: "家人", hakka: "屋下人" },
  { chinese: "學校", hakka: "學校" },
  { chinese: "工作", hakka: "食頭路" },
  { chinese: "家", hakka: "屋下" },
  { chinese: "今天", hakka: "今晡日" },
  { chinese: "明天", hakka: "天光日" },
  { chinese: "昨天", hakka: "昨晡日" },
  { chinese: "好吃", hakka: "好食" },
  { chinese: "快樂", hakka: "快樂" },
  { chinese: "累", hakka: "𤸁" },
  { chinese: "走", hakka: "來去" },
  { chinese: "跑", hakka: "走" },
  { chinese: "看", hakka: "看" },
  { chinese: "聽", hakka: "聽" },
  { chinese: "你在哪裡？", hakka: "你在哪啊？" },
  { chinese: "我很餓。", hakka: "𠊎當肚飢。" },
  { chinese: "今天天氣很好。", hakka: "今晡日天時當好。" },
  { chinese: "我愛你。", hakka: "𠊎愛你。" },
  { chinese: "可以幫我嗎？", hakka: "做得摎𠊎𢯭手無？" },
  { chinese: "這是什麼？", hakka: "這係麼个啊？" },
  { chinese: "我去市場。", hakka: "𠊎去市場。" },
  { chinese: "時間到了。", hakka: "時間到吔。" },
  { chinese: "我累了。", hakka: "𠊎𤸁吔啦。" },
  { chinese: "晚餐吃什麼？", hakka: "暗晡夜食麼个呢？" },
  { chinese: "現在幾點？", hakka: "這下幾多點？" },
  { chinese: "我需要幫助。", hakka: "𠊎需要𢯭手。" },
  { chinese: "你在做什麼？", hakka: "你在該做麼个？" },
  { chinese: "請慢一點說。", hakka: "請過慢啊講。" },
  { chinese: "這多少錢？", hakka: "這幾多錢？" },
  { chinese: "我很高興見到你。", hakka: "𠊎當歡喜看著你。" },
  { chinese: "我們去哪裡？", hakka: "𫣆來去哪啊？" },
  { chinese: "請等一下。", hakka: "請等一下。" },
  { chinese: "我不知道。", hakka: "𠊎毋知呢。" },
  { chinese: "明天見！", hakka: "天光日見喔！" },
]);
const currentCard = ref(0);

function nextCard() {
  currentCard.value = (currentCard.value + 1) % cards.value.length;
}

function prevCard() {
  currentCard.value = (currentCard.value - 1 + cards.value.length) % cards.value.length;
}

// Improved Hakka audio playback function
async function playHakkaAudio(hakkaText) {
  if (!hakkaText || !hakkaText.trim() || isPlayingAudio.value) {
    console.log('Cannot play audio:', { hakkaText, isPlayingAudio: isPlayingAudio.value });
    return;
  }
  
  try {
    isPlayingAudio.value = true;
    
    // Stop current audio if playing
    if (currentAudio.value) {
      currentAudio.value.pause();
      currentAudio.value = null;
    }
    
    const requestData = {
      text: hakkaText.trim(),
      voice_type: "hakka"
    };
    
    lastTTSRequest.value = JSON.stringify(requestData);
    console.log('🎵 Sending TTS request:', requestData);
    
    const response = await fetch(`${API_BASE_URL}/api/tts`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestData)
    });

    console.log('📡 TTS API Response Status:', response.status);

    if (!response.ok) {
      const errorText = await response.text();
      console.error('❌ TTS API HTTP Error:', response.status, errorText);
      throw new Error(`HTTP ${response.status}: ${errorText}`);
    }

    const data = await response.json();
    lastTTSResponse.value = JSON.stringify(data);
    console.log('📋 TTS API Response Data:', data);

    if (data.success && data.audio_url) {
      const fullAudioUrl = `${API_BASE_URL}${data.audio_url}`;
      console.log('🎧 Loading audio from:', fullAudioUrl);
      
      const audio = new Audio(fullAudioUrl);
      currentAudio.value = audio;
      
      // Add error handling for audio loading
      audio.onerror = (error) => {
        console.error('❌ Audio loading error:', error);
        console.error('Audio error details:', {
          error: audio.error,
          networkState: audio.networkState,
          readyState: audio.readyState,
          src: audio.src
        });
        isPlayingAudio.value = false;
        currentAudio.value = null;
        alert(`音頻加載失敗: ${audio.error ? audio.error.message : 'Unknown error'}`);
      };
      
      audio.onloadstart = () => {
        console.log('🔄 Audio loading started...');
      };
      
      audio.oncanplay = () => {
        console.log('✅ Audio can start playing');
      };
      
      audio.onended = () => {
        console.log('🏁 Audio playback ended');
        isPlayingAudio.value = false;
        currentAudio.value = null;
      };
      
      audio.onpause = () => {
        console.log('⏸️ Audio paused');
        isPlayingAudio.value = false;
      };
      
      // Wait for audio to be ready and then play
      audio.addEventListener('canplaythrough', async () => {
        try {
          console.log('▶️ Starting audio playback...');
          await audio.play();
          console.log('✅ Audio playback started successfully');
        } catch (playError) {
          console.error('❌ Audio play error:', playError);
          isPlayingAudio.value = false;
          currentAudio.value = null;
          alert(`音頻播放失敗: ${playError.message}`);
        }
      });
      
      // Load the audio
      audio.load();
      
    } else {
      console.error('❌ TTS generation failed:', data);
      throw new Error(data.error_message || 'TTS generation failed - no audio URL returned');
    }
    
  } catch (error) {
    console.error('❌ Hakka audio playback error:', error);
    isPlayingAudio.value = false;
    currentAudio.value = null;
    
    // Show user-friendly error message
    let errorMessage = '音頻播放失敗';
    if (error.message.includes('fetch')) {
      errorMessage += ': 無法連接到服務器，請確認API服務是否運行';
    } else if (error.message.includes('HTTP')) {
      errorMessage += ': 服務器錯誤';
    } else {
      errorMessage += `: ${error.message}`;
    }
    
    alert(errorMessage);
  }
}



// Quiz data and functions
const currentQuizIndex = ref(0);
const quizScore = ref(0);
const quizOptions = ref([]);

const currentQuizQuestion = computed(() => {
  return cards.value[currentQuizIndex.value] || { chinese: '', hakka: '' };
});

function initializeQuiz() {
  generateQuizQuestion();
}

function generateQuizQuestion() {
  if (cards.value.length === 0) return;
  
  const correctAnswer = cards.value[currentQuizIndex.value];
  if (!correctAnswer || !correctAnswer.hakka) {
    nextQuizQuestion();
    return;
  }
  
  const validCards = cards.value.filter((card, index) => 
    index !== currentQuizIndex.value && 
    card.hakka
  );
  
  if (validCards.length < 3) {
    alert('需要更多有效翻譯才能進行測驗');
    return;
  }
  
  const shuffledWrong = validCards.sort(() => 0.5 - Math.random()).slice(0, 3);
  
  const options = [
    { hakka: correctAnswer.hakka, isCorrect: true, style: {} },
    ...shuffledWrong.map(card => ({ hakka: card.hakka, isCorrect: false, style: {} }))
  ];
  
  quizOptions.value = options.sort(() => 0.5 - Math.random());
}

function selectOption(option) {
  quizOptions.value.forEach(opt => {
    if (opt.isCorrect) {
      opt.style = { backgroundColor: '#9cff9c' };
    } else if (opt === option && !opt.isCorrect) {
      opt.style = { backgroundColor: '#ff9c9c' };
    }
  });
  
  if (option.isCorrect) {
    quizScore.value++;
  }
}

function nextQuizQuestion() {
  quizOptions.value.forEach(opt => {
    opt.style = {};
  });
  
  currentQuizIndex.value = (currentQuizIndex.value + 1) % cards.value.length;
  generateQuizQuestion();
}

// Translation section
const chineseInput = ref('');
const translationResult = ref('');
const translationError = ref('');
const isTranslating = ref(false);
const translationHistory = ref([]);

async function translateSingleText() {
  if (!chineseInput.value.trim() || isTranslating.value) return;
  
  isTranslating.value = true;
  translationResult.value = '';
  translationError.value = '';
  
  try {
    console.log('🔄 Translating single text:', chineseInput.value);
    
    const response = await fetch(`${API_BASE_URL}/api/translate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text: chineseInput.value.trim(),
        index: `single_${Date.now()}`
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log('📋 Single translation response:', data);

    if (data.success && data.translation_result) {
      const hakkaText = extractTranslationText(data.translation_result);
      
      if (hakkaText) {
        translationResult.value = hakkaText;
        
        translationHistory.value.unshift({
          chinese: chineseInput.value.trim(),
          hakka: hakkaText,
          timestamp: new Date().toLocaleString('zh-TW')
        });
        
        if (translationHistory.value.length > 10) {
          translationHistory.value = translationHistory.value.slice(0, 10);
        }
        
        console.log('✅ Single translation success:', hakkaText);
      } else {
        translationError.value = '翻譯結果格式錯誤';
        console.log('❌ Translation format error:', data.translation_result);
      }
    } else {
      translationError.value = data.error_message || '翻譯失敗';
      console.log('❌ Translation failed:', data.error_message);
    }
  } catch (error) {
    console.error('❌ Single translation error:', error);
    translationError.value = `翻譯失敗: ${error.message}`;
  } finally {
    isTranslating.value = false;
  }
}

function extractTranslationText(translationResult) {
  if (!translationResult) return null;
  
  if (typeof translationResult === 'string') {
    return translationResult.trim();
  }
  
  if (translationResult.output) {
    return translationResult.output.trim();
  }
  
  if (translationResult.translation) {
    return translationResult.translation.trim();
  }
  
  if (translationResult.result) {
    return translationResult.result.trim();
  }
  
  if (typeof translationResult === 'object') {
    const textFields = ['text', 'content', 'hakka', 'translated'];
    for (const field of textFields) {
      if (translationResult[field]) {
        return translationResult[field].trim();
      }
    }
    
    const values = Object.values(translationResult);
    for (const value of values) {
      if (typeof value === 'string' && value.trim()) {
        return value.trim();
      }
    }
  }
  
  return null;
}

function loadHistoryItem(item) {
  chineseInput.value = item.chinese;
  translationResult.value = item.hakka;
  translationError.value = '';
}

function clearHistory() {
  translationHistory.value = [];
}

// Initialize quiz on component mount
onMounted(() => {
  console.log('🚀 Component mounted, initializing...');
  console.log('📡 API Base URL:', API_BASE_URL);
  initializeQuiz();
});
</script>

<style scoped>
/* Background styles */
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

/* Background overlay */
.background-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(3px);
  z-index: -1;
}

/* Container styles with enhanced transparency */
.container {
  max-width: 500px;
  padding: 2em;
  background-color: rgba(255, 255, 255, 0.92);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  margin-top: -10vh;
}

h1 {
  color: #d6336c;
}

.tabs button {
  margin: 0 0.5em;
  padding: 0.5em 1.2em;
  border: none;
  border-radius: 6px;
  background-color: rgba(224, 224, 224, 0.9);
  cursor: pointer;
  transition: background-color 0.2s;
  font-size: 1rem;
}

.tabs button.active {
  background-color: rgba(208, 208, 255, 0.9);
  font-weight: bold;
}

#flashcard-section {
  border: 2px solid rgba(224, 224, 224, 0.8);
  border-radius: 10px;
  padding: 1.5em 1em;
  margin-bottom: 1.5em;
  background-color: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(5px);
}

#quiz-section, #translate-section {
  border: 2px solid rgba(224, 224, 224, 0.8);
  border-radius: 10px;
  padding: 1.5em 1em;
  margin-bottom: 1.5em;
  background-color: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(5px);
}

.big {
  font-size: 1.6rem;
  margin: 0.3em 0 0.6em 0;
}

.roman {
  font-size: 1.3rem;
  color: #555;
  margin: 0.3em 0 1em 0;
}

.hakka-content {
  background-color: rgba(248, 249, 250, 0.9);
  border: 2px solid rgba(224, 224, 224, 0.8);
  border-radius: 8px;
  padding: 1em;
  margin: 0.5em 0;
}

button {
  margin: 0.4em;
  padding: 0.6em 1.2em;
  border: none;
  border-radius: 6px;
  background-color: rgba(224, 224, 224, 0.9);
  cursor: pointer;
  transition: background-color 0.2s;
  font-size: 1rem;
}

button:hover:not(:disabled) {
  background-color: rgba(208, 208, 255, 0.9);
}

button:disabled {
  background-color: rgba(204, 204, 204, 0.7);
  cursor: not-allowed;
}

/* Audio Section Styles */
.audio-section, .quiz-audio-section {
  margin: 1em 0;
  text-align: center;
}

.audio-btn {
  margin: 0.3em;
  padding: 0.6em 1.2em;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.95rem;
  font-weight: 500;
}

.audio-btn.hakka-audio {
  background-color: #28a745;
  color: white;
}

.audio-btn.hakka-audio:hover:not(:disabled) {
  background-color: #218838;
  transform: translateY(-1px);
}

.audio-btn:disabled {
  background-color: rgba(204, 204, 204, 0.7);
  color: #888;
  cursor: not-allowed;
  transform: none;
}

.translation-audio-section {
  display: flex;
  justify-content: center;
  gap: 1em;
  margin-top: 1em;
}

.nav {
  margin-top: 1em;
}

#quiz-options button {
  display: block;
  width: 70%;
  max-width: 320px;
  margin: 0.4em auto;
}

/* Translation Section Styles */
#translate-container {
  max-width: 100%;
}

.input-section {
  margin-bottom: 1.5em;
}

.input-label, .result-label {
  display: block;
  font-weight: bold;
  color: #333;
  margin-bottom: 0.5em;
  font-size: 1.1rem;
}

#chinese-input {
  width: 100%;
  padding: 0.8em;
  border: 2px solid rgba(224, 224, 224, 0.8);
  border-radius: 6px;
  font-size: 1rem;
  resize: vertical;
  min-height: 80px;
  box-sizing: border-box;
  font-family: inherit;
  background-color: rgba(255, 255, 255, 0.9);
}

#chinese-input:focus {
  outline: none;
  border-color: #d6336c;
}

#chinese-input:disabled {
  background-color: rgba(245, 245, 245, 0.9);
  cursor: not-allowed;
}

.translate-button-section {
  text-align: center;
  margin-bottom: 1.5em;
}

.translate-btn {
  background-color: #d6336c;
  color: white;
  font-size: 1.1rem;
  padding: 0.8em 2em;
  border-radius: 8px;
}

.translate-btn:hover:not(:disabled) {
  background-color: #b8295a;
}

.translate-btn:disabled {
  background-color: rgba(204, 204, 204, 0.7);
  color: #888;
  cursor: not-allowed;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

.translate-btn:disabled span {
  animation: pulse 1.5s infinite;
}

.result-section {
  margin-bottom: 1.5em;
}

#translation-result {
  background-color: rgba(248, 249, 250, 0.9);
  border: 2px solid rgba(224, 224, 224, 0.8);
  border-radius: 8px;
  padding: 1.2em;
  text-align: center;
}

.hakka-text {
  font-size: 1.4rem;
  font-weight: bold;
  margin: 0 0 0.8em 0;
}

.hakka-text.error {
  color: #dc3545;
  font-weight: normal;
}

.hakka-text.success {
  color: #2c5aa0;
  font-weight: bold;
}

.history-section {
  margin-top: 2em;
}

.history-section h3 {
  color: #555;
  font-size: 1.2rem;
  margin-bottom: 1em;
  border-bottom: 1px solid rgba(224, 224, 224, 0.8);
  padding-bottom: 0.5em;
}

.history-list {
  max-height: 300px;
  overflow-y: auto;
  margin-bottom: 1em;
}

.history-item {
  background-color: rgba(248, 249, 250, 0.9);
  border: 1px solid rgba(224, 224, 224, 0.8);
  border-radius: 6px;
  padding: 0.8em;
  margin-bottom: 0.5em;
  display: flex;
  align-items: center;
  gap: 1em;
  transition: background-color 0.2s;
}

.history-item:hover {
  background-color: rgba(233, 236, 239, 0.9);
}

.history-content {
  flex: 1;
  cursor: pointer;
}

.history-chinese {
  font-size: 1rem;
  color: #333;
  margin-bottom: 0.3em;
}

.history-hakka {
  font-size: 0.9rem;
  color: #666;
  font-style: italic;
}

.history-timestamp {
  font-size: 0.8rem;
  color: #999;
  margin-top: 0.3em;
}

.history-audio-controls {
  display: flex;
  gap: 0.3em;
}

.history-audio-btn {
  border: none;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 0.8rem;
  font-weight: bold;
  transition: all 0.2s;
  margin: 0;
  padding: 0;
}

.history-audio-btn.hakka {
  background-color: #28a745;
  color: white;
}

.history-audio-btn.hakka:hover:not(:disabled) {
  background-color: #218838;
}

.history-audio-btn:disabled {
  background-color: rgba(204, 204, 204, 0.7);
  cursor: not-allowed;
}

.clear-btn {
  background-color: #dc3545;
  color: white;
  font-size: 0.9rem;
  padding: 0.5em 1.2em;
}

.clear-btn:hover {
  background-color: #c82333;
}

/* Debug Section Styles */
.debug-section {
  margin-top: 2em;
  padding: 1em;
  background-color: rgba(240, 240, 240, 0.9);
  border-radius: 8px;
  border: 1px solid rgba(200, 200, 200, 0.8);
}

.debug-section h3 {
  color: #666;
  font-size: 1.1rem;
  margin-bottom: 0.8em;
}

.debug-section p {
  font-size: 0.9rem;
  color: #555;
  margin: 0.3em 0;
  word-break: break-all;
}

/* Responsive design */
@media (max-width: 600px) {
  .container {
    max-width: 90%;
    padding: 1.5em;
    margin-top: -5vh;
  }
  
  .tabs button {
    margin: 0.2em;
    padding: 0.4em 0.8em;
    font-size: 0.9rem;
  }
  
  .big {
    font-size: 1.4rem;
  }
  
  .roman {
    font-size: 1.1rem;
  }
  
  .translation-audio-section {
    flex-direction: column;
    align-items: center;
    gap: 0.5em;
  }
  
  .history-item {
    flex-direction: column;
    align-items: stretch;
    gap: 0.5em;
  }
  
  .history-audio-controls {
    align-self: center;
    margin-top: 0.5em;
  }
  
  .debug-section {
    font-size: 0.8rem;
  }
}
</style>