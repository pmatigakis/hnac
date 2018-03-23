import logging

import pika
from pika.credentials import PlainCredentials

from hnac.channels import MessageChannel


logger = logging.getLogger(__name__)


def create_publisher(host, port, username, password, exchange, routing_key):
    credentials = None
    if username and password:
        credentials = PlainCredentials(username, password)

    return RabbitMQPublisher(
        host=host,
        port=port,
        credentials=credentials,
        exchange=exchange,
        routing_key=routing_key
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
        channel = self._connection.channel()

        channel.exchange_declare(
            exchange=self._exchange,
            exchange_type="topic"
        )

        self._channel = MessageChannel(
            channel=channel,
            exchange=self._exchange,
            routing_key=self._routing_key
        )

    def close(self):
        self._connection.close()

    def publish_message(self, message):
        self._channel.publish_message(message)
