# XPack 开源版本 - Copilot 编程指导

## 项目架构

### 服务依赖关系
- `services/admin_service` 和 `services/api_service` 不互相依赖
- 两个服务都依赖于 `services/common`
- 遵循微服务架构模式，保持服务间的松耦合

### 目录结构规范
```
services/
├── admin_service/          # 管理端服务
│   ├── controllers/        # 控制器层
│   ├── services/          # 业务逻辑层
│   ├── repositories/      # 数据访问层
│   ├── utils/            # 工具函数
│   └── constants/        # 常量定义
├── api_service/           # API服务
└── common/               # 公共模块
    ├── models/           # 数据模型
    ├── response/         # 响应模型
    ├── utils/           # 公共工具
    └── config.py        # 配置管理
```

## 编码规范

### Python 代码风格
- 遵循 PEP 8 编码规范
- 使用类型注解提高代码可读性
- 函数和类使用 docstring 文档
- 变量和函数名使用 snake_case
- 类名使用 PascalCase

### 模块导入规范
- 优先从 `services/common` 导入公共功能
- 避免跨服务直接导入（admin_service ↔ api_service）
- 使用相对导入引用同一服务内的模块

### 错误处理
- 使用 `services/common/error_msg.py` 中定义的错误消息
- 统一异常处理格式
- 记录必要的错误日志

### 日志规范
- **语言要求**：所有日志消息必须使用英文
- **格式统一**：使用 `services/common/logging_config.py` 提供的统一日志格式
- **日志级别**：
  - `DEBUG`: 详细调试信息
  - `INFO`: 一般信息记录
  - `WARNING`: 警告信息
  - `ERROR`: 错误信息
  - `CRITICAL`: 严重错误
- **消息格式**：
  ```python
  # ✅ 正确示例
  logger.info("Starting to download content from URL: {url}")
  logger.error("Failed to process request: {error_message}")
  logger.warning("Invalid content type detected: {content_type}")
  
  # ❌ 错误示例
  logger.info(f"开始从URL下载内容: {url}")  # 中文消息
  logger.error(f"处理请求失败: {error_message}")  # 中文消息
  ```
- **日志内容**：
  - 使用描述性的英文消息
  - 包含必要的上下文信息（如 URL、用户ID、操作类型等）
  - 避免敏感信息（如密码、API密钥）
  - 使用结构化的消息格式便于后续分析

### 数据库操作
- 通过 `services/common/database.py` 进行数据库连接
- 使用 Repository 模式进行数据访问
- 遵循事务处理最佳实践

### API 设计
- RESTful API 设计原则
- 统一的响应格式（使用 `services/common/response/`）
- 适当的 HTTP 状态码
- API 版本控制

## 开发建议

### 开发流程规范
**🚀 核心原则：思考在前，编码在后**

在动手编写代码之前，必须先完成以下思路整理步骤：

1. **需求分析**
   - 明确功能需求和业务逻辑
   - 识别输入、输出和边界条件
   - 确定性能和安全要求

2. **架构设计**
   - 确定功能属于哪个服务（admin_service 或 api_service）
   - 设计数据流和接口定义
   - 规划数据库模型变更（如需要）

3. **技术方案**
   - 选择合适的技术栈和工具
   - 设计API接口和数据结构
   - 考虑错误处理和异常情况

4. **代码实现**
   - 实现代码前先需要确认
   - 确保所有日志消息使用英文
   - 遵循统一的日志格式规范

**⚠️ 重要提醒：只有在完成上述思路整理并得到确认后，才能开始编写代码！**

### 新功能开发
1. 确定功能属于哪个服务（admin_service 或 api_service）
2. 如果是公共功能，考虑放在 `services/common`
3. 遵循分层架构：Controller → Service → Repository

### 测试
- 为每个服务编写单元测试（`tests/test_admin/`, `tests/test_api/`）
- 公共模块测试放在 `tests/test_common/`
- 使用适当的测试框架和 mock 对象

### 安全考虑
- 用户认证和授权
- 输入验证和数据清理
- SQL 注入防护
- API 访问频率限制

### 性能优化
- 数据库查询优化
- 缓存策略（Redis）
- 异步处理（RabbitMQ）
- 分页处理大数据集

## 技术栈
- **后端框架**: FastAPI/Flask (推断)
- **数据库**: 关系型数据库
- **缓存**: Redis
- **消息队列**: RabbitMQ
- **认证**: JWT/API Key
- **文档**: OpenAPI/Swagger
- **MCP服务**: fastmcp

## 代码审查要点
- 是否遵循了服务依赖规则
- 错误处理是否完整
- 是否有适当的日志记录（英文格式，统一格式）
- 性能和安全考虑
- 代码注释和文档完整性