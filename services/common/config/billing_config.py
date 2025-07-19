"""
计费配置常量
"""

# Redis配置
BILLING_LOCK_TIMEOUT = 5  # 分布式锁超时时间(秒)
WALLET_CACHE_EXPIRE = 300  # 钱包缓存过期时间(秒)
SERVICE_CACHE_EXPIRE = 3600  # 服务价格缓存过期时间(秒)

# RabbitMQ配置
BILLING_QUEUE_NAME = "billing.api.calls"
BILLING_EXCHANGE_NAME = "billing.exchange"
BILLING_ROUTING_KEY = "api.call.billing"

# 业务配置
BILLING_RETRY_TIMES = 3  # 计费消息重试次数
BILLING_BATCH_SIZE = 100  # 批量处理大小

# 计费开关
ENABLE_BILLING = True  # 是否启用计费功能
