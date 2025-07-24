<template>
  <div class="course-container" v-if="currentCourse">
    <!-- Page Navigation -->
    <div class="pagination">
      <button @click="prevPage" :disabled="currentPage === 0">上一章</button>
      <span>第 {{ currentPage + 1 }} / {{ courses.length }} 章</span>
      <button @click="nextPage" :disabled="currentPage === courses.length - 1">下一章</button>
    </div>

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

     <!-- Page Navigation at the bottom -->
    <div class="pagination bottom-pagination">
      <button @click="prevPage" :disabled="currentPage === 0">上一章</button>
      <button @click="nextPage" :disabled="currentPage === courses.length - 1">下一章</button>
    </div>

  </div>
  <div v-else>
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

// Fetch all course data once
onMounted(async () => {
  try {
    const response = await fetch('/data/page1.json');
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    const data = await response.json();
    courses.value = data;
    // Initialize answers for the first page
    resetQuizState();
  } catch (error) {
    console.error('Failed to fetch course data:', error);
  }
});

// Get the current course based on currentPage
const currentCourse = computed(() => {
  return courses.value.length > 0 ? courses.value[currentPage.value] : null;
});

// Render markdown for the current course
const renderedMarkdown = computed(() => {
  if (currentCourse.value && currentCourse.value.text) {
    marked.setOptions({ breaks: true });
    return marked(currentCourse.value.text);
  }
  return '';
});

// Function to reset quiz state, to be called when page changes
const resetQuizState = () => {
  submitted.value = false;
  if (currentCourse.value && currentCourse.value.output && currentCourse.value.output.quiz_questions) {
    userAnswers.value = Array(currentCourse.value.output.quiz_questions.length).fill(null);
  } else {
    userAnswers.value = [];
  }
};

// Watch for page changes and reset the quiz
watch(currentPage, () => {
  resetQuizState();
  // Scroll to top of the course container
  document.querySelector('.course-container')?.scrollTo(0, 0);
});


const nextPage = () => {
  if (currentPage.value < courses.value.length - 1) {
    currentPage.value++;
  }
};

const prevPage = () => {
  if (currentPage.value > 0) {
    currentPage.value--;
  }
};

const submitQuiz = () => {
  submitted.value = true;
};
</script>

<style scoped>
.course-container {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  margin: 0 auto;
  padding: 20px;
  max-width: 800px;
  background-color: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #ddd;
}

.pagination button {
  background-color: #007bff;
  color: white;
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.pagination button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.pagination button:not(:disabled):hover {
  background-color: #0056b3;
}

.pagination span {
  font-weight: bold;
  color: #555;
}

.bottom-pagination {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #ddd;
  border-bottom: none;
}

.prose {
  line-height: 1.6;
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