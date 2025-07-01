"""
直接测试RAG查询性能和错误
"""

import requests
import time
import json

def test_rag_query_debug():
    """详细测试RAG查询"""
    print("🔍 详细测试RAG查询...")
    
    start_time = time.time()
    
    try:
        # 测试一个简单问题
        print("发送请求...")
        response = requests.post(
            "http://127.0.0.1:5001/api/query",
            json={"question": "你好"},
            timeout=60,  # 增加超时时间
            stream=False
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"响应状态: {response.status_code}")
        print(f"响应时间: {duration:.2f}秒")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ RAG查询成功")
            print(f"成功标志: {result.get('success', 'N/A')}")
            print(f"回答: {result.get('answer', 'N/A')[:100]}...")
            print(f"模式: {result.get('mode', 'N/A')}")
            return True
        else:
            print(f"❌ RAG查询失败: {response.status_code}")
            print(f"错误内容: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"❌ 请求超时 (>60秒)")
        return False
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_rag_through_proxy():
    """通过Node.js代理测试"""
    print("\n🔄 通过Node.js代理测试...")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            "http://127.0.0.1:3001/api/rag/query",
            json={"question": "你好"},
            timeout=60
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"代理响应状态: {response.status_code}")
        print(f"代理响应时间: {duration:.2f}秒")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 代理RAG查询成功")
            print(f"回答: {result.get('answer', 'N/A')[:100]}...")
            return True
        else:
            print(f"❌ 代理查询失败: {response.status_code}")
            print(f"错误: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 代理异常: {e}")
        return False

if __name__ == "__main__":
    print("🚀 RAG查询调试测试")
    print("=" * 50)
    
    # 直接测试RAG
    test_rag_query_debug()
    
    # 通过代理测试
    test_rag_through_proxy()
