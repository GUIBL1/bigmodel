# 🤖 BigModel AI智能助手

一个功能丰富的本地AI智能助手平台，基于Vue 3 + Node.js + Python + MySQL构建，集成了用户管理、AI对话和RAG知识库问答等完整功能。

## ✨ 项目亮点

- 🧠 **本地化部署**: 完全离线运行，数据隐私安全可控
- 🔄 **多模式对话**: 支持普通AI对话和RAG增强问答模式  
- 📚 **智能知识库**: 上传文档即可构建专属知识库
- 🎨 **现代化界面**: Vue 3 + Element Plus打造的优美用户体验
- 🔐 **安全认证**: JWT token + bcrypt密码加密

## 🚀 核心功能

### 🔐 用户认证系统
- 用户注册/登录，支持JWT令牌认证
- 密码bcrypt加密存储，安全性保障
- 自动登录状态保持，无缝用户体验

### 💬 AI智能对话
- 集成Ollama本地大语言模型
- 支持流式响应和实时对话
- 可中断AI回复，用户体验友好
- 对话历史记录，上下文连续

### 📚 RAG知识库问答
- 支持PDF、Word、Excel、Markdown、TXT等多格式文档
- ChromaDB向量数据库，高效语义检索
- 智能文档分块，上下文增强回答
- 来源追踪，显示参考文档和相似度评分
- 索引管理，支持重建、清空等维护操作

### 🎨 用户界面
- Vue 3 Composition API + Element Plus组件库
- 响应式设计，支持桌面和移动端
- 现代化UI设计，渐变背景和毛玻璃效果
- 模式切换指示，操作直观友好

## 🛠️ 技术架构

### 前端技术栈
```
Vue 3 (Composition API)    # 现代前端框架
├── Vue Router 4           # 路由管理
├── Pinia                  # 状态管理
├── Element Plus           # UI组件库
├── Axios                  # HTTP请求
└── Vite                   # 构建工具
```

### 后端技术栈
```
Node.js + Express          # Web服务器
├── MySQL2                 # 数据库驱动
├── JWT + bcrypt           # 身份认证和密码加密
├── CORS                   # 跨域支持
└── http-proxy-middleware  # RAG服务代理
```

### RAG服务技术栈
```
Python + Flask             # RAG API服务
├── LlamaIndex            # RAG框架
├── ChromaDB              # 向量数据库
├── Sentence Transformers # 文本嵌入
├── Ollama                # 本地大语言模型
└── PyPDF2 + python-docx  # 文档解析
```

## 📁 项目结构

```
bigmodel/
├── 📄 package.json              # 项目依赖和脚本配置
├── 📄 package-lock.json         # 依赖版本锁定
├── 📄 vite.config.js            # Vite构建配置
├── 📄 index.html                # 应用入口页面
├── 📄 jsconfig.json             # JavaScript配置
├── 📄 .gitignore                # Git忽略文件配置
├── 📚 README.md                 # 项目说明文档
│
├── 📁 src/                      # 前端源代码
│   ├── 📄 App.vue               # 根组件
│   ├── 📄 main.js               # 应用入口文件
│   ├── 📁 views/                # 页面组件
│   │   ├── login.vue            # 登录/注册页面
│   │   ├── index.vue            # AI对话主界面
│   │   └── rag.vue              # RAG知识库管理页面
│   ├── 📁 router/               # 路由配置
│   │   └── index.js             # 路由定义和导航守卫
│   ├── 📁 stores/               # 状态管理
│   │   └── user.js              # 用户状态管理(Pinia)
│   └── 📁 utils/                # 工具函数
│       └── api.js               # 统一API请求封装
│
├── 📁 server/                   # 后端API服务
│   ├── 📄 package.json          # 服务器依赖配置
│   ├── 📄 package-lock.json     # 服务器依赖锁定
│   └── 📄 app.js                # Express服务器主文件
│                                # - 用户认证API (注册/登录)
│                                # - 数据库初始化和连接
│                                # - RAG服务代理中间件
│                                # - JWT令牌验证中间件
│
└── 📁 rag_service/              # RAG知识库服务
    ├── 📄 app.py                # Flask RAG API服务主文件
    ├── 📄 rag_core.py           # RAG核心功能实现
    ├── 📄 requirements.txt      # Python依赖包列表
    ├── 📄 ENVIRONMENT_SETUP.md  # RAG环境安装详细指南
    ├── 📁 documents/            # 知识库文档存储目录
    ├── 📁 vector_store/         # ChromaDB向量数据库文件
    └── 📁 embeddings_cache/     # Sentence Transformers缓存
```

