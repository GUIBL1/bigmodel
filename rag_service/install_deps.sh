#!/bin/bash
# 分步安装RAG依赖，避免版本冲突

echo "📦 开始安装RAG服务依赖..."

# 第一步：安装基础包
echo "1️⃣ 安装基础包..."
pip install flask flask-cors python-dotenv

# 第二步：安装文档处理包
echo "2️⃣ 安装文档处理包..."
pip install PyPDF2 python-docx openpyxl beautifulsoup4 lxml markdown

# 第三步：安装ML相关包
echo "3️⃣ 安装机器学习包..."
pip install torch transformers sentence-transformers

# 第四步：安装ChromaDB
echo "4️⃣ 安装ChromaDB..."
pip install chromadb

# 第五步：安装LlamaIndex核心
echo "5️⃣ 安装LlamaIndex核心..."
pip install llama-index

# 第六步：安装LlamaIndex扩展
echo "6️⃣ 安装LlamaIndex扩展..."
pip install llama-index-llms-ollama
pip install llama-index-embeddings-huggingface  
pip install llama-index-vector-stores-chroma

echo "✅ 所有依赖安装完成！"
echo "🧪 测试导入..."

python -c "
try:
    import llama_index
    import chromadb
    import flask
    print('✅ 核心包导入成功')
except ImportError as e:
    print(f'❌ 导入失败: {e}')
"
