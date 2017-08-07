from abc import ABCMeta, abstractmethod
import logging
from time import time, sleep

from firebase import FirebaseApplication
from requests import RequestException

from hnac.schemas import is_story_item
from hnac.jobs import JobExecutionError


logger = logging.getLogger(__name__)


class RetryCountExceeded(Exception):
    pass


class Source(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def items(self):
        pass

    def configure(self, config):
        pass

    def job_started(self, job):
        pass

    def job_finished(self, job):
        pass


class HackernewsStories(Source):
    def __init__(self):
        super(HackernewsStories, self).__init__()

        self.wait_time = 1.0
        self.backoff_time = 5.0
        self.abort_after = 3

        self._last_request_time = 0.0

        api_endpoint = "https://hacker-news.firebaseio.com"

        self._firebase = FirebaseApplication(api_endpoint, None)

        self._story_ids = None

    def configure(self, config):
        if "CRAWLER_WAIT_TIME" in config:
            self.wait_time = config["CRAWLER_WAIT_TIME"]

        if "CRAWLER_BACKOFF_TIME" in config:
            self.backoff_time = config["CRAWLER_BACKOFF_TIME"]

        if "CRAWLER_ABORT_AFTER" in config:
            self.abort_after = config["CRAWLER_ABORT_AFTER"]

    def _throttle(self):
        time_diff = time() - self._last_request_time

        sleep_for = self.wait_time - time_diff

        if sleep_for > 0.0:
            logger.debug("sleeping due to throttling for %f seconds",
                         sleep_for)

            sleep(sleep_for)

    def _get_new_stories(self):
        failure_count = 0

        while True:
            try:
                return self._firebase.get("/v0/newstories", None)
            except RequestException:
                logger.exception("Failed to fetch new story ids")

                failure_count += 1
                if failure_count > self.abort_after:
                    raise RetryCountExceeded()

                sleep(self.backoff_time)

    def _get_story_data(self, story_id):
        logger.info("Fetching hackernews item %d", story_id)

        failure_count = 0

        while True:
            try:
                self._last_request_time = time()

                return self._firebase.get("/v0/item", story_id)
            except RequestException:
                logger.exception("Failed to fetch story %d", story_id)

                failure_count += 1
                if failure_count > self.abort_after:
                    raise RetryCountExceeded()

                sleep(self.backoff_time)

    def items(self):
        try:
            story_ids = self._get_new_stories()
        except RetryCountExceeded:
            logger.error("Job stopped because maximum retry count has been "
                         "exceeded while fetching new story id's")
            raise JobExecutionError()

        for story_id in story_ids:
            self._throttle()

            try:
                story_data = self._get_story_data(story_id)
            except RetryCountExceeded:
                logger.error("Job stopped because maximum retry count has "
                             "been exceeded while fetching stories")
                raise JobExecutionError()

            if not is_story_item(story_data):
                logger.warning("Hackernews item with id %d is not a story",
                               story_id)
                continue

            yield story_data
