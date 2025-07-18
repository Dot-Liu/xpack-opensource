#!/usr/bin/env python3
"""
测试 update 方法的 update_type 功能
"""

import sys
import os
import requests
import json

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_update_with_openapi_type():
    """测试 update_type="openapi" 的功能"""
    
    # 服务端点
    base_url = "http://localhost:8000"  # 假设服务运行在8000端口
    
    # 测试参数
    service_id = "test-service-id"  # 需要替换为实际存在的服务ID
    
    print("=== 测试 update_type='openapi' 功能 ===")
    
    # 第一步：先通过 openapi_parse_update 创建临时数据
    print("1. 通过 openapi_parse_update 创建临时数据...")
    openapi_url = "https://petstore.swagger.io/v2/swagger.json"
    
    update_data = {
        "id": service_id,
        "url": openapi_url
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/mcp/openapi_parse_update",
            data=update_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ 临时数据创建成功!")
                print(f"临时服务名称: {result['data']['name']}")
                print(f"临时API数量: {len(result['data']['apis'])}")
            else:
                print("❌ 创建临时数据失败:")
                print(f"错误信息: {result.get('error_message', '未知错误')}")
                return
        else:
            print(f"❌ 创建临时数据HTTP请求失败: {response.status_code}")
            return
            
    except Exception as e:
        print(f"❌ 创建临时数据异常: {e}")
        return
    
    # 第二步：使用 update_type="openapi" 应用临时数据
    print("\n2. 使用 update_type='openapi' 应用临时数据...")
    
    apply_data = {
        "id": service_id,
        "update_type": "openapi",
        "base_url": "https://api.example.com",  # 额外设置一些字段
        "enabled": 1
    }
    
    try:
        response = requests.put(
            f"{base_url}/api/mcp/service",
            json=apply_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ OpenAPI数据应用成功!")
                
                # 第三步：验证数据是否正确应用
                print("\n3. 验证应用结果...")
                verify_response = requests.get(
                    f"{base_url}/api/mcp/service/info?id={service_id}",
                    timeout=30
                )
                
                if verify_response.status_code == 200:
                    verify_result = verify_response.json()
                    if verify_result.get("success"):
                        service_info = verify_result['data']
                        print(f"✅ 验证成功!")
                        print(f"服务名称: {service_info['name']}")
                        print(f"Base URL: {service_info['base_url']}")
                        print(f"启用状态: {service_info['enabled']}")
                        print(f"API数量: {len(service_info['apis'])}")
                        
                        # 显示前3个API
                        apis = service_info['apis']
                        print("\nAPI列表:")
                        for i, api in enumerate(apis[:3]):
                            print(f"  {i+1}. {api['name']} - {api['description']}")
                        if len(apis) > 3:
                            print(f"  ... 还有 {len(apis) - 3} 个API")
                    else:
                        print("❌ 验证失败:")
                        print(f"错误信息: {verify_result.get('error_message', '未知错误')}")
                else:
                    print(f"❌ 验证HTTP请求失败: {verify_response.status_code}")
                        
            else:
                print("❌ 应用OpenAPI数据失败:")
                print(f"错误信息: {result.get('error_message', '未知错误')}")
        else:
            print(f"❌ 应用数据HTTP请求失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except Exception as e:
        print(f"❌ 应用数据异常: {e}")


def test_update_with_default_type():
    """测试 update_type="default" 的功能（传统更新）"""
    
    base_url = "http://localhost:8000"
    service_id = "test-service-id"  # 需要替换为实际存在的服务ID
    
    print("\n=== 测试 update_type='default' 功能 ===")
    
    # 传统的字段更新
    update_data = {
        "id": service_id,
        "update_type": "default",  # 可选，默认就是 default
        "name": "Updated Service Name",
        "short_description": "Updated description",
        "tags": "updated,test"
    }
    
    try:
        response = requests.put(
            f"{base_url}/api/mcp/service",
            json=update_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ 传统更新成功!")
            else:
                print("❌ 传统更新失败:")
                print(f"错误信息: {result.get('error_message', '未知错误')}")
        else:
            print(f"❌ 传统更新HTTP请求失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except Exception as e:
        print(f"❌ 传统更新异常: {e}")


def print_usage():
    """打印使用说明"""
    print("""
使用说明:
1. 确保后端服务正在运行 (默认端口8000)
2. 替换代码中的 service_id 为实际存在的服务ID
3. 运行此脚本: python test_update_type.py

测试流程:
1. 先通过 openapi_parse_update 创建临时数据
2. 使用 update_type='openapi' 应用临时数据到正式表
3. 验证数据是否正确迁移和清理
4. 测试传统的 update_type='default' 功能

注意:
- 这个测试会实际修改数据库中的服务数据
- 建议在测试环境中运行
- 需要有效的管理员权限
""")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print_usage()
    else:
        # 测试 OpenAPI 类型更新
        test_update_with_openapi_type()
        
        # 测试传统类型更新
        test_update_with_default_type()
        
        print("\n=== 测试完成 ===")
