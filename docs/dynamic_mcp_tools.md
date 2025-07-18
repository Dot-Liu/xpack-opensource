# 动态MCP工具服务使用说明

## 功能概述

这个实现支持根据不同的 `service_id` 从数据库中动态获取和返回不同的MCP工具列表，实现了多租户/多服务的工具管理。每个服务都可以配置独立的base_url和认证信息。

## 主要特性

1. **动态工具加载**：根据 `service_id` 从数据库中查询对应的工具配置
2. **自动Schema生成**：将数据库中的API配置自动转换为MCP工具Schema
3. **HTTP请求代理**：自动将MCP工具调用转换为HTTP API请求
4. **多参数类型支持**：支持路径参数、查询参数、请求头和请求体参数
5. **服务级认证**：支持每个服务独立的base_url和认证配置
6. **智能URL拼接**：自动处理base_url与API路径的拼接

## API使用

### 连接端点
```
GET /sse/{service_id}
```

其中 `{service_id}` 是您要访问的服务标识符。

### 示例
- `/sse/user-service` - 访问用户服务的工具
- `/sse/payment-service` - 访问支付服务的工具
- `/sse/notification-service` - 访问通知服务的工具

## 数据库配置

### 服务配置表 (mcp_service)

存储服务的基本信息和认证配置：

- `id`: 服务唯一标识符
- `name`: 服务名称
- `base_url`: 服务的基础URL
- `auth_method`: 认证方法 (free/apikey/token)
- `auth_header`: 认证头名称 (如: Authorization, X-API-Key)
- `auth_token`: 认证令牌值
- `enabled`: 启用状态

### 工具配置表 (mcp_tool_api)

存储具体的API工具配置：

- `service_id`: 关联的服务ID
- `name`: 工具名称
- `description`: 工具描述
- `path`: API请求路径 (相对或绝对路径)
- `method`: HTTP方法
- `path_parameters`: 路径参数定义（JSON格式）
- `query_parameters`: 查询参数定义（JSON格式）
- `header_parameters`: 请求头参数定义（JSON格式）
- `request_body_schema`: 请求体Schema（JSON格式）
- `enabled`: 启用状态（1=启用，0=禁用）

### 参数格式示例

#### 路径参数
```json
[
  {
    "name": "user_id",
    "type": "string",
    "description": "用户ID",
    "required": true
  }
]
```

#### 查询参数
```json
[
  {
    "name": "page",
    "type": "integer",
    "description": "页码",
    "required": false
  },
  {
    "name": "limit",
    "type": "integer",
    "description": "每页数量",
    "required": false
  }
]
```

#### 请求体Schema
```json
{
  "type": "object",
  "properties": {
    "name": {
      "type": "string",
      "description": "用户姓名"
    },
    "email": {
      "type": "string",
      "description": "用户邮箱"
    }
  },
  "required": ["name", "email"]
}
```

## 启动服务

```bash
python services/api_service/mcp/mcp_server.py
```

服务将在 `http://127.0.0.1:8801` 启动。

## 测试

使用提供的测试脚本验证功能：

```bash
python test_dynamic_mcp.py
```

## 配置示例

#### 服务配置示例
```sql
INSERT INTO mcp_service (
    id, name, base_url, auth_method, auth_header, auth_token, 
    charge_type, price, enabled
) VALUES (
    'user-service-001', 
    'User Management Service',
    'https://api.example.com/v1',
    'apikey',
    'X-API-Key',
    'your-api-key-here',
    'free',
    0.00,
    1
);
```

#### URL拼接规则

1. **绝对路径**：如果工具的path是完整URL（以http://或https://开头），则直接使用
   ```
   工具path: "https://external-api.com/users"
   最终URL: "https://external-api.com/users"
   ```

2. **相对路径**：如果工具的path是相对路径，则与服务的base_url拼接
   ```
   服务base_url: "https://api.example.com/v1"
   工具path: "/users/{id}"
   最终URL: "https://api.example.com/v1/users/{id}"
   ```

3. **智能处理**：自动处理多余的斜杠
   ```
   服务base_url: "https://api.example.com/v1/"
   工具path: "/users/{id}"
   最终URL: "https://api.example.com/v1/users/{id}"
   ```

#### 认证配置

1. **免费访问**
   ```json
   {
     "auth_method": "free"
   }
   ```

2. **API Key认证**
   ```json
   {
     "auth_method": "apikey",
     "auth_header": "X-API-Key",
     "auth_token": "your-api-key"
   }
   ```

3. **Bearer Token认证**
   ```json
   {
     "auth_method": "token", 
     "auth_header": "Authorization",
     "auth_token": "Bearer your-token"
   }
   ```

## 工作流程

### 1. 工具列表查询流程
```
客户端请求 /sse/{service_id}
    ↓
系统查询 mcp_service 表获取服务信息
    ↓  
系统查询 mcp_tool_api 表获取工具列表
    ↓
转换为 MCP Tool 格式返回给客户端
```

### 2. 工具执行流程
```
客户端调用工具
    ↓
系统获取工具配置和服务认证信息
    ↓
构建完整的API URL (base_url + path)
    ↓
添加认证头信息
    ↓
处理参数映射 (路径/查询/请求体)
    ↓
发起HTTP请求
    ↓
返回响应结果
```

## 测试

使用提供的测试脚本验证功能：

```bash
# 基础功能测试
python test_dynamic_mcp.py

# 增强功能测试（包含认证信息）
python test_enhanced_mcp.py
```

## 架构说明

### 核心组件

1. **McpService**: 业务逻辑层，负责工具的查询和转换
2. **McpToolApiRepository**: 数据访问层，负责数据库操作
3. **create_mcp_server()**: 为指定service_id创建MCP服务器实例
4. **execute_tool()**: 执行工具调用，将MCP调用转换为HTTP请求

### 数据流

1. 客户端连接 `/sse/{service_id}`
2. 系统根据 `service_id` 查询数据库中的工具配置
3. 将工具配置转换为MCP Tool格式
4. 客户端调用工具时，系统将调用转换为HTTP请求
5. 返回API响应结果

## 架构优势

### 增强特性

1. **服务级配置**：每个服务独立的base_url和认证设置
2. **灵活的URL处理**：支持绝对和相对路径
3. **多种认证方式**：支持免费、API Key、Bearer Token等
4. **自动参数映射**：智能处理各种参数类型
5. **错误处理**：完善的异常处理和错误响应

### 扩展性

- **新增服务**：只需在mcp_service表中添加配置
- **新增工具**：在mcp_tool_api表中添加工具配置
- **修改认证**：直接更新服务配置即可
- **URL变更**：支持动态修改base_url

## 注意事项

1. **安全性**：认证token应妥善保管，避免明文存储
2. **URL格式**：确保base_url和path的格式正确
3. **参数验证**：工具参数的JSON Schema应准确定义
4. **错误处理**：API调用失败时会返回错误信息
5. **性能考虑**：数据库连接会在每次调用时创建和关闭

## 最佳实践

1. **服务分组**：按业务模块组织不同的service_id
2. **统一认证**：同一服务下的工具共享认证配置
3. **版本管理**：通过base_url区分不同版本的API
4. **监控日志**：记录工具调用情况和错误信息
5. **缓存策略**：可考虑缓存服务配置以提高性能
