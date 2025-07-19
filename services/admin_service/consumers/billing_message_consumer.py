"""
RabbitMQ计费消息消费者
"""
import json
import pika
import threading
import time
import logging
from typing import Callable

from services.common.config import Config
from services.common.database import get_db
from services.admin_service.services.billing_message_handler import BillingMessageHandler

logger = logging.getLogger(__name__)


class BillingMessageConsumer:
    """计费消息消费者"""
    
    def __init__(self):
        self.queue_name = "billing.api.calls"
        self.connection = None
        self.channel = None
        self.consuming = False
        self._setup_connection()
    
    def _setup_connection(self):
        """设置RabbitMQ连接"""
        max_retries = 3
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                credentials = pika.PlainCredentials(Config.RABBITMQ_USER, Config.RABBITMQ_PASSWORD)
                parameters = pika.ConnectionParameters(
                    host=Config.RABBITMQ_HOST,
                    port=Config.RABBITMQ_PORT,
                    virtual_host=Config.RABBITMQ_VHOST,
                    credentials=credentials,
                    heartbeat=600,  # 增加心跳间隔
                    blocked_connection_timeout=300  # 连接阻塞超时
                )
                
                self.connection = pika.BlockingConnection(parameters)
                self.channel = self.connection.channel()
                
                # 声明队列
                self.channel.queue_declare(queue=self.queue_name, durable=True)
                
                # 设置QoS，一次只处理一条消息
                self.channel.basic_qos(prefetch_count=1)
                
                logger.info("RabbitMQ connection established successfully")
                return
                
            except Exception as e:
                logger.error(f"Failed to establish RabbitMQ connection (attempt {attempt + 1}/{max_retries}): {str(e)}")
                
                if attempt < max_retries - 1:
                    logger.info(f"Waiting {retry_delay} seconds before retry...")
                    time.sleep(retry_delay)
                else:
                    logger.error("All connection attempts failed")
                    raise
    
    def start_consuming(self):
        """开始消费消息"""
        try:
            # 确保连接已建立
            if not self.connection or self.connection.is_closed:
                self._setup_connection()
            
            if not self.channel:
                raise Exception("RabbitMQ channel is not available")
            
            self.consuming = True
            
            # 设置消息回调
            self.channel.basic_consume(
                queue=self.queue_name,
                on_message_callback=self._process_message,
                auto_ack=False  # 手动确认
            )
            
            logger.info(f"开始消费队列: {self.queue_name}")
            self.channel.start_consuming()
            
        except KeyboardInterrupt:
            logger.info("接收到中断信号，停止消费")
            self.stop_consuming()
        except Exception as e:
            logger.error(f"消费消息时发生异常: {str(e)}")
            raise
    
    def stop_consuming(self):
        """停止消费消息"""
        self.consuming = False
        if self.channel:
            self.channel.stop_consuming()
        if self.connection and not self.connection.is_closed:
            self.connection.close()
        logger.info("消息消费已停止")
    
    def _process_message(self, channel, method, properties, body):
        """
        处理单条消息
        
        Args:
            channel: 通道对象
            method: 方法对象
            properties: 属性对象
            body: 消息体
        """
        message_data = None
        try:
            # 解析消息
            message_data = json.loads(body)
            logger.info(f"收到计费消息: 用户ID={message_data.get('user_id')}, 工具={message_data.get('tool_name')}")
            
            # 获取数据库会话并处理消息
            db = next(get_db())
            try:
                handler = BillingMessageHandler(db)
                success = handler.process_billing_message(message_data)
                
                if success:
                    # 确认消息处理成功
                    channel.basic_ack(delivery_tag=method.delivery_tag)
                    logger.info(f"消息处理成功并已确认: {message_data.get('user_id')}")
                else:
                    # 处理失败，直接丢弃消息（避免无限重试）
                    channel.basic_ack(delivery_tag=method.delivery_tag)
                    logger.error(f"消息处理失败，已丢弃消息: {message_data.get('user_id')}")
                    
            finally:
                db.close()
                
        except json.JSONDecodeError as e:
            logger.error(f"消息格式错误: {str(e)}, 消息体: {body}")
            # 消息格式错误，直接确认（不重新入队）
            channel.basic_ack(delivery_tag=method.delivery_tag)
            
        except Exception as e:
            logger.error(f"处理消息时发生异常: {str(e)}", exc_info=True)
            # 异常处理，直接确认消息（避免无限重试）
            try:
                channel.basic_ack(delivery_tag=method.delivery_tag)
                logger.error(f"异常处理失败，已丢弃消息")
            except:
                # 如果连确认都失败了，记录错误但不抛出异常
                logger.error("无法确认消息", exc_info=True)
    
    def _get_retry_count(self, properties):
        """
        获取消息重试次数
        
        Args:
            properties: 消息属性
            
        Returns:
            int: 重试次数
        """
        if properties and properties.headers:
            return properties.headers.get('x-retry-count', 0)
        return 0


def start_billing_consumer():
    """启动计费消息消费者"""
    consumer = BillingMessageConsumer()
    consumer.start_consuming()


if __name__ == "__main__":
    start_billing_consumer()
