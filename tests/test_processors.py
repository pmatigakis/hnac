from unittest import TestCase, main

from mock import MagicMock

from hnac.processors import CouchDBStorage

from mock_data import story_1_data


class NewStoryMatcher(object):
    def __init__(self, story_data):
        self.story_data = story_data

    def __eq__(self, other):
        if other["data"] != self.story_data:
            return False

        if "updated_at" not in other:
            return False

        return True


class UpdateStoryMatcher(object):
    def __init__(self, story_data):
        self.story_data = story_data

    def __eq__(self, other):
        if other["data"] != self.story_data:
            return False

        if "updated_at" not in other:
            return False

        if "_id" not in other:
            return False

        if "_rev" not in other:
            return False

        return True


class CouchDBStorageTests(TestCase):
    def test_configure(self):
        UPDATE_DELTA = 123
        HOST = "localhost:9999"
        DATABASE_NAME = "test_database"

        config = {
            "COUCHDB_SERVER": HOST,
            "COUCHDB_DATABASE": DATABASE_NAME,
            "CRAWLER_STORY_UPDATE_DELTA": UPDATE_DELTA
        }

        processor = CouchDBStorage()
        processor._init_database = MagicMock()

        processor.configure(config)

        self.assertEqual(processor.update_delta, UPDATE_DELTA)

        processor._init_database.assert_called_once_with(HOST, DATABASE_NAME)

    def test_save_new_story(self):
        processor = CouchDBStorage()

        mocked_db = MagicMock()
        mocked_db_instance = mocked_db.return_value
        mocked_db_instance.get = MagicMock(return_value=None)
        mocked_db_instance.__setitem__ = MagicMock()

        processor._db = mocked_db_instance

        processor.process_item(None, story_1_data)

        processor._db.get.assert_called_once_with('hackernews/item/11976079')

        processor._db.__setitem__.assert_called_once_with(
            'hackernews/item/11976079',
            NewStoryMatcher(story_1_data)
        )

    def test_update_story(self):
        processor = CouchDBStorage()

        existing_story_data = {
            "data": story_1_data,
            "updated_at": 123456,
            "_id": "hackernews/item/11976079",
            "_rev": "abcde"
        }

        mocked_db = MagicMock()
        mocked_db_instance = mocked_db.return_value
        mocked_db_instance.get = MagicMock(return_value=existing_story_data)
        mocked_db_instance.__setitem__ = MagicMock()

        processor._db = mocked_db_instance

        processor.process_item(None, story_1_data)

        processor._db.get.assert_called_once_with('hackernews/item/11976079')

        processor._db.__setitem__.assert_called_once_with(
            'hackernews/item/11976079',
            UpdateStoryMatcher(story_1_data)
        )


if __name__ == "__main__":
    main()
