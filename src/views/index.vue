<template>
  <div class="main-container">
    <!-- 顶部导航栏 -->
    <header class="header">
      <div class="header-content">
        <div class="logo">
          <h1>🤖 AI智能助手</h1>
        </div>
        <div class="user-info">
          <span class="welcome-text">欢迎，{{ userStore.userInfo?.username || '用户' }}</span>
          <el-button type="primary" @click="handleLogout" size="small">退出登录</el-button>
        </div>
      </div>
    </header>

    <!-- 主要内容区域 -->
    <main class="main-content">
      <!-- 对话历史区域 -->
      <div class="chat-container">
        <div class="chat-history" ref="chatHistoryRef">
          <!-- 欢迎消息 -->
          <div v-if="chatHistory.length === 0" class="welcome-message">
            <div class="welcome-card">
              <h2>👋 欢迎使用AI智能助手</h2>
              <p>我是您的专属AI助手，可以帮您解答问题、提供建议、进行创作等。</p>
            </div>
          </div>
          
          <!-- 聊天消息列表 -->
          <div v-for="(message, index) in chatHistory" :key="index" class="message-item">
            <!-- 用户消息 -->
            <div v-if="message.role === 'user'" class="message user-message">
              <div class="message-content">
                <div class="message-text">{{ message.content }}</div>
                <div class="message-time">{{ formatTime(message.timestamp) }}</div>
              </div>
              <div class="message-avatar user-avatar">👤</div>
            </div>
            
            <!-- AI回复消息 -->
            <div v-else class="message ai-message">
              <div class="message-avatar ai-avatar">🤖</div>
              <div class="message-content">
                <!-- AI思考过程 -->
                <div v-if="message.thinking" class="thinking-process">
                  <div class="thinking-header">
                    <span>🧠 AI思考过程</span>
                    <el-button 
                      text 
                      size="small" 
                      @click="message.showThinking = !message.showThinking"
                    >
                      {{ message.showThinking ? '隐藏' : '展开' }}
                    </el-button>
                  </div>
                  <div v-show="message.showThinking" class="thinking-content">
                    <pre>{{ message.thinking }}</pre>
                  </div>
                </div>
                <!-- AI回复内容 -->
                <div class="message-text">{{ message.content }}</div>
                <div class="message-time">{{ formatTime(message.timestamp) }}</div>
              </div>
            </div>
          </div>
          
          <!-- 当前正在回复的消息 -->
          <div v-if="currentResponse.thinking || currentResponse.content" class="message-item">
            <div class="message ai-message">
              <div class="message-avatar ai-avatar">🤖</div>
              <div class="message-content">
                <!-- 实时思考过程 -->
                <div v-if="currentResponse.thinking" class="thinking-process">
                  <div class="thinking-header">
                    <span>🧠 AI正在思考...</span>
                  </div>
                  <div class="thinking-content">
                    <pre>{{ currentResponse.thinking }}</pre>
                  </div>
                </div>
                <!-- 实时回复内容 -->
                <div v-if="currentResponse.content" class="message-text">
                  {{ currentResponse.content }}
                  <span class="typing-indicator">▌</span>
                </div>
              </div>
            </div>
          </div>
          
          <!-- AI状态显示 -->
          <div v-if="loading && !currentResponse.thinking && !currentResponse.content" class="ai-status">
            <div class="message ai-message">
              <div class="message-avatar ai-avatar">🤖</div>
              <div class="message-content status-content">
                <div class="status-text">
                  <span class="status-icon">🔄</span>
                  AI正在响应中...
                </div>
              </div>
            </div>
          </div>
          
          <!-- AI思考状态显示 -->
          <div v-if="currentResponse.thinking && !currentResponse.content" class="ai-status">
            <div class="message ai-message">
              <div class="message-avatar ai-avatar">🤖</div>
              <div class="message-content status-content">
                <div class="status-text">
                  <span class="status-icon">🧠</span>
                  我正在思考中...
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 输入区域 -->
        <div class="input-section">
          <div class="input-container">
            <el-input
              v-model="userMessage"
              type="textarea"
              :rows="3"
              placeholder="请输入您的问题或需求..."
              class="message-input"
              @keydown.ctrl.enter="sendMessage"
              :disabled="loading"
            />
            <div class="input-actions">
              <div class="input-tips">
                <span>💡 提示：按 Ctrl + Enter 快速发送</span>
              </div>
              <el-button 
                type="primary" 
                @click="sendMessage"
                :loading="loading"
                :disabled="!userMessage.trim()"
                size="large"
                class="send-button"
              >
                {{ loading ? '发送中...' : '发送消息' }}
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>
<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { useUserStore } from '@/stores/user'

// 路由和状态管理
const router = useRouter()
const userStore = useUserStore()

// 响应式数据
const userMessage = ref('') // 用户输入的消息
const loading = ref(false) // 加载状态
const chatHistory = ref([]) // 聊天历史记录
const chatHistoryRef = ref(null) // 聊天历史容器引用