## 🌐 服务架构

```
用户浏览器 (http://localhost:5173)
    ↓
前端Vue应用 (Vite开发服务器)
    ↓
后端Express服务器 (http://localhost:3001)
    ├── 用户认证API (/api/login, /api/register)
    ├── MySQL数据库连接 (用户数据存储)
    └── RAG服务代理 (/api/rag/* → http://localhost:5001)
            ↓
RAG Flask服务 (http://localhost:5001)
    ├── 文档管理API (/api/upload, /api/documents)
    ├── 查询API (/api/query)
    ├── ChromaDB向量数据库
    └── Ollama模型服务 (http://localhost:11434)
```

## 📋 环境要求

### 系统要求
- **操作系统**: Windows 10/11, macOS 10.15+, Ubuntu 18.04+
- **内存**: 最少4GB RAM (推荐8GB+，RAG服务占用较多内存)
- **存储**: 至少5GB可用空间 (模型和依赖包)
- **网络**: 安装阶段需要网络下载依赖

### 软件环境
- **Node.js**: >= 16.0.0 (推荐18.x LTS版本)
- **Python**: >= 3.8 (推荐3.10或3.11)
- **MySQL**: >= 5.7 (推荐8.0)
- **包管理器**: npm或yarn

## 🚀 快速启动

#### 步骤1：前端环境
```bash
# 安装前端依赖
npm install

# 启动前端开发服务器
npm run dev
```

#### 步骤2：数据库配置
```bash
# 启动MySQL服务
# Windows: net start mysql
# Linux: sudo systemctl start mysql
# macOS: brew services start mysql

# 登录MySQL(可选，系统会自动创建)
mysql -u root -p
```

#### 步骤3：后端服务
```bash
# 修改数据库配置 (server/app.js)
# 根据实际情况修改数据库密码
cd server
# 启动后端服务
npm run app.js
```

#### 步骤4：RAG环境配置
```bash
cd rag_service

# 安装Python依赖
pip install -r requirements.txt
```

#### 步骤5：启动Ollama
```bash
# 启动Ollama服务
ollama serve

# 启动本地模型
ollama pull maoniang:latest

# 验证模型
ollama list
```

#### 步骤6：启动RAG服务
```bash
# 在rag_service目录下
python app.py
```

## 📊 访问地址

启动成功后，通过以下地址访问：

- **🖥️ 主应用**: http://localhost:5173
- **📚 RAG管理**: http://localhost:5173/rag  
- **🔌 后端API**: http://localhost:3001
- **🤖 RAG API**: http://localhost:5001
- **📋 API健康检查**: http://localhost:5001/api/health

## 📋 可用脚本

### 前端脚本
```bash
npm run dev          # 启动前端开发服务器
npm run build        # 构建生产版本
npm run preview      # 预览生产版本
```

### 后端脚本  
```bash
npm run server       # 启动后端服务器
npm run server:dev   # 启动后端开发模式(自动重启)
```

### 统一脚本
```bash
npm run start:unified # 同时启动前后端服务(推荐)
npm run install:all   # 安装所有依赖(前端+后端)
```

## 🎯 使用指南

### 1. 首次使用
1. 访问 http://localhost:5173
2. 点击"立即注册"创建账户
3. 登录系统进入主界面

### 2. AI对话
1. 在主界面输入问题
2. 点击发送或按Ctrl+Enter
3. 观看AI实时回复
4. 支持多轮连续对话

