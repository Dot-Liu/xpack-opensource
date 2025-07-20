# Author: Eolink-liujian
# Date: 2025-07-19
# Description: Dockerfile for XPack
FROM  python:3.12.11-alpine3.22

RUN apk add nodejs=~22 npm git

RUN npm install -g pnpm

ENV TZ=Asia/Shanghai

RUN ln -sf /usr/share/zoneinfo/${TZ} /etc/localtime \
    && echo "Asia/Shanghai" > /etc/timezone