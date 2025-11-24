import axios from 'axios'
import { ElMessage } from 'element-plus'

// 根据环境配置 API 地址
const getBaseURL = () => {
  // 优先使用环境变量
  if (process.env.VUE_APP_API_BASE_URL) {
    return process.env.VUE_APP_API_BASE_URL
  }
  // 默认使用 /api（由 Nginx 反向代理到后端）
  return '/api'
}

const service = axios.create({
  baseURL: getBaseURL(),
  timeout: 30000
})

// 请求拦截器
service.interceptors.request.use(
  config => {
    // 添加JWT token到请求头
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  response => {
    const res = response.data
    
    if (res.success === false) {
      ElMessage.error(res.message || '请求失败')
      return Promise.reject(new Error(res.message || '请求失败'))
    }
    
    return res
  },
  error => {
    console.error('Response error:', error)
    
    // 401认证失败，清除token并跳转到登录页
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      ElMessage.error('认证已过期，请重新登录')
      window.location.href = '/login'
      return Promise.reject(error)
    }
    
    ElMessage.error(error.message || '网络错误')
    return Promise.reject(error)
  }
)

export default service
