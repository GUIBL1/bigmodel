"""
测试前端RAG功能的完整流程
"""

import requests
import json

def test_node_rag_proxy():
    """测试Node.js的RAG代理"""
    print("🔄 测试Node.js RAG代理...")
    
    try:
        # 测试通过Node.js代理调用RAG
        url = "http://localhost:3001/api/rag/query"
        data = {
            "question": "什么是RAG？"
        }
        
        response = requests.post(url, json=data, timeout=10)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Node.js RAG代理测试成功")
            print(f"回答: {result.get('answer', 'N/A')[:100]}...")
            return True
        else:
            print(f"❌ 代理失败: {response.status_code}")
            print(f"响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 代理测试失败: {e}")
        return False

def test_direct_rag():
    """直接测试RAG服务"""
    print("\n🔄 直接测试RAG服务...")
    
    try:
        # 直接调用RAG服务
        url = "http://localhost:5001/api/query"
        data = {
            "question": "什么是RAG？"
        }
        
        response = requests.post(url, json=data, timeout=10)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 直接RAG调用成功")
            print(f"回答: {result.get('answer', 'N/A')[:100]}...")
            return True
        else:
            print(f"❌ 直接调用失败: {response.status_code}")
            print(f"响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 直接调用失败: {e}")
        return False

def test_services_health():
    """检查服务健康状态"""
    print("\n🏥 检查服务健康状态...")
    
    # 检查Node.js服务
    try:
        response = requests.get("http://localhost:3001", timeout=5)
        print("✅ Node.js服务运行正常")
    except:
        print("❌ Node.js服务不可达")
    
    # 检查RAG服务
    try:
        response = requests.get("http://localhost:5001/api/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            print("✅ RAG服务运行正常")
            print(f"模型: {health.get('model_name', 'N/A')}")
            print(f"文档数量: {health.get('document_count', 'N/A')}")
        else:
            print("❌ RAG服务健康检查失败")
    except Exception as e:
        print(f"❌ RAG服务不可达: {e}")

if __name__ == "__main__":
    print("🚀 前端RAG功能测试")
    print("=" * 50)
    
    # 检查服务状态
    test_services_health()
    
    # 测试直接RAG调用
    if test_direct_rag():
        print("\n✨ 直接RAG调用正常")
    
    # 测试Node.js代理
    if test_node_rag_proxy():
        print("\n🎉 前端RAG代理功能正常！")
        print("前端应该能够正常调用RAG服务")
    else:
        print("\n❌ 前端RAG代理存在问题")
        print("请检查Node.js代理配置")
