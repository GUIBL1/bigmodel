# 🚀 RAG服务环境安装指南

## 📋 系统要求

- **Python**: 3.8+ (推荐 3.10 或 3.11)

## 🚀安装依赖包

#### 方法一：一键安装（推荐）
```bash
cd rag_service
pip install -r requirements.txt
```

#### 方法二：分步安装（如有冲突）
```bash
# 步骤1: 安装核心Web框架
pip install flask==3.0.0 flask-cors==4.0.0 python-dotenv==1.0.0

# 步骤2: 安装文档处理包
pip install PyPDF2==3.0.1 python-docx==1.1.0 openpyxl==3.1.2 beautifulsoup4==4.12.2

# 步骤3: 安装AI核心包
pip install torch>=2.0.0 transformers>=4.30.0 sentence-transformers>=2.6.1

# 步骤4: 安装向量数据库
pip install chromadb>=0.4.0 numpy>=1.24.0 scikit-learn>=1.3.0

# 步骤5: 安装LlamaIndex
pip install llama-index>=0.10.50
pip install llama-index-llms-ollama llama-index-embeddings-huggingface llama-index-vector-stores-chroma

# 步骤6: 安装辅助包
pip install requests pandas jieba
```

## 🚀 启动RAG服务

### 方法二：手动启动
```bash
# 确保在虚拟环境中
cd rag_service
# 启动服务
python app.py
```