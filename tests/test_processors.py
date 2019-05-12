from unittest import TestCase, main
from unittest.mock import MagicMock

from hnac.processors import Processors


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
