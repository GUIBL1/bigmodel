/**
 * AI智能对话系统 - Express后端服务器
 * 
 * 功能概述：
 * 1. 用户认证系统：注册、登录、JWT令牌验证
 * 2. 数据库管理：MySQL用户数据存储
 * 3. 安全防护：密码加密、CORS跨域、令牌验证
 * 4. API接口：RESTful风格的用户管理接口
 * 
 * 技术栈：
 * - Express.js: Web框架
 * - MySQL: 数据库
 * - JWT: 身份验证
 * - bcrypt: 密码加密
 *
 * 创建时间：2025年7月3日
 * 版本：v1.0.0
 */

// ========================= 依赖模块导入 =========================
const express = require('express');           // Express Web框架
const mysql = require('mysql2/promise');      // MySQL数据库驱动（Promise版本）
const bcrypt = require('bcrypt');             // 密码加密工具
const jwt = require('jsonwebtoken');          // JSON Web Token认证
const cors = require('cors');                 // 跨域资源共享中间件
const { createProxyMiddleware } = require('http-proxy-middleware'); // HTTP代理中间件

// ========================= 应用初始化配置 =========================
const app = express();                       // 创建Express应用实例
const PORT = 3001;                          // 服务器监听端口号

// ========================= 中间件配置 =========================
app.use(cors());                            // 启用CORS跨域请求支持
app.use(express.json());                    // 解析JSON格式的请求体数据

// ========================= 数据库配置 =========================
/**
 * MySQL数据库连接配置
 */
const dbConfig = {
  host: 'localhost',                        // 数据库主机地址
  user: 'root',                            // 数据库用户名
  password: '123123',                      // 数据库密码（请根据实际情况修改）
  database: 'ai'                           // 数据库名称
};

// ========================= JWT安全配置 =========================
/**
 * JWT密钥配置
 */
const JWT_SECRET = 'your-secret-key-change-in-production';

// ========================= 数据库初始化模块 =========================
/**
 * 初始化数据库和数据表
 * 功能：
 * 1. 创建ai数据库（如果不存在）
 * 2. 创建users用户表（如果不存在）
 * 3. 设置表结构和约束
 * 
 * @returns {Promise<void>} 异步执行数据库初始化
 */
async function initDatabase() {
  try {
    // 第一步：创建数据库连接（不指定具体数据库）
    const connection = await mysql.createConnection({
      host: dbConfig.host,
      user: dbConfig.user,
      password: dbConfig.password
    });
    
    // 第二步：创建ai数据库（如果不存在）
    await connection.execute('CREATE DATABASE IF NOT EXISTS ai');
    console.log('数据库ai创建成功');
    
    // 关闭临时连接
    await connection.end();
    
    // 第三步：连接到ai数据库
    const dbConnection = await mysql.createConnection(dbConfig);
    
    // 第四步：创建用户表结构
    const createUserTable = `
      CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY COMMENT '用户ID，自增主键',
        username VARCHAR(50) UNIQUE NOT NULL COMMENT '用户名，唯一标识',
        password VARCHAR(255) NOT NULL COMMENT '加密后的密码',
        email VARCHAR(100) COMMENT '邮箱地址（可选）',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '账户创建时间',
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间'
      ) COMMENT '用户信息表 - 存储系统用户的基本信息'
    `;
    
    // 执行表创建SQL
    await dbConnection.execute(createUserTable);
    console.log('用户表创建成功');
    
    // 关闭数据库连接
    await dbConnection.end();
  } catch (error) {
    console.error('数据库初始化失败:', error);
  }
}

// ========================= 用户注册API接口 =========================
/**
 * 用户注册接口
 * 
 * 路由：POST /api/register
 * 功能：创建新用户账户
 * 
 * 请求体参数：
 * @param {string} username - 用户名（必填，8位以上）
 * @param {string} password - 密码（必填，6位以上）
 * @param {string} email - 邮箱（可选）
 * 
 * 响应格式：
 * @returns {Object} JSON响应 - {success: boolean, message: string}
 * 
 * 业务逻辑：
 * 1. 验证输入参数格式
 * 2. 检查用户名是否已存在
 * 3. 加密存储用户密码
 * 4. 插入新用户记录
 */
