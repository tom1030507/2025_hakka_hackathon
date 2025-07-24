<template>
  <div class="course-layout" v-if="courses.length > 0">
    <!-- Left Sidebar for Outline -->
    <aside class="outline-sidebar">
      <h3>課程大綱</h3>
      <ul>
        <li
          v-for="(outline, index) in courseOutlines"
          :key="index"
          @click="goToPage(index)"
          :class="{ 'active': currentPage === index }"
          class="outline-item"
        >
          {{ outline.title }}
        </li>
      </ul>
    </aside>

    <!-- Right Main Content -->
    <main class="course-main-content">
      <div class="course-container" v-if="currentCourse">

        <!-- Course Content -->
        <div class="prose" v-html="renderedMarkdown"></div>

        <!-- Quiz Section -->
        <div class="quiz-container" v-if="currentCourse.output && currentCourse.output.quiz_questions">
          <h2>章節測驗</h2>
          <div v-for="(quiz, index) in currentCourse.output.quiz_questions" :key="quiz.question_number" class="quiz-question">
            <p><strong>第 {{ quiz.question_number }} 題：</strong>{{ quiz.question_text }}</p>
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
                <label :for="`p${currentPage}_q${quiz.question_number}_${optionKey}`">{{ optionKey }}: {{ optionText }}</label>
              </div>
            </div>
            <div v-if="submitted" class="feedback" :class="{
              'correct': userAnswers[index] === quiz.correct_answer,
              'incorrect': userAnswers[index] !== quiz.correct_answer
            }">
              <p v-if="userAnswers[index] === quiz.correct_answer"><strong>正確！</strong></p>
              <p v-else>
                <strong>答錯了。</strong>
                正確答案是：{{ quiz.correct_answer }}
              </p>
              <p class="explanation"><strong>解析：</strong>{{ quiz.explanation }}</p>
            </div>
          </div>
          <button @click="submitQuiz" :disabled="submitted" class="submit-btn">提交答案</button>
        </div>

      </div>
    </main>
  </div>
  <div v-else class="loading-container">
    <p>正在載入課程資料...</p>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { marked } from 'marked';

const courses = ref([]);
const currentPage = ref(0); // 0-indexed
const userAnswers = ref([]);
const submitted = ref(false);

onMounted(async () => {
  try {
    const response = await fetch('/data/page1.json');
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
</script>

<style scoped>
.course-layout {
  display: flex;
  height: 100vh; /* Full height layout */
  max-width: 1400px;
  margin: 0 auto;
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  background-color: #f0f2f5;
}

.outline-sidebar {
  width: 280px;
  flex-shrink: 0;
  background-color: #fff;
  padding: 20px;
  border-right: 1px solid #e0e0e0;
  overflow-y: auto;
}

.outline-sidebar h3 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #333;
  font-size: 1.2em;
  border-bottom: 1px solid #ddd;
  padding-bottom: 10px;
}

.outline-sidebar ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.outline-item {
  padding: 12px 15px;
  cursor: pointer;
  border-radius: 5px;
  transition: background-color 0.2s, color 0.2s;
  color: #333;
  margin-bottom: 8px;
  font-size: 0.95em;
}

.outline-item:hover {
  background-color: #e9ecef;
}

.outline-item.active {
  background-color: #007bff;
  color: white;
  font-weight: bold;
  box-shadow: 0 2px 5px rgba(0, 123, 255, 0.3);
}

.course-main-content {
  flex-grow: 1;
  overflow-y: auto; /* Allows content to scroll independently */
  padding: 20px 40px;
}

/* Custom Scrollbar for Webkit browsers */
.course-main-content::-webkit-scrollbar {
  width: 12px; /* Makes the scrollbar wider */
}

.course-main-content::-webkit-scrollbar-track {
  background: #f1f1f1; /* Light grey track */
  border-radius: 10px;
}

.course-main-content::-webkit-scrollbar-thumb {
  background: #c1c1c1; /* A visible grey thumb */
  border-radius: 10px;
  border: 2px solid #f1f1f1; /* Creates a padding effect */
}

.course-main-content::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8; /* Darker thumb on hover */
}

.course-container {
  background-color: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  padding: 20px;
  max-width: 800px;
  margin: 0 auto; /* Center the container within the main content area */
  padding-bottom: 20vh; /* Add significant space at the bottom */
}

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
}

.prose {
  line-height: 1.7;
  color: #333;
}

.prose :deep(h1), .prose :deep(h2), .prose :deep(h3) {
  border-bottom: 1px solid #eaecef;
  padding-bottom: 0.3em;
  margin-top: 24px;
  margin-bottom: 16px;
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
}

.prose :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin-top: 1em;
  margin-bottom: 1em;
}

.prose :deep(th), .prose :deep(td) {
  border: 1px solid #dfe2e5;
  padding: 8px 12px;
}

.prose :deep(th) {
  background-color: #f6f8fa;
  font-weight: bold;
}

.quiz-container {
  margin-top: 40px;
  border-top: 2px solid #eee;
  padding-top: 20px;
}

.quiz-question {
  margin-bottom: 25px;
  padding: 15px;
  background-color: #fff;
  border-radius: 5px;
  border: 1px solid #ddd;
}

.options {
  margin-top: 10px;
}

.option {
  margin-bottom: 8px;
}

.option input[type="radio"] {
  margin-right: 10px;
}

.submit-btn {
  background-color: #4CAF50;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.3s;
}

.submit-btn:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.submit-btn:not(:disabled):hover {
  background-color: #45a049;
}

.feedback {
  margin-top: 15px;
  padding: 10px;
  border-radius: 4px;
}

.feedback.correct {
  border: 1px solid #4CAF50;
  background-color: #e8f5e9;
}

.feedback.incorrect {
  border: 1px solid #f44336;
  background-color: #ffebee;
}

.feedback p {
  margin: 0;
}

.explanation {
  margin-top: 8px !important;
  font-size: 0.9em;
  color: #555;
}
</style>