# XPack 开源项目

## 目录结构

```
项目结构
├── docs/                  # 项目文档、数据库文件
│   ├── api.md
│   ├── db.sql
│   └── ...
├── services/              # 后端服务代码
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

- `doc`：包含数据库文件
- `.env`：项目环境变量配置文件
- `services`：各服务的代码
- `web`：前端代码
- `tests`：测试代码
- `requirements.txt`：依赖包列表
- `README.md`：项目说明文档
- `scripts`：脚本文件

## 启动

```shell
# 启动 admin 服务
uvicorn services.admin_service.main:app --host 0.0.0.0 --port 8001 --reload
```

## 模块功能说明

- **common**：公共模块，包含常用工具类、数据库实体、Redis 配置、RabbitMQ 配置等中间件相关配置。
- **admin_service**：管理后台 API 服务，提供用户登录注册、计费、支付、MCP 服务上下架等功能。与 api_service 在代码层面无直接依赖，均依赖 common。
- **api_service**：MCP 服务相关接口，MCP 客户端直接对接该服务。与 admin_service 在代码层面无直接依赖，均依赖 common。