app.post('/api/register', async (req, res) => {
  try {
    // 提取请求参数
    const { username, password, email } = req.body;
    
    // ========== 输入验证阶段 ==========
    // 检查必填字段
    if (!username || !password) {
      return res.status(400).json({ 
        success: false, 
        message: '用户名和密码不能为空' 
      });
    }
    
    // 检查用户名长度限制
    if (username.length < 8) {
      return res.status(400).json({ 
        success: false, 
        message: '用户名长度不能少于8位' 
      });
    }
    
    // 检查密码强度要求
    if (password.length < 6) {
      return res.status(400).json({ 
        success: false, 
        message: '密码长度不能少于6位' 
      });
    }
    
    // ========== 数据库操作阶段 ==========
    const connection = await mysql.createConnection(dbConfig);
    
    // 检查用户名唯一性
    const [existingUsers] = await connection.execute(
      'SELECT id FROM users WHERE username = ?',
      [username]
    );
    
    // 如果用户名已存在，返回错误
    if (existingUsers.length > 0) {
      await connection.end();
      return res.status(400).json({ 
        success: false, 
        message: '用户名已存在' 
      });
    }
    
    // ========== 密码加密阶段 ==========
    // 使用bcrypt进行密码哈希加密（盐轮数：10）
    const hashedPassword = await bcrypt.hash(password, 10);
    
    // ========== 用户创建阶段 ==========
    // 插入新用户记录到数据库
    await connection.execute(
      'INSERT INTO users (username, password, email) VALUES (?, ?, ?)',
      [username, hashedPassword, email || null]
    );
    
    // 关闭数据库连接
    await connection.end();
    
    // 返回成功响应
    res.json({ 
      success: true, 
      message: '注册成功' 
    });
    
  } catch (error) {
    // 错误处理：记录错误日志并返回通用错误信息
    console.error('注册错误:', error);
    res.status(500).json({ 
      success: false, 
      message: '服务器错误' 
    });
  }
});

// ========================= 用户登录API接口 =========================
/**
 * 用户登录接口
 * 
 * 路由：POST /api/login
 * 功能：验证用户身份并生成访问令牌
 * 
 * 请求体参数：
 * @param {string} username - 用户名（必填）
 * @param {string} password - 密码（必填）
 * 
 * 响应格式：
 * @returns {Object} JSON响应 - {success: boolean, message: string, token?: string, user?: Object}
 * 
 * 业务逻辑：
 * 1. 验证输入参数
 * 2. 查询用户信息
 * 3. 验证密码正确性
 * 4. 生成JWT访问令牌
 * 5. 返回用户信息和令牌
 */
app.post('/api/login', async (req, res) => {
  try {
    // 提取登录凭证
    const { username, password } = req.body;
    
    // ========== 输入验证阶段 ==========
    // 检查必填字段
    if (!username || !password) {
      return res.status(400).json({ 
        success: false, 
        message: '用户名和密码不能为空' 
      });
    }
    
    // ========== 用户查询阶段 ==========
    const connection = await mysql.createConnection(dbConfig);
    
    // 根据用户名查询用户信息
    const [users] = await connection.execute(
      'SELECT id, username, password FROM users WHERE username = ?',
      [username]
    );
    
    // 检查用户是否存在
    if (users.length === 0) {
      await connection.end();
      return res.status(400).json({ 
        success: false, 
        message: '用户名或密码错误'  // 故意模糊错误信息，提高安全性
      });
    }
    
    const user = users[0];
    
    // ========== 密码验证阶段 ==========
    // 使用bcrypt比较原始密码和哈希密码
    const isPasswordValid = await bcrypt.compare(password, user.password);
    
    if (!isPasswordValid) {
      await connection.end();
      return res.status(400).json({ 
        success: false, 
        message: '用户名或密码错误'  // 保持错误信息一致性
      });
    }
    
    // ========== JWT令牌生成阶段 ==========
    // 生成包含用户信息的JWT令牌
    const token = jwt.sign(
      { 
        userId: user.id,           // 用户ID
        username: user.username    // 用户名
      },
      JWT_SECRET,                  // 签名密钥
      { expiresIn: '24h' }        // 令牌有效期：24小时
    );
    
    // 关闭数据库连接
    await connection.end();
    
    // ========== 成功响应阶段 ==========
    res.json({ 
      success: true, 
      message: '登录成功',
      token,                       // 访问令牌
      user: {                      // 用户基本信息（不包含敏感数据）
        id: user.id,
        username: user.username
      }
    });
    
  } catch (error) {
    // 错误处理：记录错误日志并返回通用错误信息
    console.error('登录错误:', error);
    res.status(500).json({ 
      success: false, 
      message: '服务器错误' 
    });
  }
});

// ========================= JWT令牌验证中间件 =========================
/**
 * JWT令牌验证中间件
 * 
 * 功能：验证请求头中的JWT令牌有效性
 * 用途：保护需要身份验证的API路由
 * 
 * 工作流程：
 * 1. 从Authorization头部提取Bearer令牌
 * 2. 验证令牌签名和有效期
 * 3. 解析用户信息并添加到请求对象
 * 4. 继续处理请求或返回错误
 * 
 * @param {Object} req - Express请求对象
 * @param {Object} res - Express响应对象  
 * @param {Function} next - Express下一步函数
 */
