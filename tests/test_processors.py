from unittest import TestCase, main
from ConfigParser import ConfigParser

from hnac.processors import SQLAlchemyStorage
from hnac.models import Story
from hnac.schemas import HackernewsStorySchema

from mock_data import story_1_data


class SQLAlchemyStorageTests(TestCase):
    def setUp(self):
        self.config = {}
        self.config["HNAC_DB"] = "sqlite:///:memory:"

    def test_process_item(self):
        processor = SQLAlchemyStorage()

        processor.configure(self.config)

        processor.job_started(None)

        schema = HackernewsStorySchema()
        story_item = schema.load(story_1_data) 

        story = processor.process_item(None, story_item)

        self.assertIsNotNone(story)
        self.assertIsNotNone(story.id)
        self.assertEqual(story.id, story_1_data["id"])
        self.assertEqual(story.user.username, story_1_data["by"])
        self.assertEqual(story.comment_count, story_1_data["descendants"])
        self.assertEqual(story.score, story_1_data["score"])
        self.assertEqual(story.title, story_1_data["title"])
        self.assertEqual(story.url.url, story_1_data["url"])
        self.assertEqual(story.created_at_timestamp, story_1_data["time"])
        self.assertIsNotNone(story.created_at)
        self.assertIsNotNone(story.added_at)
        self.assertIsNone(story.updated_at)

        processor.job_finished(None)


class SQLAlchemyStorageItemUpdateTests(TestCase):
    def setUp(self):
        self.config = {}
        self.config["HNAC_DB"] = "sqlite:///:memory:"

    def test_process_item(self):
        processor = SQLAlchemyStorage()

        processor.configure(self.config)

        processor.job_started(None)

        Story.create_from_dict(processor._session, story_1_data)

        updated_story_data = story_1_data.copy()

        updated_story_data["score"] = 100
        updated_story_data["descendants"] = 200

        schema = HackernewsStorySchema()
        updated_story_item = schema.load(updated_story_data)

        story = processor.process_item(None, updated_story_item)

        self.assertIsNotNone(story)
        self.assertIsNotNone(story.id)
        self.assertEqual(story.id, story_1_data["id"])
        self.assertEqual(story.user.username, story_1_data["by"])

        self.assertEqual(story.comment_count,
                         updated_story_data["descendants"])

        self.assertEqual(story.score, updated_story_data["score"])
        self.assertEqual(story.title, story_1_data["title"])
        self.assertEqual(story.url.url, story_1_data["url"])
        self.assertEqual(story.created_at_timestamp, story_1_data["time"])
        self.assertIsNotNone(story.created_at)
        self.assertIsNotNone(story.added_at)
        self.assertIsNotNone(story.updated_at)

        processor.job_finished(None)


if __name__ == "__main__":
    main()
