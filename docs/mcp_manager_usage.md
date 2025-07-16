# MCP Manager 使用文档

## 概述

MCP Manager 提供了两个主要功能：
1. 通过 URL 下载 OpenAPI 文档并解析
2. 通过文件上传方式处理 OpenAPI 文档并解析

所有解析的文档都会被转换为 `OpenApiForAI` 对象，这是一个为 AI 生成 API 调用参数而优化的简化结构。

## API 接口

### 1. 通过 URL 下载 OpenAPI 文档

**接口地址：** `POST /api/mcp/openapi/download-from-url`

**请求参数：**
```json
{
  "url": "https://example.com/openapi.json",
  "description": "可选的描述信息"
}
```

**响应示例：**
```json
{
  "code": 200,
  "message": "成功解析OpenAPI文档，包含 10 个API端点",
  "data": {
    "source": "url",
    "source_url": "https://example.com/openapi.json",
    "description": "可选的描述信息",
    "openapi_info": {
      "title": "Pet Store API",
      "version": "1.0.0",
      "description": "A sample API",
      "apis": [
        {
          "path": "/pets",
          "method": "GET",
          "summary": "List all pets",
          "description": "Returns a list of pets",
          "tags": ["pets"],
          "query_parameters": [
            {
              "name": "limit",
              "description": "Maximum number of items to return",
              "required": false,
              "schema": {
                "type": "integer",
                "format": "int32"
              }
            }
          ],
          "response_schema": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"}
              }
            }
          }
        }
      ]
    }
  }
}
```

### 2. 上传 OpenAPI 文档文件

**接口地址：** `POST /api/mcp/openapi/upload-file`

**请求方式：** `multipart/form-data`

**请求参数：**
- `file`: OpenAPI 文档文件（支持 .json, .yaml, .yml, .txt 格式）
- `description`: 可选的描述信息

**响应示例：**
```json
{
  "code": 200,
  "message": "成功解析OpenAPI文档，包含 5 个API端点",
  "data": {
    "source": "file",
    "source_filename": "openapi.json",
    "file_size": 2048,
    "description": "上传的API文档",
    "openapi_info": {
      "title": "My API",
      "version": "2.0.0",
      "description": "My custom API",
      "apis": [...]
    }
  }
}
```

### 3. 验证 URL 可访问性

**接口地址：** `GET /api/mcp/openapi/validate-url?url=https://example.com/openapi.json`

**响应示例：**
```json
{
  "code": 200,
  "message": "URL验证完成",
  "data": {
    "url": "https://example.com/openapi.json",
    "is_valid": true
  }
}
```

### 4. 获取解析器信息

**接口地址：** `GET /api/mcp/openapi/info`

**响应示例：**
```json
{
  "code": 200,
  "message": "获取解析器信息成功",
  "data": {
    "supported_formats": ["JSON", "YAML"],
    "supported_extensions": [".json", ".yaml", ".yml", ".txt"],
    "max_file_size": 10485760,
    "timeout": 30,
    "max_file_size_mb": 10.0
  }
}
```

## 功能特性

### 支持的格式
- JSON 格式的 OpenAPI 文档
- YAML 格式的 OpenAPI 文档（自动转换为 JSON）

### 安全特性
- 文件大小限制（默认 10MB）
- 请求超时控制（默认 30 秒）
- 文件类型验证
- 内容类型检查
- 编码自动检测（支持 UTF-8 和 GBK）

### 错误处理
- 网络错误处理
- 文件格式错误处理
- JSON/YAML 解析错误处理
- 超时错误处理

## 使用示例

### Python 客户端示例

```python
import requests
import json

# 1. 通过 URL 下载解析
url_data = {
    "url": "https://petstore.swagger.io/v2/swagger.json",
    "description": "Pet Store API"
}

response = requests.post(
    "http://localhost:8000/api/mcp/openapi/download-from-url",
    json=url_data
)

if response.status_code == 200:
    result = response.json()
    print(f"解析成功: {result['message']}")
    openapi_info = result['data']['openapi_info']
    print(f"API标题: {openapi_info['title']}")
    print(f"API版本: {openapi_info['version']}")
    print(f"API端点数量: {len(openapi_info['apis'])}")

# 2. 上传文件解析
with open('openapi.json', 'rb') as f:
    files = {'file': f}
    data = {'description': '我的API文档'}
    
    response = requests.post(
        "http://localhost:8000/api/mcp/openapi/upload-file",
        files=files,
        data=data
    )

if response.status_code == 200:
    result = response.json()
    print(f"上传解析成功: {result['message']}")
```

### JavaScript 客户端示例

```javascript
// 1. 通过 URL 下载解析
const urlData = {
    url: "https://petstore.swagger.io/v2/swagger.json",
    description: "Pet Store API"
};

fetch('/api/mcp/openapi/download-from-url', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify(urlData)
})
.then(response => response.json())
.then(data => {
    if (data.code === 200) {
        console.log('解析成功:', data.message);
        const openApiInfo = data.data.openapi_info;
        console.log('API标题:', openApiInfo.title);
        console.log('API版本:', openApiInfo.version);
        console.log('API端点数量:', openApiInfo.apis.length);
    }
});

// 2. 上传文件解析
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('description', '我的API文档');

fetch('/api/mcp/openapi/upload-file', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => {
    if (data.code === 200) {
        console.log('上传解析成功:', data.message);
    }
});
```

## OpenApiForAI 数据结构

解析后的 OpenAPI 文档会被转换为以下结构：

```json
{
  "title": "API标题",
  "version": "API版本",
  "description": "API描述",
  "apis": [
    {
      "path": "/api/endpoint",
      "method": "GET",
      "summary": "端点摘要",
      "description": "端点描述",
      "tags": ["tag1", "tag2"],
      "path_parameters": [
        {
          "name": "参数名",
          "description": "参数描述",
          "required": true,
          "schema": {
            "type": "string"
          }
        }
      ],
      "query_parameters": [...],
      "header_parameters": [...],
      "request_body_schema": {
        "type": "object",
        "properties": {...}
      },
      "response_schema": {
        "type": "object",
        "properties": {...}
      },
      "response_examples": {...},
      "response_headers": [...],
      "operation_examples": {...}
    }
  ]
}
```

这个结构专门为 AI 优化，简化了原始 OpenAPI 规范的复杂性，使其更容易理解和使用。
