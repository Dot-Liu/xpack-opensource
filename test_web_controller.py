#!/usr/bin/env python3
"""
测试 web_controller 的实现
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from services.common.database import get_db
from services.admin_service.services.mcp_manager_service import McpManagerService
from services.admin_service.repositories.mcp_service_repository import McpServiceRepository

def test_public_services():
    """测试公开服务查询功能"""
    # 获取数据库会话
    db: Session = next(get_db())
    
    try:
        # 测试 Repository 方法
        print("=== 测试 McpServiceRepository.get_public_services_paginated ===")
        repo = McpServiceRepository(db)
        services, total = repo.get_public_services_paginated("", 1, 10)
        print(f"找到 {total} 个启用的服务")
        for service in services[:3]:  # 只显示前3个
            print(f"- {service.name}: {service.short_description}")
        
        # 测试 Service 方法
        print("\n=== 测试 McpManagerService.get_public_services_paginated ===")
        service_manager = McpManagerService(db)
        service_list, total = service_manager.get_public_services_paginated("", 1, 10)
        print(f"找到 {total} 个格式化后的服务")
        for service_info in service_list[:3]:  # 只显示前3个
            print(f"- {service_info['name']}: {len(service_info['apis'])} 个API")
        
        # 测试服务详细信息获取
        if service_list:
            print("\n=== 测试 McpManagerService.get_public_service_info ===")
            first_service_id = service_list[0]['id']
            service_detail = service_manager.get_public_service_info(first_service_id)
            if service_detail:
                print(f"服务详情: {service_detail['name']}")
                print(f"- 计费方式: {service_detail['charge_type']}")
                print(f"- 价格: {service_detail['price']}")
                print(f"- API数量: {len(service_detail['apis'])}")
                for api in service_detail['apis'][:2]:  # 只显示前2个API
                    print(f"  * {api['name']}: {api['description']}")
            else:
                print("服务详情获取失败")
            
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_public_services()
