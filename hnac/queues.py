import json

import pika
from pika.credentials import PlainCredentials


def create_story_publisher_from_config(config):
    username = config.get("RABBITMQ_STORY_PROCESSOR_USERNAME")
    password = config.get("RABBITMQ_STORY_PROCESSER_PASSWORD")
    credentials = None
    if username and password:
        credentials = PlainCredentials(username, password)

    return RabbitMQStoryPublisher(
        host=config["RABBITMQ_STORY_PROCESSOR_HOST"],
        port=config.get("RABBITMQ_STORY_PROCESSOR_PORT"),
        credentials=credentials,
        exchange=config.get("RABBITMQ_STORY_PROCESSOR_EXCHANGE", ""),
        routing_key=config["RABBITMQ_STORY_PROCESSOR_ROUTING_KEY"]
    )


def create_url_publisher_from_config(config):
    username = config.get("RABBITMQ_URL_PROCESSOR_USERNAME")
    password = config.get("RABBITMQ_URL_PROCESSER_PASSWORD")
    credentials = None
    if username and password:
        credentials = PlainCredentials(username, password)

    return RabbitMQPublisher(
        host=config["RABBITMQ_URL_PROCESSOR_HOST"],
        port=config.get("RABBITMQ_URL_PROCESSOR_PORT"),
        credentials=credentials,
        exchange=config.get("RABBITMQ_URL_PROCESSOR_EXCHANGE", ""),
        routing_key=config["RABBITMQ_URL_PROCESSOR_ROUTING_KEY"]
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

    def publish_item(self, item):
        self._channel.basic_publish(
            exchange=self._exchange,
            routing_key=self._routing_key,
            body=item
        )


class RabbitMQStoryPublisher(RabbitMQPublisher):
    """The RabbitMQStoryPublisher object is used to publish hacked news
    stories to RabbitMQ"""

    def __init__(self, host, port, credentials, exchange, routing_key):
        """Create a new RabbitMQStoryPublisher object

        :param str host: the RabbitMQ host
        :param int port: the port on which RabbitMQ listens
        :param PlainCredentials credentials: the credentials to use in order to
        connect to RabbitMQ
        :param str exchange: the exchange to publish the stories
        :param str routing_key: the routing key to use
        """
        super(RabbitMQStoryPublisher, self).__init__(
            host=host,
            port=port,
            credentials=credentials,
            exchange=exchange,
            routing_key=routing_key
        )

    def publish_story(self, story_data):
        """Publish a story to RabbitMQ

        :param dict story_data: the story data
        """
        encoded_story_data = json.dumps(story_data)

        self.publish_item(encoded_story_data)
