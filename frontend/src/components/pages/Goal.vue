<script setup>
import { ref, computed, onMounted, watch } from 'vue';

const props = defineProps({
  dayIndex: String,
  loadDailyActivities: Function
});

const currentDayIndex = computed(() => parseInt(props.dayIndex));

const displayDate = computed(() => {
  const dayNumber = currentDayIndex.value + 1;
  return `Day${dayNumber < 10 ? '0' + dayNumber : dayNumber}`;
});

const activities = ref({
  morning: [],
  afternoon: [],
  evening: []
});

const newActivities = ref({
  morning: '',
  afternoon: '',
  evening: ''
});

const showInputs = ref({
  morning: false,
  afternoon: false,
  evening: false
});

const allActivities = computed(() => {
  return [...activities.value.morning, ...activities.value.afternoon, ...activities.value.evening];
});

const completionRate = computed(() => {
  if (allActivities.value.length === 0) return 0;
  const completedCount = allActivities.value.filter(a => a.completed).length;
  return Math.round((completedCount / allActivities.value.length) * 100);
});

const circumference = 2 * Math.PI * 90; // 2 * pi * r
const strokeOffset = computed(() => {
  return circumference - (completionRate.value / 100) * circumference;
});

function handleSave(period) {
  const newActivityText = newActivities.value[period].trim();
  if (newActivityText !== '') {
    activities.value[period].push({ text: newActivityText, completed: false });
    newActivities.value[period] = '';
  }
  showInputs.value[period] = false;
}

function toggleComplete(activity) {
  activity.completed = !activity.completed;
}

// Load activities from localStorage on component mount
onMounted(() => {
  const savedActivities = localStorage.getItem(`dailyActivities_${currentDayIndex.value}`);
  if (savedActivities) {
    activities.value = JSON.parse(savedActivities);
  }
});

// Watch for changes in activities and save to localStorage
watch(activities, (newActivities) => {
  localStorage.setItem(`dailyActivities_${currentDayIndex.value}`, JSON.stringify(newActivities));
  if (props.loadDailyActivities) {
    props.loadDailyActivities();
  }
}, { deep: true });

// Watch for dayIndex changes and reload activities
watch(currentDayIndex, (newDayIndex) => {
  const savedActivities = localStorage.getItem(`dailyActivities_${newDayIndex}`);
  if (savedActivities) {
    activities.value = JSON.parse(savedActivities);
  } else {
    activities.value = { morning: [], afternoon: [], evening: [] };
  }
});
</script>

<template>
  <div class="page-container">
    <section id="workout-card">
      <div class="plan-card card">
        <h2>每日計畫 - {{ displayDate }}</h2>
      </div>

      <div class="task-list">
        <h4>早上</h4>
        <ul>
          <li v-for="(activity, index) in activities.morning" :key="index" :class="{ completed: activity.completed }">
            <span>{{ activity.text }}</span>
            <button @click="toggleComplete(activity)" class="complete-btn">
              <i :class="['far', activity.completed ? 'fa-check-circle' : 'fa-circle']"></i>
            </button>
          </li>
        </ul>
        <div class="add-task-container">
          <button v-if="!showInputs.morning" @click="showInputs.morning = true">新增</button>
          <div v-else class="add-task">
            <input v-model="newActivities.morning" @keyup.enter="handleSave('morning')" placeholder="新增待辦事項" />
            <button @click="handleSave('morning')">儲存</button>
          </div>
        </div>
      </div>

      <div class="task-list">
        <h4>中午</h4>
        <ul>
          <li v-for="(activity, index) in activities.afternoon" :key="index" :class="{ completed: activity.completed }">
            <span>{{ activity.text }}</span>
            <button @click="toggleComplete(activity)" class="complete-btn">
              <i :class="['far', activity.completed ? 'fa-check-circle' : 'fa-circle']"></i>
            </button>
          </li>
        </ul>
        <div class="add-task-container">
          <button v-if="!showInputs.afternoon" @click="showInputs.afternoon = true">新增</button>
          <div v-else class="add-task">
            <input v-model="newActivities.afternoon" @keyup.enter="handleSave('afternoon')" placeholder="新增待辦事項" />
            <button @click="handleSave('afternoon')">儲存</button>
          </div>
        </div>
      </div>

      <div class="task-list">
        <h4>晚上</h4>
        <ul>
          <li v-for="(activity, index) in activities.evening" :key="index" :class="{ completed: activity.completed }">
            <span>{{ activity.text }}</span>
            <button @click="toggleComplete(activity)" class="complete-btn">
              <i :class="['far', activity.completed ? 'fa-check-circle' : 'fa-circle']"></i>
            </button>
          </li>
        </ul>
        <div class="add-task-container">
          <button v-if="!showInputs.evening" @click="showInputs.evening = true">新增</button>
          <div v-else class="add-task">
            <input v-model="newActivities.evening" @keyup.enter="handleSave('evening')" placeholder="新增待辦事項" />
            <button @click="handleSave('evening')">儲存</button>
          </div>
        </div>
      </div>
    </section>

    <aside class="progress-container">
      <svg class="progress-ring" width="200" height="200">
        <circle class="progress-ring__circle-bg" stroke="#eee" stroke-width="15" fill="transparent" r="90" cx="100" cy="100"/>
        <circle class="progress-ring__circle" 
                stroke="var(--color-link)" 
                stroke-width="15" 
                fill="transparent" 
                r="90" 
                cx="100" 
                cy="100"
                :stroke-dasharray="circumference"
                :stroke-dashoffset="strokeOffset" />
        <text x="50%" y="50%" text-anchor="middle" dy=".3em" class="progress-text">{{ completionRate }}%</text>
      </svg>
    </aside>
  </div>
</template>

<style scoped>
.page-container {
  display: flex;
  gap: 2rem;
  align-items: flex-start;
}

#workout-card {
  flex: 3;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.progress-container {
  flex: 2;
  display: flex;
  align-items: center;
  justify-content: center;
}

.plan-card {
  padding: 1rem;
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.add-task {
  display: flex;
  gap: 0.5rem;
}

ul {
  list-style-type: none;
  padding: 0;
}

li {
  background-color: var(--background-muted);
  padding: 0.5rem 1rem;
  border-radius: 4px;
  margin-bottom: 0.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

li.completed span {
  text-decoration: line-through;
  color: #888;
}

.complete-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  font-size: 1.2rem;
  color: #888;
}

.complete-btn:hover {
  color: var(--color-link);
}

.progress-ring__circle {
  transition: stroke-dashoffset 0.35s;
  transform: rotate(-90deg);
  transform-origin: 50% 50%;
}

.progress-text {
  font-size: 2rem;
  font-weight: bold;
  fill: var(--color-text);
}
</style>
