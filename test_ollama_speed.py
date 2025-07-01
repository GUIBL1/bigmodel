"""
快速测试Ollama生成速度
"""

import requests
import time

def test_ollama_speed():
    """测试Ollama响应速度"""
    print("🚀 测试Ollama生成速度...")
    
    start_time = time.time()
    
    try:
        response = requests.post("http://localhost:11434/api/generate", 
                               json={
                                   "model": "maoniang:latest",
                                   "prompt": "简单回答：你好",
                                   "stream": False
                               },
                               timeout=30)
        
        end_time = time.time()
        duration = end_time - start_time
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Ollama响应成功 (耗时: {duration:.2f}秒)")
            print(f"回答: {result.get('response', 'N/A')}")
            return True
        else:
            print(f"❌ Ollama错误: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ollama测试失败: {e}")
        return False

if __name__ == "__main__":
    test_ollama_speed()
