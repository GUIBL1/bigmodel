<template>
  <div class="login-container">
    <!-- 背景装饰元素 -->
    <div class="bg-decoration">
      <div class="circle circle-1"></div>
      <div class="circle circle-2"></div>
      <div class="circle circle-3"></div>
    </div>
    
    <!-- 主要登录卡片 -->
    <el-card class="login-card" shadow="always">
      <template #header>
        <div class="card-header">
          <h2 class="title">{{ isLoginMode ? '用户登录' : '用户注册' }}</h2>
          <p class="subtitle">{{ isLoginMode ? '欢迎回来！' : '创建您的账户' }}</p>
        </div>
      </template>
      
      <!-- 登录表单 -->
      <el-form
        v-if="isLoginMode"
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        label-position="top"
        @submit.prevent="handleLogin"
        class="auth-form"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名（至少8位）"
            prefix-icon="User"
            size="large"
          />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码（至少6位）"
            prefix-icon="Lock"
            show-password
            size="large"
          />
        </el-form-item>
        <el-form-item>
          <el-button 
            type="primary" 
            native-type="submit" 
            :loading="loading" 
            size="large"
            class="auth-button"
          >
            {{ loading ? '登录中...' : '立即登录' }}
          </el-button>
        </el-form-item>
      </el-form>
      
      <!-- 注册表单 -->
      <el-form
        v-else
        ref="registerFormRef"
        :model="registerForm"
        :rules="registerRules"
        label-position="top"
        @submit.prevent="handleRegister"
        class="auth-form"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="registerForm.username"
            placeholder="请输入用户名（至少8位）"
            prefix-icon="User"
            size="large"
          />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input
            v-model="registerForm.email"
            placeholder="请输入邮箱地址（可选）"
            prefix-icon="Message"
            size="large"
          />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="registerForm.password"
            type="password"
            placeholder="请输入密码（至少6位）"
            prefix-icon="Lock"
            show-password
            size="large"
          />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="registerForm.confirmPassword"
            type="password"
            placeholder="请再次输入密码"
            prefix-icon="Lock"
            show-password
            size="large"
          />
        </el-form-item>
        <el-form-item>
          <el-button 
            type="primary" 
            native-type="submit" 
            :loading="loading" 
            size="large"
            class="auth-button"
          >
            {{ loading ? '注册中...' : '立即注册' }}
          </el-button>
        </el-form-item>
      </el-form>
      
      <!-- 切换登录/注册模式 -->
      <div class="mode-switch">
        <span>{{ isLoginMode ? '还没有账户？' : '已有账户？' }}</span>
        <el-button 
          type="text" 
          @click="toggleMode"
          class="switch-button"
        >
          {{ isLoginMode ? '立即注册' : '立即登录' }}
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, Message } from '@element-plus/icons-vue'
import { userAPI } from '@/utils/api'
import { useUserStore } from '@/stores/user'

// 路由和状态管理
const router = useRouter()
const userStore = useUserStore()

// 表单引用
const loginFormRef = ref(null)
const registerFormRef = ref(null)

// 当前模式（登录/注册）
const isLoginMode = ref(true)

// 加载状态
const loading = ref(false)

// 登录表单数据
const loginForm = reactive({
  username: '',
  password: ''
})

// 注册表单数据
const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

// 登录表单验证规则
const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 8, message: '用户名长度不能少于8位', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ]
}

// 注册表单验证规则
const registerRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 8, message: '用户名长度不能少于8位', trigger: 'blur' },
    { max: 20, message: '用户名长度不能超过20位', trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' },
    { max: 20, message: '密码长度不能超过20位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== registerForm.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 切换登录/注册模式
const toggleMode = () => {
  isLoginMode.value = !isLoginMode.value
  // 清空表单数据
  Object.keys(loginForm).forEach(key => {
    loginForm[key] = ''
  })
  Object.keys(registerForm).forEach(key => {
    registerForm[key] = ''
  })
}

// 登录处理函数
const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        // 调用登录API
        const response = await userAPI.login({
          username: loginForm.username,
          password: loginForm.password
        })
        
        if (response.success) {
          // 保存用户信息和token
          userStore.setToken(response.token)
          userStore.setUserInfo(response.user)
          
          ElMessage.success('登录成功，欢迎回来！')
          
          // 跳转到主页
          setTimeout(() => {
            router.push('/')
          }, 1000)
        } else {
          ElMessage.error(response.message || '登录失败')
        }
      } catch (error) {
        console.error('登录错误:', error)
        ElMessage.error('登录失败，请检查用户名和密码')
      } finally {
        loading.value = false
      }
    }
  })
}

