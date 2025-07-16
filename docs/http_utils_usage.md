# HTTP工具类使用示例

## 概述

`HttpUtils` 是一个通用的HTTP请求工具类，提供了下载文件、验证URL、获取URL信息等功能。它被`MCPManager`使用来处理OpenAPI文档的下载。

## 主要功能

### 1. 下载内容 (`download_content_from_url`)

从指定URL下载内容，支持多种配置选项：

```python
from services.common.utils.http_utils import HttpUtils

# 基本使用
content = await HttpUtils.download_content_from_url("https://example.com/api.json")

# 高级配置
content = await HttpUtils.download_content_from_url(
    url="https://example.com/api.yaml",
    timeout=60,  # 60秒超时
    max_file_size=20 * 1024 * 1024,  # 20MB最大文件大小
    allowed_content_types=["application/yaml", "text/yaml"],
    headers={"Authorization": "Bearer token123"}
)
```

### 2. 验证URL可访问性 (`validate_url_accessibility`)

快速检查URL是否可访问：

```python
is_accessible = await HttpUtils.validate_url_accessibility("https://example.com/api.json")
if is_accessible:
    print("URL可以访问")
else:
    print("URL无法访问")
```

### 3. 获取URL信息 (`get_url_info`)

获取URL的详细信息：

```python
info = await HttpUtils.get_url_info("https://example.com/api.json")
print(f"状态码: {info['status']}")
print(f"内容类型: {info['content_type']}")
print(f"内容长度: {info['content_length']}")
print(f"最后修改时间: {info['last_modified']}")
print(f"服务器: {info['server']}")
print(f"是否可访问: {info['accessible']}")
```

### 4. 发送JSON POST请求 (`post_json`)

发送JSON数据到指定URL：

```python
data = {"key": "value", "number": 123}
response = await HttpUtils.post_json(
    url="https://api.example.com/endpoint",
    data=data,
    timeout=30,
    headers={"API-Key": "your-api-key"}
)
print(response)
```

## MCP Manager中的使用

重构后的`MCPManager`现在使用`HttpUtils`来处理所有HTTP操作：

```python
from services.admin_service.services.mcp_manager import mcp_manager

# 通过URL下载并解析OpenAPI文档
openapi_result = await mcp_manager.download_openapi_from_url("https://example.com/openapi.json")

# 验证URL
is_valid = await mcp_manager.validate_openapi_url("https://example.com/openapi.json")
```

## 错误处理

所有方法都会抛出适当的`HTTPException`：

```python
try:
    content = await HttpUtils.download_content_from_url("https://invalid-url.com")
except HTTPException as e:
    print(f"HTTP错误: {e.status_code} - {e.detail}")
except Exception as e:
    print(f"其他错误: {e}")
```

## 配置选项

### 默认超时时间
- 下载内容: 30秒
- URL验证: 10秒
- POST请求: 30秒

### 默认文件大小限制
- 最大文件大小: 10MB (10 * 1024 * 1024 字节)

### 默认允许的内容类型
- application/json
- text/plain
- application/yaml
- text/yaml
- application/x-yaml
- text/x-yaml

### 默认请求头
- User-Agent: "XPack-OpenAPI-Downloader/1.0" (下载时)
- User-Agent: "XPack-HTTP-Client/1.0" (POST请求时)

## 优势

1. **代码复用**: 将HTTP操作集中到一个工具类中，避免重复代码
2. **统一错误处理**: 所有HTTP操作使用相同的错误处理机制
3. **配置灵活**: 支持多种配置选项来满足不同需求
4. **日志记录**: 内置日志记录，便于调试和监控
5. **类型安全**: 使用类型提示，提高代码质量

## 扩展性

`HttpUtils`设计为可扩展的，可以轻松添加新的HTTP操作方法：

```python
@staticmethod
async def put_json(url: str, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    # 实现PUT请求
    pass

@staticmethod  
async def delete_request(url: str, **kwargs) -> bool:
    # 实现DELETE请求
    pass
```

这种设计使得项目中的所有HTTP操作都可以统一管理和维护。
