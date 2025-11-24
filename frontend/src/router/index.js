import { createRouter, createWebHistory } from 'vue-router'
import Install from '../views/Install.vue'
import Login from '../views/Login.vue'
import Dashboard from '../views/Dashboard.vue'
import ProjectDetail from '../views/ProjectDetail.vue'
import UserSettings from '../views/UserSettings.vue'
import DomainMap from '../views/DomainMap.vue'
import CurlTasks from '../views/CurlTasks.vue'
import BigScreen from '../views/BigScreen.vue'
import SharedCredentials from '../views/SharedCredentials.vue'
import VulnerabilityManagement from '../views/VulnerabilityManagement.vue'
import AdminPanel from '../views/AdminPanel.vue'
import ReportTemplates from '../views/ReportTemplates.vue'
import ReportEditor from '../views/ReportEditor.vue'
import request from '../utils/request'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/install',
    name: 'Install',
    component: Install,
    meta: { requiresNotInstalled: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/project/:id',
    name: 'ProjectDetail',
    component: ProjectDetail,
    meta: { requiresAuth: true }
  },
  {
    path: '/project/:id/domain-map',
    name: 'DomainMap',
    component: DomainMap,
    meta: { requiresAuth: true }
  },
  {
    path: '/project/:id/curl-tasks',
    name: 'CurlTasks',
    component: CurlTasks,
    meta: { requiresAuth: true }
  },
  {
    path: '/project/:id/vulnerabilities',
    name: 'VulnerabilityManagement',
    component: VulnerabilityManagement,
    meta: { requiresAuth: true }
  },
  {
    path: '/settings',
    name: 'UserSettings',
    component: UserSettings,
    meta: { requiresAuth: true }
  },
  {
    path: '/bigscreen',
    name: 'BigScreen',
    component: BigScreen,
    meta: { requiresAuth: true }
  },
  {
    path: '/credentials',
    name: 'SharedCredentials',
    component: SharedCredentials,
    meta: { requiresAuth: true }
  },
  {
    path: '/report-templates',
    name: 'ReportTemplates',
    component: ReportTemplates,
    meta: { requiresAuth: true }
  },
  {
    path: '/reports/:id/edit',
    name: 'ReportEditor',
    component: ReportEditor,
    meta: { requiresAuth: true }
  },
  {
    path: '/admin',
    name: 'AdminPanel',
    component: AdminPanel,
    meta: { requiresAuth: true, requiresSuperAdmin: true }
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const user = localStorage.getItem('user')
  const userObj = user ? JSON.parse(user) : null
  
  // 检查是否需要验证未安装状态
  if (to.meta.requiresNotInstalled) {
    try {
      const response = await request.get('/check-install')
      if (response.installed) {
        // 系统已安装，禁止访问安装页面
        next('/login')
        return
      }
    } catch (error) {
      console.error('Check install error:', error)
    }
  }
  
  // 检查是否需要登录
  if (to.meta.requiresAuth && !user) {
    next('/login')
    return
  }
  
  // 检查是否需要超级管理员权限
  if (to.meta.requiresSuperAdmin && userObj) {
    if (!userObj.is_super_admin) {
      next('/dashboard')
      return
    }
  }
  
  next()
})

export default router
