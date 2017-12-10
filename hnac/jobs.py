import logging
from uuid import uuid4
from datetime import datetime


logger = logging.getLogger(__name__)


class JobExecutionError(Exception):
    pass


class Report(object):
    def __init__(self, job, start_time, end_time):
        self.job = job
        self.start_time = start_time
        self.end_time = end_time


class Job(object):
    def __init__(self, config, source, processors):
        self._config = config
        self._source = source
        self._processors = processors

        self.id = uuid4().hex
        self.processed_item_count = 0
        self.failed = False

    def _notify_job_started(self):
        self._source.job_started(self)

        for processor in self._processors:
            processor.job_started(self)

    def _notify_job_finished(self):
        self._source.job_finished(self)

        for processor in self._processors:
            processor.job_finished(self)

    def _process_item(self, processor, item):
        try:
            result = processor.process_item(self._source, item)
        except Exception:
            logger.exception("processor failed to process item")
            return

        if not result:
            logger.error("Processor didn't process successfully "
                         "this item")

    def _process_item_with_processors(self, item):
        for processor in self._processors:
            self._process_item(processor, item)

        self.processed_item_count += 1

    def _retrieve_and_process_items(self):
        for item in self._source.items():
            self._process_item_with_processors(item)

    def run(self):
        logger.info("starting job with id %s", self.id)

        self.failed = False
        self.processed_item_count = 0

        start_time = datetime.utcnow()
        self._notify_job_started()

        try:
            self._retrieve_and_process_items()
        except (KeyboardInterrupt, SystemExit):
            logger.warning("Job with %s stopped by user or system", self.id)
        except JobExecutionError:
            logger.error("Failed to execute job with id %s", self.id)
            self.failed = True
        except Exception:
            logger.exception("Error occurred in job with id %s", self.id)

            self.failed = True
        finally:
            self._notify_job_finished()

        logger.info("Finished executing job with id %s", self.id)

        end_time = datetime.utcnow()
        return Report(self, start_time, end_time)
