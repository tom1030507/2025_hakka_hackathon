<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import Layout from './components/layouts/Layout.vue'
import { workoutProgram } from './utils'

const router = useRouter()

const workouts = ref(workoutProgram)
const selectedWorkout = ref(null)

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
  router.push('/dashboard')
}
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
    >
      <component :is="Component" />
    </router-view>
  </Layout>
</template>

<style scoped>
</style>
