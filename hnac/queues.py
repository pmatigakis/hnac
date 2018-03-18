import json
import logging

import pika
from pika.credentials import PlainCredentials

from hnac.schemas import HackernewsStorySchema


logger = logging.getLogger(__name__)


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

    return RabbitMQUrlPublisher(
        host=config["RABBITMQ_URL_PROCESSOR_HOST"],
        port=config.get("RABBITMQ_URL_PROCESSOR_PORT"),
        credentials=credentials,
        exchange=config.get("RABBITMQ_URL_PROCESSOR_EXCHANGE", ""),
        routing_key=config["RABBITMQ_URL_PROCESSOR_ROUTING_KEY"]
    )


class RabbitMQPublisher(object):
    def __init__(self, host, port, credentials, exchange, routing_key):
        """Create a new RabbitMQPublisher object

        :param str host: the RabbitMQ host
        :param int port: the port on which RabbitMQ listens
        :param PlainCredentials credentials: the credentials to use in order to
        connect to RabbitMQ
        :param str exchange: the exchange to publish the stories
        :param str routing_key: the routing key to use
        """
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

        self._channel.exchange_declare(
            exchange=self._exchange,
            exchange_type="topic"
        )

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

    def publish_story(self, story_data):
        """Publish a story to RabbitMQ

        :param dict story_data: the story data
        """
        schema = HackernewsStorySchema()
        serialization_result = schema.dumps(story_data)
        if serialization_result.errors:
            logger.warning(
                "failed to serialize story: errors(%s)",
                serialization_result.errors
            )

        self.publish_item(serialization_result.data)


class RabbitMQUrlPublisher(RabbitMQPublisher):
    """The RabbitMQUrlPublisher object is used to publish the urls of
    hackednews stories to RabbitMQ"""

    def publish_url(self, url):
        """Publish a story to RabbitMQ

        :param dict story_data: the story data
        """
        encoded_url_data = json.dumps({"url": url})

        self.publish_item(encoded_url_data)
