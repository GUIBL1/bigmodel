#!/bin/bash

# RAG系统完整启动脚本

echo "🚀 启动RAG增强AI对话系统"
echo "=================================="

# 检查必要的服务
echo "📋 检查系统环境..."

# 检查Ollama
if ! curl -s http://localhost:11434/api/tags &> /dev/null; then
    echo "❌ Ollama服务未运行，请先启动Ollama:"
    echo "   ollama serve"
    echo "   ollama pull llama3.1"
    exit 1
fi
echo "✅ Ollama服务正常"

# 检查Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js未安装"
    exit 1
fi
echo "✅ Node.js已安装"

# 检查Python
if ! command -v python &> /dev/null; then
    echo "❌ Python未安装"
    exit 1
fi
echo "✅ Python已安装"

echo ""
echo "🔧 启动服务组件..."

# 启动RAG服务
echo "📚 启动RAG服务..."
cd rag_service
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  建议在虚拟环境中运行RAG服务"
fi

# 安装Python依赖
pip install -r requirements.txt --quiet

# 启动RAG服务（后台运行）
python app.py &
RAG_PID=$!
echo "✅ RAG服务已启动 (PID: $RAG_PID)"

cd ..

# 启动后端API服务
echo "🔗 启动后端API服务..."
cd server
npm install --silent
npm run dev &
API_PID=$!
echo "✅ 后端API服务已启动 (PID: $API_PID)"

cd ..

# 启动前端开发服务器
echo "🎨 启动前端服务..."
npm install --silent
npm run dev &
FRONTEND_PID=$!
echo "✅ 前端服务已启动 (PID: $FRONTEND_PID)"

echo ""
echo "🎉 所有服务启动完成！"
echo "=================================="
echo "📱 前端地址: http://localhost:5173"
echo "🔗 后端API: http://localhost:3001"
echo "📚 RAG服务: http://localhost:5001"
echo ""
echo "💡 使用说明："
echo "  1. 访问 http://localhost:5173 开始对话"
echo "  2. 访问 http://localhost:5173/rag 管理知识库"
echo "  3. 在对话界面切换RAG模式使用知识库"
echo ""
echo "⏹️  停止所有服务: Ctrl+C"
echo ""

# 等待用户中断
trap "echo ''; echo '🛑 正在停止所有服务...'; kill $RAG_PID $API_PID $FRONTEND_PID 2>/dev/null; echo '✅ 所有服务已停止'; exit 0" INT

# 保持脚本运行
wait
