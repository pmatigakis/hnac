import json

import pika
from pika.credentials import PlainCredentials


def create_publisher_from_config(config):
    username = config.get("URLPUB_RABBITMQ_USERNAME")
    password = config.get("URLPUB_RABBITMQ_PASSWORD")
    credentials = None
    if username and password:
        credentials = PlainCredentials(username, password)

    return RabbitMQPublisher(
        host=config["URLPUB_RABBITMQ_HOST"],
        port=config.get("URLPUB_RABBITMQ_PORT"),
        credentials=credentials,
        exchange=config.get("URLPUB_RABBITMQ_EXCHANGE", ""),
        routing_key=config["URLPUB_RABBITMQ_ROUTING_KEY"]
    )


class RabbitMQPublisher(object):
    def __init__(self, host, port, credentials, exchange, routing_key):
        self._exchange = exchange
        self._routing_key = routing_key

        self._connection_parameters = pika.ConnectionParameters(
            host=host,
            port=port,
            credentials=credentials
        )

        self._connection = None
        self._channel = None

    def open(self):
        self._connection = pika.BlockingConnection(self._connection_parameters)
        self._channel = self._connection.channel()

    def close(self):
        self._connection.close()

    def publish_story(self, story_data):
        encoded_story_data = json.dumps(story_data)

        self._channel.basic_publish(
            exchange=self._exchange,
            routing_key=self._routing_key,
            body=encoded_story_data
        )
