from unittest import TestCase, main
from unittest.mock import MagicMock

from hnac.processors import CouchDBStorage, Processors
from hnac.models import HackernewsStoryItem

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
        HOST = "localhost:9999"
        DATABASE_NAME = "test_database"

        config = {
            "COUCHDB_SERVER": HOST,
            "COUCHDB_DATABASE": DATABASE_NAME
        }

        processor = CouchDBStorage()
        processor._init_database = MagicMock()

        processor.configure(config)

        processor._init_database.assert_called_once_with(HOST, DATABASE_NAME)

    def test_save_new_story(self):
        processor = CouchDBStorage()

        mocked_db = MagicMock()
        mocked_db_instance = mocked_db.return_value
        mocked_db_instance.get = MagicMock(return_value=None)
        mocked_db_instance.__setitem__ = MagicMock()

        processor._db = mocked_db_instance

        processor.process_item(None, HackernewsStoryItem(**story_1_data))

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

        processor.process_item(None, HackernewsStoryItem(**story_1_data))

        processor._db.get.assert_called_once_with('hackernews/item/11976079')

        processor._db.__setitem__.assert_called_once_with(
            'hackernews/item/11976079',
            UpdateStoryMatcher(story_1_data)
        )


class ProcessorsTests(TestCase):
    def test_add_processors(self):
        processors = Processors()

        processor_1 = MagicMock()
        processor_2 = MagicMock()
        processor_3 = MagicMock()

        processors.add(processor_1)
        processors.add(processor_2)
        processors.add(processor_3)

        self.assertEqual(processors.count, 3)
        self.assertEqual(
            processors._processors,
            [processor_1, processor_2, processor_3]
        )

    def test_add_multiple_processors(self):
        processors = Processors()

        processor_1 = MagicMock()
        processor_2 = MagicMock()
        processor_3 = MagicMock()

        processors.add_multiple([processor_1, processor_2, processor_3])

        self.assertEqual(processors.count, 3)
        self.assertEqual(
            processors._processors,
            [processor_1, processor_2, processor_3]
        )

    def test_get_processor(self):
        processors = Processors()

        processor_1 = MagicMock()
        processor_2 = MagicMock()

        processors.add(processor_1)
        processors.add(processor_2)

        self.assertEqual(processors.get(0), processor_1)
        self.assertEqual(processors.get(1), processor_2)
        self.assertRaises(IndexError, processors.get, 2)

    def test_remove_processor(self):
        processors = Processors()

        processor_1 = MagicMock()
        processor_2 = MagicMock()

        processors.add(processor_1)
        processors.add(processor_2)

        processors.remove(0)
        self.assertEqual(
            processors._processors,
            [processor_2]
        )

    def test_configure_processors(self):
        processors = Processors()
        processor = MagicMock()
        processors.add(processor)

        config = {}
        processors.configure_all(config)

        processor.configure.assert_called_once_with(config)

    def test_job_started(self):
        processors = Processors()
        processor = MagicMock()
        processors.add(processor)
        job = MagicMock()

        processors.job_started(job)
        processor.job_started.assert_called_once_with(job)

    def test_job_finished(self):
        processors = Processors()
        processor = MagicMock()
        processors.add(processor)
        job = MagicMock()

        processors.job_finished(job)
        processor.job_finished.assert_called_once_with(job)

    def test_process_item(self):
        processors = Processors()
        processor = MagicMock()
        processors.add(processor)
        source = MagicMock()
        item = MagicMock()

        processors.process_item(source, item)
        processor.process_item.assert_called_once_with(source, item)


if __name__ == "__main__":
    main()
