# MCP Service ID 和 Slug Name 支持说明

## 功能概述

MCP Streamable HTTP 服务现在支持通过两种方式访问服务：

1. **Service ID（UUID）**: 例如 `a1b2c3d4-e5f6-7890-abcd-ef1234567890`
2. **Slug Name**: 例如 `weather_service` 或 `openai_gpt_4`

## API 端点

所有涉及 `{service_id}` 参数的端点现在都支持两种模式：

### SSE 连接端点
- 使用 Service ID: `/mcp/sse/a1b2c3d4-e5f6-7890-abcd-ef1234567890`
- 使用 Slug Name: `/mcp/sse/weather_service`

### 服务状态检查端点
- 使用 Service ID: `/mcp/status/a1b2c3d4-e5f6-7890-abcd-ef1234567890`
- 使用 Slug Name: `/mcp/status/weather_service`

## 实现细节

### 查找优先级
系统按以下顺序查找服务：
1. 首先尝试按 Service ID 查找
2. 如果未找到，再按 Slug Name 查找
3. 如果都未找到，返回错误

### 日志记录
- 查找到服务时会记录调试日志，显示找到的服务名称和实际的 Service ID
- 未找到服务时会记录警告日志

### 错误处理
- 如果提供的标识符既不是有效的 Service ID 也不是存在的 Slug Name，返回 400 错误
- 数据库查询异常时会记录错误日志并返回服务器错误

## 使用示例

### MCP 客户端配置

#### 使用 Service ID
```json
{
    "mcpServers": {
        "weather-service": {
            "url": "https://api.xpack.ai/mcp/sse/a1b2c3d4-e5f6-7890-abcd-ef1234567890?apikey=your_api_key"
        }
    }
}
```

#### 使用 Slug Name (推荐)
```json
{
    "mcpServers": {
        "weather-service": {
            "url": "https://api.xpack.ai/mcp/sse/weather_service?apikey=your_api_key"
        }
    }
}
```

### 状态检查

#### 使用 Service ID
```bash
curl "https://api.xpack.ai/mcp/status/a1b2c3d4-e5f6-7890-abcd-ef1234567890"
```

#### 使用 Slug Name
```bash
curl "https://api.xpack.ai/mcp/status/weather_service"
```

### 响应格式

状态检查端点的响应现在包含更多信息：

```json
{
    "service_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "service_identifier": "weather_service",
    "service_name": "Weather Service API",
    "status": "available",
    "protocol": "streamable-http",
    "endpoint": "/mcp/sse/weather_service",
    "message": "Service is ready for connections",
    "active_connections": 2,
    "reconnect_supported": true
}
```

## 优势

1. **用户友好**: Slug Name 更容易记忆和使用
2. **向后兼容**: 现有的 Service ID 方式继续工作
3. **灵活性**: 开发者可以选择适合的标识符类型
4. **一致性**: 所有相关 API 端点都支持两种模式

## 注意事项

1. Slug Name 必须在数据库中唯一
2. Slug Name 由管理员在创建或导入服务时自动生成
3. 建议在生产环境中使用 Slug Name 以提高可读性
4. Service ID 在内部系统中仍然是主要标识符
