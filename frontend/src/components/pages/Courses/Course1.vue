<!-- <template>
  <div>
    <h1>待....c1</h1>
  </div>
</template>

<script setup>
</script>

<style scoped>
</style> -->


<template>
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
        <p id="hakka" class="roman">{{ cards[currentCard].hakka }}</p>
        <button @click="playAudio(cards[currentCard].audio)" :disabled="!cards[currentCard].audio">🔊 播放客語</button>
      </div>
      <div class="nav">
        <button @click="prevCard">上一張</button>
        <button @click="nextCard">下一張</button>
      </div>
      <p id="progress">第 {{ currentCard + 1 }} / {{ cards.length }} 張</p>
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
            @input="onInputChange"
          ></textarea>
        </div>
        
        <div class="translate-button-section">
          <button @click="translateText" :disabled="!chineseInput.trim()" class="translate-btn">翻譯成客語</button>
        </div>
        
        <div class="result-section" v-if="translationResult.show">
          <label class="result-label">客語翻譯：</label>
          <div id="translation-result">
            <p class="hakka-text">{{ translationResult.hakka }}</p>
            <button 
              @click="playTranslationAudio" 
              :disabled="!translationResult.audio"
              class="audio-btn"
            >🔊 播放客語</button>
          </div>
        </div>
        
        <div class="history-section" v-if="translationHistory.length > 0">
          <h3>翻譯記錄</h3>
          <div class="history-list">
            <div 
              v-for="(item, index) in translationHistory" 
              :key="index" 
              class="history-item"
              @click="loadHistoryItem(item)"
            >
              <div class="history-chinese">{{ item.chinese }}</div>
              <div class="history-hakka">{{ item.hakka }}</div>
            </div>
          </div>
          <button @click="clearHistory" class="clear-btn">清除記錄</button>
        </div>
      </div>
    </div>

    <!-- Quiz Section -->
    <div v-if="currentSection === 'quiz'" id="quiz-section">
      <template v-if="quizIndex < quizOrder.length">
        <p id="quiz-question" class="big">「{{ cards[quizOrder[quizIndex]].chinese }}」的客語是？</p>
        <button @click="playAudio(cards[quizOrder[quizIndex]].audio)" :disabled="!cards[quizOrder[quizIndex]].audio">🔊 播放客語</button>
        <div id="quiz-options">
          <button v-for="option in quizOptions" :key="option" @click="checkQuizAnswer(option, cards[quizOrder[quizIndex]].hakka)" :style="option.style">{{ option.text }}</button>
        </div>
        <button @click="nextQuizQuestion" :disabled="!quizAnswered">下一題</button>
        <p id="quiz-score">目前得分：{{ quizScore }}</p>
      </template>
      <template v-else>
        <p id="quiz-question" class="big">測驗完成！</p>
        <p id="quiz-score">總得分：{{ quizScore }} / {{ cards.length }}</p>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';

