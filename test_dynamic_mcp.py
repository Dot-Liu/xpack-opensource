"""
测试动态MCP工具功能的脚本
"""
import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from services.common.database import get_db, init_db
from services.api_service.repositories.mcp_tool_api_repository import McpToolApiRepository
from services.api_service.services.mcp_service import McpService


async def test_mcp_service():
    """测试MCP服务功能"""
    try:
        # 初始化数据库（如果需要）
        # init_db()
        
        # 获取数据库连接
        db = next(get_db())
        
        try:
            # 创建仓储和服务实例
            repository = McpToolApiRepository(db)
            mcp_service = McpService(repository)
            
            # 测试service_id
            test_service_id = "test-service-001"
            
            print(f"测试服务ID: {test_service_id}")
            
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
                    print(f"找到工具配置: {tool_config.name}")
                    print(f"  路径: {tool_config.path}")
                    print(f"  方法: {tool_config.method.value}")
                else:
                    print(f"未找到工具配置: {first_tool_name}")
            else:
                print("没有找到任何工具，请检查数据库中是否有对应的mcp_tool_api记录")
                
        finally:
            db.close()
            
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_mcp_service())
