// 用户状态管理 - 使用Pinia
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  // 用户信息
  const userInfo = ref(null)
  
  // 登录状态
  const isLoggedIn = ref(false)
  
  // 访问token
  const token = ref(localStorage.getItem('token') || '')
  
  // 设置用户信息
  const setUserInfo = (user) => {
    userInfo.value = user
    isLoggedIn.value = true
  }
  
  // 设置token
  const setToken = (newToken) => {
    token.value = newToken
    localStorage.setItem('token', newToken)
  }
  
  // 登出功能
  const logout = () => {
    userInfo.value = null
    isLoggedIn.value = false
    token.value = ''
    localStorage.removeItem('token')
  }
  
  // 初始化用户状态（从本地存储恢复）
  const initUser = () => {
    const savedToken = localStorage.getItem('token')
    if (savedToken) {
      token.value = savedToken
      // 这里可以调用API验证token是否有效
      // 暂时简单处理
      isLoggedIn.value = true
    }
  }
  
  return {
    userInfo,
    isLoggedIn,
    token,
    setUserInfo,
    setToken,
    logout,
    initUser
  }
})
