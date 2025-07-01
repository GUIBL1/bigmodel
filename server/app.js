// Express后端服务器
const express = require('express');
const mysql = require('mysql2/promise');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const cors = require('cors');
const { createProxyMiddleware } = require('http-proxy-middleware');

const app = express();
const PORT = 3001;

// 中间件配置
app.use(cors()); // 允许跨域请求
app.use(express.json()); // 解析JSON数据

// 数据库连接配置
const dbConfig = {
  host: 'localhost',
  user: 'root',
  password: '123123', // 请根据实际情况修改
  database: 'ai'
};

// JWT密钥
const JWT_SECRET = 'your-secret-key-change-in-production';

// 初始化数据库
async function initDatabase() {
  try {
    // 创建不带数据库名的连接
    const connection = await mysql.createConnection({
      host: dbConfig.host,
      user: dbConfig.user,
      password: dbConfig.password
    });
    
    // 创建数据库
    await connection.execute('CREATE DATABASE IF NOT EXISTS ai');
    console.log('数据库ai创建成功');
    
    await connection.end();
    
    // 连接到ai数据库
    const dbConnection = await mysql.createConnection(dbConfig);
    
    // 创建用户表
    const createUserTable = `
      CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL COMMENT '用户名，唯一',
        password VARCHAR(255) NOT NULL COMMENT '加密后的密码',
        email VARCHAR(100) COMMENT '邮箱地址',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
      ) COMMENT '用户信息表'
    `;
    
    await dbConnection.execute(createUserTable);
    console.log('用户表创建成功');
    
    await dbConnection.end();
  } catch (error) {
    console.error('数据库初始化失败:', error);
  }
}

// 用户注册接口
app.post('/api/register', async (req, res) => {
  try {
    const { username, password, email } = req.body;
    
    // 验证输入
    if (!username || !password) {
      return res.status(400).json({ 
        success: false, 
        message: '用户名和密码不能为空' 
      });
    }
    
    if (username.length < 8) {
      return res.status(400).json({ 
        success: false, 
        message: '用户名长度不能少于8位' 
      });
    }
    
    if (password.length < 6) {
      return res.status(400).json({ 
        success: false, 
        message: '密码长度不能少于6位' 
      });
    }
    
    const connection = await mysql.createConnection(dbConfig);
    
    // 检查用户名是否已存在
    const [existingUsers] = await connection.execute(
      'SELECT id FROM users WHERE username = ?',
      [username]
    );
    
    if (existingUsers.length > 0) {
      await connection.end();
      return res.status(400).json({ 
        success: false, 
        message: '用户名已存在' 
      });
    }
    
    // 加密密码
    const hashedPassword = await bcrypt.hash(password, 10);
    
    // 插入新用户
    await connection.execute(
      'INSERT INTO users (username, password, email) VALUES (?, ?, ?)',
      [username, hashedPassword, email || null]
    );
    
    await connection.end();
    
    res.json({ 
      success: true, 
      message: '注册成功' 
    });
    
  } catch (error) {
    console.error('注册错误:', error);
    res.status(500).json({ 
      success: false, 
      message: '服务器错误' 
    });
  }
});

// 用户登录接口
app.post('/api/login', async (req, res) => {
  try {
    const { username, password } = req.body;
    
    // 验证输入
    if (!username || !password) {
      return res.status(400).json({ 
        success: false, 
        message: '用户名和密码不能为空' 
      });
    }
    
    const connection = await mysql.createConnection(dbConfig);
    
    // 查找用户
    const [users] = await connection.execute(
      'SELECT id, username, password FROM users WHERE username = ?',
      [username]
    );
    
    if (users.length === 0) {
      await connection.end();
      return res.status(400).json({ 
        success: false, 
        message: '用户名或密码错误' 
      });
    }
    
    const user = users[0];
    
    // 验证密码
    const isPasswordValid = await bcrypt.compare(password, user.password);
    
    if (!isPasswordValid) {
      await connection.end();
      return res.status(400).json({ 
        success: false, 
        message: '用户名或密码错误' 
      });
    }
    
    // 生成JWT token
    const token = jwt.sign(
      { userId: user.id, username: user.username },
      JWT_SECRET,
      { expiresIn: '24h' }
    );
    
    await connection.end();
    
    res.json({ 
      success: true, 
      message: '登录成功',
      token,
      user: {
        id: user.id,
        username: user.username
      }
    });
    
  } catch (error) {
    console.error('登录错误:', error);
    res.status(500).json({ 
      success: false, 
      message: '服务器错误' 
    });
  }
});

// 验证token中间件
const authenticateToken = (req, res, next) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];
  
  if (!token) {
    return res.status(401).json({ 
      success: false, 
      message: '访问令牌缺失' 
    });
  }
  
  jwt.verify(token, JWT_SECRET, (err, user) => {
    if (err) {
      return res.status(403).json({ 
        success: false, 
        message: '访问令牌无效' 
      });
    }
    req.user = user;
    next();
  });
};

// 受保护的路由示例
app.get('/api/profile', authenticateToken, (req, res) => {
  res.json({
    success: true,
    user: req.user
  });
});

// RAG服务代理路由
app.use('/api/rag', createProxyMiddleware({
  target: 'http://127.0.0.1:5001', // 使用127.0.0.1而不是localhost
  changeOrigin: true,
  timeout: 120000, // 2分钟超时
  proxyTimeout: 120000,
  pathRewrite: {
    '^/api/rag': '/api'
  },
  onProxyReq: (proxyReq, req, res) => {
    console.log('代理请求:', req.method, req.originalUrl, '-> http://127.0.0.1:5001' + req.url.replace('/api/rag', '/api'));
    // 设置请求超时
    proxyReq.setTimeout(120000);
  },
  onProxyRes: (proxyRes, req, res) => {
    console.log('代理响应:', proxyRes.statusCode, req.originalUrl);
  },
  onError: (err, req, res) => {
    console.error('RAG服务代理错误:', err.message);
    if (!res.headersSent) {
      res.status(503).json({
        success: false,
        message: 'RAG服务不可用：' + err.message
      });
    }
  }
}));

// 启动服务器
app.listen(PORT, async () => {
  console.log(`服务器运行在 http://localhost:${PORT}`);
  await initDatabase();
});
