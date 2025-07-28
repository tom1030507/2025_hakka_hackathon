<template>
  <div class="course-container">
    <!-- Initial Input Screen -->
    <div class="initial-screen" v-if="!showContent && !generatingCourse">
      <div class="course-header">
        <h1>AI 智能課程生成</h1>
        <p class="course-subtitle">輸入您想學習的主題，AI 將為您生成個人化課程內容</p>
      </div>
      
      <div class="input-container">
        <div class="input-section">
          <label for="topic-input" class="input-label">請輸入學習主題：</label>
          <textarea 
            id="topic-input"
            v-model="inputValue" 
            placeholder="例如：客家文化、客語語法、客家歷史等..."
            class="input-field"
            rows="3"
            @keydown.enter.prevent="submitInput"
          ></textarea>
        </div>
        <div class="button-section">
          <button @click="submitInput" :disabled="!inputValue.trim()" class="submit-button">
            開始學習
          </button>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-else-if="generatingCourse" class="loading-container">
      <div class="loading-content">
        <div class="loading-spinner"></div>
        <p>正在為您生成個人化課程內容...</p>
      </div>
    </div>

    <!-- Main Course Content -->
    <div class="course-layout" v-else-if="courses.length > 0">
      <!-- Course Header -->
      <div class="course-header">
        <h1>{{ inputValue }} - 學習課程</h1>
        <div class="course-controls">
          <button @click="resetCourse" class="reset-button">重新開始</button>
          <div class="progress-indicator">
            {{ currentPage + 1 }} / {{ courses.length }} 章節
          </div>
        </div>
      </div>

      <!-- Main Content Area -->
      <div class="content-wrapper">
        <!-- Left Sidebar for Outline -->
        <aside class="outline-sidebar">
          <h3>課程大綱</h3>
          <ul>
            <li
              v-for="(outline, index) in courseOutlines"
              :key="index"
              @click="goToPage(index)"
              :class="{ 
                'active': currentPage === index,
                'completed': index < currentPage 
              }"
              class="outline-item"
            >
              <span class="chapter-number">{{ index + 1 }}</span>
              <span class="chapter-title">{{ outline.title }}</span>
            </li>
          </ul>
        </aside>

        <!-- Right Main Content -->
        <main class="course-main-content">
          <div class="course-content-container" v-if="currentCourse">
            <!-- Course Content -->
            <div class="prose" v-html="renderedMarkdown"></div>

            <!-- Quiz Section -->
            <div class="quiz-container" v-if="currentCourse.output && currentCourse.output.quiz_questions">
              <h2>章節測驗</h2>
              <div v-for="(quiz, index) in currentCourse.output.quiz_questions" :key="quiz.question_number" class="quiz-question">
                <p class="question-text">
                  <strong>第 {{ quiz.question_number }} 題：</strong>{{ quiz.question_text }}
                </p>
                <div class="options">
                  <div v-for="(optionText, optionKey) in quiz.options" :key="optionKey" class="option">
                    <input
                      type="radio"
                      :id="`p${currentPage}_q${quiz.question_number}_${optionKey}`"
                      :name="`page${currentPage}_question_${quiz.question_number}`"
                      :value="optionKey"
                      v-model="userAnswers[index]"
                      :disabled="submitted"
                    />
                    <label :for="`p${currentPage}_q${quiz.question_number}_${optionKey}`" 
                           :class="{ 
                             'correct': submitted && optionKey === quiz.correct_answer,
                             'incorrect': submitted && userAnswers[index] === optionKey && optionKey !== quiz.correct_answer
                           }">
                      {{ optionKey }}: {{ optionText }}
                    </label>
                  </div>
                </div>
                <div v-if="submitted" class="feedback" :class="{
                  'correct': userAnswers[index] === quiz.correct_answer,
                  'incorrect': userAnswers[index] !== quiz.correct_answer
                }">
                  <p v-if="userAnswers[index] === quiz.correct_answer" class="feedback-text correct">
                    <span class="icon">✓</span> 正確！
                  </p>
                  <p v-else class="feedback-text incorrect">
                    <span class="icon">✗</span> 答錯了。正確答案是：{{ quiz.correct_answer }}
                  </p>
                  <p class="explanation">
                    <strong>解析：</strong>{{ quiz.explanation }}
                  </p>
                </div>
              </div>
              
              <div class="quiz-actions">
                <button @click="submitQuiz" :disabled="submitted || !allQuestionsAnswered" class="submit-btn">
                  {{ submitted ? '已提交' : '提交答案' }}
                </button>
                <button v-if="submitted && hasNextChapter" @click="goToPage(currentPage + 1)" class="next-chapter-btn">
                  下一章節
                </button>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
    
    <!-- Error State -->
    <div v-else class="loading-container">
      <div class="error-content">
        <p>課程載入失敗，請重新整理頁面或重新輸入主題</p>
        <button @click="resetCourse" class="retry-button">重試</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { marked } from 'marked';

