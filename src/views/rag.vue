<template>
  <div class="rag-container">
    <!-- 顶部导航栏 -->
    <header class="header">
      <div class="header-content">
        <div class="logo">
          <h1>📚 RAG知识库管理</h1>
        </div>
        <div class="user-info">
          <el-button type="primary" @click="$router.push('/index')" size="small">
            🤖 返回对话
          </el-button>
          <el-button type="info" @click="handleLogout" size="small">退出登录</el-button>
        </div>
      </div>
    </header>

    <!-- 主要内容区域 -->
    <main class="main-content">
      <div class="content-wrapper">
        <!-- 系统状态卡片 -->
        <el-card class="status-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>🔍 系统状态</span>
              <el-button type="primary" @click="checkHealth" :loading="statusLoading" size="small">
                刷新状态
              </el-button>
            </div>
          </template>
          <div class="status-grid">
            <div class="status-item">
              <span class="status-label">Ollama状态:</span>
              <el-tag :type="systemStatus.ollama_status === '正常' ? 'success' : 'danger'">
                {{ systemStatus.ollama_status || '未知' }}
              </el-tag>
            </div>
            <div class="status-item">
              <span class="status-label">当前模型:</span>
              <el-tag type="info">{{ systemStatus.model_name || '未配置' }}</el-tag>
            </div>
            <div class="status-item">
              <span class="status-label">已索引文档:</span>
              <el-tag type="warning">{{ systemStatus.document_count || 0 }} 个</el-tag>
            </div>
            <div class="status-item">
              <span class="status-label">嵌入模型:</span>
              <el-tag type="primary">{{ systemStatus.embedding_model || '未配置' }}</el-tag>
            </div>
          </div>
        </el-card>

        <!-- 文档上传卡片 -->
        <el-card class="upload-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>📤 文档上传</span>
            </div>
          </template>
          <el-upload
            ref="uploadRef"
            class="upload-dragger"
            drag
            :action="uploadUrl"
            :before-upload="beforeUpload"
            :on-success="handleUploadSuccess"
            :on-error="handleUploadError"
            :show-file-list="false"
            multiple
          >
            <el-icon class="upload-icon"><upload-filled /></el-icon>
            <div class="upload-text">将文件拖到此处，或<em>点击上传</em></div>
            <div class="upload-hint">
              支持 PDF, Word, Excel, Markdown, TXT 等格式，单个文件最大 16MB
            </div>
          </el-upload>
        </el-card>

        <!-- 文档管理卡片 -->
        <el-card class="documents-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>📋 文档管理</span>
              <div class="header-actions">
                <el-button type="warning" @click="rebuildIndex" :loading="rebuildLoading" size="small">
                  🔄 重建索引
                </el-button>
                <el-button type="primary" @click="loadDocuments" :loading="documentsLoading" size="small">
                  刷新列表
                </el-button>
              </div>
            </div>
          </template>

          <div v-if="documentsLoading" class="loading-container">
            <el-skeleton :rows="5" animated />
          </div>

          <div v-else-if="documents.length === 0" class="empty-container">
            <el-empty description="暂无文档，请先上传文档">
              <el-button type="primary" @click="$refs.uploadRef.$el.click()">
                立即上传
              </el-button>
            </el-empty>
          </div>

          <div v-else class="documents-list">
            <div class="documents-stats">
              <el-tag type="info">总计: {{ documents.length }} 个文档</el-tag>
              <el-tag type="success">已索引: {{ documentsInfo.indexed_count }} 个</el-tag>
            </div>

            <el-table :data="documents" style="width: 100%" stripe>
              <el-table-column prop="filename" label="文件名" min-width="200">
                <template #default="{ row }">
                  <div class="filename-cell">
                    <el-icon class="file-icon">
                      <document />
                    </el-icon>
                    {{ row.filename }}
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="size" label="文件大小" width="120">
                <template #default="{ row }">
                  {{ formatFileSize(row.size) }}
                </template>
              </el-table-column>
              <el-table-column prop="modified_time" label="修改时间" width="180">
                <template #default="{ row }">
                  {{ formatTime(row.modified_time * 1000) }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="100">
                <template #default="{ row }">
                  <el-button 
                    type="danger" 
                    size="small" 
                    @click="deleteDocument(row.filename)"
                    :loading="deletingFiles.includes(row.filename)"
                  >
                    删除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-card>

        <!-- RAG测试卡片 -->
        <el-card class="test-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>🧪 RAG测试</span>
            </div>
          </template>
          <div class="test-section">
            <el-input
              v-model="testQuestion"
              type="textarea"
              :rows="3"
              placeholder="输入测试问题..."
              :disabled="testLoading"
            />
            <div class="test-actions">
              <el-button 
                type="primary" 
                @click="testRAG" 
                :loading="testLoading"
                :disabled="!testQuestion.trim()"
              >
                🔍 测试查询
              </el-button>
              <el-button @click="testQuestion = ''">清空</el-button>
            </div>
          </div>
          
          <div v-if="testResult" class="test-result">
            <h4>测试结果:</h4>
            <div class="result-content">
              <p><strong>问题:</strong> {{ testResult.question }}</p>
              <p><strong>回答:</strong></p>
              <div class="answer-text">{{ testResult.answer }}</div>
              <div v-if="testResult.sources && testResult.sources.length > 0" class="sources">
                <p><strong>引用来源:</strong></p>
                <ul>
                  <li v-for="(source, index) in testResult.sources" :key="index">
                    {{ source.file_name }} (相似度: {{ (source.score * 100).toFixed(2) }}%)
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </el-card>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { UploadFilled, Document } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import axios from 'axios'

const router = useRouter()
const userStore = useUserStore()

// 响应式数据
const systemStatus = ref({})
const statusLoading = ref(false)
const documents = ref([])
const documentsInfo = ref({})
const documentsLoading = ref(false)
const rebuildLoading = ref(false)
const deletingFiles = ref([])
const testQuestion = ref('')
const testResult = ref(null)
const testLoading = ref(false)
const uploadRef = ref()

// 上传URL
const uploadUrl = 'http://localhost:3001/api/rag/upload'

// 检查系统健康状态
const checkHealth = async () => {
  statusLoading.value = true
  try {
    const response = await axios.get('http://localhost:3001/api/rag/health')
    if (response.data.success) {
      systemStatus.value = response.data
      ElMessage.success('系统状态检查完成')
    } else {
      ElMessage.error(response.data.error || '系统状态检查失败')
    }
  } catch (error) {
    console.error('系统状态检查失败:', error)
    ElMessage.error('无法连接到RAG服务，请确保RAG服务已启动')
  } finally {
    statusLoading.value = false
  }
}

// 加载文档列表
const loadDocuments = async () => {
  documentsLoading.value = true
  try {
    const response = await axios.get('http://localhost:3001/api/rag/documents')
    if (response.data.success) {
      documents.value = response.data.documents
      documentsInfo.value = response.data
    } else {
      ElMessage.error(response.data.error || '加载文档列表失败')
    }
  } catch (error) {
    console.error('加载文档列表失败:', error)
    ElMessage.error('无法连接到RAG服务')
  } finally {
    documentsLoading.value = false
  }
}

// 文件上传前检查
const beforeUpload = (file) => {
  const allowedTypes = ['pdf', 'doc', 'docx', 'txt', 'md', 'html', 'xlsx', 'xls', 'csv']
  const fileType = file.name.split('.').pop().toLowerCase()
  
  if (!allowedTypes.includes(fileType)) {
    ElMessage.error(`不支持的文件类型: ${fileType}`)
    return false
  }
  
  const isLt16M = file.size / 1024 / 1024 < 16
  if (!isLt16M) {
    ElMessage.error('文件大小不能超过 16MB!')
    return false
  }
  
  return true
}

// 文件上传成功
const handleUploadSuccess = (response, file) => {
  if (response.success) {
    ElMessage.success(`文件 ${file.name} 上传成功`)
    loadDocuments()
    checkHealth()
  } else {
    ElMessage.error(response.error || '文件上传失败')
  }
}

// 文件上传失败
const handleUploadError = (error, file) => {
  console.error('文件上传失败:', error)
  ElMessage.error(`文件 ${file.name} 上传失败`)
}

// 删除文档
const deleteDocument = async (filename) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除文档 "${filename}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    deletingFiles.value.push(filename)
    
    const response = await axios.delete(`http://localhost:3001/api/rag/documents/${filename}`)
    if (response.data.success) {
      ElMessage.success('文档删除成功')
      loadDocuments()
      checkHealth()
    } else {
      ElMessage.error(response.data.error || '文档删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除文档失败:', error)
      ElMessage.error('删除文档失败')
    }
  } finally {
    deletingFiles.value = deletingFiles.value.filter(f => f !== filename)
  }
}