const authenticateToken = (req, res, next) => {
  // ========== 令牌提取阶段 ==========
  // 获取Authorization请求头
  const authHeader = req.headers['authorization'];
  // 提取Bearer令牌（格式：Bearer <token>）
  const token = authHeader && authHeader.split(' ')[1];
  
  // 检查令牌是否存在
  if (!token) {
    return res.status(401).json({ 
      success: false, 
      message: '访问令牌缺失' 
    });
  }
  
  // ========== 令牌验证阶段 ==========
  jwt.verify(token, JWT_SECRET, (err, user) => {
    if (err) {
      // 令牌无效（过期、签名错误等）
      return res.status(403).json({ 
        success: false, 
        message: '访问令牌无效' 
      });
    }
    
    // 令牌验证成功，将用户信息添加到请求对象
    req.user = user;
    next(); // 继续处理请求
  });
};

// ========================= 受保护的API路由示例 =========================
/**
 * 用户资料获取接口（受保护路由）
 * 
 * 路由：GET /api/profile
 * 功能：获取当前登录用户的基本信息
 * 权限：需要有效的JWT令牌
 * 
 * 请求头：
 * @header {string} Authorization - Bearer <JWT_TOKEN>
 * 
 * 响应格式：
 * @returns {Object} JSON响应 - {success: boolean, user: Object}
 * 
 * 说明：此接口演示了如何使用JWT中间件保护API路由
 */
app.get('/api/profile', authenticateToken, (req, res) => {
  // 从JWT令牌中获取用户信息（已通过中间件验证）
  res.json({
    success: true,
    user: req.user  // 包含userId和username等信息
  });
});

// ========================= RAG服务代理模块 =========================
/**
 * RAG（检索增强生成）服务代理路由
 * 
 * 功能：将前端的RAG相关请求代理到后端RAG服务
 * 目标服务：http://127.0.0.1:5001
 * 代理路径：/api/rag/* -> /api/*
 * 
 * 配置说明：
 * - 超时时间：2分钟（RAG处理需要较长时间）
 * - 路径重写：移除/rag前缀
 * - 错误处理：网络错误和超时处理
 * 
 * 支持的RAG接口：
 * - /api/rag/health -> /api/health（健康检查）
 * - /api/rag/upload -> /api/upload（文档上传）
 * -/api/rag/documents -> /api/documents（文档获取）
 */
app.use('/api/rag', createProxyMiddleware({
  target: 'http://127.0.0.1:5001',          // RAG服务地址（使用127.0.0.1避免DNS解析问题）
  changeOrigin: true,                       // 修改请求头中的Origin
  timeout: 120000,                          // 请求超时：2分钟
  proxyTimeout: 120000,                     // 代理超时：2分钟
  pathRewrite: {
    '^/api/rag': '/api'                     // 路径重写：移除/rag前缀
  },
  
  // ========== 代理事件处理 ==========
  
  /**
   * 代理请求事件处理
   * 记录代理请求的详细信息，便于调试
   */
  onProxyReq: (proxyReq, req, res) => {
    const targetUrl = 'http://127.0.0.1:5001' + req.url.replace('/api/rag', '/api');
    console.log('代理请求:', req.method, req.originalUrl, '->', targetUrl);
    
    // 设置请求超时时间
    proxyReq.setTimeout(120000);
  },
  
  /**
   * 代理响应事件处理
   * 记录代理响应状态，监控服务健康状况
   */
  onProxyRes: (proxyRes, req, res) => {
    const statusIcon = proxyRes.statusCode < 400 ? '✅' : '❌';
    console.log(`${statusIcon} 代理响应:`, proxyRes.statusCode, req.originalUrl);
  },
  
  /**
   * 代理错误事件处理
   * 处理RAG服务不可用的情况
   */
  onError: (err, req, res) => {
    console.error('RAG服务代理错误:', err.message);
    
    // 避免重复发送响应
    if (!res.headersSent) {
      res.status(503).json({
        success: false,
        message: 'RAG服务暂时不可用：' + err.message,
        error_code: 'RAG_SERVICE_UNAVAILABLE'
      });
    }
  }
}));

// ========================= 服务器启动模块 =========================
/**
 * 启动Express服务器
 * 
 * 启动流程：
 * 1. 监听指定端口
 * 2. 输出启动信息
 * 3. 初始化数据库
 * 
 * 服务器信息：
 * - 端口：3001
 * - 协议：HTTP
 * - 环境：开发环境
 */
app.listen(PORT, async () => {
  console.log('========================================');
  console.log('   AI智能对话系统后端服务器已启动    ');
  console.log('========================================');
  console.log(`服务器地址: http://localhost:${PORT}`);
  console.log(`监听端口: ${PORT}`);
  console.log(`启动时间: ${new Date().toLocaleString('zh-CN')}`);
  console.log('========================================');
  
  // 执行数据库初始化
  console.log('开始初始化数据库...');
  await initDatabase();
  console.log('服务器启动完成，等待客户端连接...');
});
