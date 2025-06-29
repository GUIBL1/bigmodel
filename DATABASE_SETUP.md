# 数据库配置说明

## MySQL 数据库安装与配置

### 1. 安装 MySQL
请根据您的操作系统下载并安装 MySQL：
- Windows: https://dev.mysql.com/downloads/mysql/
- macOS: 可使用 Homebrew `brew install mysql`
- Linux: `sudo apt-get install mysql-server` (Ubuntu/Debian)

### 2. 启动 MySQL 服务
```bash
# Windows (以管理员身份运行命令提示符)
net start mysql

# macOS
brew services start mysql

# Linux
sudo systemctl start mysql
```

### 3. 登录 MySQL
```bash
mysql -u root -p
```

### 4. 创建数据库和用户（可选）
```sql
-- 创建专用数据库用户（推荐）
CREATE USER 'aiuser'@'localhost' IDENTIFIED BY 'aipassword123';
GRANT ALL PRIVILEGES ON ai.* TO 'aiuser'@'localhost';
FLUSH PRIVILEGES;

-- 或直接使用 root 用户（简单但不推荐生产环境）
```

### 5. 修改后端配置
在 `server/app.js` 文件中修改数据库连接配置：

```javascript
const dbConfig = {
  host: 'localhost',
  user: 'root',          // 或您创建的用户名
  password: '123456',    // 修改为您的MySQL密码
  database: 'ai'
};
```

### 6. 自动创建数据库和表
当您首次运行后端服务器时，会自动：
- 创建 `ai` 数据库
- 创建 `users` 用户表

## 数据库表结构

### users 表
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

## 常见问题

### 1. 连接被拒绝
- 确保 MySQL 服务已启动
- 检查用户名和密码是否正确
- 确认 MySQL 在默认端口 3306 运行

### 2. 权限问题
- 确保用户有足够的权限访问数据库
- 检查防火墙设置

### 3. 字符编码问题
建议在 MySQL 配置中设置：
```sql
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;
```
