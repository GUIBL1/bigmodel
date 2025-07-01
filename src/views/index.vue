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
          <el-button type="info" @click="$router.push('/rag')" size="small">
            📚 知识库管理
          </el-button>
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
              <div class="message-avatar user-avatar">
                👨‍💻
              </div>
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
                <div class="message-text" :class="{ 'interrupted-text': message.interrupted }">
                  {{ message.content }}
                  <span v-if="message.interrupted" class="interrupted-label">（已中断）</span>
                </div>
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
                <div class="status-header">
                  <div class="status-text">
                    <span class="status-icon">🔄</span>
                    AI正在响应中...
                  </div>
                  <el-button 
                    text 
                    size="small" 
                    @click="stopAIResponse"
                    class="status-stop-btn"
                  >
                    停止
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 输入区域 -->
        <div class="input-section">
          <div class="input-container">
            <!-- RAG模式切换 -->
            <div class="rag-switch-container">
              <el-switch
                v-model="ragMode"
                size="large"
                active-text="📚 RAG模式"
                inactive-text="💬 普通对话"
                active-color="#667eea"
                inactive-color="#dcdfe6"
              />
              <el-tooltip content="RAG模式使用知识库增强回答准确性" placement="top">
                <el-icon class="info-icon"><info-filled /></el-icon>
              </el-tooltip>
            </div>
            
            <el-input
              v-model="userMessage"
              type="textarea"
              :rows="3"
              :placeholder="ragMode ? '请输入您想查询的问题，我会基于知识库为您回答...' : '请输入您的问题或需求...'"
              class="message-input"
              @keydown.ctrl.enter="sendMessage"
              :disabled="loading"
            />
            <div class="input-actions">
              <div class="input-tips">
                <span v-if="ragMode">🔍 当前为RAG模式，将基于知识库回答</span>
                <span v-else>💡 提示：按 Ctrl + Enter 快速发送</span>
              </div>
              <div class="button-group">
                <!-- 停止按钮 -->
                <el-button 
                  v-if="loading"
                  type="danger" 
                  @click="stopAIResponse"
                  size="large"
                  class="stop-button"
                >
                  <span class="stop-icon">⏹</span>
                  停止回复
                </el-button>
                <!-- 发送按钮 -->
                <el-button 
                  v-else
                  type="primary" 
                  @click="sendMessage"
                  :disabled="!userMessage.trim()"
                  size="large"
                  class="send-button"
                >
                  发送消息
                </el-button>
              </div>
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
import { InfoFilled } from '@element-plus/icons-vue'
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
const ragMode = ref(false) // RAG模式开关

// 中断控制器
let abortController = null
let isStoppedByUser = false // 用户是否主动停止

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

// 中断AI回复功能
const stopAIResponse = () => {
  console.log('用户点击停止按钮')
  
  // 设置用户停止标志
  isStoppedByUser = true
  
  // 立即停止加载状态
  loading.value = false
  
  // 中断网络请求
  if (abortController) {
    console.log('中断网络请求')
    abortController.abort() // 中断网络请求
    abortController = null
  }
  
  // 如果有正在进行的回复，保存到历史记录
  if (currentResponse.thinking || currentResponse.content) {
    console.log('保存被中断的回复到历史记录')
    chatHistory.value.push({
      role: 'assistant',
      content: currentResponse.content || '回复被用户中断',
      thinking: currentResponse.thinking,
      timestamp: Date.now(),
      showThinking: false,
      interrupted: true // 标记为被中断的消息
    })
  }
  
  // 立即清空当前回复状态
  currentResponse.thinking = ''
  currentResponse.content = ''
  
  ElMessage.info('已停止AI回复')
  scrollToBottom()
}

// 发送消息主函数
const sendMessage = async () => {
  // 如果正在加载中，先停止当前请求
  if (loading.value) {
    stopAIResponse()
    return
  }
  
  // 验证输入
  if (!userMessage.value.trim()) {
    ElMessage.warning('请输入消息内容')
    return
  }
  
  // 保存用户输入并清空输入框
  const inputContent = userMessage.value.trim()
  
  // 添加用户消息到历史记录
  const userMsg = {
    role: 'user',
    content: inputContent,
    timestamp: Date.now(),
    isRAG: ragMode.value // 标记是否为RAG模式
  }
  chatHistory.value.push(userMsg)
  
  userMessage.value = ''
  
  // 设置加载状态
  loading.value = true
  isStoppedByUser = false // 重置停止标志
  
  // 创建新的中断控制器
  abortController = new AbortController()
  
  // 清空当前回复状态
  currentResponse.thinking = ''
  currentResponse.content = ''
  
  // 滚动到底部
  scrollToBottom()
  
  try {
    if (ragMode.value) {
      // RAG模式：调用RAG API
      await handleRAGQuery(inputContent)
    } else {
      // 普通模式：调用Ollama API
      await handleNormalChat(inputContent)
    }
  } catch (error) {
    console.error('发送消息失败:', error)
    
    if (!isStoppedByUser) {
      ElMessage.error('发送消息失败，请重试')
      
      // 添加错误消息到历史记录
      chatHistory.value.push({
        role: 'assistant',
        content: '抱歉，我遇到了一些问题，请稍后重试。',
        timestamp: Date.now(),
        error: true
      })
    }
  } finally {
    loading.value = false
    scrollToBottom()
  }
}

