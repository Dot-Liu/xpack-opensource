#!/usr/bin/env python3
"""
测试 openapi_parse_update 接口的功能
"""

import sys
import os
import requests
import json

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_openapi_parse_update():
    """测试 openapi_parse_update 接口"""
    
    # 服务端点
    base_url = "http://localhost:8000"  # 假设服务运行在8000端口
    
    # 测试参数
    service_id = "test-service-id"  # 需要替换为实际存在的服务ID
    openapi_url = "https://petstore.swagger.io/v2/swagger.json"
    
    # 构建请求数据
    data = {
        "id": service_id,
        "url": openapi_url
    }
    
    try:
        print(f"正在测试更新服务 {service_id}...")
        print(f"使用OpenAPI URL: {openapi_url}")
        
        # 发送POST请求
        response = requests.post(
            f"{base_url}/api/mcp/openapi_parse_update",
            data=data,
            timeout=30
        )
        
        # 检查响应
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ 接口测试成功!")
                print(f"服务名称: {result['data']['name']}")
                print(f"API数量: {len(result['data']['apis'])}")
                print(f"服务描述: {result['data']['short_description']}")
                
                # 显示前3个API
                apis = result['data']['apis']
                print("\nAPI列表预览:")
                for i, api in enumerate(apis[:3]):
                    print(f"  {i+1}. {api['name']} - {api['description']}")
                if len(apis) > 3:
                    print(f"  ... 还有 {len(apis) - 3} 个API")
                    
            else:
                print("❌ 接口返回失败:")
                print(f"错误信息: {result.get('error_message', '未知错误')}")
        else:
            print(f"❌ HTTP请求失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求异常: {e}")
    except Exception as e:
        print(f"❌ 未知错误: {e}")


def print_usage():
    """打印使用说明"""
    print("""
使用说明:
1. 确保后端服务正在运行 (默认端口8000)
2. 替换 test_openapi_parse_update() 中的 service_id 为实际存在的服务ID
3. 运行此脚本: python test_openapi_parse_update.py

注意:
- 此脚本仅用于测试新接口的基本功能
- 需要有效的管理员权限和现有的服务ID
- 数据会保存到临时表中，不会影响正式数据
""")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print_usage()
    else:
        test_openapi_parse_update()
