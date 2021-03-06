import logging
from uuid import uuid4
from datetime import datetime

from hnac.sources import HackernewsStories, SourceError
from hnac.exceptions import JobExecutionError


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
        :param Processors processors: the hackernews item processors
        """
        self._source = source
        self._processors = processors

        self.id = uuid4().hex

    def _notify_job_started(self):
        self._source.job_started(self)
        self._processors.job_started(self)

    def _notify_job_finished(self):
        self._source.job_finished(self)
        self._processors.job_finished(self)

    def _retrieve_and_process_items(self):
        processed_item_count = 0

        try:
            for item in self._source.items():
                self._processors.process_item(self._source, item)
                processed_item_count += 1
        except SourceError as e:
            logger.info(
                "an error occurred while retrieving hackernews stories")
            raise JobExecutionError("failed to retrieve items") from e

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
        except Exception:
            logger.exception(
                "failed to retrieve and process items for job %s", self.id)
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
        :param Processors processors: the hackernews item processors
        """
        source = HackernewsStories()
        source.configure(config)

        super(HackernewsCrawlJob, self).__init__(source, processors)