// 处理RAG查询
const handleRAGQuery = async (question) => {
  try {
    // 直接调用RAG服务，避免代理超时问题
    const response = await axios.post('http://127.0.0.1:5001/api/query', {
      question: question
    }, {
      signal: abortController.signal,
      timeout: 120000 // 2分钟超时
    })
    
    if (response.data.success) {
      const ragResult = response.data
      
      // 构造AI回复消息
      let replyContent = ragResult.answer
      
      // 如果有引用来源，添加到回复中
      if (ragResult.sources && ragResult.sources.length > 0) {
        replyContent += '\n\n📚 **参考来源：**\n'
        ragResult.sources.forEach((source, index) => {
          replyContent += `${index + 1}. ${source.file_name}`
          if (source.page_label && source.page_label !== '未知') {
            replyContent += ` (第${source.page_label}页)`
          }
          if (source.score) {
            replyContent += ` [相似度: ${(source.score * 100).toFixed(1)}%]`
          }
          replyContent += '\n'
        })
      }
      
      // 添加RAG回复到历史记录
      chatHistory.value.push({
        role: 'assistant',
        content: replyContent,
        timestamp: Date.now(),
        isRAG: true,
        sources: ragResult.sources
      })
    } else {
      throw new Error(response.data.error || 'RAG查询失败')
    }
  } catch (error) {
    if (error.name === 'AbortError') {
      return // 用户取消了请求
    }
    throw error
  }
}

// 处理普通对话
const handleNormalChat = async (inputContent) => {
  // 准备API请求数据 - Ollama格式
  const requestData = {
    "model": "maoniang", // 我部署的模型名称
    "messages": [
      {
        "role": "user", 
        "content": inputContent
      }
    ],
    "stream": true // 启用流式响应
  }
  
  // 调用本地Ollama API
  const response = await fetch('http://localhost:11434/api/chat', {
    method: 'POST',
    headers: { 
      'Content-Type': 'application/json'
      // Ollama通常不需要Authorization header
    },
    body: JSON.stringify(requestData),
    signal: abortController.signal // 添加中断信号
  })
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }
  
  // 处理流式响应
  await processStreamResponse(response)
}

// 处理流式响应数据
const processStreamResponse = async (response) => {
  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  
  let accumulatedThinking = '' // 累积的思考内容
  let accumulatedContent = ''  // 累积的回复内容
  let buffer = '' // 用于处理分片数据
  
  try {
    while (true) {
      // 检查是否被用户停止
      if (isStoppedByUser || abortController?.signal.aborted) {
        console.log('流式处理被用户中断')
        reader.cancel() // 取消流读取
        return
      }
      
      const { done, value } = await reader.read()
      
      if (done) {
        break
      }
      
      // 解码数据并添加到缓冲区
      buffer += decoder.decode(value, { stream: true })
      
      // 按行分割数据
      const lines = buffer.split('\n')
      buffer = lines.pop() || '' // 保留最后一行未完成的数据
      
      for (const line of lines) {
        // 检查是否被用户停止
        if (isStoppedByUser || abortController?.signal.aborted) {
          console.log('流式处理被用户中断（处理行时）')
          reader.cancel()
          return
        }
        
        const trimmedLine = line.trim()
        
        // 跳过空行
        if (!trimmedLine) {
          continue
        }
        
        // 移除 "data: " 前缀（如果存在）
        let jsonStr = trimmedLine
        if (trimmedLine.startsWith('data: ')) {
          jsonStr = trimmedLine.substring(6)
        }
        
        try {
          // 解析JSON数据
          const jsonData = JSON.parse(jsonStr)
          
          // Ollama的响应格式：检查message.content
          if (jsonData.message && jsonData.message.content) {
            const content = jsonData.message.content
            
            // Ollama通常不分思考和回复内容，直接累积所有内容
            accumulatedContent += content
            currentResponse.content = accumulatedContent
            
            // 实时滚动到底部
            scrollToBottom()
            
            // 添加小延迟以创建打字效果
            await new Promise(resolve => setTimeout(resolve, 30))
          }
          
          // 检查是否完成
          if (jsonData.done === true) {
            console.log('Ollama流式响应结束')
            break
          }
          
        } catch (parseError) {
          console.warn('解析JSON失败:', parseError, '原始数据:', jsonStr)
        }
      }
    }
    
    // 将完整的AI回复添加到聊天历史（仅在未被中断时）
    if (!isStoppedByUser && (accumulatedContent || accumulatedThinking)) {
      console.log('保存完整的AI回复到历史记录')
      chatHistory.value.push({
        role: 'assistant',
        content: accumulatedContent || '我正在思考中...',
        thinking: accumulatedThinking,
        timestamp: Date.now(),
        showThinking: false // 默认收起思考过程
      })
    } else if (isStoppedByUser) {
      console.log('因为用户中断，不保存到历史记录（已在stopAIResponse中处理）')
    }
    
  } catch (error) {
    if (error.name === 'AbortError') {
      console.log('流读取被中断')
      return
    }
    throw error
  } finally {
    // 清空当前回复状态
    currentResponse.thinking = ''
    currentResponse.content = ''
    
    // 确保读取器关闭
    try {
      reader.cancel()
    } catch (e) {
      // 忽略取消错误
    }
  }
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
  width: 100%;
}

