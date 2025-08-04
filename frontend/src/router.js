
import { createRouter, createWebHistory } from 'vue-router';
import Welcome from './components/pages/Welcome.vue';
import Dashboard from './components/pages/Dashboard.vue';
import Blank from './components/pages/Blank.vue';
import Workout from './components/pages/Goal.vue';
import Learning from './components/pages/Learning.vue';

const routes = [
  { path: '/', component: Welcome },
  { path: '/dashboard', component: Dashboard },
  { path: '/blank1', component: Learning },
  { path: '/workout/:dayIndex', component: Workout, props: true },
  {
    path: '/course/1',
    component: () => import('./components/pages/Courses/Course1.vue')
  },
  {
    path: '/course/2',
    component: () => import('./components/pages/Courses/Course2.vue')
  },
  {
    path: '/course/3',
    component: () => import('./components/pages/Courses/Course3.vue')
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
