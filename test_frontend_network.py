"""
测试前端网络连接到RAG服务
"""

import requests

def test_cors_and_connection():
    """测试CORS和连接"""
    print("🔄 测试CORS和连接...")
    
    # 测试健康检查（GET请求）
    try:
        response = requests.get("http://127.0.0.1:5001/api/health", timeout=10)
        print(f"✅ GET健康检查: {response.status_code}")
        print(f"CORS头: {response.headers.get('Access-Control-Allow-Origin', '未设置')}")
    except Exception as e:
        print(f"❌ GET请求失败: {e}")
    
    # 测试POST请求（模拟前端）
    try:
        headers = {
            'Content-Type': 'application/json',
            'Origin': 'http://localhost:80'  # 模拟前端源
        }
        
        response = requests.post(
            "http://127.0.0.1:5001/api/query",
            json={"question": "测试"},
            headers=headers,
            timeout=30
        )
        
        print(f"✅ POST查询请求: {response.status_code}")
        print(f"CORS头: {response.headers.get('Access-Control-Allow-Origin', '未设置')}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 响应成功: {result.get('success', False)}")
        else:
            print(f"❌ 响应错误: {response.text}")
            
    except Exception as e:
        print(f"❌ POST请求失败: {e}")

def test_preflight():
    """测试CORS预检请求"""
    print("\n🔄 测试CORS预检请求...")
    
    try:
        headers = {
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'content-type',
            'Origin': 'http://localhost:80'
        }
        
        response = requests.options("http://127.0.0.1:5001/api/query", headers=headers, timeout=10)
        print(f"OPTIONS预检: {response.status_code}")
        print(f"允许方法: {response.headers.get('Access-Control-Allow-Methods', '未设置')}")
        print(f"允许头: {response.headers.get('Access-Control-Allow-Headers', '未设置')}")
        print(f"允许源: {response.headers.get('Access-Control-Allow-Origin', '未设置')}")
        
    except Exception as e:
        print(f"❌ OPTIONS请求失败: {e}")

if __name__ == "__main__":
    print("🚀 前端网络连接测试")
    print("=" * 50)
    
    test_cors_and_connection()
    test_preflight()
