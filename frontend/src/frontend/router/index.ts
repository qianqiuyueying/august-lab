import type { RouteRecordRaw } from 'vue-router'

export const frontendRoutes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('../layouts/FrontendLayout.vue'),
    children: [
      {
        path: '',
        name: 'Home',
        component: () => import('../pages/HomePage.vue')
      },
      {
        path: '/portfolio',
        name: 'Portfolio',
        component: () => import('../pages/PortfolioPage.vue')
      },
      {
        path: '/portfolio/:id',
        name: 'PortfolioDetail',
        component: () => import('../pages/PortfolioDetailPage.vue')
      },
      {
        path: '/blog',
        name: 'Blog',
        component: () => import('../pages/BlogPage.vue')
      },
      {
        path: '/blog/:id',
        name: 'BlogDetail',
        component: () => import('../pages/BlogDetailPage.vue')
      },
      {
        path: '/about',
        name: 'About',
        component: () => import('../pages/AboutPage.vue')
      },
      {
        path: '/products',
        name: 'Products',
        component: () => import('../pages/ProductsPage.vue')
      },
      {
        path: '/product/:id',
        name: 'ProductDetail',
        component: () => import('../pages/ProductPage.vue'),
        props: true
      }
    ]
  }
]