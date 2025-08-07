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
            placeholder="例如：客家文化、客家歷史、小六數學等..."
            class="input-field"
            rows="3"
            @keydown.enter.prevent="submitInput"
          ></textarea>
        </div>
        
        <!-- 課程難易度選擇 -->
        <div class="difficulty-section">
          <div class="section-row">
            <label class="section-label">課程難易度：</label>
            <div class="difficulty-options">
              <label class="difficulty-option" :class="{ active: selectedDifficulty === 'beginner' }">
                <input type="radio" v-model="selectedDifficulty" value="beginner" />
                <span class="difficulty-content">
                  <span class="difficulty-title">初級</span>
                </span>
              </label>
              <label class="difficulty-option" :class="{ active: selectedDifficulty === 'intermediate' }">
                <input type="radio" v-model="selectedDifficulty" value="intermediate" />
                <span class="difficulty-content">
                  <span class="difficulty-title">中級</span>
                </span>
              </label>
              <label class="difficulty-option" :class="{ active: selectedDifficulty === 'advanced' }">
                <input type="radio" v-model="selectedDifficulty" value="advanced" />
                <span class="difficulty-content">
                  <span class="difficulty-title">高級</span>
                </span>
              </label>
            </div>
          </div>
        </div>
        
        <!-- 練習題選項 -->
        <div class="quiz-option-section">
          <div class="section-row">
            <label class="section-label">學習選項：</label>
            <div class="quiz-checkbox-container">
              <label class="quiz-checkbox" :class="{ checked: includeQuiz }">
                <input type="checkbox" v-model="includeQuiz" />
                <span class="checkmark"></span>
                <span class="checkbox-content">
                  <span class="checkbox-title">包含練習題</span>
                </span>
              </label>
            </div>
          </div>
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
          <div class="language-toggle">
            <button 
              @click="toggleLanguage"
              :disabled="translating"
              class="lang-button"
              :class="{ 'translating': translating }"
            >
              <span v-if="!translating">{{ isHakka ? '中文' : '客語' }}</span>
              <span v-else class="translating-text">
                <span class="spinner"></span>
                翻譯中...
              </span>
            </button>
          </div>
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
                    <button
                      type="button"
                      :class="{
                        'option-button': true,
                        'selected': userAnswers[index] === optionKey,
                        'correct': submitted && optionKey === quiz.correct_answer,
                        'incorrect': submitted && userAnswers[index] === optionKey && optionKey !== quiz.correct_answer,
                        'disabled': submitted
                      }"
                      @click="!submitted && (userAnswers[index] = optionKey)"
                      :disabled="submitted"
                    >
                      <span class="option-letter">{{ optionKey }}</span>
                      <span class="option-text">{{ optionText }}</span>
                      <span v-if="submitted && optionKey === quiz.correct_answer" class="check-icon">✓</span>
                      <span v-else-if="submitted && userAnswers[index] === optionKey && optionKey !== quiz.correct_answer" class="cross-icon">✗</span>
                    </button>
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
const selectedDifficulty = ref('intermediate'); // Default to intermediate
const includeQuiz = ref(true); // Default to include quiz
const isHakka = ref(false); // 控制當前顯示語言
const hakkaContent = ref({}); // 存儲翻譯後的內容 {pageIndex: translatedText}
const translating = ref(false); // 翻譯狀態

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
    
    // 如果是客語模式且有翻譯內容，顯示翻譯版本
    if (isHakka.value && hakkaContent.value[currentPage.value]) {
      return marked(hakkaContent.value[currentPage.value]);
    }
    
    // 否則顯示原文
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
  
  try {
    // 調用後端課程生成 API
    const response = await fetch('http://localhost:8000/api/generate_course', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        topic: inputValue.value,
        difficulty: selectedDifficulty.value,
        includeQuiz: includeQuiz.value
      })
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const result = await response.json();
    
    if (result.success && result.data) {
      // 使用 API 返回的課程數據
      courses.value = result.data;
      resetQuizState();
      showContent.value = true;
      console.log('課程生成成功，包含', courses.value.length, '個章節');
    } else {
      throw new Error(result.message || '課程生成失敗');
    }
    
  } catch (error) {
    console.error('課程生成失敗:', error);
    
    // 如果 API 調用失敗，使用靜態數據作為後備
    try {
      const response = await fetch('/data/response.json');
      if (response.ok) {
        const data = await response.json();
        courses.value = data;
        resetQuizState();
        showContent.value = true;
        console.log('使用靜態課程數據作為後備');
      } else {
        throw new Error('無法加載靜態課程數據');
      }
    } catch (fallbackError) {
      console.error('後備數據載入也失敗:', fallbackError);
      alert('課程生成失敗，請稍後再試');
    }
  } finally {
    generatingCourse.value = false;
  }
};

