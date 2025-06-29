# AI智能助手项目

一个基于Vue 3 + Node.js + MySQL的智能聊天应用，支持用户注册登录和AI对话功能。

## 🚀 功能特性

- 🔐 **用户认证**: 完整的注册/登录系统，支持JWT token认证
- 💬 **智能对话**: 集成AI聊天API，支持流式响应和思考过程展示
- 🎨 **精美界面**: 现代化UI设计，响应式布局
- 🔒 **数据安全**: 密码加密存储，安全的用户会话管理
- 📱 **移动友好**: 支持移动端设备访问

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
├── src/                    # 前端源码
│   ├── views/             # 页面组件
│   │   ├── login.vue      # 登录/注册页面
│   │   └── index.vue      # 主聊天页面
│   ├── stores/            # 状态管理
│   │   ├── user.js        # 用户状态
│   │   └── counter.js     # 计数器示例
│   ├── utils/             # 工具函数
│   │   └── api.js         # API请求封装
│   ├── router/            # 路由配置
│   │   └── index.js       # 路由定义
│   ├── components/        # 组件
│   ├── assets/           # 静态资源
│   ├── App.vue           # 根组件
│   └── main.js           # 入口文件
├── server/                # 后端源码
│   ├── app.js            # 服务器主文件
│   └── package.json      # 后端依赖
├── public/               # 公共静态文件
├── package.json          # 前端依赖
├── vite.config.js        # Vite配置
└── README.md            # 项目说明
```

## 🚀 快速开始

### 1. 环境要求
- Node.js >= 16.0.0
- MySQL >= 5.7
- npm 或 yarn

### 2. 克隆项目
```bash
git clone <项目地址>
cd bigmodel
```

### 3. 安装前端依赖
```bash
npm install
```

### 4. 安装后端依赖
```bash
cd server
npm install
cd ..
```

### 5. 配置数据库
请参考 [DATABASE_SETUP.md](./DATABASE_SETUP.md) 文件进行数据库配置。

### 6. 启动项目

#### 启动后端服务（端口3001）
```bash
cd server
npm start
# 或使用开发模式
npm run dev
```

#### 启动前端服务（端口5173）
```bash
npm run dev
```

### 7. 访问应用
打开浏览器访问: http://localhost:5173

## 🔧 配置说明

### 数据库配置
在 `server/app.js` 中修改数据库连接配置：
```javascript
const dbConfig = {
  host: 'localhost',
  user: 'root',
  password: '你的MySQL密码',
  database: 'ai'
};
```

### AI API配置
在 `src/views/index.vue` 中可以修改AI服务提供商和API密钥。

## 📱 使用说明

### 用户注册
1. 访问登录页面
2. 点击"立即注册"切换到注册模式
3. 填写用户名（至少8位）、邮箱（可选）、密码（至少6位）
4. 确认密码后点击"立即注册"

### 用户登录
1. 在登录页面输入用户名和密码
2. 点击"立即登录"
3. 登录成功后自动跳转到聊天页面

### AI对话
1. 在输入框中输入您的问题
2. 按Ctrl+Enter或点击发送按钮
3. 查看AI的思考过程和回复
4. 支持多轮对话

## 🔒 安全特性

- 密码使用bcrypt加密存储
- JWT token有效期24小时
- 前端路由守卫保护私有页面
- API请求自动携带认证token
- CORS配置防止恶意跨域请求

## 🎨 UI特性

- 渐变背景和毛玻璃效果
- 流畅的动画过渡
- 响应式设计适配移动端
- 深色/浅色主题适配
- 优雅的聊天气泡设计

## 🐛 常见问题

### 1. 数据库连接失败
- 检查MySQL服务是否启动
- 确认数据库配置信息正确
- 查看防火墙设置

### 2. 前端无法访问后端API
- 确认后端服务在端口3001正常运行
- 检查CORS配置
- 确认API地址配置正确

### 3. 登录状态丢失
- 检查浏览器本地存储
- 确认JWT token未过期
- 查看网络请求是否正常

## 📝 开发说明

### 添加新功能
1. 后端: 在 `server/app.js` 中添加新的API路由
2. 前端: 在 `src/utils/api.js` 中添加对应的API方法
3. 页面: 在对应的Vue组件中调用API

### 自定义样式
- 主要样式在各个Vue组件的 `<style scoped>` 中
- 全局样式在 `src/assets/` 目录下
- 使用Element Plus主题自定义

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 发起 Pull Request

## 📄 许可证

MIT License

## 📞 联系方式

如有问题或建议，欢迎提交Issue或联系开发者。

---

**享受AI聊天的乐趣！** 🎉

## Recommended IDE Setup

[VSCode](https://code.visualstudio.com/) + [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (and disable Vetur).

## Customize configuration

See [Vite Configuration Reference](https://vite.dev/config/).

## Project Setup

```sh
npm install
```

### Compile and Hot-Reload for Development

```sh
npm run dev
```

### Compile and Minify for Production

```sh
npm run build
```
