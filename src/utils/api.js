// API请求工具 - 统一管理所有API请求
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

// 创建axios实例
const api = axios.create({
  baseURL: 'http://localhost:3001/api', // 后端API地址
  timeout: 10000, // 请求超时时间
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器 - 自动添加token
api.interceptors.request.use(
  (config) => {
    const userStore = useUserStore()
    if (userStore.token) {
      config.headers.Authorization = `Bearer ${userStore.token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器 - 统一处理错误
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    const userStore = useUserStore()
    
    if (error.response) {
      const { status, data } = error.response
      
      switch (status) {
        case 401:
          // token无效，清除用户信息并跳转登录
          userStore.logout()
          ElMessage.error('登录已过期，请重新登录')
          window.location.href = '/login'
          break
        case 403:
          ElMessage.error('没有权限访问')
          break
        case 500:
          ElMessage.error('服务器错误，请稍后重试')
          break
        default:
          ElMessage.error(data.message || '请求失败')
      }
    } else if (error.request) {
      ElMessage.error('网络连接失败，请检查网络')
    } else {
      ElMessage.error('请求配置错误')
    }
    
    return Promise.reject(error)
  }
)

// 用户相关API
export const userAPI = {
  // 用户注册
  register: (userData) => {
    return api.post('/register', userData)
  },
  
  // 用户登录
  login: (credentials) => {
    return api.post('/login', credentials)
  },
  
  // 获取用户信息
  getProfile: () => {
    return api.get('/profile')
  }
}

export default api