// 当前AI回复状态（用于实时显示）
const currentResponse = reactive({
  thinking: '', // AI思考过程
  content: ''   // AI回复内容
})

// 格式化时间显示
const formatTime = (timestamp) => {
  const date = new Date(timestamp)
  return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
}

// 滚动到聊天底部
const scrollToBottom = () => {
  nextTick(() => {
    if (chatHistoryRef.value) {
      chatHistoryRef.value.scrollTop = chatHistoryRef.value.scrollHeight
    }
  })
}

// 退出登录处理
const handleLogout = () => {
  userStore.logout()
  ElMessage.success('已退出登录')
  router.push('/login')
}

// 发送消息主函数
const sendMessage = async () => {
  // 验证输入
  if (!userMessage.value.trim()) {
    ElMessage.warning('请输入消息内容')
    return
  }
  
  // 添加用户消息到历史记录
  const userMsg = {
    role: 'user',
    content: userMessage.value.trim(),
    timestamp: Date.now()
  }
  chatHistory.value.push(userMsg)
  
  // 保存用户输入并清空输入框
  const inputContent = userMessage.value.trim()
  userMessage.value = ''
  
  // 设置加载状态
  loading.value = true
  
  // 清空当前回复状态
  currentResponse.thinking = ''
  currentResponse.content = ''
  
  // 滚动到底部
  scrollToBottom()
  
  try {
    // 准备API请求数据
    const requestData = {
      "model": "deepseek-ai/DeepSeek-R1-0528-Qwen3-8B", 
      "messages": [
        {
          "role": "user", 
          "content": inputContent
        }
      ],
      "stream": true // 启用流式响应
    }
    
    // 发送请求到AI API
    const response = await axios.request({
      url: 'https://api.siliconflow.cn/v1/chat/completions',
      method: 'post',
      headers: { 
        'Content-Type': 'application/json', 
        'Accept': 'application/json', 
        'Authorization': 'Bearer sk-dhyofqmlqevepadtfbjjmtvelluvgoqixawhgqcyhmiysdtl'
      },
      data: JSON.stringify(requestData)
    })
    
    // 处理流式响应
    await processStreamResponse(response.data)
    
  } catch (error) {
    console.error('发送消息错误:', error)
    ElMessage.error('发送失败，请稍后重试')
    
    // 添加错误消息到聊天历史
    chatHistory.value.push({
      role: 'assistant',
      content: '抱歉，我遇到了一些问题，请稍后再试。',
      timestamp: Date.now(),
      thinking: '',
      showThinking: false
    })
  } finally {
    loading.value = false
    scrollToBottom()
  }
}

// 处理流式响应数据
const processStreamResponse = async (responseData) => {
  // 按双换行符分割响应数据
  const dataChunks = responseData.split('\n\n')
  
  let accumulatedThinking = '' // 累积的思考内容
  let accumulatedContent = ''  // 累积的回复内容
  
  // 逐个处理数据块
  for (let i = 0; i < dataChunks.length; i++) {
    const chunk = dataChunks[i]
    
    // 跳过空白行
    if (chunk === '') {
      continue
    }
    
    // 移除 "data: " 前缀
    const jsonStr = chunk.substring(6)
    
    // 检查是否结束
    if (jsonStr === '[DONE]') {
      break
    }
    
    try {
      // 解析JSON数据
      const jsonData = JSON.parse(jsonStr)
      
      // 模拟延迟以创建打字效果
      await new Promise(resolve => setTimeout(resolve, 50))
      
      // 处理思考内容
      if (jsonData.choices[0].delta.reasoning_content) {
        accumulatedThinking += jsonData.choices[0].delta.reasoning_content
        currentResponse.thinking = accumulatedThinking
      }
      
      // 处理回复内容
      if (jsonData.choices[0].delta.content) {
        accumulatedContent += jsonData.choices[0].delta.content
        currentResponse.content = accumulatedContent
      }
      
      // 实时滚动到底部
      scrollToBottom()
      
    } catch (parseError) {
      console.warn('解析JSON失败:', parseError, '原始数据:', jsonStr)
    }
  }
  
  // 将完整的AI回复添加到聊天历史
  if (accumulatedContent || accumulatedThinking) {
    chatHistory.value.push({
      role: 'assistant',
      content: accumulatedContent || '我正在思考中...',
      thinking: accumulatedThinking,
      timestamp: Date.now(),
      showThinking: false // 默认收起思考过程
    })
  }
  
  // 清空当前回复状态
  currentResponse.thinking = ''
  currentResponse.content = ''
}

// 组件挂载时的初始化
onMounted(() => {
  // 检查用户登录状态
  if (!userStore.isLoggedIn && !userStore.token) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  
  // 初始化用户状态
  userStore.initUser()
})
</script>
<style scoped>
/* 主容器样式 */
.main-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

/* 顶部导航栏 */
.header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  z-index: 100;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 30px;
  max-width: 1200px;
  margin: 0 auto;
}

.logo h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.welcome-text {
  color: #2c3e50;
  font-weight: 500;
}

/* 主要内容区域 */
.main-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
  gap: 20px;
}

