#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的RAG测试脚本
适用于无网络环境或依赖缺失的情况
"""

import os
import sys
import json

def check_basic_dependencies():
    """检查基础依赖"""
    print("🔍 检查基础Python环境...")
    
    # 检查Python版本
    python_version = sys.version_info
    print(f"🐍 Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("⚠️ 建议使用Python 3.8+")
    
    return True

def test_offline_rag():
    """测试离线RAG功能"""
    print("\n📋 开始离线RAG测试...")
    
    try:
        # 尝试导入scikit-learn
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity
            import numpy as np
            print("✅ scikit-learn可用")
            has_sklearn = True
        except ImportError:
            print("❌ scikit-learn不可用")
            has_sklearn = False
        
        # 尝试导入jieba（中文分词）
        try:
            import jieba
            print("✅ jieba中文分词可用")
            has_jieba = True
        except ImportError:
            print("❌ jieba不可用")
            has_jieba = False
        
        if not has_sklearn:
            print("\n💡 安装建议:")
            print("pip install scikit-learn numpy")
            if not has_jieba:
                print("pip install jieba")
            return False
        
        # 创建简单的文档存储
        documents = [
            "RAG（检索增强生成）是一种结合信息检索和文本生成的AI技术",
            "本系统支持多种文档格式，包括PDF、Word、Excel等",
            "向量数据库用于存储和检索文档的语义表示",
            "Ollama是一个本地运行大语言模型的工具",
            "ChromaDB是一个开源的向量数据库"
        ]
        
        print(f"📚 测试文档数量: {len(documents)}")
        
        # 创建TF-IDF向量化器
        if has_jieba:
            # 使用jieba进行中文分词
            def chinese_tokenizer(text):
                return list(jieba.cut(text))
            
            vectorizer = TfidfVectorizer(
                tokenizer=chinese_tokenizer,
                max_features=1000,
                ngram_range=(1, 2)
            )
        else:
            vectorizer = TfidfVectorizer(
                max_features=1000,
                ngram_range=(1, 2)
            )
        
        # 训练向量化器并转换文档
        print("🔄 正在创建文档向量...")
        doc_vectors = vectorizer.fit_transform(documents)
        print(f"✅ 文档向量化完成，维度: {doc_vectors.shape}")
        
        # 测试查询
        queries = [
            "什么是RAG",
            "支持哪些文档格式",
            "向量数据库的作用",
            "本地模型工具"
        ]
        
        print("\n🔍 开始检索测试...")
        for query in queries:
            print(f"\n查询: {query}")
            
            # 查询向量化
            query_vector = vectorizer.transform([query])
            
            # 计算相似度
            similarities = cosine_similarity(query_vector, doc_vectors).flatten()
            
            # 获取最相关的文档
            best_match_idx = similarities.argmax()
            best_score = similarities[best_match_idx]
            
            print(f"📄 最相关文档: {documents[best_match_idx]}")
            print(f"🎯 相似度分数: {best_score:.3f}")
            
            if best_score > 0.1:  # 设置一个较低的阈值
                print("✅ 检索成功")
            else:
                print("⚠️ 检索结果相关性较低")
        
        return True
        
    except Exception as e:
        print(f"❌ 离线RAG测试失败: {e}")
        return False

def test_flask_server():
    """测试Flask服务可用性"""
    print("\n🌐 检查Flask服务...")
    
    try:
        import requests
        response = requests.get("http://localhost:5000/health", timeout=3)
        if response.status_code == 200:
            print("✅ RAG服务运行正常")
            return True
        else:
            print(f"⚠️ RAG服务响应异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接到RAG服务: {e}")
        print("💡 请确保已启动: python app.py")
        return False

def show_installation_guide():
    """显示安装指南"""
    print("\n📋 安装指南:")
    print("=" * 50)
    print("1. 基础依赖（离线RAG必需）:")
    print("   pip install scikit-learn numpy")
    print("   pip install jieba  # 中文分词支持")
    print("")
    print("2. 完整RAG依赖（需要网络）:")
    print("   pip install sentence-transformers")
    print("   pip install chromadb")
    print("   pip install llama-index")
    print("")
    print("3. 启动服务:")
    print("   python app.py")
    print("")
    print("4. 测试:")
    print("   python test_simple_rag.py")

def main():
    """主函数"""
    print("🚀 简化RAG系统测试")
    print("=" * 40)
    
    # 检查基础环境
    if not check_basic_dependencies():
        return
    
    # 测试离线RAG
    offline_success = test_offline_rag()
    
    # 尝试测试Flask服务
    server_success = test_flask_server()
    
    print("\n📊 测试结果汇总:")
    print("=" * 30)
    print(f"离线RAG功能: {'✅ 通过' if offline_success else '❌ 失败'}")
    print(f"Flask服务: {'✅ 运行' if server_success else '❌ 未运行'}")
    
    if not offline_success:
        show_installation_guide()
    
    if offline_success and server_success:
        print("\n🎉 RAG系统测试完成！系统运行正常。")
    elif offline_success:
        print("\n✅ 离线RAG功能正常，可以进行基本的文档检索。")
        print("💡 启动Flask服务后可获得完整功能。")
    else:
        print("\n❌ 请按照安装指南安装必要依赖。")

if __name__ == "__main__":
    main()