const courses = ref([]);
const currentPage = ref(0); // 0-indexed
const userAnswers = ref([]);
const submitted = ref(false);
const showContent = ref(false); // New ref to control content visibility
const inputValue = ref(''); // New ref for input field
const generatingCourse = ref(false); // Loading state for course generation

onMounted(async () => {
  try {
    const response = await fetch('/data/response.json');
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    const data = await response.json();
    courses.value = data;
    resetQuizState();
  } catch (error) {
    console.error('Failed to fetch course data:', error);
  }
});

const currentCourse = computed(() => {
  return courses.value.length > 0 ? courses.value[currentPage.value] : null;
});

const courseOutlines = computed(() => {
  return courses.value.map(course => {
    const titleMatch = course.text.match(/^#\s*(.*)/);
    return {
      title: titleMatch ? titleMatch[1] : '未命名章節'
    };
  });
});

const renderedMarkdown = computed(() => {
  if (currentCourse.value && currentCourse.value.text) {
    marked.setOptions({ breaks: true });
    return marked(currentCourse.value.text);
  }
  return '';
});

const allQuestionsAnswered = computed(() => {
  if (!currentCourse.value?.output?.quiz_questions) return true;
  return userAnswers.value.length === currentCourse.value.output.quiz_questions.length &&
         userAnswers.value.every(answer => answer !== null && answer !== undefined);
});

const hasNextChapter = computed(() => {
  return currentPage.value < courses.value.length - 1;
});

const resetQuizState = () => {
  submitted.value = false;
  if (currentCourse.value && currentCourse.value.output && currentCourse.value.output.quiz_questions) {
    userAnswers.value = Array(currentCourse.value.output.quiz_questions.length).fill(null);
  } else {
    userAnswers.value = [];
  }
};

watch(currentPage, () => {
  resetQuizState();
  const mainContent = document.querySelector('.course-main-content');
  if (mainContent) {
    mainContent.scrollTo(0, 0);
  }
});

const goToPage = (index) => {
  currentPage.value = index;
};

const submitQuiz = () => {
  submitted.value = true;
};

const submitInput = async () => {
  if (!inputValue.value.trim()) return;
  
  generatingCourse.value = true;
  
  // Simulate course generation delay
  await new Promise(resolve => setTimeout(resolve, 1500));
  
  showContent.value = true;
  generatingCourse.value = false;
  
  // You can also do something with inputValue here, e.g., send it to a backend
  console.log('Input submitted:', inputValue.value);
};

const resetCourse = () => {
  showContent.value = false;
  inputValue.value = '';
  currentPage.value = 0;
  courses.value = [];
  generatingCourse.value = false;
  resetQuizState();
};
</script>

<style scoped>
/* Main Container */
.course-container {
  width: 100%;
  height: calc(100vh - 140px); /* 扣除header(約60px)、border(1px)、padding(2rem=32px)等空間 */
  min-height: 450px; /* 最小高度保證可用性 */
  max-height: calc(100vh - 140px); /* 防止超出視窗 */
  background-color: #f9f9f9;
  font-family: 'Helvetica Neue', Arial, sans-serif;
  overflow: hidden;
  position: relative;
  display: flex;
  flex-direction: column;
}

/* Initial Screen Styles */
.initial-screen {
  width: 100%;
  height: 100%;
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  position: relative;
  overflow: hidden;
  box-sizing: border-box;
}

.initial-screen::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Ccircle cx='30' cy='30' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E") repeat;
  pointer-events: none;
}

