from argparse import ArgumentParser
import json

from pika import BlockingConnection, ConnectionParameters
from pika.credentials import PlainCredentials


def get_arguments():
    parser = ArgumentParser()

    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", default=5672, type=int)
    parser.add_argument("--username", default="guest")
    parser.add_argument("--password", default="guest")
    parser.add_argument("--exchange", default="stories")
    parser.add_argument(
        "--routing-key", default="stories.new", dest="routing_key")
    parser.add_argument("--queue", default="story-reader")

    return parser.parse_args()


def on_message(channel, method_frame, header_frame, body):
    story_message = json.loads(body.decode("utf-8"))
    for field in ["title", "url", "by"]:
        print("{}: {}".format(field, story_message["data"][field]))
    print()
    channel.basic_ack(delivery_tag=method_frame.delivery_tag)


def main():
    args = get_arguments()

    credentials = None
    if args.username and args.password:
        credentials = PlainCredentials(args.username, args.password)

    parameters = ConnectionParameters(
        host=args.host,
        port=args.port,
        credentials=credentials
    )

    connection = BlockingConnection(parameters)
    channel = connection.channel()
    response = channel.queue_declare(
        queue=args.queue,
        exclusive=True,
        auto_delete=True
    )
    queue = response.method.queue

    channel.queue_bind(
        exchange=args.exchange,
        queue=queue,
        routing_key=args.routing_key
    )

    channel.basic_consume(queue, on_message)

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
    connection.close()


if __name__ == "__main__":
    main()
