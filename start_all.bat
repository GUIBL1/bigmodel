@echo off
REM RAG系统完整启动脚本 (Windows)

echo 🚀 启动RAG增强AI对话系统
echo ==================================

REM 检查必要的服务
echo 📋 检查系统环境...

REM 检查Ollama
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo ❌ Ollama服务未运行，请先启动Ollama:
    echo    ollama serve
    echo    ollama pull llama3.1
    pause
    exit /b 1
)
echo ✅ Ollama服务正常

REM 检查Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js未安装
    pause
    exit /b 1
)
echo ✅ Node.js已安装

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装
    pause
    exit /b 1
)
echo ✅ Python已安装

echo.
echo 🔧 启动服务组件...

REM 启动RAG服务
echo 📚 启动RAG服务...
cd rag_service
if "%VIRTUAL_ENV%"=="" (
    echo ⚠️  建议在虚拟环境中运行RAG服务
)

REM 安装Python依赖
pip install -r requirements.txt --quiet

REM 启动RAG服务（后台运行）
start /b python app.py
echo ✅ RAG服务已启动

cd ..

REM 启动后端API服务
echo 🔗 启动后端API服务...
cd server
npm install --silent
start /b npm run dev
echo ✅ 后端API服务已启动

cd ..

REM 启动前端开发服务器
echo 🎨 启动前端服务...
npm install --silent
start npm run dev

echo.
echo 🎉 所有服务启动完成！
echo ==================================
echo 📱 前端地址: http://localhost:5173
echo 🔗 后端API: http://localhost:3001
echo 📚 RAG服务: http://localhost:5001
echo.
echo 💡 使用说明：
echo   1. 访问 http://localhost:5173 开始对话
echo   2. 访问 http://localhost:5173/rag 管理知识库
echo   3. 在对话界面切换RAG模式使用知识库
echo.
echo ⏹️  停止服务: 关闭此窗口或按Ctrl+C
echo.

pause