.course-header {
  text-align: center;
  margin-bottom: 1.5rem;
  position: relative;
  z-index: 1;
}

.initial-screen .course-header h1 {
  font-size: 2.2rem;
  margin-bottom: 0.8rem;
  color: white;
  text-shadow: 0 2px 8px rgba(0,0,0,0.3);
  font-weight: 700;
  letter-spacing: -0.5px;
}

.course-subtitle {
  font-size: 1rem;
  opacity: 0.9;
  margin-bottom: 0;
  text-shadow: 0 1px 3px rgba(0,0,0,0.2);
}

.input-container {
  background-color: rgba(255, 255, 255, 0.98);
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 
    0 20px 40px rgba(0,0,0,0.1),
    0 8px 16px rgba(0,0,0,0.05),
    inset 0 1px 0 rgba(255,255,255,0.8);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255,255,255,0.2);
  width: 100%;
  max-width: 480px;
  position: relative;
  z-index: 1;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.input-container:hover {
  transform: translateY(-2px);
  box-shadow: 
    0 25px 50px rgba(0,0,0,0.15),
    0 12px 20px rgba(0,0,0,0.08),
    inset 0 1px 0 rgba(255,255,255,0.9);
}

.input-section {
  margin-bottom: 1.8rem;
}

.input-label {
  display: block;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 0.8rem;
  font-size: 1.1rem;
  letter-spacing: -0.2px;
}

.input-field {
  width: 100%;
  padding: 1.2rem;
  border: 2px solid #e9ecef;
  border-radius: 12px;
  font-size: 1rem;
  resize: vertical;
  box-sizing: border-box;
  font-family: inherit;
  transition: all 0.3s ease;
  background-color: #fafbfc;
  color: #2c3e50;
  line-height: 1.5;
  min-height: 120px;
}

.input-field:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 
    0 0 0 3px rgba(102, 126, 234, 0.1),
    0 2px 8px rgba(102, 126, 234, 0.08);
  background-color: #ffffff;
  transform: translateY(-1px);
}

.input-field::placeholder {
  color: #8b95a1;
  font-style: italic;
}

.button-section {
  text-align: center;
}

.submit-button {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1.2rem 2.5rem;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  font-size: 1.1rem;
  font-weight: 600;
  transition: all 0.3s ease;
  min-width: 180px;
  position: relative;
  overflow: hidden;
  letter-spacing: 0.5px;
  box-shadow: 
    0 4px 15px rgba(102, 126, 234, 0.3),
    0 2px 4px rgba(0,0,0,0.1);
}

.submit-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
  transition: left 0.5s;
}

.submit-button:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 
    0 8px 25px rgba(102, 126, 234, 0.4),
    0 4px 12px rgba(0,0,0,0.15);
}

.submit-button:hover:not(:disabled)::before {
  left: 100%;
}

.submit-button:active:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 
    0 4px 15px rgba(102, 126, 234, 0.3),
    0 2px 4px rgba(0,0,0,0.1);
}

