class MessageChannel(object):
    """Message channel wrapper for rabbitmq's channels"""

    def __init__(self, channel, exchange, routing_key):
        self._channel = channel
        self._exchange = exchange
        self._routing_key = routing_key

    def publish_message(self, message):
        """Publish a message to the channel

        :param MessageBase message: the message to publish
        """
        serialized_message = message.dumps()

        self._channel.basic_publish(
            exchange=self._exchange,
            routing_key=self._routing_key,
            body=serialized_message
        )
