# 认证中间件配置化改进

## 概述
将管理员服务（admin_service）中间件的无需认证路径从硬编码改为配置文件管理，并统一错误响应格式，提高系统的可维护性和一致性。

## 修改内容

### 1. 配置文件修改 (`services/common/config.py`)
- 添加了 `NO_AUTH_PATHS` 配置项
- 支持通过环境变量 `NO_AUTH_PATHS` 覆盖默认配置
- 环境变量格式：使用逗号分隔的路径列表

### 2. 中间件修改 (`services/admin_service/middleware.py`)
- 导入配置类 `Config` 和 `ResponseUtils`
- 添加日志记录功能，增强异常记录
- 将硬编码的路径列表替换为配置读取
- **统一错误响应格式**：使用 `ResponseUtils.error()` 生成标准格式响应
- 增加详细的类和方法文档说明

### 3. 响应格式统一
**之前的错误响应格式：**
```json
{
  "detail": "Authorization header is required"
}
```

**现在的统一错误响应格式：**
```json
{
  "success": false,
  "code": "401",
  "error_message": "Authorization header is required",
  "data": null
}
```

## 使用方式

### 默认配置
系统使用预定义的无需认证路径列表，包括：
- `/` - 根路径
- `/health` - 健康检查
- `/docs`, `/openapi.json`, `/redoc` - API文档相关
- `/api/auth/*` - 认证相关接口
- `/api/common/config` - 公共配置接口
- `/api/web/*` - Web相关接口
- `/api/payment/callback_stripe` - 支付回调

### 环境变量配置
可通过设置环境变量 `NO_AUTH_PATHS` 来覆盖默认配置：

```bash
export NO_AUTH_PATHS="/,/health,/docs,/api/auth/login,/api/public/*"
```

### 日志记录
- 中间件初始化时记录配置的路径数量
- 调试模式下记录跳过认证的路径请求

## 优势
1. **可维护性**：无需修改代码即可调整无需认证的路径
2. **灵活性**：支持环境变量动态配置
3. **一致性**：统一管理所有配置项，统一错误响应格式
4. **可观测性**：增加日志记录便于调试和监控
5. **标准化**：错误响应格式与系统其他模块保持一致

## 注意事项
- 修改无需认证路径时要谨慎，避免安全风险
- 环境变量配置会完全替换默认配置，不是追加
- 路径匹配是精确匹配，不支持通配符（如需要可后续扩展）
- 错误响应格式现在与系统其他接口保持一致
- 响应头包含正确的字符集设置（UTF-8）
