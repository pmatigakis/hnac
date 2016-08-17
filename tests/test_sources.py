from unittest import TestCase, main

from mock import patch

from hnac.sources import HackernewsStories

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
    @patch("hnac.sources.FirebaseApplication")
    def test_get_next_item(self, mocked_firebase_application):
        instance = mocked_firebase_application.return_value
        instance.get.side_effect = firebase_get

        source = HackernewsStories()

        stories = [story for story in source.items()]

        self.assertEqual(len(stories), 2)

        self.assertDictEqual(stories[0], story_1_data)
        self.assertDictEqual(stories[1], story_2_data)


if __name__ == "__main__":
    main()
