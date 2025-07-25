<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import Layout from './components/layouts/Layout.vue'
import { workoutProgram } from './utils'

const router = useRouter()

const workouts = ref(workoutProgram)
const selectedWorkout = ref(null)
const allDailyActivities = ref([]);

const loadDailyActivities = () => {
  let all = [];
  for (let i = 0; i < 7; i++) {
    const savedActivities = localStorage.getItem(`dailyActivities_${i}`);
    if (savedActivities) {
      const dayActivities = JSON.parse(savedActivities);
      all = all.concat(dayActivities.morning, dayActivities.afternoon, dayActivities.evening);
    }
  }
  allDailyActivities.value = all;
};

onMounted(() => {
  loadDailyActivities();
  window.addEventListener('storage', loadDailyActivities); // Listen for storage changes
});

onUnmounted(() => {
  window.removeEventListener('storage', loadDailyActivities);
});

const firstIncompleteWorkoutIndex = computed(() => {
  const incompleteWorkouts = Object.entries(workouts.value).filter(([key, value]) => !value.completed)
  return incompleteWorkouts.length > 0 ? Number(incompleteWorkouts[0][0]) : -1
})

const handleSelectWorkout = (workoutIndex) => {
  selectedWorkout.value = workoutIndex
  router.push(`/workout/${workoutIndex}`)
}

const handleCompleteWorkout = () => {
  workouts.value[selectedWorkout.value].completed = true
  loadDailyActivities(); // Reload activities after completing a workout
  router.push('/dashboard')
}

const handleResetPlan = () => {
  // Reset workout completion status
  for (const key in workouts.value) {
    if (Object.hasOwnProperty.call(workouts.value, key)) {
      workouts.value[key].completed = false;
    }
  }

  // Clear daily activities from localStorage
  for (let i = 0; i < 7; i++) {
    localStorage.removeItem(`dailyActivities_${i}`);
  }
  loadDailyActivities(); // Reload activities after clearing
  
  // Optionally, navigate back to the dashboard or another appropriate page
  router.push('/dashboard');
};

const sevenDayCompletionRate = computed(() => {
  if (allDailyActivities.value.length === 0) return 0;
  const completedCount = allDailyActivities.value.filter(a => a.completed).length;
  return Math.round((completedCount / allDailyActivities.value.length) * 100);
});
</script>

<template>
  <Layout>
    <router-view
      v-slot="{ Component }"
      :workouts="workouts"
      :firstIncompleteWorkoutIndex="firstIncompleteWorkoutIndex"
      :selectedWorkout="selectedWorkout"
      :handleSelectWorkout="handleSelectWorkout"
      :handleCompleteWorkout="handleCompleteWorkout"
      :handleResetPlan="handleResetPlan"
      :sevenDayCompletionRate="sevenDayCompletionRate"
      :loadDailyActivities="loadDailyActivities"
    >
      <component :is="Component" />
    </router-view>
  </Layout>
</template>

<style scoped>
</style>
