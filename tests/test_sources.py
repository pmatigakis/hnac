from unittest import TestCase, main
from unittest.mock import patch

from requests import RequestException
import responses

from hnac.sources import HackernewsStories, SourceError
from hnac.models import HackernewsStoryItem

from mock_data import story_1_data, story_2_data


def firebase_get(url, *args, **kwargs):
    if url == "/v0/newstories":
        return [11976079, 12299134]
    elif url == "/v0/item":
        story_id = args[0]

        stories = {
            11976079: story_1_data,
            12299134: story_2_data
        }

        return stories[story_id]


class HackernewsStoriesItemRetrieval(TestCase):
    @responses.activate
    def test_get_next_item(self):
        responses.add(
            responses.GET,
            'https://hacker-news.firebaseio.com/v0/newstories.json',
            json=[story_1_data["id"], story_2_data["id"]],
            status=200
        )

        responses.add(
            responses.GET,
            f'https://hacker-news.firebaseio.com'
            f'/v0/item/{story_1_data["id"]}.json',
            json=story_1_data,
            status=200
        )

        responses.add(
            responses.GET,
            f'https://hacker-news.firebaseio.com'
            f'/v0/item/{story_2_data["id"]}.json',
            json=story_2_data,
            status=200
        )

        source = HackernewsStories()

        stories = [story for story in source.items()]

        self.assertEqual(len(stories), 2)

        self.assertEqual(stories[0], HackernewsStoryItem(
            raw_data=story_1_data, **story_1_data))
        self.assertEqual(stories[1], HackernewsStoryItem(
            raw_data=story_2_data, **story_2_data))

    @patch("hnac.sources.sleep")
    @patch("hnac.sources.HackernewsStories._execute_new_stories_request")
    def test_connection_retry_exceeded_while_retrieving_new_stories(
            self, _execute_new_stories_request_mock, sleep_mock):
        _execute_new_stories_request_mock.side_effect = RequestException
        sleep_mock.return_value = None

        source = HackernewsStories()

        with self.assertRaises(SourceError):
            [item for item in source.items()]

    @patch("hnac.sources.HackernewsStories._get_story_data")
    @patch("hnac.sources.HackernewsStories._get_new_stories")
    def test_received_items_are_not_stories(
            self, get_new_stories_mock, get_story_data_mock):
        get_new_stories_mock.return_value = [1]
        get_story_data_mock.return_value = {"hello": "world"}
        source = HackernewsStories()

        items = [item for item in source.items()]
        self.assertEquals(items, [])

    def test_configure(self):
        source = HackernewsStories()

        configuration = {
            "CRAWLER_WAIT_TIME": 111,
            "CRAWLER_BACKOFF_TIME": 222,
            "CRAWLER_ABORT_AFTER": 333
        }
        source.configure(configuration)

        self.assertEqual(source.wait_time, 111)
        self.assertEqual(source.backoff_time, 222)
        self.assertEqual(source.abort_after, 333)

    @responses.activate
    @patch("hnac.sources.sleep")
    def test_abort_after_failing_to_retrieve_new_stories(self, sleep_mock):
        responses.add(
            responses.GET,
            'https://hacker-news.firebaseio.com/v0/newstories.json',
            body=RequestException(),
            status=200
        )

        sleep_mock.return_value = None

        source = HackernewsStories()

        with self.assertRaises(SourceError):
            [item for item in source.items()]

    @responses.activate
    @patch("hnac.sources.sleep")
    def test_abort_after_failing_to_retrieve_story(self, sleep_mock):
        responses.add(
            responses.GET,
            'https://hacker-news.firebaseio.com/v0/newstories.json',
            json=[story_1_data["id"]],
            status=200
        )

        responses.add(
            responses.GET,
            f'https://hacker-news.firebaseio.com'
            f'/v0/item/{story_1_data["id"]}.json',
            body=RequestException(),
            status=500
        )

        sleep_mock.return_value = None

        source = HackernewsStories()

        with self.assertRaises(SourceError):
            [item for item in source.items()]


if __name__ == "__main__":
    main()
