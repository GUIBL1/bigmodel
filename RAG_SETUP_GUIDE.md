# RAG功能集成指南

本指南将帮助您在现有的Vue+Node.js+MySQL AI对话项目中集成RAG（检索增强生成）功能。

## 1. 系统架构

```
前端 (Vue.js) 
    ↓
后端 (Node.js + Express) 
    ↓
RAG服务 (Python + Flask + LlamaIndex)
    ↓
本地LLM (Ollama) + 向量数据库 (ChromaDB)
```

## 2. 前置要求

### 2.1 环境依赖
- **Python 3.8+**: RAG服务需要
- **Node.js 16+**: 现有项目依赖
- **Ollama**: 本地大语言模型运行环境

### 2.2 安装Ollama
```bash
# Windows
winget install Ollama.Ollama

# MacOS
brew install ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh
```

### 2.3 启动Ollama并拉取模型
```bash
# 启动Ollama服务
ollama serve

# 拉取推荐模型
ollama pull llama3.1
ollama pull qwen2
```

## 3. 安装步骤

### 3.1 安装项目依赖

#### 前端依赖（已完成）
```bash
cd e:\shixi\bigmodel
npm install
```

#### 后端依赖
```bash
cd e:\shixi\bigmodel\server
npm install
```

#### RAG服务依赖
```bash
cd e:\shixi\bigmodel\rag_service

# 建议创建虚拟环境
python -m venv rag_env

# 激活虚拟环境
# Windows
rag_env\Scripts\activate
# Linux/Mac
source rag_env/bin/activate

# 安装Python依赖
pip install -r requirements.txt
```

### 3.2 配置环境变量

编辑 `rag_service\.env` 文件：
```env
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_MODEL=llama3.1
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
VECTOR_STORE_PATH=./vector_store
DOCUMENTS_PATH=./documents
CHUNK_SIZE=1024
CHUNK_OVERLAP=20
TOP_K=5
FLASK_PORT=5001
FLASK_HOST=0.0.0.0
```

## 4. 启动服务

### 4.1 启动顺序
1. **启动Ollama服务**:
   ```bash
   ollama serve
   ```

2. **启动RAG服务**:
   ```bash
   cd e:\shixi\bigmodel\rag_service
   # Windows
   start.bat
   # Linux/Mac
   ./start.sh
   ```

3. **启动后端API服务**:
   ```bash
   cd e:\shixi\bigmodel\server
   npm run dev
   ```

4. **启动前端开发服务器**:
   ```bash
   cd e:\shixi\bigmodel
   npm run dev
   ```

### 4.2 一键启动（推荐）
```bash
cd e:\shixi\bigmodel
npm run start:unified
```

## 5. 功能使用

### 5.1 访问应用
- **对话界面**: http://localhost:5173
- **RAG管理**: http://localhost:5173/rag
- **RAG API**: http://localhost:5001/api

### 5.2 上传知识库文档
1. 访问RAG管理界面
2. 拖拽或点击上传文档
3. 支持格式：PDF、Word、Excel、Markdown、TXT等
4. 文档会自动进行分块和向量化

### 5.3 使用RAG对话
1. 在对话界面开启"RAG模式"开关
2. 输入问题，系统会基于知识库回答
3. 回答会显示参考来源和相似度

### 5.4 管理知识库
- **查看文档**: 查看已上传的文档列表
- **删除文档**: 删除不需要的文档
- **重建索引**: 重新处理所有文档
- **测试查询**: 测试RAG查询效果

## 6. API接口

### 6.1 RAG查询
```javascript
POST /api/rag/query
Content-Type: application/json

{
  "question": "用户问题"
}

// 响应
{
  "success": true,
  "answer": "AI回答",
  "sources": [
    {
      "file_name": "文档名",
      "page_label": "页码",
      "score": 0.85
    }
  ],
  "question": "用户问题"
}
```

### 6.2 文档上传
```javascript
POST /api/rag/upload
Content-Type: multipart/form-data

FormData: {
  "file": 文件对象
}
```

### 6.3 健康检查
```javascript
GET /api/rag/health

// 响应
{
  "success": true,
  "ollama_status": "正常",
  "model_name": "llama3.1",
  "document_count": 5,
  "embedding_model": "sentence-transformers/all-MiniLM-L6-v2"
}
```

## 7. 高级配置

### 7.1 更换模型
编辑 `.env` 文件中的 `DEFAULT_MODEL`：
```env
DEFAULT_MODEL=qwen2
```

### 7.2 调优参数
- **CHUNK_SIZE**: 文档分块大小，影响检索精度
- **TOP_K**: 检索返回的文档片段数量
- **CHUNK_OVERLAP**: 文档分块重叠字符数

### 7.3 自定义嵌入模型
```env
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

## 8. 故障排除

### 8.1 常见问题

**Q: RAG服务无法启动**
A: 检查Python环境和依赖安装：
```bash
python --version
pip list | grep llama-index
```

**Q: Ollama连接失败**
A: 确保Ollama服务正在运行：
```bash
curl http://localhost:11434/api/tags
```

**Q: 文档上传失败**
A: 检查文档格式和大小（最大16MB）

**Q: 查询结果不准确**
A: 
1. 检查知识库文档质量
2. 调整CHUNK_SIZE和TOP_K参数
3. 重建索引

### 8.2 日志查看
- **RAG服务日志**: 在RAG服务启动终端查看
- **后端API日志**: 在Node.js服务终端查看
- **前端错误**: 浏览器开发者工具Console

### 8.3 性能优化
1. **硬件要求**: 建议8GB+内存，支持CUDA的显卡
2. **模型选择**: 根据硬件选择合适大小的模型
3. **文档预处理**: 清理文档格式，提高质量

## 9. 扩展功能

### 9.1 多语言支持
添加多语言嵌入模型：
```env
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

### 9.2 云端部署
- 使用Docker容器化部署
- 配置反向代理
- 添加SSL证书

### 9.3 企业功能
- 用户权限管理
- 文档分类标签
- 查询日志记录
- 性能监控

## 10. 安全注意事项

1. **数据隐私**: 所有数据本地处理，不上传云端
2. **访问控制**: 生产环境需添加身份验证
3. **文件上传**: 限制文件类型和大小
4. **API安全**: 添加请求频率限制

## 结语

通过以上步骤，您已成功在项目中集成了功能完整的RAG系统。该系统支持：

- ✅ 多格式文档上传
- ✅ 智能文档检索
- ✅ 上下文增强回答
- ✅ 来源引用追踪
- ✅ 可视化管理界面
- ✅ 本地部署安全

如有问题，请检查日志或参考故障排除部分。
