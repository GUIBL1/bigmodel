"""
简化的RAG测试和安装验证
"""

def test_imports():
    """测试所需包的导入"""
    print("🧪 测试包导入...")
    
    try:
        import flask
        print("✅ Flask导入成功")
    except ImportError as e:
        print(f"❌ Flask导入失败: {e}")
        return False
    
    try:
        import chromadb
        print("✅ ChromaDB导入成功")
    except ImportError as e:
        print(f"❌ ChromaDB导入失败: {e}")
        return False
    
    try:
        import sentence_transformers
        print("✅ SentenceTransformers导入成功")
    except ImportError as e:
        print(f"❌ SentenceTransformers导入失败: {e}")
        return False
    
    try:
        import torch
        print("✅ PyTorch导入成功")
    except ImportError as e:
        print(f"❌ PyTorch导入失败: {e}")
        return False
    
    try:
        import llama_index
        print("✅ LlamaIndex导入成功")
    except ImportError as e:
        print(f"❌ LlamaIndex导入失败: {e}")
        return False
    
    print("🎉 所有核心包导入成功！")
    return True

def test_ollama_connection():
    """测试Ollama连接"""
    print("\n🔗 测试Ollama连接...")
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama服务正常运行")
            models = response.json().get('models', [])
            if models:
                print(f"📋 可用模型: {[m['name'] for m in models]}")
            else:
                print("⚠️ 没有可用模型，请运行: ollama pull llama3.1")
            return True
        else:
            print(f"❌ Ollama服务响应异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接Ollama: {e}")
        print("请确保Ollama正在运行: ollama serve")
        return False

def create_simple_rag():
    """创建简化的RAG服务"""
    print("\n🏗️ 创建简化RAG服务...")
    
    try:
        # 基本导入测试
        import chromadb
        from sentence_transformers import SentenceTransformer
        import os
        
        # 检查网络连接
        import requests
        has_internet = False
        try:
            response = requests.get("https://huggingface.co", timeout=5)
            has_internet = response.status_code == 200
        except:
            has_internet = False
        
        print(f"🌐 网络状态: {'可用' if has_internet else '离线'}")
        
        # 尝试使用本地可用的嵌入模型
        embed_model = None
        
        if has_internet:
            # 有网络时尝试在线模型
            model_options = [
                'all-MiniLM-L6-v2',
                'paraphrase-MiniLM-L6-v2',
                'all-mpnet-base-v2'
            ]
            
            for model_name in model_options:
                try:
                    print(f"🔍 尝试加载在线模型: {model_name}")
                    cache_dir = "./embeddings_cache"
                    os.makedirs(cache_dir, exist_ok=True)
                    embed_model = SentenceTransformer(model_name, cache_folder=cache_dir)
                    print(f"✅ 嵌入模型加载成功: {model_name}")
                    break
                except Exception as e:
                    print(f"⚠️ 模型 {model_name} 加载失败: {str(e)[:100]}...")
                    continue
        
        if embed_model is None:
            print("🔄 切换到离线模式...")
            # 使用scikit-learn的TfidfVectorizer作为离线替代
            try:
                from sklearn.feature_extraction.text import TfidfVectorizer
                from sklearn.metrics.pairwise import cosine_similarity
                import numpy as np
                
                print("✅ 使用离线TF-IDF向量化器")
                
                # 创建简单的TF-IDF嵌入类
                class OfflineEmbedding:
                    def __init__(self):
                        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
                        self.is_fitted = False
                    
                    def encode(self, texts):
                        if isinstance(texts, str):
                            texts = [texts]
                        
                        if not self.is_fitted:
                            vectors = self.vectorizer.fit_transform(texts)
                            self.is_fitted = True
                        else:
                            vectors = self.vectorizer.transform(texts)
                        
                        return vectors.toarray()
                
                embed_model = OfflineEmbedding()
                print("✅ 离线嵌入模型创建成功")
                
            except ImportError:
                print("❌ 无法导入scikit-learn，请安装:")
                print("pip install scikit-learn")
                return False
        
        # 创建向量数据库
        chroma_client = chromadb.PersistentClient(path="./test_vector_store")
        collection = chroma_client.get_or_create_collection("test_collection")
        print("✅ 向量数据库创建成功")
        
        # 测试文档处理
        test_docs = [
            "这是一个测试文档，用于验证RAG功能。",
            "RAG（检索增强生成）是一种结合信息检索和文本生成的AI技术。",
            "本系统支持多种文档格式，包括PDF、Word、Excel等。"
        ]
        
        # 文档向量化
        print("🔄 正在进行文档向量化...")
        embeddings = embed_model.encode(test_docs)
        
        # 清空现有数据（如果有的话）
        try:
            collection.delete()
        except:
            pass
        
        # 存储到向量数据库
        collection.add(
            embeddings=embeddings.tolist(),
            documents=test_docs,
            ids=[f"doc_{i}" for i in range(len(test_docs))]
        )
        print("✅ 测试文档向量化和存储成功")
        
        # 测试检索
        query = "什么是RAG？"
        print(f"🔍 测试查询: {query}")
        query_embedding = embed_model.encode([query])
        
        results = collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=2
        )
        
        if results['documents'] and len(results['documents'][0]) > 0:
            print("✅ 文档检索测试成功")
            print(f"� 最相关结果: {results['documents'][0][0]}")
            if len(results['distances'][0]) > 0:
                print(f"🎯 相似度分数: {1 - results['distances'][0][0]:.3f}")
            return True
        else:
            print("❌ 文档检索失败")
            return False
            
    except Exception as e:
        print(f"❌ RAG服务创建失败: {e}")
        import traceback
        print("📋 详细错误信息:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 RAG服务安装和功能验证")
    print("=" * 50)
    
    # 测试导入
    if not test_imports():
        print("\n❌ 包导入测试失败，请先安装依赖")
        print("运行: python install_deps.bat")
        exit(1)
    
    # 测试Ollama
    test_ollama_connection()
    
    # 测试基本RAG功能
    if create_simple_rag():
        print("\n🎉 基本RAG功能验证成功！")
        print("✨ 可以继续启动完整的RAG服务")
    else:
        print("\n❌ RAG功能验证失败")
        print("请检查错误信息并重试")
