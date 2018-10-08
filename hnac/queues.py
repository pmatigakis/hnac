import logging

import pika
from pika.credentials import PlainCredentials

from hnac.channels import MessageChannel


logger = logging.getLogger(__name__)


def create_publisher(host, port, username, password, exchange, exchange_type,
                     durable, auto_delete, routing_key):
    credentials = None
    if username and password:
        credentials = PlainCredentials(username, password)

    return RabbitMQPublisher(
        host=host,
        port=port,
        credentials=credentials,
        exchange=exchange,
        routing_key=routing_key,
        exchange_type=exchange_type,
        durable=durable,
        auto_delete=auto_delete
    )


class RabbitMQPublisher(object):
    def __init__(self, host, port, credentials, exchange, exchange_type,
                 durable, auto_delete, routing_key):
        """Create a new RabbitMQPublisher object

        :param str host: the RabbitMQ host
        :param int port: the port on which RabbitMQ listens
        :param PlainCredentials credentials: the credentials to use in order to
        connect to RabbitMQ
        :param str exchange: the exchange to publish the stories
        :param str exchange_type: the exchange type
        :param boolean durable: is the exchange durable
        :param boolean auto_delete: will the exchange be auto deleted
        :param str routing_key: the routing key to use
        """
        self._exchange = exchange
        self._routing_key = routing_key
        self._exchange_type = exchange_type
        self._durable = durable
        self._auto_delete = auto_delete

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
            exchange_type=self._exchange_type,
            durable=self._durable,
            auto_delete=self._auto_delete
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
