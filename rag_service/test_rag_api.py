#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试RAG功能的简单脚本
"""

import requests
import json
import time

# RAG服务地址
RAG_SERVICE_URL = "http://localhost:5001"

def test_rag_health():
    """测试RAG服务健康状态"""
    try:
        response = requests.get(f"{RAG_SERVICE_URL}/api/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ RAG服务健康检查:")
            print(f"   状态: {'正常' if data.get('success') else '异常'}")
            print(f"   Ollama状态: {data.get('ollama_status', '未知')}")
            print(f"   模型: {data.get('model_name', '未知')}")
            print(f"   文档数量: {data.get('document_count', 0)}")
            return True
        else:
            print(f"❌ RAG服务健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接RAG服务: {e}")
        return False

def test_add_documents():
    """测试添加文档"""
    try:
        response = requests.post(f"{RAG_SERVICE_URL}/api/index/rebuild", timeout=30)
        if response.status_code == 200:
            data = response.json()
            print("✅ 文档索引重建结果:")
            print(f"   成功: {data.get('success')}")
            print(f"   消息: {data.get('message', '无消息')}")
            print(f"   文档数量: {data.get('document_count', 0)}")
            return True
        else:
            print(f"❌ 文档索引重建失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 文档索引重建出错: {e}")
        return False

def test_rag_query(question):
    """测试RAG查询"""
    try:
        data = {"question": question}
        response = requests.post(
            f"{RAG_SERVICE_URL}/api/query", 
            json=data, 
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ RAG查询结果:")
            print(f"   问题: {result.get('question', question)}")
            print(f"   成功: {result.get('success')}")
            if result.get('success'):
                print(f"   回答: {result.get('answer', '无回答')}")
                print(f"   模式: {result.get('mode', '在线')}")
                sources = result.get('sources', [])
                if sources:
                    print("   来源文档:")
                    for i, source in enumerate(sources[:3]):
                        print(f"     {i+1}. {source.get('file_name', '未知')} (相似度: {source.get('score', 0):.3f})")
            else:
                print(f"   错误: {result.get('error', '未知错误')}")
            return True
        else:
            print(f"❌ RAG查询失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ RAG查询出错: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始RAG功能测试")
    print("=" * 50)
    
    # 测试服务健康状态
    if not test_rag_health():
        print("❌ RAG服务不可用，请先启动服务")
        return
    
    print("\n" + "=" * 50)
    
    # 测试添加文档
    print("📄 测试文档添加...")
    test_add_documents()
    
    # 等待文档处理完成
    print("\n⏳ 等待文档处理完成...")
    time.sleep(5)
    
    print("\n" + "=" * 50)
    
    # 测试查询
    test_questions = [
        "什么是RAG？",
        "RAG有什么优势？",
        "RAG技术的应用场景有哪些？",
        "本系统使用了什么技术栈？"
    ]
    
    for i, question in enumerate(test_questions):
        print(f"\n🔍 测试查询 {i+1}:")
        test_rag_query(question)
        if i < len(test_questions) - 1:
            time.sleep(2)  # 间隔等待
    
    print("\n🎉 RAG功能测试完成！")

if __name__ == "__main__":
    main()
