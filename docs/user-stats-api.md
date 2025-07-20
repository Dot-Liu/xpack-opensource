# 用户统计API接口文档

## 接口概述

**接口路径**: `GET /api/stats/key_call_tool_count`

**功能描述**: 根据apikey_id获取最近N天的工具调用次数统计

**标签**: 统计

## 请求参数

### Query Parameters

| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|-------|------|
| apikey_id | string | 是 | - | API密钥ID（注意：这是user_apikey表中的id字段，不是apikey字段） |
| last_day | number | 否 | 30 | 最近几天，默认30天，最大不超过365天 |

## 响应格式

### 成功响应 (HTTP 200)

```json
{
  "success": true,
  "error_message": "",
  "code": "200",
  "data": {
    "days": [
      {
        "stats_day": "2024-01-01",
        "call_tool_count": 10
      },
      {
        "stats_day": "2024-01-02", 
        "call_tool_count": 5
      }
    ]
  }
}
```

### 错误响应

#### 参数错误 (HTTP 400)
```json
{
  "success": false,
  "error_message": "apikey_id is required and cannot be empty",
  "code": "400",
  "data": null
}
```

#### API密钥不存在 (HTTP 400)
```json
{
  "success": false,
  "error_message": "Invalid apikey_id: test-invalid-id",
  "code": "400", 
  "data": null
}
```

#### 服务器错误 (HTTP 500)
```json
{
  "success": false,
  "error_message": "Internal server error occurred while retrieving statistics",
  "code": "500",
  "data": null
}
```

## 请求示例

### cURL
```bash
curl -X GET "http://localhost:8001/api/stats/key_call_tool_count?apikey_id=12345678-1234-1234-1234-123456789012&last_day=7" \
  -H "Accept: application/json"
```

### JavaScript (Fetch API)
```javascript
const response = await fetch('/api/stats/key_call_tool_count?apikey_id=12345678-1234-1234-1234-123456789012&last_day=7');
const data = await response.json();
console.log(data);
```

### Python (requests)
```python
import requests

url = "http://localhost:8001/api/stats/key_call_tool_count"
params = {
    "apikey_id": "12345678-1234-1234-1234-123456789012",
    "last_day": 7
}

response = requests.get(url, params=params)
data = response.json()
print(data)
```

## 数据说明

1. **stats_day**: 统计日期，格式为 YYYY-MM-DD
2. **call_tool_count**: 该日期的工具调用次数，整数类型
3. 返回的日期是连续的，包含没有调用记录的日期（call_tool_count为0）
4. 日期按升序排列，最早日期在前

## 业务逻辑

1. 根据apikey_id查询user_apikey表验证密钥有效性
2. 计算日期范围：从今天往前推last_day天
3. 查询mcp_call_log表，按日期分组统计调用次数
4. 补全没有调用记录的日期，设置调用次数为0
5. 返回完整的日期序列统计数据

## 性能考虑

- 查询天数限制在365天内，避免大量数据查询
- 使用数据库日期函数进行高效分组统计
- 建议在call_start_time字段上创建索引以提升查询性能

## 错误处理

- 参数验证：检查apikey_id非空、last_day有效范围
- 业务验证：验证apikey_id存在性
- 异常处理：数据库连接失败、查询超时等异常情况
- 日志记录：记录请求信息和错误详情便于排查问题
