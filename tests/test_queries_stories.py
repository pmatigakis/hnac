from unittest import TestCase, main

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from hnac.models import Base
from hnac.queries.stories import save_story, save_or_update_story

from mock_data import story_1_data


class SaveStoryTests(TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")

        Base.metadata.create_all(self.engine)

        self.Session = scoped_session(sessionmaker(bind=self.engine))

    def tearDown(self):
        self.Session.remove()

        Base.metadata.drop_all(self.engine)

    def test_save_story(self):
        session = self.Session()

        story = save_story(session, story_1_data)

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

    def test_save_or_update_story(self):
        session = self.Session()

        story = save_or_update_story(session, story_1_data)

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


class StoryUpdateTests(TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")

        Base.metadata.create_all(self.engine)

        self.Session = scoped_session(sessionmaker(bind=self.engine))

        session = self.Session()
        save_story(session, story_1_data)
        session.close()

    def tearDown(self):
        self.Session.remove()

        Base.metadata.drop_all(self.engine)

    def test_save_or_update_story(self):
        updated_story_data = story_1_data.copy()

        updated_story_data["score"] = 100
        updated_story_data["descendants"] = 200

        session = self.Session()

        story = save_or_update_story(session, updated_story_data)

        self.assertEqual(story.score, updated_story_data["score"])
        self.assertEqual(story.comment_count,
                         updated_story_data["descendants"])


if __name__ == "__main__":
    main()