.message {
  display: flex;
  gap: 5px;
  align-items: flex-start;
}

.message-avatar {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
  box-shadow: 0 3px 12px rgba(0, 0, 0, 0.15);
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.user-avatar {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  font-size: 18px;
}

.ai-avatar {
  background: linear-gradient(135deg, #f093fb, #f5576c);
  color: white;
  font-size: 20px;
}

.message-content {
  flex: 1;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 18px;
  padding: 16px 20px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  position: relative;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

/* 用户消息样式 */
.user-message {
  justify-content: flex-end;
  margin-left: auto;
  display: flex;
  flex-direction: row;
  max-width: 75%;
  width: fit-content;
}

.user-message .message-content {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border-bottom-right-radius: 6px;
  margin-right: 3px;
  position: relative;
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.user-message .message-content::after {
  content: '';
  position: absolute;
  right: -10px;
  top: 15px;
  width: 0;
  height: 0;
  border: 10px solid transparent;
  border-left-color: #667eea;
  border-right: none;
  z-index: 1;
}

/* AI消息样式 */
.ai-message {
  justify-content: flex-start;
  max-width: 75%;
  width: fit-content;
}

.ai-message .message-content {
  border-bottom-left-radius: 6px;
  position: relative;
  margin-left: 3px;
}

.ai-message .message-content::after {
  content: '';
  position: absolute;
  left: -10px;
  top: 15px;
  width: 0;
  height: 0;
  border: 10px solid transparent;
  border-right-color: rgba(255, 255, 255, 0.9);
  border-left: none;
  z-index: 1;
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

/* 中断消息样式 */
.interrupted-text {
  opacity: 0.8;
  border-left: 3px solid #ff6b6b;
  padding-left: 10px;
}

.interrupted-label {
  color: #ff6b6b;
  font-size: 12px;
  font-weight: 500;
  margin-left: 8px;
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

.status-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.status-stop-btn {
  color: #ff6b6b !important;
  font-size: 12px;
  padding: 4px 8px;
  height: auto;
  min-height: auto;
}

.status-stop-btn:hover {
  color: #ff5252 !important;
  background: rgba(255, 107, 107, 0.1) !important;
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

/* RAG切换样式 */
.rag-switch-container {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 15px;
  background: rgba(102, 126, 234, 0.05);
  border-radius: 12px;
  border-left: 4px solid #667eea;
}

.info-icon {
  color: #667eea;
  cursor: pointer;
  font-size: 16px;
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

/* 按钮组样式 */
.button-group {
  display: flex;
  gap: 10px;
}

/* 停止按钮样式 */
.stop-button {
  background: linear-gradient(135deg, #ff6b6b, #ee5a52);
  border: none;
  border-radius: 12px;
  padding: 12px 30px;
  font-weight: 600;
  transition: all 0.3s ease;
  color: white;
}

.stop-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(255, 107, 107, 0.3);
  background: linear-gradient(135deg, #ff5252, #e53935);
}

.stop-icon {
  font-size: 16px;
  margin-right: 5px;
  animation: pulse-stop 1.5s ease-in-out infinite;
}

@keyframes pulse-stop {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
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
  
  .user-message,
  .ai-message {
    max-width: 90%;
  }
  
  .message-avatar {
    width: 36px;
    height: 36px;
    font-size: 16px;
  }
  
  .feature-list {
    grid-template-columns: 1fr;
  }
  
  .input-actions {
    flex-direction: column;
    gap: 10px;
    align-items: stretch;
  }
  
  .button-group {
    flex-direction: column;
    width: 100%;
  }
  
  .send-button,
  .stop-button {
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