from argparse import ArgumentParser
import json

from couchdb import Server


def get_arguments():
    parser = ArgumentParser()

    parser.add_argument(
        "--couchdb-url",
        default="http://localhost:5984",
        help="the url of the CouchDB server"
    )

    parser.add_argument(
        "--database",
        default="hnac",
        help="the database to dump"
    )

    parser.add_argument("output")

    return parser.parse_args()


def main():
    args = get_arguments()

    print("Dumping stories from {}".format(args.couchdb_url))

    server = Server(args.couchdb_url)
    database = server[args.database]

    cnt = 0
    tick_size = 1000
    batch = 100
    with open(args.output, "w") as f:
        for row in database.iterview("stories/by_doc_id", batch=batch,
                                     include_docs=True):
            f.write("{}\n".format(json.dumps(row.doc)))

            cnt += 1
            if (cnt % tick_size) == 0:
                print(".", end="", flush=True)

    print("\n")


if __name__ == "__main__":
    main()
