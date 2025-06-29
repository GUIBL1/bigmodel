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
echo 请选择启动方式：
echo [1] 统一依赖管理（推荐）- 前后端共享node_modules
echo [2] 分离依赖管理 - 前后端独立依赖
echo.
set /p choice=请输入选择 (1/2): 

if "%choice%"=="1" goto unified
if "%choice%"=="2" goto separated
echo 无效选择，使用默认统一管理方式
goto unified

:unified
echo.
echo [统一依赖模式] 安装项目依赖...
call npm install
if %errorlevel% neq 0 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)

echo.
echo [统一依赖模式] 启动前端和后端服务...
echo 前端服务: http://localhost:5173
echo 后端服务: http://localhost:3001
echo.
npm run start:unified
goto end

:separated
echo.
echo [分离依赖模式] 安装前端依赖...
call npm install
if %errorlevel% neq 0 (
    echo [错误] 前端依赖安装失败
    pause
    exit /b 1
)

echo.
echo [分离依赖模式] 安装后端依赖...
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
echo [分离依赖模式] 启动后端服务...
start "AI助手-后端服务" cmd /k "cd server && npm start"
timeout /t 3 /nobreak >nul

echo.
echo [分离依赖模式] 启动前端服务...
echo 前端服务: http://localhost:5173
echo 后端服务: http://localhost:3001
echo.
npm run dev

:end
echo.
echo ========================================
echo     项目启动完成！
echo ========================================
