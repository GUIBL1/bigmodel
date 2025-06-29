@echo off
echo ========================================
echo     AI智能助手项目启动脚本
echo ========================================
echo.

echo 正在检查Node.js环境...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到Node.js，请先安装Node.js
    pause
    exit /b 1
)
echo [✓] Node.js环境正常

echo.
echo 正在检查MySQL服务...
sc query mysql >nul 2>&1
if %errorlevel% neq 0 (
    echo [警告] 未检测到MySQL服务，请确保MySQL已安装并启动
    echo 继续执行可能会导致后端启动失败
    pause
)

echo.
echo [1] 安装前端依赖...
call npm install
if %errorlevel% neq 0 (
    echo [错误] 前端依赖安装失败
    pause
    exit /b 1
)

echo.
echo [2] 安装后端依赖...
cd server
call npm install
if %errorlevel% neq 0 (
    echo [错误] 后端依赖安装失败
    cd ..
    pause
    exit /b 1
)
cd ..

echo.
echo [3] 启动后端服务...
start "AI助手-后端服务" cmd /k "cd server && npm start"
timeout /t 3 /nobreak >nul

echo.
echo [4] 启动前端服务...
echo 前端服务将在 http://localhost:5173 启动
echo 后端服务运行在 http://localhost:3001
echo.
echo ========================================
echo     项目启动完成！
echo ========================================
echo.
echo 请确保：
echo 1. MySQL服务已启动
echo 2. 已修改 server/app.js 中的数据库配置
echo 3. 浏览器将自动打开登录页面
echo.
npm run dev
