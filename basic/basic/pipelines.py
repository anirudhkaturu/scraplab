# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from email import message

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

import pika
import json
import os

class RabbitMqPipeline:

    def __init__(self):
        self.connection = None
        self.channel = None

    def open_spider(self, spider):
        RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
        RABBITMQ_PORT = int(os.getenv('RABBITMQ_PORT', 5672))
        RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'guest')
        RABBITMQ_PASS = os.getenv('RABBITMQ_PASS', 'guest')
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)

        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT, credentials=credentials))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='basic_spider', durable=True)

    def process_item(self, item, spider):
        message = json.dumps(dict(item))

        self.channel.basic_publish(
            exchange='',
            routing_key='basic_spider',
            body= message.encode('utf-8'),
            properties=pika.BasicProperties(
                delivery_mode=2,
            )
        )

        return item

    def close_spider(self, spider):
        self.connection.close()
        pass
