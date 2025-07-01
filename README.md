# 🤖 AI智能助手项目

一个基于Vue 3 + Node.js + MySQL的智能聊天应用，支持用户注册登录和AI对话功能。

## 🚀 功能特性

- 🔐 **用户认证**: 完整的注册/登录系统，支持JWT token认证
- 💬 **智能对话**: 集成AI聊天API，支持流式响应和思考过程展示
- 🎨 **精美界面**: 现代化UI设计，响应式布局
- 🔒 **数据安全**: 密码加密存储，安全的用户会话管理
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

## 📦 项目结构

```
bigmodel/
├── 📄 package.json          # 统一的项目依赖配置
├── 📄 vite.config.js        # Vite构建配置
├── 📄 index.html            # 入口HTML文件
├── 📚 README.md             # 项目说明文档
├── 📁 src/                  # 前端源代码
│   ├── App.vue              # 根组件
│   ├── main.js              # 入口文件
│   ├── 📁 views/            # 页面组件
│   │   ├── login.vue        # 登录/注册页面
│   │   └── index.vue        # AI对话主界面
│   ├── 📁 router/           # 路由配置
│   │   └── index.js         # 路由定义
│   ├── 📁 stores/           # 状态管理
│   │   └── user.js          # 用户状态管理
│   └──  📁 utils/            # 工具函数
│        └── api.js           # API请求封装
└── 📁 server/               # 后端源代码
    ├── package.json         # 服务器模块配置（使用根目录依赖）
    └── app.js               # Express服务器（CommonJS）
```

## 🚀 快速启动指南

### 1. 环境要求
- Node.js >= 16.0.0
- MySQL >= 5.7
- npm 或 yarn

### 2. 克隆项目
```bash
git clone https://github.com/GUIBL1/bigmodel.git
cd bigmodel
```

### 3. 启动方式
前后端共享同一个node_modules，节省空间和管理成本。

```bash
# 1. 安装统一依赖
npm install

# 2. 启动前后端服务
npm run start:unified
```

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

```bash
# 开发模式启动前端
npm run dev

# 构建生产版本
npm run build

# 预览生产版本
npm run preview

# 启动后端服务
npm run server

# 开发模式启动后端
npm run server:dev

# 同时启动前后端（统一依赖模式）
npm run start:unified

# 安装所有依赖（分离模式）
npm run install:all
```