const resetCourse = () => {
  showContent.value = false;
  inputValue.value = '';
  currentPage.value = 0;
  courses.value = [];
  generatingCourse.value = false;
  selectedDifficulty.value = 'intermediate';
  includeQuiz.value = true;
  isHakka.value = false;
  hakkaContent.value = {};
  translating.value = false;
  resetQuizState();
};

// 語言切換函數
const toggleLanguage = async () => {
  if (translating.value) return;
  
  // 如果切換到客語模式且當前頁面還沒翻譯，則進行翻譯
  if (!isHakka.value && !hakkaContent.value[currentPage.value]) {
    await translateCurrentPage();
  }
  
  // 切換語言
  isHakka.value = !isHakka.value;
};

// 翻譯當前頁面內容
const translateCurrentPage = async () => {
  if (!currentCourse.value || translating.value) return;
  
  translating.value = true;
  
  try {
    const response = await fetch('http://localhost:8000/api/translate/course', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text: currentCourse.value.text,
        index: currentPage.value
      })
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const result = await response.json();
    
    if (result.success && result.translatedText) {
      // 存儲翻譯結果
      hakkaContent.value[currentPage.value] = result.translatedText;
    } else {
      console.error('翻譯失敗:', result.error_message || '未知錯誤');
      alert('翻譯失敗，請稍後再試');
    }
    
  } catch (error) {
    console.error('翻譯API調用失敗:', error);
    alert('翻譯服務暫時不可用，請稍後再試');
  } finally {
    translating.value = false;
  }
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
  background-color: #f8f9fa;
  color: #2c3e50;
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
  margin: 0 0 0.8rem 0;
  color: #2c3e50;
  font-weight: 700;
  letter-spacing: -0.5px;
  text-align: center;
  width: 100%;
}

.course-subtitle {
  font-size: 1rem;
  color: #6c757d;
  margin-bottom: 0;
}

.input-container {
  background-color: rgba(255, 255, 255, 0.98);
  border-radius: 16px;
  padding: 2.2rem;
  box-shadow: 
    0 20px 40px rgba(0,0,0,0.1),
    0 8px 16px rgba(0,0,0,0.05),
    inset 0 1px 0 rgba(255,255,255,0.8);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255,255,255,0.2);
  width: 100%;
  max-width: 520px;
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
  margin-bottom: 2rem;
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
  padding: 1rem;
  border: 2px solid #e9ecef;
  border-radius: 10px;
  font-size: 0.95rem;
  resize: vertical;
  box-sizing: border-box;
  font-family: inherit;
  transition: all 0.3s ease;
  background-color: #fafbfc;
  color: #2c3e50;
  line-height: 1.4;
  min-height: 90px;
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
  padding: 0.9rem 2rem;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  transition: all 0.3s ease;
  min-width: 140px;
  position: relative;
  overflow: hidden;
  letter-spacing: 0.3px;
  box-shadow: 
    0 3px 12px rgba(102, 126, 234, 0.3),
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
  background: linear-gradient(135deg, #c1c9d0 0%, #9ca3af 100%);
  cursor: not-allowed;
  transform: none;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  opacity: 0.6;
  color: #6b7280;
}

/* New styles for difficulty selection and quiz options */
.difficulty-section {
  margin-bottom: 2rem;
}

.quiz-option-section {
  margin-bottom: 2.2rem;
}

.section-row {
  display: flex;
  align-items: center;
  gap: 1.2rem;
}

.section-label {
  font-weight: 600;
  color: #2c3e50;
  font-size: 1.1rem;
  letter-spacing: -0.2px;
  white-space: nowrap;
  margin: 0;
  min-width: 100px;
}

/* Difficulty Options Styles */
.difficulty-options {
  display: flex;
  flex-direction: row;
  gap: 0.8rem;
}

.difficulty-option {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 0.8rem;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  background-color: #fafbfc;
  min-width: 60px;
  text-align: center;
  min-height: 44px;
}

.difficulty-option:hover {
  border-color: #667eea;
  background-color: #f8f9ff;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
}

.difficulty-option.active {
  border-color: #667eea;
  background-color: #f0f4ff;
  box-shadow: 0 2px 12px rgba(102, 126, 234, 0.2);
}

.difficulty-option input[type="radio"] {
  display: none;
}