// 重建索引
const rebuildIndex = async () => {
  try {
    await ElMessageBox.confirm(
      '重建索引将清空现有索引并重新处理所有文档，确定要继续吗？',
      '确认重建索引',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    rebuildLoading.value = true
    
    const response = await axios.post('http://localhost:3001/api/rag/index/rebuild')
    if (response.data.success) {
      ElMessage.success('索引重建成功')
      loadDocuments()
      checkHealth()
    } else {
      ElMessage.error(response.data.error || '索引重建失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('重建索引失败:', error)
      ElMessage.error('重建索引失败')
    }
  } finally {
    rebuildLoading.value = false
  }
}

// 测试RAG
const testRAG = async () => {
  if (!testQuestion.value.trim()) {
    ElMessage.warning('请输入测试问题')
    return
  }
  
  testLoading.value = true
  try {
    const response = await axios.post('http://localhost:3001/api/rag/query', {
      question: testQuestion.value.trim()
    })
    
    if (response.data.success) {
      testResult.value = response.data
      ElMessage.success('RAG测试完成')
    } else {
      ElMessage.error(response.data.error || 'RAG测试失败')
    }
  } catch (error) {
    console.error('RAG测试失败:', error)
    ElMessage.error('RAG测试失败')
  } finally {
    testLoading.value = false
  }
}

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 格式化时间
const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleString()
}

// 退出登录
const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}

