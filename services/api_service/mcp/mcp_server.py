import anyio
import click
import json
import mcp.types as types
from typing import List
from mcp.server.lowlevel import Server
from mcp.shared._httpx_utils import create_mcp_http_client
from services.common.database import get_db
from services.api_service.repositories.mcp_tool_api_repository import McpToolApiRepository
from services.api_service.repositories.mcp_service_repository import McpServiceRepository
from services.api_service.services.mcp_service import McpService


async def fetch_website(
    url: str,
) -> list[types.ContentBlock]:
    headers = {"User-Agent": "MCP Test Server (github.com/modelcontextprotocol/python-sdk)"}
    async with create_mcp_http_client(headers=headers) as client:
        response = await client.get(url)
        response.raise_for_status()
        return [types.TextContent(type="text", text=response.text)]


def main(port: int, transport: str) -> int:
    from mcp.server.sse import SseServerTransport
    from starlette.applications import Starlette
    from starlette.responses import Response
    from starlette.routing import Mount, Route
    import uvicorn

    sse = SseServerTransport("/messages/")

    async def handle_sse(request):
        # 从URL路径中提取service_id
        service_id = request.path_params.get("service_id")
        print(f"[MCP Server] 收到SSE连接请求 - 服务ID: {service_id}")
        
        if not service_id:
            print(f"[MCP Server] 错误: 缺少service_id参数")
            return Response("Missing service_id parameter", status_code=400)

        print(f"[MCP Server] 为服务 {service_id} 创建MCP服务器实例")
        # 创建带有service_id的MCP服务器
        app = create_mcp_server(service_id)

        async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
            print(f"[MCP Server] SSE连接已建立 - 服务ID: {service_id}")
            si = app.create_initialization_options()
            si.server_name = f"mcp-service-{service_id}"
            print(f"[MCP Server] 服务器名称设置为: {si.server_name}")
            await app.run(streams[0], streams[1], si)
            print(f"[MCP Server] MCP服务器运行结束 - 服务ID: {service_id}")
        return Response()

    starlette_app = Starlette(
        debug=True,
        routes=[
            Route("/sse/{service_id}", endpoint=handle_sse, methods=["GET"]),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )

    uvicorn.run(starlette_app, host="127.0.0.1", port=port)
    return 0


def create_mcp_server(service_id: str) -> Server:
    """
    为指定的service_id创建MCP服务器

    Args:
        service_id: 服务ID

    Returns:
        Server: 配置好的MCP服务器实例
    """
    print(f"[MCP Server] 创建MCP服务器实例 - 服务ID: {service_id}")
    app = Server(f"mcp-service-{service_id}")
    print(f"[MCP Server] MCP服务器实例创建完成")

    @app.list_tools()
    async def list_tools() -> List[types.Tool]:
        """返回该服务可用的工具列表"""
        print(f"[MCP Server] 收到工具列表查询请求 - 服务ID: {service_id}")
        
        # 获取数据库连接和服务实例
        db = next(get_db())
        try:
            tool_api_repository = McpToolApiRepository(db)
            service_repository = McpServiceRepository(db)
            mcp_service = McpService(tool_api_repository, service_repository)
            
            tools = mcp_service.get_tools_by_service_id(service_id)
            print(f"[MCP Server] 找到 {len(tools)} 个工具")
            for tool in tools:
                print(f"[MCP Server]   - {tool.name}: {tool.description}")
            
            return tools
        finally:
            db.close()

    @app.call_tool()
    async def call_tool(name: str, arguments: dict) -> List[types.ContentBlock]:
        """执行指定的工具"""
        print(f"[MCP Server] 收到工具调用请求 - 服务ID: {service_id}, 工具名称: {name}")
        print(f"[MCP Server] 工具参数: {arguments}")
        
        # 获取数据库连接和服务实例
        db = next(get_db())
        try:
            tool_api_repository = McpToolApiRepository(db)
            service_repository = McpServiceRepository(db)
            mcp_service = McpService(tool_api_repository, service_repository)

            # 查找工具配置
            print(f"[MCP Server] 查找工具配置...")
            tool_config = mcp_service.get_tool_by_name(service_id, name)
            if not tool_config:
                error_msg = f"Unknown tool: {name}"
                print(f"[MCP Server] 错误: {error_msg}")
                raise ValueError(error_msg)

            print(f"[MCP Server] 找到工具配置: {tool_config.name}")

            # 获取服务认证信息
            print(f"[MCP Server] 获取服务认证信息...")
            auth_info = mcp_service.get_service_auth_info(service_id)
            print(f"[MCP Server] 认证信息: {auth_info}")

            # 根据工具配置执行相应的逻辑
            print(f"[MCP Server] 开始执行工具...")
            return await execute_tool(tool_config, arguments, auth_info)
        finally:
            db.close()
            print(f"[MCP Server] 数据库连接已关闭")

    return app


async def execute_tool(tool_config, arguments: dict, auth_info: dict) -> List[types.ContentBlock]:
    """
    执行工具调用

    Args:
        tool_config: 工具配置
        arguments: 工具参数
        auth_info: 服务认证信息

    Returns:
        List[types.ContentBlock]: 执行结果
    """
    try:
        print(f"[MCP Tool] 开始执行工具: {tool_config.name}")
        print(f"[MCP Tool] 原始路径: {tool_config.path}")
        print(f"[MCP Tool] HTTP方法: {tool_config.method.value}")
        print(f"[MCP Tool] 传入参数: {arguments}")
        
        # 构建请求URL
        base_url = auth_info.get("base_url", "")
        url = tool_config.path
        
        print(f"[MCP Tool] 服务Base URL: {base_url}")
        
        # 如果工具路径不是完整URL，则拼接base_url
        if not url.startswith(("http://", "https://")) and base_url:
            # 确保base_url末尾没有斜杠，path开头没有斜杠
            base_url = base_url.rstrip("/")
            url = url.lstrip("/")
            url = f"{base_url}/{url}"
            print(f"[MCP Tool] URL拼接完成: {url}")
        else:
            print(f"[MCP Tool] 使用原始URL: {url}")

        # 替换路径参数
        if tool_config.path_parameters:
            try:
                path_params = json.loads(tool_config.path_parameters)
                print(f"[MCP Tool] 处理路径参数: {path_params}")
                for param in path_params:
                    if isinstance(param, dict) and "name" in param:
                        param_name = param["name"]
                        if param_name in arguments:
                            old_url = url
                            url = url.replace(f"{{{param_name}}}", str(arguments[param_name]))
                            print(f"[MCP Tool] 路径参数替换: {param_name} = {arguments[param_name]}")
                print(f"[MCP Tool] 路径参数替换后URL: {url}")
            except (json.JSONDecodeError, TypeError) as e:
                print(f"[MCP Tool] 路径参数解析失败: {e}")

        # 构建查询参数
        query_params = {}
        if tool_config.query_parameters:
            try:
                query_param_defs = json.loads(tool_config.query_parameters)
                print(f"[MCP Tool] 处理查询参数定义: {query_param_defs}")
                for param in query_param_defs:
                    if isinstance(param, dict) and "name" in param:
                        param_name = param["name"]
                        if param_name in arguments:
                            query_params[param_name] = arguments[param_name]
                print(f"[MCP Tool] 构建的查询参数: {query_params}")
            except (json.JSONDecodeError, TypeError) as e:
                print(f"[MCP Tool] 查询参数解析失败: {e}")

        # 构建请求头
        headers = {"User-Agent": "MCP Tool Server (XPack)"}
        
        # 添加认证头
        auth_method = auth_info.get("auth_method", "free")
        print(f"[MCP Tool] 认证方法: {auth_method}")
        if auth_method != "free":
            auth_header = auth_info.get("auth_header")
            auth_token = auth_info.get("auth_token")
            if auth_header and auth_token:
                headers[auth_header] = auth_token
                print(f"[MCP Tool] 添加认证头: {auth_header} = {auth_token[:8]}..." if len(auth_token) > 8 else f"{auth_header} = ***")
        
        # 处理自定义请求头参数
        if tool_config.header_parameters:
            try:
                header_params = json.loads(tool_config.header_parameters)
                print(f"[MCP Tool] 处理自定义请求头: {header_params}")
                for param in header_params:
                    if isinstance(param, dict) and "name" in param:
                        param_name = param["name"]
                        if param_name in arguments:
                            headers[param_name] = str(arguments[param_name])
                            print(f"[MCP Tool] 添加自定义请求头: {param_name} = {arguments[param_name]}")
            except (json.JSONDecodeError, TypeError) as e:
                print(f"[MCP Tool] 请求头参数解析失败: {e}")

        print(f"[MCP Tool] 最终请求头: {headers}")

        # 构建请求体
        request_body = None
        if tool_config.request_body_schema and tool_config.method.value in ["POST", "PUT", "PATCH"]:
            try:
                body_schema = json.loads(tool_config.request_body_schema)
                print(f"[MCP Tool] 请求体Schema: {body_schema}")
                if isinstance(body_schema, dict) and "properties" in body_schema:
                    request_body = {}
                    for prop_name in body_schema["properties"]:
                        if prop_name in arguments:
                            request_body[prop_name] = arguments[prop_name]
                    print(f"[MCP Tool] 构建的请求体: {request_body}")
            except (json.JSONDecodeError, TypeError) as e:
                print(f"[MCP Tool] 请求体Schema解析失败: {e}")

        # 打印最终请求信息
        print(f"[MCP Tool] ===== 最终请求信息 =====")
        print(f"[MCP Tool] URL: {url}")
        print(f"[MCP Tool] 方法: {tool_config.method.value}")
        print(f"[MCP Tool] 查询参数: {query_params}")
        print(f"[MCP Tool] 请求体: {request_body}")
        print(f"[MCP Tool] ========================")

        # 发起HTTP请求
        async with create_mcp_http_client(headers=headers) as client:
            print(f"[MCP Tool] 开始发起HTTP请求...")
            if tool_config.method.value == "GET":
                response = await client.get(url, params=query_params)
            elif tool_config.method.value == "POST":
                response = await client.post(url, params=query_params, json=request_body)
            elif tool_config.method.value == "PUT":
                response = await client.put(url, params=query_params, json=request_body)
            elif tool_config.method.value == "DELETE":
                response = await client.delete(url, params=query_params)
            elif tool_config.method.value == "PATCH":
                response = await client.patch(url, params=query_params, json=request_body)
            else:
                raise ValueError(f"Unsupported HTTP method: {tool_config.method.value}")

            print(f"[MCP Tool] HTTP响应状态码: {response.status_code}")
            print(f"[MCP Tool] HTTP响应头: {dict(response.headers)}")
            
            response.raise_for_status()

            # 打印响应内容长度
            response_text = response.text
            print(f"[MCP Tool] 响应内容长度: {len(response_text)} 字符")
            print(f"[MCP Tool] 响应内容预览: {response_text[:200]}..." if len(response_text) > 200 else f"[MCP Tool] 响应内容: {response_text}")

            # 返回响应结果
            print(f"[MCP Tool] 工具执行成功完成")
            return [types.TextContent(type="text", text=response_text)]

    except Exception as e:
        error_msg = f"Tool execution failed: {str(e)}"
        print(f"[MCP Tool] 工具执行失败: {error_msg}")
        print(f"[MCP Tool] 异常详情: {type(e).__name__}")
        import traceback
        print(f"[MCP Tool] 异常堆栈: {traceback.format_exc()}")
        return [types.TextContent(type="text", text=error_msg)]


if __name__ == "__main__":
    main(8801, "streamable-http")
