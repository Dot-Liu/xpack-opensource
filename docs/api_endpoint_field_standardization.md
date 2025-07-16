# ApiEndpoint 字段命名标准化文档

## 概述

本文档记录了对 `ApiEndpoint` 类字段命名的标准化改进，旨在提高代码的可读性、一致性和语义表达。

## 标准化原则

1. **一致性**：所有字段使用统一的命名风格（snake_case）
2. **语义清晰**：字段名称能够清楚地表达其含义和用途
3. **完整性**：避免缩写，使用完整的单词描述
4. **分类明确**：相同类型的字段使用相似的命名模式

## 字段命名变更

### 参数相关字段

| 原字段名 | 新字段名 | 说明 |
|---------|---------|------|
| `path_params` | `path_parameters` | 路径参数，使用完整单词 |
| `query_params` | `query_parameters` | 查询参数，使用完整单词 |
| `header_params` | `header_parameters` | 请求头参数，使用完整单词 |

### 示例相关字段

| 原字段名 | 新字段名 | 说明 |
|---------|---------|------|
| `response_example` | `response_examples` | 响应示例，使用复数形式更准确 |
| `examples` | `operation_examples` | 操作示例，增加前缀提高语义清晰度 |

### 保持不变的字段

以下字段因为已经符合标准化原则，保持不变：

- `path` - API 路径
- `method` - HTTP 方法
- `summary` - 简要说明
- `description` - 详细描述
- `tags` - 标签列表
- `request_body_schema` - 请求体 Schema
- `response_schema` - 响应体 Schema
- `response_headers` - 响应头信息

## 标准化后的 ApiEndpoint 构造函数

```python
def __init__(
    self,
    path: str,
    method: str,
    summary: str = "",
    description: str = "",
    tags: Optional[List[str]] = None,
    path_parameters: Optional[List[Dict]] = None,
    query_parameters: Optional[List[Dict]] = None,
    header_parameters: Optional[List[Dict]] = None,
    request_body_schema: Optional[Dict] = None,
    response_schema: Optional[Dict] = None,
    response_examples: Optional[Dict] = None,
    response_headers: Optional[List[Dict]] = None,
    operation_examples: Optional[Dict] = None,
):
```

## 影响范围

这次标准化修改了以下内容：

1. **ApiEndpoint 类**
   - 构造函数参数名称
   - 实例属性名称
   - `to_dict()` 方法中的字段映射

2. **convert_openapi_for_ai 函数**
   - 局部变量名称
   - ApiEndpoint 实例化参数

## 兼容性说明

这是一个**重大变更**，如果有其他代码依赖原来的字段名称，需要相应地更新：

- 任何直接访问 `path_params`、`query_params`、`header_params` 的代码
- 任何直接访问 `response_example`、`examples` 的代码
- 任何解析 `to_dict()` 输出 JSON 的代码

## 优势

1. **提高可读性**：完整的单词比缩写更容易理解
2. **增强一致性**：所有参数字段都使用 `_parameters` 后缀
3. **语义更准确**：`response_examples` 和 `operation_examples` 的命名更精确
4. **便于维护**：标准化的命名使代码更易于维护和扩展

## 后续建议

1. 更新相关的文档和注释
2. 如果有单元测试，需要相应更新测试用例
3. 考虑在其他相关类中应用相同的命名标准
4. 建立代码审查检查清单，确保新增字段遵循相同标准

---

*文档版本：v1.0*  
*更新日期：2025年7月16日*
