import logging
from uuid import uuid4
from datetime import datetime

from hnac.sources import HackernewsStories
from hnac.exceptions import JobExecutionError, ItemProcessingError


logger = logging.getLogger(__name__)


class JobExecutionResult(object):
    def __init__(self, job, start_time, end_time, processed_item_count,
                 failed):
        self.job = job
        self.start_time = start_time
        self.end_time = end_time
        self.processed_item_count = processed_item_count
        self.failed = failed


class Job(object):
    """Crawl job base class"""

    def __init__(self, source, processors):
        """Create a new Job object

        :param Source source: the hackernews source object to use
        :param list[Processor] processors: the hackernews item processors
        """
        self._source = source
        self._processors = processors

        self.id = uuid4().hex

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
            processor.process_item(self._source, item)
        except ItemProcessingError:
            logger.info("processor %s failed to process item", type(processor))
        except Exception:
            logger.exception("processor failed to process item")

    def _process_item_with_processors(self, item):
        for processor in self._processors:
            self._process_item(processor, item)

    def _retrieve_and_process_items(self):
        processed_item_count = 0

        try:
            for item in self._source.items():
                self._process_item_with_processors(item)
                processed_item_count += 1
        except Exception as e:
            logger.exception(
                "failed to retrieve and process items for job %s", self.id)
            raise JobExecutionError(
                "failed to retrieve and process items") from e

        return processed_item_count

    def run(self):
        """Start the job"""
        logger.info("starting job with id %s", self.id)

        start_time = datetime.utcnow()
        self._notify_job_started()

        failed = False
        processed_item_count = 0
        try:
            processed_item_count = self._retrieve_and_process_items()
        except JobExecutionError:
            logger.info("Failed to execute job with id %s", self.id)
            failed = True
        finally:
            self._notify_job_finished()

        logger.info("Finished executing job with id %s", self.id)

        end_time = datetime.utcnow()
        return JobExecutionResult(
            job=self,
            start_time=start_time,
            end_time=end_time,
            processed_item_count=processed_item_count,
            failed=failed
        )


class HackernewsCrawlJob(Job):
    """Hackaernews crawl job"""

    def __init__(self, config, processors):
        """Create a new HackernewsCrawlJob object

        :param dict config: the job configuration
        :param list[Processor] processors: the hackernews item processors
        """
        source = HackernewsStories()
        source.configure(config)

        super(HackernewsCrawlJob, self).__init__(source, processors)
