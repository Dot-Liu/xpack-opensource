import pika
import logging
from .config import Config

logger = logging.getLogger(__name__)


class RabbitMQClient:
    def __init__(self):
        self.connection = None
        self.channel = None
        self._setup_connection()

    def _setup_connection(self):
        """建立RabbitMQ连接"""
        try:
            credentials = pika.PlainCredentials(Config.RABBITMQ_USER, Config.RABBITMQ_PASSWORD)
            parameters = pika.ConnectionParameters(
                host=Config.RABBITMQ_HOST,
                port=Config.RABBITMQ_PORT,
                virtual_host=Config.RABBITMQ_VHOST,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300,
            )
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            logger.info("RabbitMQ连接建立成功")
        except Exception as e:
            logger.error(f"建立RabbitMQ连接失败: {str(e)}")
            raise

    def publish(self, queue: str, message: str, persistent: bool = True):
        """
        发布消息到队列

        Args:
            queue: 队列名称
            message: 消息内容
            persistent: 是否持久化消息
        """
        try:
            # 确保连接可用
            if not self.connection or self.connection.is_closed:
                self._setup_connection()

            if not self.channel:
                raise Exception("RabbitMQ channel is not available")

            # 声明队列（持久化）
            self.channel.queue_declare(queue=queue, durable=True)

            # 发布消息
            properties = None
            if persistent:
                properties = pika.BasicProperties(delivery_mode=2)  # 消息持久化

            self.channel.basic_publish(exchange="", routing_key=queue, body=message, properties=properties)
            logger.debug(f"消息已发送到队列 {queue}")

        except Exception as e:
            logger.error(f"发送消息失败: {str(e)}")
            # 尝试重新连接
            try:
                self._setup_connection()
                if not self.channel:
                    raise Exception("Unable to establish RabbitMQ channel")

                # 重试发送
                self.channel.queue_declare(queue=queue, durable=True)
                properties = pika.BasicProperties(delivery_mode=2) if persistent else None
                self.channel.basic_publish(exchange="", routing_key=queue, body=message, properties=properties)
                logger.info(f"消息重新发送成功到队列 {queue}")
            except Exception as retry_error:
                logger.error(f"重试发送消息失败: {str(retry_error)}")
                raise

    def close(self):
        """关闭连接"""
        try:
            if self.connection and not self.connection.is_closed:
                self.connection.close()
                logger.info("RabbitMQ连接已关闭")
        except Exception as e:
            logger.warning(f"关闭RabbitMQ连接时发生错误: {str(e)}")


rabbitmq_client = RabbitMQClient()