// 注册处理函数
const handleRegister = async () => {
  if (!registerFormRef.value) return
  
  await registerFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        // 调用注册API
        const response = await userAPI.register({
          username: registerForm.username,
          email: registerForm.email || null,
          password: registerForm.password
        })
        
        if (response.success) {
          ElMessage.success('注册成功！请登录您的账户')
          
          // 切换到登录模式并填充用户名
          isLoginMode.value = true
          loginForm.username = registerForm.username
          
          // 清空注册表单
          Object.keys(registerForm).forEach(key => {
            registerForm[key] = ''
          })
        } else {
          ElMessage.error(response.message || '注册失败')
        }
      } catch (error) {
        console.error('注册错误:', error)
        ElMessage.error('注册失败，请稍后重试')
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
/* 登录容器样式 */
.login-container {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  overflow: hidden;
}

/* 背景装饰元素 */
.bg-decoration {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  z-index: 1;
}

.circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  animation: float 6s ease-in-out infinite;
}

.circle-1 {
  width: 200px;
  height: 200px;
  top: 10%;
  left: 10%;
  animation-delay: 0s;
}

.circle-2 {
  width: 150px;
  height: 150px;
  top: 70%;
  right: 10%;
  animation-delay: 2s;
}

.circle-3 {
  width: 100px;
  height: 100px;
  top: 50%;
  left: 80%;
  animation-delay: 4s;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
  }
  50% {
    transform: translateY(-20px) rotate(180deg);
  }
}

/* 登录卡片样式 */
.login-card {
  position: relative;
  z-index: 2;
  width: 450px;
  max-width: 90vw;
  border-radius: 20px;
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 25px 45px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.login-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 35px 55px rgba(0, 0, 0, 0.15);
}

/* 卡片头部样式 */
.card-header {
  text-align: center;
  padding: 20px 0 10px;
}

.title {
  font-size: 28px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 8px 0;
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  font-size: 16px;
  color: #7f8c8d;
  margin: 0;
  font-weight: 400;
}

/* 表单样式 */
.auth-form {
  padding: 20px 0;
}

.auth-form .el-form-item {
  margin-bottom: 24px;
}

.auth-form .el-form-item__label {
  font-weight: 500;
  color: #2c3e50;
  font-size: 15px;
  margin-bottom: 8px;
}

.auth-form .el-input__wrapper {
  border-radius: 12px;
  border: 2px solid #e8ecf4;
  transition: all 0.3s ease;
  background: #f8f9fc;
}

.auth-form .el-input__wrapper:hover {
  border-color: #667eea;
  background: #ffffff;
}

.auth-form .el-input__wrapper.is-focus {
  border-color: #667eea;
  background: #ffffff;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

/* 按钮样式 */
.auth-button {
  width: 100%;
  height: 50px;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border: none;
  transition: all 0.3s ease;
  margin-top: 10px;
}

.auth-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 15px 25px rgba(102, 126, 234, 0.3);
}

.auth-button:active {
  transform: translateY(0);
}

/* 模式切换样式 */
.mode-switch {
  text-align: center;
  padding: 20px 0 10px;
  border-top: 1px solid #e8ecf4;
  margin-top: 10px;
}

.mode-switch span {
  color: #7f8c8d;
  font-size: 14px;
  margin-right: 8px;
}

.switch-button {
  color: #667eea !important;
  font-weight: 600;
  font-size: 14px;
  padding: 0;
  height: auto;
}

.switch-button:hover {
  color: #764ba2 !important;
  text-decoration: underline;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .login-card {
    margin: 20px;
    width: calc(100vw - 40px);
  }
  
  .title {
    font-size: 24px;
  }
  
  .circle {
    display: none;
  }
}

/* Element Plus 深度样式覆盖 */
:deep(.el-card__header) {
  padding: 0;
  border-bottom: none;
}

:deep(.el-card__body) {
  padding: 30px;
}
</style>
