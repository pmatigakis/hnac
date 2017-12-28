from unittest import TestCase, main
from unittest.mock import patch, MagicMock, call

from requests import RequestException

from hnac.sources import HackernewsStories, RetryCountExceeded
from hnac.exceptions import JobExecutionError

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
    @patch("hnac.sources.create_hackernews_firebase_app")
    def test_get_next_item(self, create_hackernews_firebase_app):
        instance = MagicMock()
        create_hackernews_firebase_app.return_value = instance
        instance.get.side_effect = firebase_get

        source = HackernewsStories()

        stories = [story for story in source.items()]

        self.assertEqual(len(stories), 2)

        self.assertDictEqual(stories[0], story_1_data)
        self.assertDictEqual(stories[1], story_2_data)

    @patch("hnac.sources.HackernewsStories._get_new_stories")
    def test_connection_retry_exceeded_while_retrieving_new_stories(
            self, get_new_stories_mock):
        get_new_stories_mock.side_effect = RetryCountExceeded
        source = HackernewsStories()

        with self.assertRaises(JobExecutionError):
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

    @patch("hnac.sources.sleep")
    @patch("hnac.sources.create_hackernews_firebase_app")
    def test_abort_after_failing_to_retrieve_new_stories(
            self, create_hackernews_firebase_app_mock, sleep_mock):

        def firebase_get(url, *args):
            if url == "/v0/newstories":
                raise RequestException("something went wrong")
            elif url == "/v0/item":
                return story_1_data

        instance = MagicMock()
        create_hackernews_firebase_app_mock.return_value = instance
        instance.get.side_effect = firebase_get
        sleep_mock.return_value = None

        source = HackernewsStories()

        with self.assertRaises(JobExecutionError):
            [item for item in source.items()]

        instance.get.assert_has_calls(
            [
                call("/v0/newstories", None),
                call("/v0/newstories", None),
                call("/v0/newstories", None)
            ]
        )

    @patch("hnac.sources.sleep")
    @patch("hnac.sources.create_hackernews_firebase_app")
    def test_abort_after_failing_to_retrieve_story(
            self, create_hackernews_firebase_app_mock, sleep_mock):

        def firebase_get(url, *args):
            if url == "/v0/newstories":
                return [123, 456]
            elif url == "/v0/item":
                raise RequestException("something went wrong")

        instance = MagicMock()
        create_hackernews_firebase_app_mock.return_value = instance
        instance.get.side_effect = firebase_get
        sleep_mock.return_value = None

        source = HackernewsStories()

        with self.assertRaises(JobExecutionError):
            [item for item in source.items()]

        instance.get.assert_has_calls(
            [
                call("/v0/item", 123),
                call("/v0/item", 123),
                call("/v0/item", 123)
            ]
        )


if __name__ == "__main__":
    main()