const cards = ref([
  { chinese: "你好", hakka: "ngi ho", audio: "/audio/ngi_ho.m4a" },
  { chinese: "謝謝", hakka: "an zii se", audio: "/audio/an_zii_se.m4a" },
  { chinese: "再見", hakka: "zai jien", audio: "/audio/zai_jien.mp3" },
  { chinese: "早安", hakka: "zao an", audio: "/audio/zao_an.mp3" },
  { chinese: "午安", hakka: "ngou an", audio: "/audio/ngou_an.mp3" },
  { chinese: "晚安", hakka: "ban an", audio: "/audio/ban_an.mp3" },
  { chinese: "水", hakka: "chui", audio: "/audio/chui.mp3" },
  { chinese: "火", hakka: "foi", audio: "/audio/foi.mp3" },
  { chinese: "吃", hakka: "sik", audio: "/audio/sik.mp3" },
  { chinese: "喝", hakka: "ham", audio: "/audio/ham.mp3" },
  { chinese: "學習", hakka: "hok sip", audio: "/audio/hok_sip.mp3" },
  { chinese: "請", hakka: "qin", audio: "/audio/qin.mp3" },
  { chinese: "對不起", hakka: "te pu qi", audio: "/audio/te_pu_qi.mp3" },
  { chinese: "是", hakka: "si", audio: "/audio/si.mp3" },
  { chinese: "不是", hakka: "m si", audio: "/audio/m_si.mp3" },
  { chinese: "飯", hakka: "pan", audio: "/audio/pan.mp3" },
  { chinese: "買", hakka: "mai", audio: "/audio/mai.mp3" },
  { chinese: "賣", hakka: "mai vun", audio: "/audio/mai_vun.mp3" },
  { chinese: "貴", hakka: "gui", audio: "/audio/gui.mp3" },
  { chinese: "便宜", hakka: "pien yi", audio: "/audio/pien_yi.mp3" },
  { chinese: "這個", hakka: "li ge", audio: "/audio/li_ge.mp3" },
  { chinese: "那個", hakka: "ga ge", audio: "/audio/ga_ge.mp3" },
  { chinese: "在哪裡", hakka: "di bin du", audio: "/audio/di_bin_du.mp3" },
  { chinese: "多少", hakka: "toi to", audio: "/audio/toi_to.mp3" },
  { chinese: "我", hakka: "ngai", audio: "/audio/ngai.mp3" },
  { chinese: "你", hakka: "ngi", audio: "/audio/ngi.mp3" },
  { chinese: "他", hakka: "hi", audio: "/audio/hi.mp3" },
  { chinese: "我們", hakka: "ngai do", audio: "/audio/ngai_do.mp3" },
  { chinese: "今天", hakka: "gim zhin", audio: "/audio/gim_zhin.mp3" },
  { chinese: "明天", hakka: "me gin", audio: "/audio/me_gin.mp3" },
  { chinese: "好", hakka: "ho", audio: "/audio/ho.mp3" },
  { chinese: "不用客氣", hakka: "m yong hak qi", audio: "/audio/m_yong_hak_qi.mp3" },
  { chinese: "聽不懂", hakka: "ngai m dong", audio: "/audio/ngai_m_dong.mp3" },
  { chinese: "我愛你", hakka: "ngai oi ngi", audio: "/audio/ngai_oi_ngi.mp3" },
  { chinese: "你食飽無？", hakka: "ngi sik pan mo?", audio: "/audio/ngi_sik_pan_mo.mp3" },
  { chinese: "這個多少錢？", hakka: "li ge toi to ngien?", audio: "/audio/li_ge_toi_to_ngien.mp3" },
  { chinese: "請再說一次。", hakka: "qin zoi so it ci.", audio: "/audio/qin_zoi_so_it_ci.mp3" },
  { chinese: "我聽不懂客語。", hakka: "ngai m dong hak ngi.", audio: "/audio/ngai_m_dong_hak_ngi.mp3" },
  { chinese: "謝謝你幫忙！", hakka: "to sia ngi bong mang!", audio: "/audio/to_sia_ngi_bong_mang.mp3" }
]);

const currentCard = ref(parseInt(localStorage.getItem('hakkaCard')) || 0);
const audioPlayer = new Audio();
const currentSection = ref('flashcard');

const quizOrder = ref([]);
const quizIndex = ref(0);
const quizScore = ref(0);
const quizOptions = ref([]);
const quizAnswered = ref(false);

// Translation section variables
const chineseInput = ref('');
const translationResult = ref({
  show: false,
  hakka: '',
  audio: null
});
const translationHistory = ref([]);

function loadCard() {
  if (currentCard.value < 0) currentCard.value = 0;
  if (currentCard.value >= cards.value.length) currentCard.value = cards.value.length - 1;
  localStorage.setItem('hakkaCard', currentCard.value);
}

function playAudio(audioSrc) {
  if (audioSrc) {
    audioPlayer.src = audioSrc;
    audioPlayer.play();
  }
}

function prevCard() {
  currentCard.value = (currentCard.value - 1 + cards.value.length) % cards.value.length;
  loadCard();
}

function nextCard() {
  currentCard.value = (currentCard.value + 1) % cards.value.length;
  loadCard();
}

function shuffle(array) {
  for (let i = array.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [array[i], array[j]] = [array[j], array[i]];
  }
  return array;
}

function generateOptions(correctIdx) {
  const options = [{ text: cards.value[correctIdx].hakka, correct: true }];
  const indices = [...Array(cards.value.length).keys()].filter(i => i !== correctIdx);
  shuffle(indices);
  for (let i = 0; i < 3 && i < indices.length; i++) {
    options.push({ text: cards.value[indices[i]].hakka, correct: false });
  }
  return shuffle(options);
}

function startQuiz() {
  quizOrder.value = shuffle([...Array(cards.value.length).keys()]);
  quizIndex.value = 0;
  quizScore.value = 0;
  loadQuizQuestion();
}

function loadQuizQuestion() {
  quizAnswered.value = false;
  if (quizIndex.value < quizOrder.value.length) {
    const correctIdx = quizOrder.value[quizIndex.value];
    quizOptions.value = generateOptions(correctIdx);
  }
}

function checkQuizAnswer(option, correctAnswer) {
  if (quizAnswered.value) return;

  quizAnswered.value = true;
  if (option.text === correctAnswer) {
    quizScore.value++;
    option.style = { backgroundColor: '#9cff9c' };
  } else {
    option.style = { backgroundColor: '#ff9c9c' };
  }
}

