import pika
from .config import Config


class RabbitMQClient:
    def __init__(self):
        credentials = pika.PlainCredentials(
            Config.RABBITMQ_USER, Config.RABBITMQ_PASSWORD
        )
        parameters = pika.ConnectionParameters(
            host=Config.RABBITMQ_HOST,
            port=Config.RABBITMQ_PORT,
            virtual_host=Config.RABBITMQ_VHOST,
            credentials=credentials,
        )
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()

    def publish(self, queue: str, message: str):
        self.channel.queue_declare(queue=queue)
        self.channel.basic_publish(exchange="", routing_key=queue, body=message)

    def close(self):
        self.connection.close()


rabbitmq_client = RabbitMQClient()
