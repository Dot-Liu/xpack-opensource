# Project Name

## 目录结构

```
project_name/
├── fronts/                      # 前端项目（空目录，占位）
├── services/
│   ├── api_service/           # API 服务（端口 8000）
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── controllers/      # 处理 API 路由
│   │   │   ├── __init__.py
│   │   │   └── user.py
│   │   ├── services/        # 业务逻辑
│   │   │   ├── __init__.py
│   │   │   └── user.py
│   │   └── requirements.txt
│   ├── admin_service/        # 管理后台服务（端口 8001，提供前端 API）
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── controllers/     # 处理 API 路由
│   │   │   ├── __init__.py
│   │   │   └── dashboard.py
│   │   ├── services/       # 业务逻辑
│   │   │   ├── __init__.py
│   │   │   └── dashboard.py
│   │   └── requirements.txt
│   └── common/               # 公共模块
│       ├── __init__.py
│       ├── config.py        # 从 .env 加载配置
│       ├── database.py      # MySQL 数据库连接
│       ├── redis.py        # Redis 连接
│       ├── redis_keys.py   # 统一管理 Redis key
│       ├── rabbitmq.py     # RabbitMQ 连接
│       ├── models/
│       │   ├── __init__.py
│       │   └── user.py
│       └── utils.py        # 工具类
├── tests/
│   ├── test_api/
│   ├── test_admin/
│   └── test_common/
├── docs/
│   ├── api.md
│   ├── setup.md
│   └── contributing.md
├── .env                     # 配置文件
├── .gitignore
├── README.md
├── LICENSE                  # 推荐 MIT
└── docker-compose.yml
```

## 简介

本项目为多服务架构示例，包含 API 服务、管理后台服务、公共模块、前端占位、测试、文档等。 

## 启动
```shell
uvicorn services.admin_service.main:app --host 0.0.0.0 --port 8001 --reload
```