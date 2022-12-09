import { createRouter as createVueRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import { useUser } from './hooks'

const routes: Array<RouteRecordRaw> = [
  {
    name: 'Home',
    path: '/',
    component: () => import('./views/Home.vue'),
    meta: {},
  },
  {
    name: 'Login',
    path: '/login',
    component: () => import('./views/Login.vue'),
    meta: {},
  },
]

const router = createVueRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const { isLoggedIn } = useUser()
  console.debug('routing from', from.name, 'to', to.name, '| isLoggedIn:', isLoggedIn.value)
  if (to.meta.requiresAuth && !isLoggedIn.value) next({ name: 'Login' })
  else if (to.name === 'Login' && isLoggedIn.value) next({ name: 'Home' })
  else next()
})

router.afterEach(to => {
  document.title = `${String(to.name)} | TimTube`
  window.scrollTo({ top: 0 })
})

export const createRouter = () => router
