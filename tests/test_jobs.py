from unittest import TestCase, main
from unittest.mock import MagicMock, call, patch

from hnac.jobs import Job
from hnac.exceptions import ItemProcessingError, JobExecutionError
from hnac.processors import Processors


class JobTests(TestCase):
    def test_run_job(self):
        Source = MagicMock()
        source_instance = Source.return_value
        source_instance.items.return_value = [1, 2, 3]
        source_instance.job_started = MagicMock()
        source_instance.job_finished = MagicMock()

        Processor = MagicMock()
        processor_instance = Processor.return_value
        processor_instance.process_item = MagicMock()
        processor_instance.process_item.return_value = True
        processor_instance.job_started = MagicMock()
        processor_instance.job_finished = MagicMock()

        processors = Processors()
        processors.add(processor_instance)

        job = Job(source_instance, processors)

        result = job.run()

        self.assertFalse(result.failed)
        source_instance.job_started.assert_called_with(job)
        processor_instance.job_started.assert_called_with(job)

        source_instance.items.assert_called_with()

        calls = [
            call(source_instance, 1),
            call(source_instance, 2),
            call(source_instance, 3)
        ]

        processor_instance.process_item.assert_has_calls(calls)

        source_instance.job_finished.assert_called_with(job)
        processor_instance.job_finished.assert_called_with(job)

    def test_processor_raised_an_exception_while_processing_item(self):
        Source = MagicMock()
        source_instance = Source.return_value
        source_instance.items.return_value = [1, 2, 3]
        source_instance.job_started = MagicMock()
        source_instance.job_finished = MagicMock()

        Processor = MagicMock()
        processor_instance = Processor.return_value
        processor_instance.process_item = MagicMock()
        processor_instance.process_item.side_effect = ValueError

        processors = Processors()
        processors.add(processor_instance)

        job = Job(source_instance, processors)

        result = job.run()

        self.assertFalse(result.failed)

    def test_processor_failed_to_process_item(self):
        source_instance = MagicMock()
        source_instance.items.return_value = [1, 2, 3]

        processor_instance = MagicMock()
        processor_instance.process_item.side_effect = ItemProcessingError

        processors = Processors()
        processors.add(processor_instance)

        job = Job(source_instance, processors)
        result = job.run()

        self.assertFalse(result.failed)
        processor_instance.process_item.assert_has_calls(
            [
                call(source_instance, 1),
                call(source_instance, 2),
                call(source_instance, 3)
            ]
        )
        source_instance.items.assert_called_with()

    @patch("hnac.jobs.Job._retrieve_and_process_items")
    def test_job_failed_because_a_job_execution_exception_was_raised(
            self, retrieve_and_process_items_mock):
        retrieve_and_process_items_mock.side_effect = JobExecutionError

        source_instance = MagicMock()
        processor_instance = MagicMock()
        processors = Processors()
        processors.add(processor_instance)

        job = Job(source_instance, processors)
        result = job.run()

        self.assertTrue(result.failed)
        processor_instance.process_item.assert_not_called()

    def test_job_failed_because_the_source_raised_an_exception(self):
        source_instance = MagicMock()
        source_instance.items.side_effect = ValueError

        processor_instance = MagicMock()

        processors = Processors()
        processors.add(processor_instance)

        job = Job(source_instance, processors)
        result = job.run()

        self.assertTrue(result.failed)
        processor_instance.process_item.assert_not_called()
        source_instance.items.assert_called_with()


if __name__ == "__main__":
    main()
