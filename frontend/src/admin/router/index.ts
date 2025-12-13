import type { RouteRecordRaw } from 'vue-router'

export const adminRoutes: RouteRecordRaw[] = [
  {
    path: '/admin/login',
    name: 'AdminLogin',
    component: () => import('../pages/LoginPage.vue')
  },
  {
    path: '/admin',
    component: () => import('../layouts/AdminLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'AdminDashboard',
        component: () => import('../pages/DashboardPage.vue')
      },
      {
        path: 'portfolio',
        name: 'AdminPortfolio',
        component: () => import('../pages/PortfolioManagePage.vue')
      },
      {
        path: 'blog',
        name: 'AdminBlog',
        component: () => import('../pages/BlogManagePage.vue')
      },
      {
        path: 'products',
        name: 'AdminProducts',
        component: () => import('../pages/ProductManagePage.vue')
      },
      {
        path: 'analytics',
        name: 'AdminAnalytics',
        component: () => import('../pages/ProductAnalyticsPage.vue')
      },
      {
        path: 'monitoring',
        name: 'AdminMonitoring',
        component: () => import('../pages/ProductMonitoringPage.vue')
      },
      {
        path: 'extensions',
        name: 'AdminExtensions',
        component: () => import('../pages/ExtensionManagePage.vue')
      },
      {
        path: 'profile',
        name: 'AdminProfile',
        component: () => import('../pages/ProfileManagePage.vue')
      }
    ]
  }
]