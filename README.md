# XPack 开源项目

## 目录结构

```
项目结构
├── docs/                  # 项目文档与数据库文件
│   ├── api.md
│   ├── db.sql
│   └── ...
├── services/              # 后端服务
│   ├── admin_service/
│   │   ├── main.py
│   │   ├── controllers/
│   │   └── services/
│   ├── api_service/
│   │   ├── main.py
│   │   ├── controllers/
│   │   └── services/
│   └── common/
│       ├── config.py
│       ├── models/
│       └── utils/
├── scripts/               # 项目脚本
├── tests/                 # 测试代码
├── web/                   # 前端代码
├── requirements.txt       # 依赖包列表
├── .env                   # 环境变量配置
├── README.md              # 项目说明文档
└── LICENSE                # 许可证
```

- `docs/`：项目文档及数据库文件
- `services/`：后端服务代码（admin_service、api_service、common）
- `web/`：前端代码
- `tests/`：测试代码
- `scripts/`：脚本文件
- `requirements.txt`：依赖包列表
- `.env`：环境变量配置
- `README.md`：项目说明文档
- `LICENSE`：许可证

## 启动方式

```shell
# 启动 admin 服务
uvicorn services.admin_service.main:app --host 0.0.0.0 --port 8001 --reload
```

## 模块说明

- **common**：公共模块，包含工具类、数据库实体及中间件（如 Redis、RabbitMQ）配置。
- **admin_service**：管理后台 API，支持用户登录注册、计费、支付、MCP 服务上下架等功能。与 api_service 无直接依赖，均依赖 common。
- **api_service**：MCP 服务接口，MCP 客户端直接对接。与 admin_service 无直接依赖，均依赖 common。

## MCP 客户端 API 配置示例

```json
{
    "mcpServers": {
        "xpack-mcp": {
            "url": "https://api.xpack.ai/v1/mcp?apikey=edebf173cdb9442ea998e19a0b758883&service_id=1234567890"
        }
    }
}
```