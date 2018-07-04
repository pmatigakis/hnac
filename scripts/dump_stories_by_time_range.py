from argparse import ArgumentParser
from urllib.parse import urljoin
import json

import requests


STORIES_SEARCH_ENDPOINT = "/api/v1/stories/search"


def dump_stories(f, args):
    headers = {
        "Authorization": args.token
    }

    params = {
        "order_by": "time",
        "desc": True,
        "limit": args.limit,
        "q": "time__gte={}+time__lte={}".format(args.start_time, args.end_time)
    }
    offset = 0

    while True:
        params["offset"] = offset
        response = requests.get(
            urljoin(args.api, STORIES_SEARCH_ENDPOINT),
            params=params,
            headers=headers
        )
        stories = response.json()
        if not stories:
            break
        for story in stories:
            f.write("{}\n".format(json.dumps(story)))
        offset += args.limit


def get_arguments():
    parser = ArgumentParser()
    parser.add_argument("--token", required=True)
    parser.add_argument("--api", default="http://localhost:5000")
    parser.add_argument("--output", required=True)
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--start-time", type=int, required=True, dest="start_time")
    parser.add_argument("--end-time", type=int, required=True, dest="end_time")

    return parser.parse_args()


def main():
    args = get_arguments()

    with open(args.output, "w") as f:
        dump_stories(f, args)


if __name__ == "__main__":
    main()
