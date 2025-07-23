<template>
  <div>
    <h1>{{ message }}</h1>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';

const message = ref('Loading...');

onMounted(async () => {
  try {
    const response = await fetch('http://127.0.0.1:8000/');
    const data = await response.json();
    message.value = data.Hello;
  } catch (error) {
    console.error('Error fetching data:', error);
    message.value = 'Failed to load data';
  }
});
</script>

<style scoped>
</style>
