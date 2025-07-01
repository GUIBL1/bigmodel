"""
测试前端直接调用RAG服务
"""

import requests
import time

def test_direct_rag_call():
    """测试前端直接调用RAG的方式"""
    print("🔄 测试前端直接调用RAG...")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            "http://127.0.0.1:5001/api/query",
            json={"question": "什么是RAG？"},
            timeout=120,
            headers={'Content-Type': 'application/json'}
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"直接调用状态: {response.status_code}")
        print(f"直接调用时间: {duration:.2f}秒")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 前端直接调用RAG成功")
            print(f"回答: {result.get('answer', 'N/A')[:100]}...")
            print(f"模式: {result.get('mode', 'N/A')}")
            return True
        else:
            print(f"❌ 直接调用失败: {response.status_code}")
            print(f"错误: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 直接调用异常: {e}")
        return False

if __name__ == "__main__":
    print("🚀 前端直接调用RAG测试")
    print("=" * 50)
    
    if test_direct_rag_call():
        print("\n🎉 前端可以直接调用RAG服务！")
        print("✨ 修改前端代码使用直接调用即可解决超时问题")
    else:
        print("\n❌ 直接调用仍有问题")
