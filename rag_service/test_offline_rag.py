"""
离线RAG测试 - 不依赖网络下载模型
使用简单的TF-IDF向量化作为嵌入模型的替代方案
"""

def test_offline_rag():
    """创建完全离线的RAG服务"""
    print("\n🏗️ 创建离线RAG服务...")
    
    try:
        import chromadb
        import numpy as np
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        import jieba  # 中文分词
        
        print("✅ 导入离线依赖成功")
        
        # 创建向量数据库
        chroma_client = chromadb.PersistentClient(path="./offline_vector_store")
        collection = chroma_client.get_or_create_collection("offline_test")
        print("✅ 向量数据库创建成功")
        
        # 测试文档
        test_docs = [
            "这是一个测试文档，用于验证RAG功能。RAG系统可以检索相关信息。",
            "RAG（检索增强生成）是一种结合信息检索和文本生成的AI技术。它能提高回答准确性。",
            "本系统支持多种文档格式，包括PDF、Word、Excel等。文档会被自动处理和索引。",
            "向量数据库存储文档的嵌入表示，支持语义搜索和相似度计算。",
            "大语言模型如GPT、Llama等可以生成自然语言回答，结合检索信息更准确。"
        ]
        
        # 使用TF-IDF作为简单的向量化方法
        print("🔄 使用TF-IDF进行文档向量化...")
        
        # 中文分词预处理
        def preprocess_text(text):
            # 使用jieba分词
            words = jieba.cut(text)
            return ' '.join(words)
        
        processed_docs = [preprocess_text(doc) for doc in test_docs]
        
        # 创建TF-IDF向量化器
        vectorizer = TfidfVectorizer(max_features=1000, stop_words=None)
        doc_vectors = vectorizer.fit_transform(processed_docs)
        
        # 转换为dense numpy数组
        doc_embeddings = doc_vectors.toarray()
        
        # 清空现有数据
        try:
            collection.delete()
        except:
            pass
        
        # 存储到ChromaDB
        collection.add(
            embeddings=doc_embeddings.tolist(),
            documents=test_docs,
            metadatas=[{"doc_id": i, "length": len(doc)} for i, doc in enumerate(test_docs)],
            ids=[f"doc_{i}" for i in range(len(test_docs))]
        )
        print("✅ 文档向量化和存储成功")
        
        # 测试检索功能
        queries = [
            "什么是RAG？",
            "支持哪些文档格式？",
            "如何进行语义搜索？"
        ]
        
        print("\n🔍 测试检索功能:")
        for query in queries:
            print(f"\n查询: {query}")
            
            # 查询向量化
            processed_query = preprocess_text(query)
            query_vector = vectorizer.transform([processed_query]).toarray()
            
            # 使用ChromaDB查询
            results = collection.query(
                query_embeddings=query_vector.tolist(),
                n_results=2
            )
            
            if results['documents'] and len(results['documents'][0]) > 0:
                print(f"✅ 最相关文档: {results['documents'][0][0][:100]}...")
                if results['distances'][0]:
                    similarity = 1 - results['distances'][0][0]
                    print(f"🎯 相似度: {similarity:.3f}")
            else:
                print("❌ 未找到相关文档")
        
        return True
        
    except ImportError as e:
        print(f"❌ 缺少依赖包: {e}")
        print("请安装: pip install scikit-learn jieba")
        return False
    except Exception as e:
        print(f"❌ 离线RAG服务创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_simple_embedding():
    """测试简单的向量嵌入方法"""
    print("\n🧪 测试简单向量嵌入...")
    
    try:
        from sklearn.feature_extraction.text import CountVectorizer
        import numpy as np
        
        # 简单的词袋模型测试
        docs = ["这是测试", "RAG技术很好", "向量检索有效"]
        
        vectorizer = CountVectorizer()
        vectors = vectorizer.fit_transform(docs)
        
        print("✅ 简单向量化成功")
        print(f"📊 词汇表大小: {len(vectorizer.vocabulary_)}")
        print(f"🔢 向量维度: {vectors.shape}")
        
        return True
        
    except Exception as e:
        print(f"❌ 简单嵌入测试失败: {e}")
        return False

if __name__ == "__main__":
    print("🚀 离线RAG功能测试")
    print("=" * 50)
    
    # 测试简单嵌入
    if test_simple_embedding():
        print("\n✨ 简单嵌入测试通过")
    
    # 测试离线RAG
    if test_offline_rag():
        print("\n🎉 离线RAG功能验证成功！")
        print("✨ 基础RAG功能正常，可以继续集成")
    else:
        print("\n❌ 离线RAG功能验证失败")
        print("正在安装缺失的依赖...")
        
        import subprocess
        try:
            subprocess.run(["pip", "install", "scikit-learn", "jieba"], check=True)
            print("✅ 依赖安装完成，请重新运行测试")
        except:
            print("❌ 自动安装失败，请手动运行: pip install scikit-learn jieba")