.difficulty-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  width: 100%;
}

.difficulty-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0;
  text-align: center;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.difficulty-desc {
  font-size: 0.9rem;
  color: #6c757d;
  line-height: 1.4;
}

.difficulty-option.active .difficulty-title {
  color: #667eea;
}

.difficulty-option.active .difficulty-desc {
  color: #5a67d8;
}

/* Quiz Checkbox Styles */
.quiz-checkbox-container {
  display: flex;
  flex-direction: column;
}

.quiz-checkbox {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 1rem;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  background-color: #fafbfc;
  position: relative;
  min-height: 44px;
}

.quiz-checkbox:hover {
  border-color: #28a745;
  background-color: #f8fff9;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(40, 167, 69, 0.1);
}

.quiz-checkbox.checked {
  border-color: #28a745;
  background-color: #f0fff4;
  box-shadow: 0 2px 12px rgba(40, 167, 69, 0.2);
}

.quiz-checkbox input[type="checkbox"] {
  position: absolute;
  opacity: 0;
  cursor: pointer;
}

.checkmark {
  height: 20px;
  width: 20px;
  background-color: #fff;
  border: 2px solid #e9ecef;
  border-radius: 4px;
  margin-right: 1rem;
  position: relative;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.quiz-checkbox:hover .checkmark {
  border-color: #28a745;
}

.quiz-checkbox.checked .checkmark {
  background-color: #28a745;
  border-color: #28a745;
}

.checkmark:after {
  content: "";
  position: absolute;
  display: none;
  left: 6px;
  top: 2px;
  width: 6px;
  height: 10px;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.quiz-checkbox.checked .checkmark:after {
  display: block;
}

.checkbox-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  width: 100%;
}

.checkbox-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0;
  text-align: center;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.checkbox-desc {
  font-size: 0.9rem;
  color: #6c757d;
  line-height: 1.4;
}

.quiz-checkbox.checked .checkbox-title {
  color: #28a745;
}

.quiz-checkbox.checked .checkbox-desc {
  color: #218838;
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

/* New Option Button Styles */
.option-button {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 1rem;
  background-color: white;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 1rem;
  text-align: left;
  position: relative;
  overflow: hidden;
}

.option-button:hover:not(.disabled) {
  border-color: #667eea;
  background-color: #f8f9ff;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
}

.option-button.selected {
  border-color: #667eea;
  background-color: #f0f4ff;
  box-shadow: 0 2px 12px rgba(102, 126, 234, 0.2);
}

.option-button.correct {
  background-color: #d4edda;
  border-color: #28a745;
  color: #155724;
}

.option-button.incorrect {
  background-color: #f8d7da;
  border-color: #dc3545;
  color: #721c24;
}

.option-button.disabled {
  cursor: not-allowed;
  opacity: 0.8;
}

.option-letter {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background-color: #667eea;
  color: white;
  border-radius: 50%;
  font-weight: bold;
  font-size: 0.9rem;
  margin-right: 1rem;
  flex-shrink: 0;
}

.option-button.selected .option-letter {
  background-color: #5a67d8;
}

.option-button.correct .option-letter {
  background-color: #28a745;
}

.option-button.incorrect .option-letter {
  background-color: #dc3545;
}

.option-text {
  flex: 1;
  font-weight: 500;
  line-height: 1.4;
}

.check-icon,
.cross-icon {
  font-size: 1.2rem;
  font-weight: bold;
  margin-left: 1rem;
  flex-shrink: 0;
}

.check-icon {
  color: #28a745;
}

.cross-icon {
  color: #dc3545;
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
  
  .difficulty-options {
    gap: 0.5rem;
  }
  
  .difficulty-option {
    padding: 0.7rem 0.5rem;
  }
  
  .difficulty-title {
    font-size: 1rem;
  }
  
  .difficulty-desc {
    font-size: 0.8rem;
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

/* Language Toggle Styles */
.language-toggle {
  display: flex;
  align-items: center;
}

.lang-button {
  background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
  color: white;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
  transition: all 0.3s ease;
  min-width: 70px;
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.lang-button:hover:not(:disabled) {
  background: linear-gradient(135deg, #218838 0%, #1ea085 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3);
}

.lang-button:disabled {
  background: linear-gradient(135deg, #6c757d 0%, #5a6268 100%);
  cursor: not-allowed;
  opacity: 0.8;
}

.lang-button.translating {
  background: linear-gradient(135deg, #fd7e14 0%, #e67e22 100%);
}

.translating-text {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.spinner {
  width: 12px;
  height: 12px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>