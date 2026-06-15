import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'hero',
      component: () => import('../views/Hero.vue'),
    },
    {
      path: '/home',
      name: 'home',
      component: () => import('../views/Home.vue'),
    },
    {
      path: '/tags',
      name: 'tags',
      component: () => import('../views/Tags.vue'),
    },
    {
      path: '/article/:slug',
      name: 'article',
      component: () => import('../views/ArticleDetail.vue'),
    },
    {
      path: '/editor',
      name: 'editor',
      component: () => import('../views/Editor.vue'),
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('../views/Profile.vue'),
    },
    {
      path: '/toolbox',
      name: 'toolbox',
      component: () => import('../views/Toolbox.vue'),
    },
    {
      path: '/toolbox/doc-review',
      name: 'doc-review',
      component: () => import('../views/ToolDocReview.vue'),
    },
  ],
})

export default router