// 页面加载时初始化
onMounted(() => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  
  checkHealth()
  loadDocuments()
})
</script>

<style scoped>
/* 主容器样式 */
.rag-container {
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
  max-width: 1400px;
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

/* 主要内容区域 */
.main-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.content-wrapper {
  max-width: 1400px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

/* 卡片样式 */
.el-card {
  border-radius: 15px;
  border: none;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  font-size: 16px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

/* 状态卡片 */
.status-card {
  grid-column: 1 / -1;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: rgba(102, 126, 234, 0.05);
  border-radius: 10px;
  border-left: 4px solid #667eea;
}

.status-label {
  font-weight: 500;
  color: #2c3e50;
}

/* 上传卡片 */
.upload-card {
  grid-column: span 1;
}

.upload-dragger {
  width: 100%;
}

.upload-icon {
  font-size: 67px;
  color: #c0c4cc;
  margin-bottom: 16px;
}

.upload-text {
  color: #606266;
  font-size: 14px;
  margin-bottom: 16px;
}

.upload-hint {
  color: #909399;
  font-size: 12px;
}

/* 文档管理卡片 */
.documents-card {
  grid-column: 1 / -1;
}

.loading-container {
  padding: 20px;
}

.empty-container {
  padding: 40px 20px;
}

.documents-list {
  width: 100%;
}

.documents-stats {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.filename-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.file-icon {
  color: #667eea;
}

/* 测试卡片 */
.test-card {
  grid-column: 1 / -1;
}

.test-section {
  margin-bottom: 20px;
}

.test-actions {
  display: flex;
  gap: 10px;
  margin-top: 15px;
}

.test-result {
  background: rgba(102, 126, 234, 0.05);
  border-radius: 10px;
  padding: 20px;
  border-left: 4px solid #667eea;
}

.test-result h4 {
  margin: 0 0 15px 0;
  color: #2c3e50;
}

.result-content p {
  margin: 10px 0;
  color: #2c3e50;
}

.answer-text {
  background: white;
  padding: 15px;
  border-radius: 8px;
  margin: 10px 0;
  line-height: 1.6;
  white-space: pre-wrap;
}

.sources {
  margin-top: 15px;
}

.sources ul {
  margin: 10px 0;
  padding-left: 20px;
}

.sources li {
  margin: 5px 0;
  color: #666;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .content-wrapper {
    grid-template-columns: 1fr;
  }
  
  .status-grid {
    grid-template-columns: 1fr;
  }
  
  .header-content {
    padding: 15px 20px;
  }
  
  .logo h1 {
    font-size: 20px;
  }
  
  .main-content {
    padding: 15px;
  }
}
</style>
