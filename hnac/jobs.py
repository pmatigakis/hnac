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

    def run(self):
        logger.info("starting job with id %s", self.id)

        self.failed = False
        self.processed_item_count = 0

        start_time = datetime.utcnow()

        self._source.job_started(self)

        for processor in self._processors:
            processor.job_started(self)

        try:
            for item in self._source.items():
                for processor in self._processors:
                    processor.process_item(self._source, item)

                self.processed_item_count += 1

            logger.info("Finished job with id %s", self.id)
        except (KeyboardInterrupt, SystemExit):
            logger.info("Job with %s stopped by user or system", self.id)
        except JobExecutionError:
            logger.error("Failed to execute job with id %s", self.id)
            self.failed = True
        except Exception:
            logger.exception("Error occurred in job with id %s", self.id)

            self.failed = True
        finally:
            self._source.job_finished(self)

            for processor in self._processors:
                processor.job_finished(self)

        end_time = datetime.now()

        return Report(self, start_time, end_time)
