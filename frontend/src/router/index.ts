import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'upload',
      component: () => import('../views/UploadView.vue'),
    },
    {
      path: '/pickup',
      redirect: '/?pickup=1',
    },
    {
      path: '/get/:code',
      name: 'pickup',
      component: () => import('../views/PickupView.vue'),
    },
    {
      path: '/admin/login',
      name: 'admin-login',
      component: () => import('../views/admin/AdminLogin.vue'),
    },
    {
      path: '/admin',
      component: () => import('../components/AdminLayout.vue'),
      meta: { requiresAuth: true },
      redirect: '/admin/dashboard',
      children: [
        {
          path: 'dashboard',
          name: 'admin-dashboard',
          component: () => import('../views/admin/AdminDashboard.vue'),
        },
        {
          path: 'settings',
          name: 'admin-settings',
          component: () => import('../views/admin/AdminSettings.vue'),
        },
        {
          path: 'files',
          name: 'admin-files',
          component: () => import('../views/admin/AdminFiles.vue'),
        },
        {
          path: 'files/:id',
          name: 'admin-file-detail',
          component: () => import('../views/admin/AdminFileDetail.vue'),
        },
        {
          path: 'logs',
          name: 'admin-logs',
          component: () => import('../views/admin/AdminLogs.vue'),
        },
      ],
    },
  ],
})

router.beforeEach((to) => {
  if (to.matched.some((record) => record.meta.requiresAuth)) {
    const token = localStorage.getItem('admin_token')
    if (!token) {
      return { name: 'admin-login' }
    }
  }
})

export default router
