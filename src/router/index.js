import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/login.vue'),
      meta: { 
        title: '用户登录',
        requiresAuth: false // 不需要登录验证
      }
    },
    {
      path: '/',
      name: 'Index',
      component: () => import('@/views/index.vue'),
      meta: { 
        title: 'AI智能助手',
        requiresAuth: true // 需要登录验证
      }
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/login' // 未匹配的路径重定向到登录页
    }
  ],
})

// 路由守卫 - 检查登录状态
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  
  // 设置页面标题
  if (to.meta.title) {
    document.title = to.meta.title
  }
  
  // 检查是否需要登录验证
  if (to.meta.requiresAuth) {
    // 检查用户是否已登录
    if (!userStore.isLoggedIn && !userStore.token) {
      // 未登录，重定向到登录页
      next({
        path: '/login',
        query: { redirect: to.fullPath } // 保存原始目标路径
      })
      return
    }
  }
  
  // 如果已登录且访问登录页，重定向到主页
  if (to.path === '/login' && (userStore.isLoggedIn || userStore.token)) {
    next('/')
    return
  }
  
  next() // 继续路由导航
})

export default router