function nextQuizQuestion() {
  quizIndex.value++;
  loadQuizQuestion();
}

function showSection(section) {
  currentSection.value = section;
  if (section === 'quiz') {
    startQuiz();
  }
}

// Translation functions
function onInputChange() {
  if (translationResult.value.show) {
    translationResult.value.show = false;
  }
}

function translateText() {
  if (!chineseInput.value.trim()) return;
  
  // 模擬翻譯功能 - 這裡之後可以替換成實際的翻譯邏輯
  const inputText = chineseInput.value.trim();
  
  // 檢查是否在現有單字卡中有匹配的翻譯
  const foundCard = cards.value.find(card => card.chinese === inputText);
  
  if (foundCard) {
    translationResult.value = {
      show: true,
      hakka: foundCard.hakka,
      audio: foundCard.audio
    };
  } else {
    // 如果沒找到，顯示預設訊息
    translationResult.value = {
      show: true,
      hakka: '抱歉，暫時無法翻譯此詞彙',
      audio: null
    };
  }
  
  // 添加到翻譯記錄
  const historyItem = {
    chinese: inputText,
    hakka: translationResult.value.hakka,
    audio: translationResult.value.audio
  };
  
  // 避免重複記錄
  const existingIndex = translationHistory.value.findIndex(item => item.chinese === inputText);
  if (existingIndex !== -1) {
    translationHistory.value.splice(existingIndex, 1);
  }
  
  translationHistory.value.unshift(historyItem);
  
  // 限制記錄數量
  if (translationHistory.value.length > 10) {
    translationHistory.value = translationHistory.value.slice(0, 10);
  }
}

function playTranslationAudio() {
  if (translationResult.value.audio) {
    playAudio(translationResult.value.audio);
  }
}

function loadHistoryItem(item) {
  chineseInput.value = item.chinese;
  translationResult.value = {
    show: true,
    hakka: item.hakka,
    audio: item.audio
  };
}

function clearHistory() {
  translationHistory.value = [];
}

onMounted(() => {
  loadCard();
});

</script>

<style scoped>
/* Using the same styles from the original CSS file */
.container {
  max-width: 500px;
  margin: 2em auto;
  padding: 2em;
  background-color: rgba(255, 255, 255, 0.85);
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

h1 {
  color: #d6336c;
}

.tabs button {
  margin: 0 0.5em;
  padding: 0.5em 1.2em;
  border: none;
  border-radius: 6px;
  background-color: #e0e0e0;
  cursor: pointer;
  transition: background-color 0.2s;
  font-size: 1rem;
}

.tabs button.active {
  background-color: #d0d0ff;
  font-weight: bold;
}

#card, #quiz-section, #translate-section {
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  padding: 1.5em 1em;
  margin-bottom: 1.5em;
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

button {
  margin: 0.4em;
  padding: 0.6em 1.2em;
  border: none;
  border-radius: 6px;
  background-color: #e0e0e0;
  cursor: pointer;
  transition: background-color 0.2s;
  font-size: 1rem;
}

button:hover:not(:disabled) {
  background-color: #d0d0ff;
}

button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
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
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  font-size: 1rem;
  resize: vertical;
  min-height: 80px;
  box-sizing: border-box;
  font-family: inherit;
}

#chinese-input:focus {
  outline: none;
  border-color: #d6336c;
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
  background-color: #cccccc;
  color: #888;
}

.result-section {
  margin-bottom: 1.5em;
}

#translation-result {
  background-color: #f8f9fa;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  padding: 1.2em;
  text-align: center;
}

.hakka-text {
  font-size: 1.4rem;
  color: #2c5aa0;
  font-weight: bold;
  margin: 0 0 0.8em 0;
}

.audio-btn {
  background-color: #28a745;
  color: white;
  font-size: 1rem;
  padding: 0.6em 1.5em;
}

.audio-btn:hover:not(:disabled) {
  background-color: #218838;
}

.history-section {
  margin-top: 2em;
}

.history-section h3 {
  color: #555;
  font-size: 1.2rem;
  margin-bottom: 1em;
  border-bottom: 1px solid #e0e0e0;
  padding-bottom: 0.5em;
}

.history-list {
  max-height: 300px;
  overflow-y: auto;
  margin-bottom: 1em;
}

.history-item {
  background-color: #f8f9fa;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  padding: 0.8em;
  margin-bottom: 0.5em;
  cursor: pointer;
  transition: background-color 0.2s;
}

.history-item:hover {
  background-color: #e9ecef;
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

.clear-btn {
  background-color: #dc3545;
  color: white;
  font-size: 0.9rem;
  padding: 0.5em 1.2em;
}

.clear-btn:hover {
  background-color: #c82333;
}
</style>