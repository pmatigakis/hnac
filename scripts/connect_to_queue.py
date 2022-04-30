from argparse import ArgumentParser

import pika


def get_arguments():
    parser = ArgumentParser()

    parser.add_argument(
        "--parameters-url",
        default="amqp://guest:guest@localhost:5672/%2F"
    )
    parser.add_argument("--exchange", required=True)
    parser.add_argument("--queue", required=True)
    parser.add_argument("--routing-key", required=True, dest="routing_key")

    return parser.parse_args()


def on_message(channel, basic_deliver, properties, body):
    print(body)
    channel.basic_ack(basic_deliver.delivery_tag)


def main():
    args = get_arguments()

    connection_parameters = pika.URLParameters(args.parameters_url)
    connection = pika.BlockingConnection(connection_parameters)
    channel = connection.channel()
    channel.queue_declare(
        queue=args.queue,
        exclusive=True,
        auto_delete=True
    )
    channel.queue_bind(
        queue=args.queue,
        exchange=args.exchange,
        routing_key=args.routing_key
    )

    channel.basic_consume(args.queue, on_message)
    channel.start_consuming()


if __name__ == "__main__":
    main()
