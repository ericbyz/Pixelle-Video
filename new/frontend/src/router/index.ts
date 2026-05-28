import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/home',
    },
    {
      path: '/home',
      name: 'Home',
      component: () => import('@/views/HomeView.vue'),
    },
    {
      path: '/history',
      name: 'History',
      component: () => import('@/views/HistoryView.vue'),
    },
  ],
})

export default router
