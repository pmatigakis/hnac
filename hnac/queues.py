import logging

import pika

from hnac.channels import MessageChannel


logger = logging.getLogger(__name__)


def create_publisher(parameters_url, exchange, exchange_type,
                     durable, auto_delete, routing_key):
    return RabbitMQPublisher(
        parameters_url=parameters_url,
        exchange=exchange,
        routing_key=routing_key,
        exchange_type=exchange_type,
        durable=durable,
        auto_delete=auto_delete
    )


class RabbitMQPublisher(object):
    def __init__(self, parameters_url, exchange, exchange_type,
                 durable, auto_delete, routing_key):
        """Create a new RabbitMQPublisher object

        :param str parameters_url: the RabbitMQ parameters url
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

        self._connection_parameters = pika.URLParameters(parameters_url)

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
