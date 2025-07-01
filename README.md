# 🤖 AI智能助手项目

一个基于Vue 3 + Node.js + MySQL的智能聊天应用，支持用户注册登录、AI对话和RAG知识库问答功能。

## 🚀 功能特性

- 🔐 **用户认证**: 完整的注册/登录系统，支持JWT token认证
- 💬 **智能对话**: 集成AI聊天API，支持流式响应和思考过程展示
- 📚 **RAG知识库**: 文档上传、智能检索、上下文增强问答
- 🎨 **精美界面**: 现代化UI设计## 💡 功能说明

### 🔐 用户认证系统
- **注册功能**：创建新用户账户，密码自动加密存储
- **登录功能**：验证用户身份，生成JWT token
- **自动登录**：保存登录状态，刷新页面不丢失
- **登出功能**：清除用户信息和token

### 💬 AI对话系统
- **实时对话**：支持与AI进行自然语言对话
- **流式输出**：实时显示AI的回复过程
- **思考展示**：可查看AI的思考过程
- **中断控制**：支持随时中断AI回复
- **对话历史**：保存当前会话的聊天记录
- **模式切换**：支持普通对话和RAG增强模式切换

### 📚 RAG知识库系统
- **文档上传**：支持PDF、Word、Excel、Markdown、TXT等多种格式
- **智能分块**：自动将文档分解为适合检索的文本块
- **向量化存储**：使用ChromaDB进行高效的语义检索
- **上下文增强**：基于检索到的相关内容生成更准确的回答
- **来源追踪**：每个回答都显示参考文档和相似度评分
- **索引管理**：支持重建索引、清空索引等维护操作
- **实时监控**：显示系统状态、文档数量、模型信息等

### 🎨 界面特性
- **现代设计**：采用渐变背景和毛玻璃效果
- **响应式布局**：适配桌面和移动设备
- **动画效果**：流畅的交互动画
- **用户友好**：直观的操作界面，清晰的模式指示 **数据安全**: 完全本地部署，密码加密存储，安全的用户会话管理
- 📱 **移动友好**: 支持移动端设备访问
- ⚡ **中断控制**: 支持实时中断AI回复
- 🎯 **统一依赖**: 前后端可共享node_modules

## 🛠️ 技术栈

### 前端
- Vue 3 (Composition API)
- Vue Router 4 (路由管理)
- Pinia (状态管理)
- Element Plus (UI组件库)
- Axios (HTTP请求)
- Vite (构建工具)

### 后端
- Node.js + Express (Web框架)
- MySQL (数据库)
- JWT (身份认证)
- bcrypt (密码加密)
- CORS (跨域支持)

### RAG服务
- Python + Flask (RAG API服务)
- LlamaIndex (RAG框架)
- ChromaDB (向量数据库)
- Sentence Transformers (文本嵌入)
- Ollama (本地大语言模型)

## 📦 项目结构

```
bigmodel/
├── 📄 package.json          # 统一的项目依赖配置
├── 📄 vite.config.js        # Vite构建配置
├── 📄 index.html            # 入口HTML文件
├── 📚 README.md             # 项目说明文档
├── � start_all.bat         # 一键启动脚本(Windows)
├── 📄 start_all.sh          # 一键启动脚本(Linux/Mac)
├── �📁 src/                  # 前端源代码
│   ├── App.vue              # 根组件
│   ├── main.js              # 入口文件
│   ├── 📁 views/            # 页面组件
│   │   ├── login.vue        # 登录/注册页面
│   │   ├── index.vue        # AI对话主界面(含RAG模式)
│   │   └── rag.vue          # RAG知识库管理页面
│   ├── 📁 router/           # 路由配置
│   │   └── index.js         # 路由定义
│   ├── 📁 stores/           # 状态管理
│   │   └── user.js          # 用户状态管理
│   └── 📁 utils/            # 工具函数
│       └── api.js           # API请求封装
├── 📁 server/               # 后端源代码
│   ├── package.json         # 服务器模块配置
│   └── app.js               # Express服务器(含RAG代理)
└── 📁 rag_service/          # RAG服务(新增)
    ├── app.py               # Flask RAG API服务
    ├── rag_core.py          # RAG核心功能
    ├── requirements.txt     # Python依赖
    ├── ENVIRONMENT_SETUP.md # 环境安装指南
    ├── quick_setup.bat      # 快速设置脚本
    ├── start.bat/start.sh   # RAG服务启动脚本
    ├── test_rag.py          # RAG功能测试
    ├── 📁 documents/        # 知识库文档存储
    ├── 📁 vector_store/     # 向量数据库文件
    └── 📁 embeddings_cache/ # 嵌入模型缓存
│        └── api.js           # API请求封装
└── 📁 server/               # 后端源代码
    ├── package.json         # 服务器模块配置（使用根目录依赖）
    └── app.js               # Express服务器（CommonJS）
```

