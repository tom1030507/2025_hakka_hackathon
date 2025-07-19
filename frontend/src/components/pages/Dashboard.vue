<script setup>
    import { ref, onMounted, onUnmounted, computed } from 'vue'
    import Grid from '../Grid.vue'

    import { gymHealthFacts } from '../../utils'

    const props = defineProps({
        handleSelectWorkout: Function,
        firstIncompleteWorkoutIndex: Number
    })
    
    // generate a random whole integer number between 0 and array length - 1
    const randomNumber = Math.floor(Math.random() * gymHealthFacts.length)
    const todaysFact = gymHealthFacts[randomNumber]
    const today = ref('')
    let timerId = null;

    const updateDate = () => {
        const date = new Date();
        const options = { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' };
        today.value = date.toLocaleDateString('zh-TW', options);
    }

    const scheduleDateUpdate = () => {
        const now = new Date();
        const tomorrow = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 1);
        const msUntilMidnight = tomorrow - now;

        timerId = setTimeout(() => {
            updateDate();
            // Now update every 24 hours
            timerId = setInterval(updateDate, 24 * 60 * 60 * 1000);
        }, msUntilMidnight);
    }

    onMounted(() => {
        updateDate();
        scheduleDateUpdate();
    })

    onUnmounted(() => {
        if (timerId) {
            clearTimeout(timerId);
            clearInterval(timerId);
        }
    })

    const sevenDayActivities = computed(() => {
      let all = [];
      for (let i = 0; i < 7; i++) {
        const savedActivities = localStorage.getItem(`dailyActivities_${i}`);
        if (savedActivities) {
          const dayActivities = JSON.parse(savedActivities);
          all = all.concat(dayActivities.morning, dayActivities.afternoon, dayActivities.evening);
        }
      }
      return all;
    });

    const sevenDayCompletionRate = computed(() => {
      if (sevenDayActivities.value.length === 0) return 0;
      const completedCount = sevenDayActivities.value.filter(a => a.completed).length;
      return Math.round((completedCount / sevenDayActivities.value.length) * 100);
    });

    const circumference = 2 * Math.PI * 90; // 2 * pi * r
    const strokeOffset = computed(() => {
      return circumference - (sevenDayCompletionRate.value / 100) * circumference;
    });
</script>

<template>
    <section id="dashboard">
        <div class="dashboard-content">
            <div class="card tip-container">
                <h2>Welcome Smoldier</h2>
                <p>{{ today }}</p>
                <div>
                    <p class="tip"><strong>Daily Tip</strong><br/>{{ todaysFact }}</p>
                </div>
            </div>
            <Grid v-bind="props"  />
        </div>
        <aside class="progress-container">
            <h3>7天完成率</h3>
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
                <text x="50%" y="50%" text-anchor="middle" dy=".3em" class="progress-text">{{ sevenDayCompletionRate }}%</text>
            </svg>
        </aside>
    </section>
</template>

<style scoped>
    #dashboard {
        display: flex;
        gap: 2rem;
        flex-direction: row; /* Changed to row to place content and progress side-by-side */
        align-items: flex-start; /* Align items to the top */
    }

    .dashboard-content {
        flex: 3; /* Takes 3/5 of the space */
        display: flex;
        flex-direction: column;
        gap: 2rem;
    }

    .progress-container {
        flex: 2; /* Takes 2/5 of the space */
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: flex-start; /* Align to the top */
        gap: 1rem;
        padding-top: 1rem; /* Add some padding to push it down slightly */
    }

    .tip-container,
    .tip-container div {
        display: flex;
    }

    .tip-container {
        flex-direction: column;
        gap: 0.5rem;
    }

    @media (min-width: 640px) {
        .tip-container {
            gap: 1rem;
        }
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