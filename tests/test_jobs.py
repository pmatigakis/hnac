from unittest import TestCase, main

from hnac.jobs import Job

from mock import MagicMock, call


class JobTests(TestCase):
    def test_run_jon(self):
        Source = MagicMock()
        source_instance = Source.return_value
        source_instance.items.return_value = [1, 2, 3]
        source_instance.job_started = MagicMock()
        source_instance.job_finished = MagicMock()

        Processor = MagicMock()
        processor_instance = Processor.return_value
        processor_instance.process_item = MagicMock()
        processor_instance.job_started = MagicMock()
        processor_instance.job_finished = MagicMock()

        config = {}

        job = Job(config, source_instance, [processor_instance])

        job.run()

        source_instance.job_started.assert_called_once()
        processor_instance.job_started.assert_called_once()

        source_instance.items.assert_called_once()

        calls = [
            call(source_instance, 1),
            call(source_instance, 2),
            call(source_instance, 3)
        ]

        processor_instance.process_item.assert_has_calls(calls)

        source_instance.job_finished.assert_called_once()
        processor_instance.job_finished.assert_called_once()


if __name__ == "__main__":
    main()