## 🚀 快速启动指南

### 1. 环境要求
- **Node.js >= 16.0.0**: 前后端服务
- **Python >= 3.8**: RAG服务
- **MySQL >= 5.7**: 数据库
- **npm 或 yarn**: 包管理器

### 2. 克隆项目
```bash
git clone https://github.com/GUIBL1/bigmodel.git
cd bigmodel
```

### 3. 快速启动（推荐）

#### 方式一：一键启动所有服务
```bash
# Windows
start_all.bat

# Linux/Mac  
./start_all.sh
```

#### 方式二：分步启动
```bash
# 1. 安装前端依赖
npm install

# 2. 安装RAG服务依赖
cd rag_service
quick_setup.bat  # Windows快速设置
# 或手动设置：
python -m venv rag_env
rag_env\Scripts\activate  # Windows
pip install -r requirements.txt

# 3. 启动Ollama服务
ollama serve

# 4. 拉取AI模型
ollama pull qwen2:latest

# 5. 启动所有服务
cd ..
npm run start:unified
```

### 4. 访问应用
- **主对话界面**: http://localhost:5173
- **RAG知识库管理**: http://localhost:5173/rag
- **后端API**: http://localhost:3001
- **RAG API**: http://localhost:5001

## 🗄️ 数据库配置

### MySQL 数据库安装与配置

#### 1. 安装 MySQL
请根据您的操作系统下载并安装 MySQL：
- Windows: https://dev.mysql.com/downloads/mysql/
- macOS: 可使用 Homebrew `brew install mysql`
- Linux: `sudo apt-get install mysql-server` (Ubuntu/Debian)

#### 2. 启动 MySQL 服务
```bash
# Windows (以管理员身份运行命令提示符)
net start mysql

# macOS
brew services start mysql

# Linux
sudo systemctl start mysql
```

#### 3. 登录 MySQL
```bash
mysql -u root -p
```

#### 4. 创建数据库和用户（可选）
```sql
-- 创建专用数据库用户（推荐）
CREATE USER 'aiuser'@'localhost' IDENTIFIED BY 'aipassword123';
GRANT ALL PRIVILEGES ON ai.* TO 'aiuser'@'localhost';
FLUSH PRIVILEGES;

-- 或直接使用 root 用户（简单但不推荐生产环境）
```

#### 5. 修改后端配置
在 `server/app.js` 文件中修改数据库连接配置：

```javascript
const dbConfig = {
  host: 'localhost',
  user: 'root',          // 或您创建的用户名
  password: '123456',    // 修改为您的MySQL密码
  database: 'ai'
};
```

#### 6. 自动创建数据库和表
当您首次运行后端服务器时，会自动：
- 创建 `ai` 数据库
- 创建 `users` 用户表

### 数据库表结构

#### users 表
```sql
CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL COMMENT '用户名，唯一',
  password VARCHAR(255) NOT NULL COMMENT '加密后的密码',
  email VARCHAR(100) COMMENT '邮箱地址',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) COMMENT '用户信息表';
```

## 🎯 使用流程

### 基础功能
1. **首次访问**：自动跳转到登录页面
2. **注册账户**：点击"立即注册"创建新账户
   - 用户名：至少8位字符
   - 密码：至少6位字符
   - 邮箱：可选，需要正确格式
3. **登录系统**：使用注册的账户登录
4. **开始聊天**：在主页面与AI助手对话
   - 发送消息：输入问题并点击发送或按Ctrl+Enter
   - 查看回复：观察AI的思考过程和最终回答
   - 中断回复：点击"停止"按钮可随时中断AI回复
   - 多轮对话：支持连续对话