/* 聊天历史区域 */
.chat-history {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 20px;
  backdrop-filter: blur(10px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

/* 滚动条样式 */
.chat-history::-webkit-scrollbar {
  width: 6px;
}

.chat-history::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.1);
  border-radius: 3px;
}

.chat-history::-webkit-scrollbar-thumb {
  background: rgba(102, 126, 234, 0.3);
  border-radius: 3px;
}

.chat-history::-webkit-scrollbar-thumb:hover {
  background: rgba(102, 126, 234, 0.5);
}

/* 欢迎消息样式 */
.welcome-message {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  min-height: 300px;
}

.welcome-card {
  text-align: center;
  padding: 40px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 20px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
  max-width: 500px;
}

.welcome-card h2 {
  color: #2c3e50;
  margin-bottom: 15px;
  font-size: 28px;
}

.welcome-card p {
  color: #7f8c8d;
  margin-bottom: 30px;
  font-size: 16px;
  line-height: 1.6;
}

.feature-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

.feature-item {
  padding: 15px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border-radius: 12px;
  font-weight: 500;
  transition: transform 0.3s ease;
}

.feature-item:hover {
  transform: translateY(-3px);
}

/* 消息项样式 */
.message-item {
  margin-bottom: 25px;
}

.message {
  display: flex;
  gap: 15px;
  max-width: 85%;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
}

.user-avatar {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
}

.ai-avatar {
  background: linear-gradient(135deg, #f093fb, #f5576c);
  color: white;
}

.message-content {
  flex: 1;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 18px;
  padding: 15px 20px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  position: relative;
}

/* 用户消息样式 */
.user-message {
  justify-content: flex-end;
}

.user-message .message-content {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
}

/* AI消息样式 */
.ai-message {
  justify-content: flex-start;
}

.message-text {
  line-height: 1.6;
  font-size: 15px;
  word-wrap: break-word;
  white-space: pre-wrap;
}

.message-time {
  font-size: 12px;
  opacity: 0.7;
  margin-top: 8px;
}

/* 思考过程样式 */
.thinking-process {
  margin-bottom: 15px;
  border: 1px solid rgba(102, 126, 234, 0.2);
  border-radius: 12px;
  overflow: hidden;
}

.thinking-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 15px;
  background: rgba(102, 126, 234, 0.1);
  font-weight: 500;
  color: #667eea;
  font-size: 14px;
}

.thinking-content {
  padding: 15px;
  background: rgba(248, 249, 252, 0.8);
  max-height: 200px;
  overflow-y: auto;
}

.thinking-content pre {
  margin: 0;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.4;
  color: #666;
  white-space: pre-wrap;
  word-wrap: break-word;
}

/* 打字指示器 */
.typing-indicator {
  animation: blink 1s infinite;
  color: #667eea;
  font-weight: bold;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

/* AI状态显示样式 */
.ai-status {
  margin-bottom: 25px;
}

.status-content {
  background: rgba(102, 126, 234, 0.1) !important;
  border: 2px solid rgba(102, 126, 234, 0.2);
  animation: pulse-gentle 2s ease-in-out infinite;
}

.status-text {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 15px;
  color: #667eea;
  font-weight: 500;
}

.status-icon {
  font-size: 16px;
  animation: rotate 2s linear infinite;
}

@keyframes pulse-gentle {
  0%, 100% { 
    background: rgba(102, 126, 234, 0.1);
    border-color: rgba(102, 126, 234, 0.2);
  }
  50% { 
    background: rgba(102, 126, 234, 0.15);
    border-color: rgba(102, 126, 234, 0.3);
  }
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 输入区域样式 */
.input-section {
  background: rgba(255, 255, 255, 0.9);
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
}

.input-container {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.message-input {
  border-radius: 15px;
}

.message-input :deep(.el-textarea__inner) {
  border-radius: 15px;
  border: 2px solid #e8ecf4;
  font-size: 15px;
  line-height: 1.6;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.9);
}

.message-input :deep(.el-textarea__inner):focus {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.input-tips {
  color: #7f8c8d;
  font-size: 13px;
}

.send-button {
  background: linear-gradient(135deg, #667eea, #764ba2);
  border: none;
  border-radius: 12px;
  padding: 12px 30px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.send-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
}

.send-button:disabled {
  opacity: 0.6;
  transform: none;
  box-shadow: none;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-content {
    padding: 15px 20px;
  }
  
  .logo h1 {
    font-size: 20px;
  }
  
  .user-info {
    gap: 10px;
  }
  
  .welcome-text {
    display: none;
  }
  
  .chat-container {
    padding: 15px;
    gap: 15px;
  }
  
  .message {
    max-width: 95%;
  }
  
  .feature-list {
    grid-template-columns: 1fr;
  }
  
  .input-actions {
    flex-direction: column;
    gap: 10px;
    align-items: stretch;
  }
  
  .send-button {
    width: 100%;
  }
}

/* 加载动画 */
@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

.loading-pulse {
  animation: pulse 1.5s ease-in-out infinite;
}
</style>