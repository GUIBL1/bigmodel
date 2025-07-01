# 🛠️ RAG依赖安装问题解决方案

## 问题分析
您遇到的是典型的Python包依赖冲突问题。主要原因：
1. `sentence-transformers==2.2.2` 与 `llama-index-embeddings-huggingface>=0.2.2` 版本冲突
2. 不同版本的LlamaIndex有不同的API结构

## 🔧 解决方案

### 方案一：分步安装（推荐）

在您的虚拟环境中按顺序执行：

```bash
# 1. 清理现有安装（如果有问题的话）
pip uninstall llama-index llama-index-embeddings-huggingface sentence-transformers -y

# 2. 安装基础依赖
pip install flask flask-cors python-dotenv
pip install PyPDF2 python-docx openpyxl beautifulsoup4 lxml markdown

# 3. 安装AI核心包（让pip自动解决版本冲突）
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install transformers
pip install sentence-transformers

# 4. 安装向量数据库
pip install chromadb

# 5. 安装LlamaIndex（让它自动选择兼容版本）
pip install llama-index
pip install llama-index-llms-ollama
pip install llama-index-embeddings-huggingface
pip install llama-index-vector-stores-chroma

# 6. 验证安装
python test_rag.py
```

### 方案二：使用兼容的固定版本

创建新的requirements.txt：

```
# 兼容版本组合
flask==3.0.0
flask-cors==4.0.0
python-dotenv==1.0.0
PyPDF2==3.0.1
python-docx==1.1.0
openpyxl==3.1.2
beautifulsoup4==4.12.2
lxml==4.9.3
markdown==3.5.1

# AI核心包 - 兼容版本
torch>=2.0.0
transformers>=4.30.0
sentence-transformers>=2.6.1
chromadb>=0.4.0

# LlamaIndex - 使用较新的稳定版本
llama-index>=0.10.50
llama-index-llms-ollama
llama-index-embeddings-huggingface
llama-index-vector-stores-chroma
```

### 方案三：简化版本（仅核心功能）

如果上述方案仍有问题，可以先安装简化版本：

```bash
pip install flask flask-cors python-dotenv
pip install chromadb sentence-transformers
pip install PyPDF2 python-docx
pip install requests  # 用于直接调用Ollama API
```

然后使用我创建的 `test_rag.py` 来验证基本功能。

## 🚀 推荐执行步骤

1. **运行分步安装脚本**：
   ```bash
   cd rag_service
   install_deps.bat  # Windows
   # 或
   ./install_deps.sh  # Linux/Mac
   ```

2. **验证安装**：
   ```bash
   python test_rag.py
   ```

3. **如果验证成功，启动服务**：
   ```bash
   python app.py
   ```

## ⚡ 快速解决当前问题

立即在您的终端执行：

```bash
# 清理冲突的包
pip uninstall sentence-transformers llama-index-embeddings-huggingface -y

# 重新安装兼容版本
pip install sentence-transformers
pip install llama-index-embeddings-huggingface

# 验证
python -c "import sentence_transformers; print('✅ sentence-transformers导入成功')"
```

## 📞 如果仍有问题

1. **查看完整错误信息**
2. **提供Python版本**: `python --version`
3. **提供pip版本**: `pip --version`
4. **尝试创建新的虚拟环境**:
   ```bash
   python -m venv new_rag_env
   new_rag_env\Scripts\activate  # Windows
   pip install --upgrade pip
   ```

选择其中一个方案执行，通常方案一（分步安装）能解决大部分依赖冲突问题。
