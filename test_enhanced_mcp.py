"""
测试增强的动态MCP工具功能的脚本（包含base_url和认证信息）
"""
import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from services.common.database import get_db, init_db
from services.api_service.repositories.mcp_tool_api_repository import McpToolApiRepository
from services.api_service.repositories.mcp_service_repository import McpServiceRepository
from services.api_service.services.mcp_service import McpService


async def test_enhanced_mcp_service():
    """测试增强的MCP服务功能"""
    try:
        # 初始化数据库（如果需要）
        # init_db()
        
        # 获取数据库连接
        db = next(get_db())
        
        try:
            # 创建仓储和服务实例
            tool_api_repository = McpToolApiRepository(db)
            service_repository = McpServiceRepository(db)
            mcp_service = McpService(tool_api_repository, service_repository)
            
            # 测试service_id
            test_service_id = "test-service-001"
            
            print(f"测试服务ID: {test_service_id}")
            print("=" * 50)
            
            # 获取服务信息
            service_info = mcp_service.get_service_by_id(test_service_id)
            if service_info:
                print(f"服务信息:")
                print(f"  名称: {service_info.name}")
                print(f"  Base URL: {service_info.base_url}")
                print(f"  认证方法: {service_info.auth_method.value}")
                print(f"  认证头: {service_info.auth_header}")
                print(f"  价格类型: {service_info.charge_type.value}")
                print()
            else:
                print("未找到服务信息")
                print()
            
            # 获取认证信息
            auth_info = mcp_service.get_service_auth_info(test_service_id)
            print(f"认证信息:")
            for key, value in auth_info.items():
                if key == "auth_token" and value:
                    # 隐藏token的部分信息
                    masked_value = value[:8] + "..." if len(value) > 8 else "***"
                    print(f"  {key}: {masked_value}")
                else:
                    print(f"  {key}: {value}")
            print()
            
            # 获取工具列表
            tools = mcp_service.get_tools_by_service_id(test_service_id)
            
            print(f"找到 {len(tools)} 个工具:")
            for tool in tools:
                print(f"  - {tool.name}: {tool.description}")
                print(f"    输入schema: {tool.inputSchema}")
                print()
            
            if tools:
                # 测试获取单个工具
                first_tool_name = tools[0].name
                tool_config = mcp_service.get_tool_by_name(test_service_id, first_tool_name)
                if tool_config:
                    print(f"工具配置详情: {tool_config.name}")
                    print(f"  原始路径: {tool_config.path}")
                    print(f"  方法: {tool_config.method.value}")
                    
                    # 演示URL拼接逻辑
                    base_url = auth_info.get("base_url", "")
                    if base_url and not tool_config.path.startswith(("http://", "https://")):
                        base_url_clean = base_url.rstrip("/")
                        path_clean = tool_config.path.lstrip("/")
                        full_url = f"{base_url_clean}/{path_clean}"
                        print(f"  完整URL: {full_url}")
                    else:
                        print(f"  完整URL: {tool_config.path}")
                else:
                    print(f"未找到工具配置: {first_tool_name}")
            else:
                print("没有找到任何工具，请检查数据库中是否有对应的记录")
                print("需要确保以下表中有数据:")
                print("  - mcp_service: 服务基本信息")
                print("  - mcp_tool_api: 工具API配置")
                
        finally:
            db.close()
            
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_enhanced_mcp_service())