### 3. RAG知识库
1. 访问RAG管理页面 (右上角菜单)
2. 上传PDF、Word、Excel等文档
3. 等待文档处理完成
4. 返回主界面，开启"RAG模式"
5. 基于知识库内容进行问答

### 4. 模式切换
- **普通模式**: 使用Ollama模型直接对话
- **RAG模式**: 基于上传的文档知识库回答

## 🛠️ 配置说明

### 数据库配置
修改 `server/app.js` 中的数据库连接信息：
```javascript
const dbConfig = {
  host: 'localhost',
  user: 'root',
  password: '123123',    // 修改为你的MySQL密码
  database: 'ai'
};
```

### RAG服务配置
创建 `rag_service/.env` 文件：
```env
# Ollama配置
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_MODEL=qwen2:latest

# RAG参数调优
CHUNK_SIZE=1024         # 文档分块大小
CHUNK_OVERLAP=20        # 分块重叠度
TOP_K=5                 # 检索文档数量

# 服务配置
FLASK_PORT=5001
FLASK_HOST=0.0.0.0
```

### 前端配置
修改 `vite.config.js` 中的服务器配置：
```javascript
export default defineConfig({
  server: {
    host: '0.0.0.0',
    port: 5173      // 可修改端口
  }
})
```

## 🐛 故障排除

### 常见问题

#### 1. 端口冲突
```bash
# 检查端口占用
netstat -ano | findstr :5173  # Windows
lsof -i :5173                 # Linux/Mac

# 修改端口配置
# vite.config.js 中修改前端端口
# server/app.js 中修改后端端口
```

#### 2. MySQL连接失败
```bash
# 检查MySQL服务状态
net start mysql               # Windows启动
sudo systemctl start mysql   # Linux启动
brew services start mysql    # macOS启动

# 检查密码和配置
mysql -u root -p
```

#### 3. RAG服务无法启动
```bash
# 检查Python环境
python --version
pip list | grep llama-index

# 重新安装依赖
pip install -r requirements.txt

# 检查Ollama服务
curl http://localhost:11434/api/tags
```

#### 4. 文档上传失败
- 检查文件格式(支持PDF、Word、Excel、Markdown、TXT)
- 检查文件大小(最大16MB)
- 确保RAG服务正常运行

### 性能优化

#### 硬件优化
- **内存**: 8GB+内存提升RAG性能
- **存储**: SSD硬盘加速向量检索
- **显卡**: NVIDIA显卡可启用GPU加速

#### 配置优化
```env
# 调整RAG参数
CHUNK_SIZE=512          # 较小分块，提高精度
TOP_K=3                 # 较少检索，提高速度

# 使用轻量级模型
DEFAULT_MODEL=qwen2:1.5b  # 更快的响应速度
```

## 🔒 安全说明

1. **数据隐私**: 所有数据本地处理，不上传云端
2. **密码安全**: bcrypt加密，安全强度高
3. **访问控制**: JWT令牌验证，防止未授权访问
4. **文件安全**: 限制上传文件类型和大小
5. **网络安全**: 本地部署，减少网络攻击风险

## 🚀 扩展功能

### 模型扩展
- 支持更多Ollama模型(Claude、GPT、Llama等)
- 自定义模型参数和提示词
- 多模型切换和比较

### 功能扩展
- 多用户权限管理
- 文档分类和标签
- 对话历史持久化
- API接口开放
- Docker容器化部署

## 📄 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📞 技术支持

- **项目Issues**: 在GitHub仓库提交问题
- **Ollama文档**: https://ollama.ai/docs
- **LlamaIndex文档**: https://docs.llamaindex.ai
- **Vue.js文档**: https://vuejs.org
- **Element Plus文档**: https://element-plus.org

---

✨ **感谢使用BigModel AI智能助手！希望这个项目能为您的AI应用开发提供参考和帮助。**

🌟 **如果觉得项目有用，请给个Star支持一下！**
