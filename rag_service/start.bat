@echo off
REM RAG服务启动脚本 (Windows)

echo === RAG服务启动脚本 ===

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: Python未安装
    pause
    exit /b 1
)

REM 检查是否在虚拟环境中
if "%VIRTUAL_ENV%"=="" (
    echo 建议在虚拟环境中运行
    echo 创建虚拟环境: python -m venv rag_env
    echo 激活虚拟环境: rag_env\Scripts\activate
)

REM 检查核心依赖
echo 检查Python依赖...
python -c "import flask, chromadb, sentence_transformers" >nul 2>&1
if errorlevel 1 (
    echo 警告: 缺少必要的Python包
    echo 是否现在安装依赖？ (y/n)
    set /p install_deps=
    if /i "%install_deps%"=="y" (
        echo 开始安装依赖...
        call install_deps.bat
    ) else (
        echo 请手动安装依赖后重试
        pause
        exit /b 1
    )
)

REM 检查Ollama是否运行
echo 检查Ollama服务...
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo 警告: Ollama服务未运行
    echo 请先启动Ollama: ollama serve
    echo 并拉取模型: ollama pull llama3.1
)

REM 启动RAG服务
echo 启动RAG API服务...
python app.py

pause
