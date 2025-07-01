#!/bin/bash

# RAG服务启动脚本

echo "=== RAG服务启动脚本 ==="

# 检查Python是否安装
if ! command -v python &> /dev/null; then
    echo "错误: Python未安装"
    exit 1
fi

# 检查是否在虚拟环境中
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "建议在虚拟环境中运行"
    echo "创建虚拟环境: python -m venv rag_env"
    echo "激活虚拟环境: source rag_env/bin/activate (Linux/Mac) 或 rag_env\\Scripts\\activate (Windows)"
fi

# 安装依赖
echo "安装Python依赖..."
pip install -r requirements.txt

# 检查Ollama是否运行
echo "检查Ollama服务..."
if ! curl -s http://localhost:11434/api/tags &> /dev/null; then
    echo "警告: Ollama服务未运行"
    echo "请先启动Ollama: ollama serve"
    echo "并拉取模型: ollama pull llama3.1"
fi

# 启动RAG服务
echo "启动RAG API服务..."
python app.py