.submit-button:disabled {
  background: linear-gradient(135deg, #adb5bd 0%, #868e96 100%);
  cursor: not-allowed;
  transform: none;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  opacity: 0.7;
}

/* Course Layout Styles */
.course-layout {
  width: 100%;
  height: 100%;
  flex: 1;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
}

.course-layout .course-header {
  background-color: #fff;
  padding: 1rem 2rem;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
}

.course-layout .course-header h1 {
  color: #333;
  margin: 0;
  font-size: 1.5rem;
}

.course-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.reset-button {
  background-color: #6c757d;
  color: white;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.3s ease;
}

.reset-button:hover {
  background-color: #5a6268;
}

.progress-indicator {
  background-color: #e9ecef;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.9rem;
  color: #495057;
}

.content-wrapper {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* Sidebar Styles */
.outline-sidebar {
  width: 280px;
  flex-shrink: 0;
  background-color: #fff;
  border-right: 1px solid #e0e0e0;
  overflow-y: auto;
  padding: 1.5rem;
}

.outline-sidebar h3 {
  margin: 0 0 1.5rem 0;
  color: #333;
  font-size: 1.2rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #667eea;
}

.outline-sidebar ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.outline-item {
  display: flex;
  align-items: center;
  padding: 0.8rem;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.2s ease;
  color: #333;
  margin-bottom: 0.5rem;
  border: 1px solid transparent;
}

.outline-item:hover {
  background-color: #f8f9fa;
  border-color: #e9ecef;
}

.outline-item.active {
  background-color: #667eea;
  color: white;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.outline-item.completed {
  color: #28a745;
  border-color: #28a745;
}

.chapter-number {
  background-color: rgba(102, 126, 234, 0.1);
  color: #667eea;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  font-weight: bold;
  margin-right: 0.8rem;
  flex-shrink: 0;
}

.outline-item.active .chapter-number {
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
}

.outline-item.completed .chapter-number {
  background-color: #28a745;
  color: white;
}

.chapter-title {
  flex: 1;
  font-size: 0.9rem;
  line-height: 1.4;
}

/* Main Content Styles */
.course-main-content {
  flex: 1;
  overflow-y: auto;
  background-color: #f8f9fa;
}

.course-content-container {
  padding: 2rem;
  max-width: 800px;
  margin: 0 auto;
}

/* Prose Styles */
.prose {
  background-color: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  line-height: 1.7;
  color: #333;
  margin-bottom: 2rem;
}

.prose :deep(h1), .prose :deep(h2), .prose :deep(h3) {
  color: #2c3e50;
  border-bottom: 1px solid #eaecef;
  padding-bottom: 0.3em;
  margin-top: 24px;
  margin-bottom: 16px;
}

.prose :deep(h1) { font-size: 2rem; }
.prose :deep(h2) { font-size: 1.5rem; }
.prose :deep(h3) { font-size: 1.25rem; }

.prose :deep(p) {
  margin-bottom: 1rem;
  font-size: 1rem;
}

.prose :deep(code) {
  background-color: rgba(27,31,35,0.05);
  border-radius: 3px;
  padding: 0.2em 0.4em;
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace;
}

.prose :deep(blockquote) {
  border-left: 0.25em solid #dfe2e5;
  padding: 0 1em;
  color: #6a737d;
  margin: 1em 0;
}

/* Quiz Styles */
.quiz-container {
  background-color: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.quiz-container h2 {
  color: #2c3e50;
  margin-bottom: 1.5rem;
  font-size: 1.5rem;
  border-bottom: 2px solid #667eea;
  padding-bottom: 0.5rem;
}

.quiz-question {
  margin-bottom: 2rem;
  padding: 1.5rem;
  background-color: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #667eea;
}

.question-text {
  font-size: 1.1rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 1rem;
}

.options {
  margin: 1rem 0;
}

.option {
  margin-bottom: 0.8rem;
}

.option label {
  display: flex;
  align-items: center;
  padding: 0.8rem;
  background-color: white;
  border: 2px solid #e9ecef;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 1rem;
}

.option label:hover {
  border-color: #667eea;
  background-color: #f8f9ff;
}

.option input[type="radio"] {
  margin-right: 0.8rem;
  transform: scale(1.2);
}

.option label.correct {
  background-color: #d4edda;
  border-color: #28a745;
  color: #155724;
}

.option label.incorrect {
  background-color: #f8d7da;
  border-color: #dc3545;
  color: #721c24;
}

.feedback {
  margin-top: 1rem;
  padding: 1rem;
  border-radius: 6px;
  border-left: 4px solid;
}

.feedback.correct {
  background-color: #d4edda;
  border-left-color: #28a745;
}

.feedback.incorrect {
  background-color: #f8d7da;
  border-left-color: #dc3545;
}

.feedback-text {
  margin: 0 0 0.5rem 0;
  font-weight: bold;
  display: flex;
  align-items: center;
}

.feedback-text .icon {
  margin-right: 0.5rem;
  font-size: 1.2rem;
}

.feedback-text.correct {
  color: #155724;
}

.feedback-text.incorrect {
  color: #721c24;
}

.explanation {
  margin: 0.5rem 0 0 0;
  font-size: 0.95rem;
  color: #495057;
  font-weight: normal;
}

.quiz-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-top: 1.5rem;
}

.submit-btn, .next-chapter-btn {
  padding: 0.8rem 1.5rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: bold;
  transition: all 0.3s ease;
}

.submit-btn {
  background-color: #28a745;
  color: white;
}

.submit-btn:hover:not(:disabled) {
  background-color: #218838;
  transform: translateY(-1px);
}

.submit-btn:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}

.next-chapter-btn {
  background-color: #667eea;
  color: white;
}

.next-chapter-btn:hover {
  background-color: #5a67d8;
  transform: translateY(-1px);
}

/* Loading States */
.loading-container {
  width: 100%;
  height: 100%;
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f8f9fa;
  box-sizing: border-box;
}

.loading-content, .error-content {
  text-align: center;
  padding: 2rem;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.retry-button {
  background-color: #dc3545;
  color: white;
  padding: 0.8rem 1.5rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
  margin-top: 1rem;
}

.retry-button:hover {
  background-color: #c82333;
}

/* Responsive Design */
@media (max-width: 768px) {
  .content-wrapper {
    flex-direction: column;
  }
  
  .outline-sidebar {
    width: 100%;
    max-height: 200px;
    order: 2;
  }
  
  .course-main-content {
    order: 1;
  }
  
  .course-controls {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .initial-screen {
    padding: 1rem;
  }
  
  .course-container {
    height: calc(100vh - 120px); /* 移動端減少更多空間 */
    max-height: calc(100vh - 120px);
    min-height: 400px;
  }
  
  .initial-screen .course-header h1 {
    font-size: 1.8rem;
    margin-bottom: 0.6rem;
  }
  
  .course-subtitle {
    font-size: 0.9rem;
  }
  
  .input-container {
    padding: 1.5rem;
    max-width: 90%;
    margin: 0 auto;
  }
  
  .input-field {
    min-height: 100px;
    padding: 1rem;
  }
  
  .submit-button {
    padding: 1rem 2rem;
    min-width: 160px;
    font-size: 1rem;
  }
}

@media (max-width: 480px) {
  .initial-screen {
    padding: 0.8rem;
  }
  
  .course-container {
    height: calc(100vh - 100px); /* 小螢幕減少更多空間 */
    max-height: calc(100vh - 100px);
    min-height: 350px;
  }
  
  .initial-screen .course-header h1 {
    font-size: 1.6rem;
  }
  
  .course-subtitle {
    font-size: 0.85rem;
  }
  
  .input-container {
    padding: 1.2rem;
    max-width: 95%;
  }
  
  .input-label {
    font-size: 1rem;
  }
  
  .input-field {
    min-height: 80px;
    padding: 0.9rem;
    font-size: 0.95rem;
  }
  
  .submit-button {
    padding: 0.9rem 1.8rem;
    min-width: 140px;
    font-size: 0.95rem;
  }
}

/* High-density screens optimization */
@media (-webkit-min-device-pixel-ratio: 2), (min-resolution: 192dpi) {
  .input-container {
    backdrop-filter: blur(30px);
  }
  
  .initial-screen::before {
    background-size: 30px 30px;
  }
}

/* 確保在Layout約束下的高度適配 */
@media (max-height: 600px) {
  .course-container {
    height: calc(100vh - 100px);
    max-height: calc(100vh - 100px);
    min-height: 300px;
  }
  
  .initial-screen {
    padding: 1rem;
  }
  
  .course-subtitle {
    font-size: 0.9rem;
  }
  
  .input-container {
    padding: 1.5rem;
  }
}

/* 極小高度螢幕優化 */
@media (max-height: 500px) {
  .course-container {
    height: calc(100vh - 80px);
    max-height: calc(100vh - 80px);
    min-height: 250px;
  }
  
  .initial-screen {
    padding: 0.8rem;
  }
  
  .initial-screen .course-header h1 {
    font-size: 1.8rem;
    margin-bottom: 0.5rem;
  }
  
  .course-subtitle {
    font-size: 0.85rem;
  }
  
  .input-container {
    padding: 1.2rem;
  }
  
  .input-field {
    min-height: 80px;
  }
}

/* Scrollbar Styles */
.course-main-content::-webkit-scrollbar,
.outline-sidebar::-webkit-scrollbar {
  width: 8px;
}

.course-main-content::-webkit-scrollbar-track,
.outline-sidebar::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.course-main-content::-webkit-scrollbar-thumb,
.outline-sidebar::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.course-main-content::-webkit-scrollbar-thumb:hover,
.outline-sidebar::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>