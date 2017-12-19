from unittest import TestCase, main
from unittest.mock import patch, MagicMock

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


if __name__ == "__main__":
    main()
