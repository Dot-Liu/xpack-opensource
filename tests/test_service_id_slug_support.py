#!/usr/bin/env python3
"""
测试脚本：验证MCP服务ID和slug_name支持功能

使用方法:
python test_service_id_slug_support.py

此脚本将：
1. 创建一个测试服务
2. 验证通过service_id访问
3. 验证通过slug_name访问
4. 清理测试数据
"""

import uuid
import requests
import json
from datetime import datetime, timezone

# 测试配置
API_BASE_URL = "http://localhost:8003"  # API服务端口
TEST_SERVICE_NAME = "Test Weather Service"
TEST_SLUG_NAME = "test_weather_service"

def create_test_service():
    """创建一个测试服务用于测试"""
    service_id = str(uuid.uuid4())
    
    # 这里应该调用管理后台API创建服务，但为了简化示例，
    # 我们假设服务已经存在
    print(f"创建测试服务:")
    print(f"  Service ID: {service_id}")
    print(f"  Service Name: {TEST_SERVICE_NAME}")
    print(f"  Slug Name: {TEST_SLUG_NAME}")
    
    return service_id

def test_service_status(identifier, identifier_type):
    """测试服务状态端点"""
    url = f"{API_BASE_URL}/mcp/status/{identifier}"
    
    try:
        response = requests.get(url)
        print(f"\n测试 {identifier_type} 访问:")
        print(f"  请求URL: {url}")
        print(f"  响应状态: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  服务状态: {data.get('status', 'unknown')}")
            print(f"  服务名称: {data.get('service_name', 'unknown')}")
            print(f"  实际Service ID: {data.get('service_id', 'unknown')}")
            print(f"  标识符: {data.get('service_identifier', 'unknown')}")
            return True
        else:
            print(f"  错误信息: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"  请求失败: {e}")
        return False

def test_root_endpoint():
    """测试根端点，查看服务信息"""
    url = f"{API_BASE_URL}/"
    
    try:
        response = requests.get(url)
        print(f"\n测试根端点:")
        print(f"  请求URL: {url}")
        print(f"  响应状态: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  服务版本: {data.get('version', 'unknown')}")
            print(f"  ID支持说明: {data.get('service_id_support', 'unknown')}")
            return True
        else:
            print(f"  错误信息: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"  请求失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=== MCP Service ID 和 Slug Name 支持测试 ===")
    
    # 测试根端点
    test_root_endpoint()
    
    # 创建测试服务 (实际环境中需要通过管理后台API)
    service_id = create_test_service()
    
    print(f"\n注意：此测试脚本假设数据库中已存在以下测试数据：")
    print(f"  - Service ID: {service_id}")
    print(f"  - Slug Name: {TEST_SLUG_NAME}")
    print(f"  请手动在管理后台创建此服务，或修改脚本中的测试数据")
    
    # 测试通过Service ID访问
    success_id = test_service_status(service_id, "Service ID")
    
    # 测试通过Slug Name访问
    success_slug = test_service_status(TEST_SLUG_NAME, "Slug Name")
    
    # 测试不存在的标识符
    test_service_status("non_existent_service", "不存在的标识符")
    
    print(f"\n=== 测试结果 ===")
    print(f"Service ID 访问: {'✅ 成功' if success_id else '❌ 失败'}")
    print(f"Slug Name 访问: {'✅ 成功' if success_slug else '❌ 失败'}")
    
    if success_id and success_slug:
        print(f"\n🎉 所有测试通过！MCP服务现在支持Service ID和Slug Name两种访问方式。")
    else:
        print(f"\n⚠️  部分测试失败，请检查服务配置和数据库数据。")
    
    print(f"\n使用建议：")
    print(f"  - 在MCP客户端配置中，推荐使用Slug Name以提高可读性")
    print(f"  - 例如: /mcp/sse/{TEST_SLUG_NAME}?apikey=your_key")

if __name__ == "__main__":
    main()
