<script setup>
    import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
    import Grid from '../Grid.vue'

    import { Facts } from '../../utils'

    const props = defineProps({
        handleSelectWorkout: Function,
        firstIncompleteWorkoutIndex: Number,
        handleResetPlan: Function,
        sevenDayCompletionRate: Number,
        structuredDailyActivities: Object
    })
    
    // generate a random whole integer number between 0 and array length - 1
    const randomNumber = Math.floor(Math.random() * Facts.length)
    const todaysFact = Facts[randomNumber]
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

    const incompleteAllActivities = computed(() => {
        let all = [];
        for (const dayIndex in props.structuredDailyActivities) {
            const activities = props.structuredDailyActivities[dayIndex];
            all = all.concat(activities.morning, activities.afternoon, activities.evening);
        }
        return all.filter(activity => !activity.completed);
    });

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

    const circumference = 2 * Math.PI * 90; // 2 * pi * r
    const strokeOffset = computed(() => {
      return circumference - (props.sevenDayCompletionRate / 100) * circumference;
    });
</script>

<template>
    <section id="dashboard">
        <div class="dashboard-background"></div>
        <div class="dashboard-overlay"></div>
        <div class="dashboard-wrapper">
            <div class="dashboard-content">
                <div class="card tip-container">
                    <h2>學習計畫</h2>
                    <p>{{ today }}</p>
                    <div>
                        <p class="tip"><strong>Daily Tip</strong><br/>{{ todaysFact }}</p>
                    </div>
                </div>
                <Grid v-bind="props"  />
            </div>
            <aside class="progress-container">
                <!-- <h3>7天完成率</h3> -->
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
                    <text x="50%" y="50%" text-anchor="middle" dy=".3em" class="progress-text">{{ props.sevenDayCompletionRate }}%</text>
                </svg>
                <div class="todo-list-container card">
                    <h4>所有待辦 (未完成)</h4>
                    <ul v-if="incompleteAllActivities.length > 0">
                        <li v-for="(activity, index) in incompleteAllActivities" :key="index">
                            <span>{{ activity.text }}</span>
                        </li>
                    </ul>
                    <p v-else>目前沒有未完成的待辦事項！</p>
                    
                    
                </div>
            </aside>
        </div>
    </section>
</template>

<style scoped>
    #dashboard {
        position: relative;
        min-height: 100vh;
        overflow: hidden;
    }

    .dashboard-background {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: url('/images/dashboard_pic.jpg');
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        z-index: -2;
    }

    .dashboard-overlay {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(to bottom, rgba(255, 255, 255, 0) 0%, rgba(255, 255, 255, 0.85) 100%);
        z-index: -1;
    }

    .dashboard-wrapper {
        position: relative;
        z-index: 1;
        display: flex;
        gap: 2rem;
        flex-direction: row;
        align-items: flex-start;
        padding: 2rem;
        min-height: 100vh;
    }

    .dashboard-content {
        flex: 3;
        display: flex;
        flex-direction: column;
        gap: 2rem;
    }

    .progress-container {
        flex: 2;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: flex-start;
        gap: 1rem;
        padding-top: 1rem;
    }

    .card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }

    .tip-container,
    .tip-container div {
        display: flex;
    }

    .tip-container {
        flex-direction: column;
        gap: 2rem;
        height: 240px; 
        padding: 2rem;
        border-radius: 12px;
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

    .todo-list-container {
        width: 100%;
        margin-top: 2rem;
        padding: 1rem;
        border-radius: 12px;
    }

    .task-list {
        display: flex;
        flex-direction: column;
        gap: 1rem;
        margin-top: 1rem;
    }

    .add-task {
        display: flex;
        gap: 0.5rem;
    }

    .add-task-container {
        margin-top: 0.5rem;
    }

    ul {
        list-style-type: none;
        padding: 0;
        margin: 0;
    }

    li {
        background-color: rgba(248, 250, 252, 0.8);
        padding: 0.5rem 1rem;
        border-radius: 4px;
        margin-bottom: 0.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        backdrop-filter: blur(5px);
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

    h2, h4, p {
        color: #1a202c;
        text-shadow: 0 1px 2px rgba(255, 255, 255, 0.8);
    }

    @media (max-width: 768px) {
        .dashboard-wrapper {
            flex-direction: column;
            padding: 1rem;
        }
        
        .dashboard-content,
        .progress-container {
            flex: 1;
        }
    }
</style>