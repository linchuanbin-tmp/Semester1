import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/auth/LoginView.vue'),
      meta: { public: true },
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/auth/RegisterView.vue'),
      meta: { public: true },
    },
    {
      path: '/',
      component: () => import('@/layouts/AppLayout.vue'),
      children: [
        {
          path: '',
          redirect: { name: 'workflows' },
        },
        {
          path: 'workflows',
          name: 'workflows',
          component: () => import('@/views/workflows/WorkflowListView.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: 'workflows/new',
          name: 'workflow-new',
          component: () => import('@/views/workflows/WorkflowCreateView.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: 'workflows/detail/:id',
          name: 'workflow-detail',
          component: () => import('@/views/workflows/WorkflowDetailView.vue'),
          props: true,
          meta: { requiresAuth: true },
        },
      ],
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('@/views/NotFoundView.vue'),
      meta: { public: true },
    },
  ],
})

router.beforeEach((to, _from, next) => {
  const auth = useAuthStore()
  if (to.meta.public) {
    next()
    return
  }

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } })
    return
  }

  next()
})

export default router
