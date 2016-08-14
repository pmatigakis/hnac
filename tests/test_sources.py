import json
from unittest import TestCase, main
import re

import httpretty

from hnac.sources import HackernewsStories

from mock_data import story_1_data


class HackernewsStoriesItemRetrieval(TestCase):
    def setUp(self):
        self.skipTest("SSL issue with httpretty")

        httpretty.register_uri(
            httpretty.GET,
            "https://hacker-news.firebaseio.com/v0/newstories",
            body="[11976079]",
            content="application/json"
        )

        httpretty.register_uri(
            httpretty.GET,
            re.compile(r"http://hacker-news.firebaseio.com/v0/item/(\d+)"),
            body=json.dumps(story_1_data),
            content="application/json"
        )

    @httpretty.activate
    def test_get_next_item(self):
        HackernewsStories.api_endpoint = "http://hacker-news.firebaseio.com"

        source = HackernewsStories()

        for story in source.items():
            self.assertDictEqual(story, story_1_data)


if __name__ == "__main__":
    main()
