#!/usr/bin/env python3
"""
测试向量维度不匹配修复
"""

import requests
import json

def test_query_api():
    """测试查询API"""
    url = "http://127.0.0.1:5001/api/query"
    
    data = {
        "question": "测试查询"
    }
    
    try:
        print("发送查询请求...")
        response = requests.post(url, json=data, timeout=30)
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("rebuilt_index"):
                print("✅ 索引已自动重建")
            if result.get("success"):
                print("✅ 查询成功")
            else:
                print(f"❌ 查询失败: {result.get('error')}")
        else:
            print(f"❌ 请求失败")
            
    except Exception as e:
        print(f"请求异常: {e}")

def test_rebuild_index():
    """测试重建索引API"""
    url = "http://127.0.0.1:5001/api/index/rebuild"
    
    try:
        print("发送重建索引请求...")
        response = requests.post(url, timeout=60)
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ 索引重建成功")
                print(f"文档数量: {result.get('document_count')}")
            else:
                print(f"❌ 索引重建失败: {result.get('error')}")
        else:
            print(f"❌ 请求失败")
            
    except Exception as e:
        print(f"请求异常: {e}")

if __name__ == "__main__":
    print("=== 测试向量维度不匹配修复 ===\n")
    
    print("1. 测试查询API（可能触发自动重建）")
    test_query_api()
    
    print("\n" + "="*50 + "\n")
    
    print("2. 测试手动重建索引API")
    test_rebuild_index()
    
    print("\n" + "="*50 + "\n")
    
    print("3. 重建后再次测试查询")
    test_query_api()