### RAG知识库功能
5. **管理知识库**：访问RAG管理页面 (http://localhost:5173/rag)
   - **上传文档**：支持PDF、Word、Excel、Markdown、TXT等格式
   - **查看文档**：浏览已上传的文档列表和索引状态
   - **删除文档**：移除不需要的文档
   - **重建索引**：重新处理所有文档的向量化
   - **测试查询**：验证RAG查询效果

6. **使用RAG对话**：在主对话界面
   - **开启RAG模式**：切换右上角的"RAG模式"开关
   - **智能问答**：基于知识库内容回答问题
   - **查看来源**：每个回答都会显示参考文档和相似度评分
   - **模式切换**：随时在RAG模式和普通对话模式间切换

## � 功能说明

### 🔐 用户认证系统
- **注册功能**：创建新用户账户，密码自动加密存储
- **登录功能**：验证用户身份，生成JWT token
- **自动登录**：保存登录状态，刷新页面不丢失
- **登出功能**：清除用户信息和token

### 💬 AI对话系统
- **实时对话**：支持与AI进行自然语言对话
- **流式输出**：实时显示AI的回复过程
- **思考展示**：可查看AI的思考过程
- **中断控制**：支持随时中断AI回复
- **对话历史**：保存当前会话的聊天记录

### 🎨 界面特性
- **现代设计**：采用渐变背景和毛玻璃效果
- **响应式布局**：适配桌面和移动设备
- **动画效果**：流畅的交互动画
- **用户友好**：直观的操作界面

## 🔧 配置说明

### 🤖 AI模型配置

本项目已配置为使用本地Ollama部署的AI模型。确保您已经：

#### 1. 安装Ollama
```bash
# Windows
# 前往 https://ollama.ai 下载并安装

# 验证安装
ollama --version
```

#### 2. 下载模型
```bash
# 下载maoniang模型（或其他您喜欢的模型）
ollama pull maoniang

# 查看已安装的模型
ollama list
```

#### 3. 启动Ollama服务
```bash
# 启动Ollama服务（默认端口11434）
ollama serve
```

#### 4. 配置模型名称
在 `src/views/index.vue` 中修改模型名称：

```javascript
const requestData = {
  "model": "maoniang", // 修改为您安装的模型名称
  "messages": [...],
  "stream": true
}

const response = await fetch('http://localhost:11434/api/chat', {
  method: 'POST',
  headers: { 
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(requestData)
})
```

#### 支持的其他模型
- `qwen:7b` - 通义千问7B
- `llama2:7b` - Llama 2 7B  
- `codellama:7b` - Code Llama 7B
- `mistral:7b` - Mistral 7B

使用命令 `ollama pull <model_name>` 下载后，修改代码中的model字段即可。

## 🔒 安全特性

- 密码使用bcrypt加密存储
- JWT token有效期24小时
- 前端路由守卫保护私有页面
- API请求自动携带认证token
- CORS配置防止恶意跨域请求
- AI回复支持实时中断控制

## 📋 可用脚本

### 前端脚本
```bash
# 开发模式启动前端
npm run dev

# 构建生产版本
npm run build

# 预览生产版本
npm run preview
```

### 后端脚本
```bash
# 启动后端服务
npm run server

# 开发模式启动后端
npm run server:dev
```

### 统一启动脚本
```bash
# 同时启动前后端（推荐）
npm run start:unified

# 一键启动所有服务（包括RAG）
start_all.bat      # Windows
./start_all.sh     # Linux/Mac
```

### RAG服务脚本
```bash
# 进入RAG服务目录
cd rag_service

# 快速环境设置
quick_setup.bat    # Windows快速设置向导

# 安装RAG依赖
install_deps.bat   # Windows
./install_deps.sh  # Linux/Mac

# 启动RAG服务
start.bat          # Windows
./start.sh         # Linux/Mac

# 测试RAG功能
python test_rag.py
python test_fix.py
```

### 其他脚本
```bash
# 安装所有依赖（分离模式）
npm run install:all
```

## 📚 RAG知识库配置

### 🔧 Ollama安装与配置

#### 1. 安装Ollama
```bash
# Windows
winget install Ollama.Ollama
# 或访问 https://ollama.ai/download 下载安装

# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh
```

#### 2. 启动Ollama服务
```bash
# 启动Ollama服务（默认端口11434）
ollama serve
```

#### 3. 拉取推荐模型
```bash
# 中文友好模型
ollama pull qwen2:latest
ollama pull qwen2:7b

# 英文强力模型  
ollama pull llama3.1:latest
ollama pull mistral:latest

# 轻量级模型
ollama pull gemma2:2b

# 查看已安装模型
ollama list
```

#### 4. 验证Ollama
```bash
# 测试连接
curl http://localhost:11434/api/tags

# 测试对话
ollama run qwen2:latest "你好，请介绍一下自己"
```

### 🐍 RAG服务配置

#### 1. Python环境设置
```bash
cd rag_service

# 创建虚拟环境（推荐）
python -m venv rag_env

# 激活虚拟环境
# Windows:
rag_env\Scripts\activate
# Linux/Mac:
source rag_env/bin/activate
```

#### 2. 安装依赖
```bash
# 快速安装（推荐）
quick_setup.bat  # Windows

# 或手动安装
pip install -r requirements.txt
```

#### 3. 环境变量配置
创建 `rag_service/.env` 文件：
```env
# Ollama配置
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_MODEL=qwen2:latest

# RAG参数
CHUNK_SIZE=1024
CHUNK_OVERLAP=20
TOP_K=5

# 服务配置
FLASK_PORT=5001
FLASK_HOST=0.0.0.0

# 路径配置
DOCUMENTS_PATH=./documents
VECTOR_STORE_PATH=./vector_store
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

#### 4. 启动RAG服务
```bash
# Windows
start.bat

# Linux/Mac
./start.sh

# 或直接启动
python app.py
```

#### 5. 验证RAG服务
```bash
# 健康检查
curl http://localhost:5001/api/health

# 测试RAG查询
python test_rag.py
```

## 🛠️ 故障排除

### 常见问题

#### RAG服务问题
**Q: RAG服务无法启动**
```bash
# 检查Python环境
python --version
pip list | grep llama-index

# 重新安装依赖
pip install -r requirements.txt
```

**Q: Ollama连接失败**
```bash
# 检查Ollama状态
curl http://localhost:11434/api/tags

# 重启Ollama服务
ollama serve
```

**Q: 文档上传失败**
- 检查文档格式（支持PDF、Word、Excel、Markdown、TXT等）
- 检查文件大小（最大16MB）
- 确保RAG服务正在运行

**Q: 查询结果不准确**
1. 检查知识库文档质量
2. 调整CHUNK_SIZE和TOP_K参数
3. 重建索引：访问RAG管理页面点击"重建索引"

#### 数据库问题
**Q: MySQL连接失败**
```bash
# 检查MySQL服务状态
# Windows
net start mysql
# Linux
sudo systemctl status mysql
```

**Q: 数据库权限错误**
- 检查`server/app.js`中的数据库配置
- 确保用户名和密码正确
- 确保用户有数据库操作权限

#### 前端问题
**Q: 页面无法访问**
```bash
# 检查端口是否被占用
netstat -ano | findstr :5173  # Windows
lsof -i :5173                 # Linux/Mac

# 重新启动开发服务器
npm run dev
```

### 性能优化

#### 硬件建议
- **内存**: 8GB+ (RAG服务占用较多内存)
- **存储**: SSD硬盘提升向量检索速度
- **显卡**: 支持CUDA的显卡可加速嵌入计算

#### 配置优化
```env
# 调整分块大小（影响检索精度）
CHUNK_SIZE=512    # 更小的分块，精度更高但速度慢
CHUNK_SIZE=2048   # 更大的分块，速度快但精度可能降低

# 调整检索数量（影响回答质量）
TOP_K=3          # 返回更少相关文档，速度快
TOP_K=10         # 返回更多相关文档，回答更全面

# 使用轻量级模型
DEFAULT_MODEL=qwen2:1.5b  # 更小的模型，速度更快
```

## 🚀 扩展功能

### 🌟 企业级功能
- **多用户支持**: 用户权限管理和文档隔离
- **审计日志**: 查询历史和操作记录
- **数据备份**: 自动备份知识库和配置
- **监控告警**: 系统状态监控和异常告警

### 🔧 技术扩展
- **多语言支持**: 添加更多语言的嵌入模型
- **文档分类**: 支持文档标签和分类管理
- **高级搜索**: 关键词过滤、时间范围搜索
- **API扩展**: 提供更多RESTful API接口

### 🌐 部署扩展
- **Docker部署**: 容器化部署，简化环境配置
- **云端部署**: 支持AWS、Azure、阿里云等云平台
- **分布式部署**: 支持多实例负载均衡
- **HTTPS支持**: SSL证书配置和安全传输

## 🔒 安全注意事项

1. **数据隐私**: 所有数据本地处理，不上传云端
2. **访问控制**: 生产环境建议添加更严格的身份验证
3. **文件上传**: 限制文件类型和大小，防止恶意文件
4. **API安全**: 添加请求频率限制和输入验证
5. **数据库安全**: 使用强密码，定期备份数据

## 📖 相关文档

- **详细安装指南**: `rag_service/ENVIRONMENT_SETUP.md`
- **RAG功能指南**: `RAG_SETUP_GUIDE.md`
- **项目完成总结**: `PROJECT_COMPLETION.md`
- **API接口文档**: 启动服务后访问 http://localhost:5001/api/health

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

---

✨ **感谢使用AI智能助手项目！如有问题请提交Issue。**