from argparse import ArgumentParser

import pika


def get_arguments():
    parser = ArgumentParser()

    parser.add_argument("--username")
    parser.add_argument("--password")
    parser.add_argument("--exchange", required=True)
    parser.add_argument("--queue", required=True)
    parser.add_argument("--routing-key", required=True, dest="routing_key")
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", default=5672)

    return parser.parse_args()


def on_message(channel, basic_deliver, properties, body):
    print(body)
    channel.basic_ack(basic_deliver.delivery_tag)


def main():
    args = get_arguments()

    credentials = None
    if args.username and args.password:
        credentials = pika.PlainCredentials(args.username, args.password)

    connection_parameters = pika.ConnectionParameters(
        host=args.host,
        port=args.port,
        credentials=credentials
    )

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

    channel.basic_consume(on_message, args.queue)
    channel.start_consuming()


if __name__ == "__main__":
    main()
