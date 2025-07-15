# XPack 开源项目

## 目录结构

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